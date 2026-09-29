"""Minimal procedural 2D VFX raster engine.

All drawing happens in two float buffers:
  E : additive emission (RGB, linear-ish, unbounded) -> glow / light
  O : premultiplied RGBA occluder (normal blend)     -> debris, smoke
On export the emission is tone-mapped, converted to straight alpha
(alpha = max channel) and composited over the occluder layer, which gives a
true-transparent RGBA sprite that looks like its additive version on dark
backgrounds and has no black / white matte.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

SS = 3  # supersampling factor for polygon rasterisation


# --------------------------------------------------------------------------- utils
def col(hexstr, k=1.0):
    hexstr = hexstr.lstrip('#')
    return np.array([int(hexstr[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32) * k


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def ease_out(t, p=2.0):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** p


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode='constant')
    c = np.cumsum(p, axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma):
    """Approximate gaussian blur (3 box passes) on a 2D or HxWxC array."""
    if sigma <= 0.3:
        return a
    w = math.sqrt(12 * sigma * sigma / 3 + 1)
    r = max(1, int(round((w - 1) / 2)))
    out = a
    for _ in range(3):
        out = _box1d(out, r, 0)
        out = _box1d(out, r, 1)
    return out


def blur_dir(a, sigma_x, sigma_y):
    out = a
    rx = max(0, int(round(math.sqrt(12 * sigma_x * sigma_x / 3 + 1) - 1) // 2)) if sigma_x > 0.3 else 0
    ry = max(0, int(round(math.sqrt(12 * sigma_y * sigma_y / 3 + 1) - 1) // 2)) if sigma_y > 0.3 else 0
    for _ in range(3):
        if rx:
            out = _box1d(out, rx, 1)
        if ry:
            out = _box1d(out, ry, 0)
    return out


def noise(w, h, cells_x, cells_y, seed, octaves=3, persistence=0.5):
    """Value-noise fBm in [0,1] (bicubic upsampled random grids)."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    cx, cy = cells_x, cells_y
    for _ in range(octaves):
        g = rng.random((max(2, int(cy)), max(2, int(cx)))).astype(np.float32)
        im = Image.fromarray(g, 'F').resize((w, h), Image.BICUBIC)
        acc += np.asarray(im, np.float32) * amp
        tot += amp
        amp *= persistence
        cx *= 2
        cy *= 2
    acc /= tot
    lo, hi = np.percentile(acc, 1), np.percentile(acc, 99)
    return np.clip((acc - lo) / (hi - lo + 1e-6), 0, 1)


def sample(img, u, v):
    """Bilinear sample a 2D array at float pixel coords (u=x, v=y), wrap in x, clamp in y."""
    h, w = img.shape
    u = np.mod(u, w)
    v = np.clip(v, 0, h - 1.001)
    x0 = np.floor(u).astype(np.int32)
    y0 = np.floor(v).astype(np.int32)
    fx = u - x0
    fy = v - y0
    x1 = (x0 + 1) % w
    y1 = np.minimum(y0 + 1, h - 1)
    a = img[y0, x0] * (1 - fx) + img[y0, x1] * fx
    b = img[y1, x0] * (1 - fx) + img[y1, x1] * fx
    return a * (1 - fy) + b * fy


def grid(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x + 0.5, y + 0.5


# ----------------------------------------------------------------------- geometry
def catmull(points, n=64):
    """Catmull-Rom spline through points -> (n,2) array."""
    p = np.asarray(points, np.float32)
    if len(p) < 3:
        t = np.linspace(0, 1, n)[:, None]
        return p[0] * (1 - t) + p[-1] * t
    p = np.vstack([p[0] * 2 - p[1], p, p[-1] * 2 - p[-2]])
    segs = len(p) - 3
    out = []
    for i in range(n):
        s = i / (n - 1) * segs
        k = min(int(s), segs - 1)
        t = s - k
        p0, p1, p2, p3 = p[k], p[k + 1], p[k + 2], p[k + 3]
        t2, t3 = t * t, t * t * t
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return np.array(out, np.float32)


def arc_pts(cx, cy, rx, ry, a0, a1, n=96, rot=0.0):
    """Points on an ellipse arc; angles in degrees (0 = +x, 90 = +y/down)."""
    a = np.radians(np.linspace(a0, a1, n))
    x = np.cos(a) * rx
    y = np.sin(a) * ry
    if rot:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        x, y = x * c - y * s, x * s + y * c
    return np.stack([cx + x, cy + y], 1).astype(np.float32)


def line_pts(x0, y0, x1, y1, n=48):
    t = np.linspace(0, 1, n)[:, None]
    return (np.array([x0, y0]) * (1 - t) + np.array([x1, y1]) * t).astype(np.float32)


def profile(n, head=0.15, tail=0.15, lo=0.0, peak=1.0, pos=None):
    """Taper profile along a stroke: rises over `head`, falls over `tail`."""
    t = np.linspace(0, 1, n)
    up = smooth(t / max(head, 1e-4)) if head > 0 else np.ones(n)
    dn = smooth((1 - t) / max(tail, 1e-4)) if tail > 0 else np.ones(n)
    return lo + (peak - lo) * up * dn


# ------------------------------------------------------------------------- canvas
class FX:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.E = np.zeros((h, w, 3), np.float32)
        self.O = np.zeros((h, w, 4), np.float32)

    # ---- raster primitives (return float masks) ----
    def strip(self, pts, widths, values=None, soft=0.0):
        """Tapered quad strip along pts with per-point widths & intensity values."""
        pts = np.asarray(pts, np.float32)
        n = len(pts)
        widths = np.broadcast_to(np.asarray(widths, np.float32), (n,))
        values = np.ones(n, np.float32) if values is None else np.broadcast_to(
            np.asarray(values, np.float32), (n,))
        d = np.gradient(pts, axis=0)
        ln = np.linalg.norm(d, axis=1, keepdims=True) + 1e-6
        nrm = np.stack([-d[:, 1], d[:, 0]], 1) / ln
        L = pts + nrm * widths[:, None] / 2
        R = pts - nrm * widths[:, None] / 2
        pad = float(widths.max()) + 4
        x0 = max(0, int(pts[:, 0].min() - pad))
        y0 = max(0, int(pts[:, 1].min() - pad))
        x1 = min(self.w, int(pts[:, 0].max() + pad) + 1)
        y1 = min(self.h, int(pts[:, 1].max() + pad) + 1)
        out = np.zeros((self.h, self.w), np.float32)
        if x1 <= x0 or y1 <= y0:
            return out
        bw, bh = x1 - x0, y1 - y0
        im = Image.new('L', (bw * SS, bh * SS), 0)
        dr = ImageDraw.Draw(im)
        off = np.array([x0, y0], np.float32)
        for i in range(n - 1):
            v = int(np.clip((values[i] + values[i + 1]) * 0.5, 0, 1) * 255)
            if v <= 0:
                continue
            quad = np.array([L[i], L[i + 1], R[i + 1], R[i]]) - off
            dr.polygon([tuple(q) for q in (quad * SS)], fill=v)
        m = np.asarray(im.resize((bw, bh), Image.BOX), np.float32) / 255.0
        out[y0:y1, x0:x1] = m
        if soft > 0:
            out = blur(out, soft)
        return out

    def poly(self, pts, value=1.0):
        pts = np.asarray(pts, np.float32)
        im = Image.new('L', (self.w * SS, self.h * SS), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in pts * SS], fill=int(np.clip(value, 0, 1) * 255))
        return np.asarray(im.resize((self.w, self.h), Image.BOX), np.float32) / 255.0

    def radial(self, cx, cy, r, sx=1.0, sy=1.0, power=2.0):
        x, y = grid(self.w, self.h)
        d = np.sqrt(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2) / r
        return np.exp(-(d ** power) * 2.0).astype(np.float32)

    def star(self, cx, cy, length, width, n=4, rot=0.0, lengths=None):
        """n-point sharp star made of tapered rays."""
        m = np.zeros((self.h, self.w), np.float32)
        for i in range(n):
            a = math.radians(rot + 360.0 * i / n)
            L = length if lengths is None else lengths[i % len(lengths)]
            pts = line_pts(cx, cy, cx + math.cos(a) * L, cy + math.sin(a) * L, 24)
            w = np.linspace(width, 0.2, 24)
            m = np.maximum(m, self.strip(pts, w, np.linspace(1, 0.15, 24)))
        return m

    # ---- compositing ----
    def add(self, mask, color, k=1.0):
        self.E += mask[..., None] * (np.asarray(color, np.float32) * k)

    def glow(self, mask, color, sigma, k=1.0):
        self.add(blur(mask, sigma), color, k)

    def line(self, pts, widths, values, core, halo, glow_sigma=6, glow_k=1.0, core_k=1.0,
             halo_scale=2.5, halo_k=0.5):
        """Convenience: bright core + wider soft halo + blurred glow."""
        m = self.strip(pts, widths, values)
        self.add(m, core, core_k)
        if halo_k > 0:
            h = self.strip(pts, np.asarray(widths) * halo_scale, values, soft=1.5)
            self.add(h, halo, halo_k)
        if glow_k > 0:
            self.glow(m, halo, glow_sigma, glow_k)
        return m

    def over(self, mask, color, alpha=1.0):
        a = np.clip(mask * alpha, 0, 1)[..., None]
        c = np.asarray(color, np.float32)
        self.O[..., :3] = c * a + self.O[..., :3] * (1 - a)
        self.O[..., 3:] = a + self.O[..., 3:] * (1 - a)

    def mul_emission(self, mask):
        self.E *= mask[..., None]

    # ---- export ----
    def rgba(self, exposure=1.0, bleed=0.6):
        E = self.E * exposure
        excess = np.clip(E.max(-1) - 1.0, 0, None)
        E = E + excess[..., None] * bleed          # over-bright light desaturates to white
        T = 1.0 - np.exp(-E * 1.35)
        a = np.clip(T.max(-1), 0, 1)
        rgb_p = T + self.O[..., :3] * (1 - a[..., None])
        A = a + self.O[..., 3] * (1 - a)
        rgb = np.where(A[..., None] > 1e-5, rgb_p / np.maximum(A[..., None], 1e-5), 0)
        out = np.dstack([np.clip(rgb, 0, 1), np.clip(A, 0, 1)])
        return out


# ------------------------------------------------------------------------- export
def to_image(arr):
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    a[a[..., 3] == 0, :3] = 0
    return Image.fromarray(a, 'RGBA')


def bbox_union(frames, thresh=3, pad=8):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for f in frames:
        al = (f[..., 3] * 255) > thresh
        if not al.any():
            continue
        ys, xs = np.where(al)
        xs0.append(xs.min()); xs1.append(xs.max())
        ys0.append(ys.min()); ys1.append(ys.max())
    h, w = frames[0].shape[:2]
    if not xs0:
        return 0, 0, w, h
    x0 = max(0, min(xs0) - pad); y0 = max(0, min(ys0) - pad)
    x1 = min(w, max(xs1) + pad + 1); y1 = min(h, max(ys1) + pad + 1)
    # even dimensions keep GPU / atlas packers happy
    if (x1 - x0) % 2:
        if x1 < w: x1 += 1
        elif x0 > 0: x0 -= 1
    if (y1 - y0) % 2:
        if y1 < h: y1 += 1
        elif y0 > 0: y0 -= 1
    return x0, y0, x1, y1


def save_frames(frames, out_dir, name, pivot, fmt='webp', crop=True):
    """Save a list of RGBA float frames sharing one crop box.

    pivot: (px, py) in source-canvas pixels. Returns metadata with the pivot
    expressed as a normalised Cocos anchorPoint (0,0 = bottom-left).
    """
    os.makedirs(out_dir, exist_ok=True)
    x0, y0, x1, y1 = bbox_union(frames) if crop else (0, 0, frames[0].shape[1], frames[0].shape[0])
    files = []
    for i, f in enumerate(frames, 1):
        im = to_image(f[y0:y1, x0:x1])
        fn = f'{name}_{i:02d}.{fmt}'
        p = os.path.join(out_dir, fn)
        if fmt == 'webp':
            im.save(p, 'WEBP', quality=92, alpha_quality=100, method=6)
        else:
            im.save(p, 'PNG', optimize=True)
        files.append(fn)
    w, h = x1 - x0, y1 - y0
    ax = (pivot[0] - x0) / w
    ay = 1.0 - (pivot[1] - y0) / h
    return {'files': files, 'size': [int(w), int(h)], 'anchor': [round(float(ax), 4), round(float(ay), 4)],
            'source_canvas': [int(frames[0].shape[1]), int(frames[0].shape[0])]}
