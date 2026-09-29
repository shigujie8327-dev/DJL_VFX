"""Shared palette + reusable shape builders for Linchong (LC) VFX."""
import math

import numpy as np

from engine import FX, col, line_pts, arc_pts, catmull, profile, blur, noise, smooth, grid, sample

# ---- palettes: each skill inherits the DNA of its finalised Wiki icon ----------------
WHITE = col('#ffffff')
SILVER = col('#e4ecf6')          # 银白
SILVER_BLUE = col('#b9cde6')
SILVER_GREY = col('#a9adb4')     # 银灰

# 疾风刺 赤红 / 银白
CRIMSON = col('#ff1a22')
CRIMSON_DEEP = col('#a3000f')
CRIMSON_HOT = col('#ff5a4a')

# 回马枪 铜橙 / 金白
COPPER = col('#ff6a1c')
COPPER_DEEP = col('#b2360a')
GOLD_WHITE = col('#ffe7b0')

# 横扫千军 橙金 / 银白
ORANGE_GOLD = col('#ff9a1e')
ORANGE_DEEP = col('#c85a08')
AMBER = col('#ffc350')

# 枪阵 冰蓝 / 银白
ICE = col('#3f9bff')
ICE_DEEP = col('#1650c8')
ICE_PALE = col('#b8e0ff')

# 豹子头 香槟金 / 银灰
CHAMPAGNE = col('#f2d49a')
CHAMPAGNE_DEEP = col('#b8904a')

DEBRIS = col('#141110')


def spearhead_outline(tip, length, width, angle_deg=0.0, guard=True):
    """Leaf-shaped spear blade (枪锋) polygon + ridge line, pointing along angle."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tx, ty = tip
    # local coordinates: u from 0 (tip) backwards to length; v sideways
    prof = [(0.0, 0.0), (0.18, 0.30), (0.42, 0.50), (0.62, 0.42), (0.80, 0.20), (0.86, 0.12)]
    left = [(tx - ux * length * u + nx * width * v, ty - uy * length * u + ny * width * v) for u, v in prof]
    right = [(tx - ux * length * u - nx * width * v, ty - uy * length * u - ny * width * v) for u, v in prof]
    blade = left + right[::-1]
    socket = None
    if guard:
        g0 = 0.86
        g1 = 1.08
        socket = [(tx - ux * length * g0 + nx * width * 0.16, ty - uy * length * g0 + ny * width * 0.16),
                  (tx - ux * length * g1 + nx * width * 0.10, ty - uy * length * g1 + ny * width * 0.10),
                  (tx - ux * length * g1 - nx * width * 0.10, ty - uy * length * g1 - ny * width * 0.10),
                  (tx - ux * length * g0 - nx * width * 0.16, ty - uy * length * g0 - ny * width * 0.16)]
    ridge = line_pts(tx, ty, tx - ux * length * 0.84, ty - uy * length * 0.84, 24)
    return np.array(blade, np.float32), (np.array(socket, np.float32) if socket else None), ridge


def draw_spear_ghost(fx, tip, length, width, angle, shaft_len, color_glow, color_core, k=1.0, fill=0.35):
    """Semi-transparent silver spear (blade + shaft) with coloured glow."""
    blade, socket, ridge = spearhead_outline(tip, length, width, angle)
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    body = fx.poly(blade)
    edge = np.clip(body - blur(body, 2.2) * 0.98, 0, 1) * 3.0
    fx.add(body, color_core, fill * k)
    fx.add(np.clip(edge, 0, 1), color_core, 1.1 * k)
    r = fx.strip(ridge, np.linspace(2.2, 1.0, 24), np.linspace(1.0, 0.5, 24))
    fx.add(r, color_core, 0.9 * k)
    if socket is not None:
        s = fx.poly(socket)
        fx.add(s, color_core, 0.55 * k)
    base = (tip[0] - ux * length * 1.08, tip[1] - uy * length * 1.08)
    sh = line_pts(base[0], base[1], base[0] - ux * shaft_len, base[1] - uy * shaft_len, 40)
    shaft = fx.strip(sh, np.linspace(width * 0.10, width * 0.08, 40), np.linspace(0.8, 0.0, 40))
    fx.add(shaft, color_core, 0.6 * k)
    everything = np.clip(body + shaft + r, 0, 1)
    fx.glow(everything, color_glow, 10, 0.9 * k)
    fx.glow(everything, color_glow, 28, 0.45 * k)
    return everything


def speed_streaks(fx, rng, n, x_range, y_center, spread, tip_x, color, k=1.0, w_range=(1.0, 4.0),
                  len_range=(250, 900), converge=True, bright_head=True):
    """Thin straight high-speed streaks (not fire) that converge toward tip_x."""
    acc = np.zeros((fx.h, fx.w), np.float32)
    for _ in range(n):
        L = rng.uniform(*len_range)
        x1 = rng.uniform(x_range[0] + L, x_range[1])
        x0 = x1 - L
        off = rng.normal(0, spread)
        # converge: vertical offset shrinks toward the tip
        def yy(x):
            f = (tip_x - x) / (tip_x - x_range[0] + 1e-6) if converge else 1.0
            return y_center + off * np.clip(f, 0.08, 1.2)
        pts = np.stack([np.linspace(x0, x1, 32), yy(np.linspace(x0, x1, 32))], 1)
        w = rng.uniform(*w_range)
        wid = np.linspace(w * 0.25, w, 32) if bright_head else np.full(32, w)
        val = np.linspace(0.1, 1.0, 32) ** 1.4 * rng.uniform(0.45, 1.0)
        acc += fx.strip(pts, wid, val)
    fx.add(acc, color, k)
    return acc


def ring_swirl(fx, rng, cx, cy, R, n, arc_len, rot, color, k=1.0, sy=1.0, width=(2, 7), rjit=0.22, bright_head=True):
    """Arc streaks orbiting a centre -> ring-shaped airflow."""
    acc = np.zeros((fx.h, fx.w), np.float32)
    for _ in range(n):
        r = R * (1 - rng.uniform(0, rjit))
        a0 = rng.uniform(0, 360) + rot
        L = arc_len * rng.uniform(0.6, 1.2)
        pts = arc_pts(cx, cy, r, r * sy, a0, a0 + L, 72)
        w = rng.uniform(*width)
        wid = np.sin(np.linspace(0, math.pi, 72)) ** 0.7 * w + 0.3
        val = (np.linspace(0.15, 1.0, 72) ** 1.2 if bright_head else np.ones(72)) * rng.uniform(0.5, 1.0)
        acc += fx.strip(pts, wid, val)
    fx.add(acc, color, k)
    return acc


def burst_rays(fx, rng, cx, cy, n, r_in, r_out, width, color, k=1.0, angle_center=0.0, angle_spread=360.0,
               sx=1.0, sy=1.0, bias_len=None):
    acc = np.zeros((fx.h, fx.w), np.float32)
    for i in range(n):
        if angle_spread >= 360:
            a = math.radians(360.0 * i / n + rng.uniform(-8, 8))
        else:
            a = math.radians(angle_center + rng.uniform(-angle_spread / 2, angle_spread / 2))
        ro = r_out * rng.uniform(0.55, 1.0)
        if bias_len is not None:
            ro *= bias_len(a)
        ri = r_in * rng.uniform(0.7, 1.2)
        p = line_pts(cx + math.cos(a) * ri * sx, cy + math.sin(a) * ri * sy,
                     cx + math.cos(a) * ro * sx, cy + math.sin(a) * ro * sy, 24)
        w = width * rng.uniform(0.5, 1.2)
        acc += fx.strip(p, np.linspace(w, 0.3, 24), np.linspace(1, 0.1, 24) * rng.uniform(0.5, 1))
    fx.add(acc, color, k)
    return acc


def shards(fx, rng, cx, cy, n, spread_x, spread_y, size, edge_color=None, edge_k=0.8, dir_x=1.0, alpha=0.95):
    """Dark angular debris (occluder) with a faint lit edge."""
    for _ in range(n):
        x = cx + rng.normal(0.35 * dir_x, 0.5) * spread_x
        y = cy + rng.normal(0, 0.5) * spread_y
        s = size * rng.uniform(0.35, 1.0)
        k = rng.integers(3, 6)
        angs = np.sort(rng.uniform(0, 2 * math.pi, k))
        rad = s * rng.uniform(0.45, 1.0, k)
        stretch = rng.uniform(1.0, 1.9)
        pts = np.stack([x + np.cos(angs) * rad * stretch, y + np.sin(angs) * rad], 1)
        m = fx.poly(pts)
        fx.over(m, DEBRIS * rng.uniform(0.8, 1.6), alpha * rng.uniform(0.75, 1.0))
        if edge_color is not None:
            e = np.clip(m - blur(m, 1.6), 0, 1) * 2.0
            fx.add(e, edge_color, edge_k * rng.uniform(0.4, 1.0))
