"""Generate Linchong (林冲) battle VFX assets + manifest per DouJiangLuV2 VFX Specification v1.1.

Usage:
    python tools/vfx/gen_linchong.py            # all assets, WebP
    python tools/vfx/gen_linchong.py --png      # export PNG instead
    python tools/vfx/gen_linchong.py --only Jifengci,Common

Every asset is a transparent RGBA sprite (or frame sequence) built procedurally
from the colour / motif DNA of the finalised Wiki skill icon.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from engine import (FX, col, line_pts, arc_pts, catmull, profile, blur, blur_dir, noise, smooth, ease_out,
                    grid, sample, save_frames)
from lc_common import *  # noqa
from lc_timeline import TIMELINES, ANCHORS, LAYERS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CHAR = os.path.join(ROOT, 'Characters', 'Linchong')

REG = []


def asset(key, rel_dir, pivot, ppu, desc, blend='normal', fps=None, loop=False, group=None):
    """Register an asset generator.

    key   : file base name, e.g. LC_Jifengci_Hit  (frames saved as _01, _02 ...)
    pivot : pivot in source-canvas px (becomes Cocos anchorPoint)
    ppu   : source pixels per 1 H (H = character display height)
    """
    def deco(fn):
        REG.append(dict(key=key, dir=rel_dir, pivot=pivot, ppu=ppu, desc=desc, blend=blend, fps=fps,
                        loop=loop, fn=fn, group=group or _group(rel_dir)))
        return fn
    return deco


def _group(rel_dir):
    parts = rel_dir.split('/')
    return parts[1] if parts[0] in ('ActiveSkills', 'PassiveSkills') else parts[0]


def seq(n, f):
    return [f(i / max(1, n - 1), i) for i in range(n)]


# =====================================================================================
# CommonFX  (tint-able neutral sprites reused by several skills / particle systems)
# =====================================================================================
@asset('LC_Common_WeaponFlash', 'CommonFX/WeaponFlash', (256, 256), 1400,
       '通用武器闪光：四芒银白星光，可按技能染色')
def common_weapon_flash():
    fx = FX(512, 512)
    s = fx.star(256, 256, 220, 10, 4, rot=0, lengths=[220, 150])
    fx.add(s, SILVER, 1.4)
    s2 = fx.star(256, 256, 90, 5, 4, rot=45)
    fx.add(s2, SILVER, 0.7)
    fx.add(fx.radial(256, 256, 34), WHITE, 1.8)
    fx.glow(s, SILVER_BLUE, 10, 0.8)
    return [fx.rgba()]


@asset('LC_Common_HitFlash', 'CommonFX/HitFlash', (256, 256), 1100, '通用受击中心闪光（白，可染色）')
def common_hit_flash():
    fx = FX(512, 512)
    fx.add(fx.radial(256, 256, 60), WHITE, 1.6)
    fx.add(fx.radial(256, 256, 150, power=1.2), SILVER, 0.5)
    return [fx.rgba()]


@asset('LC_Common_Spark', 'CommonFX/Spark', (128, 128), 1600, '通用火星/锋芒粒子，3 种形态（白，可染色）')
def common_spark():
    out = []
    for i, (L, w) in enumerate([(110, 7), (80, 10), (60, 6)]):
        fx = FX(256, 256)
        if i < 2:
            p = line_pts(128 - L, 128, 128 + L * 0.2, 128, 32)
            m = fx.strip(p, np.linspace(0.5, w, 32), np.linspace(0.1, 1, 32) ** 1.5)
        else:
            m = fx.star(128, 128, L, w, 4, rot=45)
        fx.add(m, WHITE, 1.2)
        fx.glow(m, SILVER, 5, 0.9)
        out.append(fx.rgba())
    return out


@asset('LC_Common_Dust', 'CommonFX/Dust', (256, 256), 900, '通用尘土团（普通混合，低不透明）')
def common_dust():
    fx = FX(512, 512)
    n = noise(512, 512, 6, 6, 11, 4)
    r = fx.radial(256, 270, 170, sx=1.3, sy=0.8, power=2.2)
    m = np.clip(r * (0.35 + 0.9 * n) - 0.12, 0, 1)
    fx.over(blur(m, 3), col('#5d5145'), 0.75)
    return [fx.rgba()]


@asset('LC_Common_Wind', 'CommonFX/Wind', (512, 128), 1000, '通用风线（白，可染色，横向）')
def common_wind():
    fx = FX(1024, 256)
    rng = np.random.default_rng(4)
    acc = np.zeros((256, 1024), np.float32)
    for _ in range(9):
        y = 128 + rng.normal(0, 26)
        x0 = rng.uniform(40, 300); x1 = rng.uniform(700, 990)
        pts = np.stack([np.linspace(x0, x1, 48), y + np.sin(np.linspace(0, 3, 48)) * rng.uniform(-6, 6)], 1)
        acc += fx.strip(pts, profile(48, 0.2, 0.35) * rng.uniform(2, 6) + 0.3,
                        profile(48, 0.3, 0.3) * rng.uniform(0.4, 1))
    fx.add(acc, WHITE, 0.9)
    fx.glow(acc, SILVER, 6, 0.6)
    return [fx.rgba()]


@asset('LC_Common_Shard', 'CommonFX/CommonParticles', (128, 128), 1800, '通用黑色碎屑 4 种（普通混合）')
def common_shard():
    out = []
    for i in range(4):
        fx = FX(256, 256)
        rng = np.random.default_rng(100 + i)
        k = 4 + i % 2
        angs = np.sort(rng.uniform(0, 2 * math.pi, k))
        rad = rng.uniform(40, 90, k)
        pts = np.stack([128 + np.cos(angs) * rad * 1.3, 128 + np.sin(angs) * rad * 0.8], 1)
        m = fx.poly(pts)
        fx.over(m, DEBRIS * 1.4, 1.0)
        e = np.clip(m - blur(m, 2.5), 0, 1) * 2
        fx.add(e, WHITE, 0.35)
        out.append(fx.rgba())
    return out


@asset('LC_Common_Glow', 'CommonFX/CommonParticles', (128, 128), 1600, '通用柔光点（白，可染色）')
def common_glow():
    fx = FX(256, 256)
    fx.add(fx.radial(128, 128, 22), WHITE, 1.3)
    fx.add(fx.radial(128, 128, 70, power=1.3), WHITE, 0.35)
    return [fx.rgba()]


# =====================================================================================
# 疾风刺 Jifengci —— 赤红 / 银白 · 高速突刺
# =====================================================================================
@asset('LC_Jifengci_Cast', 'ActiveSkills/Jifengci/Cast', (512, 512), 1500,
       '出招：枪锋银白闪光（带极细赤红外晕），4 帧', fps=30)
def jf_cast():
    def frame(t, i):
        fx = FX(1024, 1024)
        s = math.sin(t * math.pi) ** 0.8 + 0.08
        L = 380 * (0.55 + 0.6 * ease_out(t))
        st = fx.star(512, 512, L, 14, 4, rot=0, lengths=[L, L * 0.55, L * 0.9, L * 0.55])
        fx.add(st, SILVER, 1.5 * s)
        fx.add(fx.star(512, 512, L * 0.35, 6, 4, rot=45), SILVER, 0.8 * s)
        fx.add(fx.radial(512, 512, 40 + 20 * t), WHITE, 2.2 * s)
        fx.glow(st, CRIMSON, 18, 0.55 * s)
        fx.add(fx.radial(512, 512, 150, sx=1.6, power=1.4), CRIMSON_DEEP, 0.35 * s)
        return fx.rgba()
    return seq(4, frame)


@asset('LC_Jifengci_Trail', 'ActiveSkills/Jifengci/Trail', (1900, 384), 1320,
       'Trail：银白细枪线 + 赤红高速流（速度场，非火焰）。_01 主体，_02 赤红速度场层；Cocos 用横向 Filled 揭示', )
def jf_trail():
    W, Hh = 2048, 768
    cy, tip = 384, 1900
    # _01 main thrust
    fx = FX(W, Hh)
    rng = np.random.default_rng(7)
    speed_streaks(fx, rng, 46, (120, tip - 30), cy, 60, tip, CRIMSON, 1.1, (1.2, 5.0), (260, 1100))
    speed_streaks(fx, rng, 18, (300, tip - 60), cy, 90, tip, CRIMSON_DEEP, 1.0, (3, 9), (300, 900))
    # silver core line
    pts = line_pts(160, cy, tip, cy, 96)
    t = np.linspace(0, 1, 96)
    fx.line(pts, 0.8 + 7 * t ** 2, 0.15 + 0.85 * t ** 1.6, WHITE, SILVER_BLUE, glow_sigma=7, glow_k=0.9,
            core_k=1.6, halo_k=0.6)
    # spear-point light at the tip (枪锋)
    blade, _, ridge = spearhead_outline((tip + 40, cy), 150, 44, 0, guard=False)
    b = fx.poly(blade)
    fx.add(b, SILVER, 0.9)
    fx.add(np.clip(b - blur(b, 2), 0, 1) * 3, WHITE, 1.2)
    fx.glow(b, CRIMSON, 16, 0.8)
    fx.add(fx.radial(tip - 30, cy, 60, sx=2.5), WHITE, 0.9)
    f1 = fx.rgba()
    # _02 red speed field layer (soft, wide)
    fx = FX(W, Hh)
    x, y = grid(W, Hh)
    streak = noise(W, Hh, 5, 60, 21, 3)
    cone = np.exp(-((y - cy) / (40 + 150 * np.clip((tip - x) / tip, 0, 1))) ** 2)
    fade = smooth((x - 80) / 700) * smooth((tip + 80 - x) / 120)
    m = cone * fade * (0.25 + streak ** 2.2 * 1.2)
    fx.add(blur_dir(m, 12, 1.5), CRIMSON, 0.9)
    fx.add(blur_dir(m, 30, 4), CRIMSON_DEEP, 0.7)
    f2 = fx.rgba()
    return [f1, f2]


@asset('LC_Jifengci_Hit', 'ActiveSkills/Jifengci/Hit', (512, 512), 1900,
       'Hit：小型银白爆点 + 赤红放射线，5 帧，绑定 Target_HitPoint', fps=25)
def jf_hit():
    def frame(t, i):
        fx = FX(1024, 1024)
        rng = np.random.default_rng(31)
        k = (1 - t) ** 1.3
        core = 34 + 30 * ease_out(t, 3)
        fx.add(fx.radial(512, 512, core), WHITE, 2.4 * (1 - t) ** 2.5)
        st = fx.star(512, 512, 150 + 170 * ease_out(t), 12 * (1 - 0.6 * t), 4, rot=0,
                     lengths=[330 * (0.5 + 0.5 * ease_out(t)), 150, 200, 150])
        fx.add(st, SILVER, 1.4 * k)
        # crimson radial lines, biased forward (thrust direction +x)
        r_in = 40 + 170 * ease_out(t, 2)
        r_out = 200 + 260 * ease_out(t, 2)
        rays = burst_rays(fx, rng, 512, 512, 22, r_in, r_out, 7 * (1 - 0.5 * t), CRIMSON, 1.3 * k,
                          bias_len=lambda a: 0.7 + 0.5 * max(0, math.cos(a)))
        fx.glow(rays, CRIMSON_DEEP, 8, 0.8 * k)
        fx.glow(st, CRIMSON, 14, 0.5 * k)
        return fx.rgba()
    return seq(5, lambda t, i: frame(t * 0.85, i))


@asset('LC_Jifengci_Particle', 'ActiveSkills/Jifengci/Particle', (256, 32), 1500,
       '粒子：_01 赤红速度线，_02 银红锋芒火星')
def jf_particle():
    fx = FX(512, 64)
    p = line_pts(20, 32, 492, 32, 48)
    t = np.linspace(0, 1, 48)
    m = fx.strip(p, 0.5 + 5 * t ** 2, t ** 1.5)
    fx.add(m, CRIMSON, 1.3)
    fx.add(fx.strip(p, 0.4 + 1.6 * t ** 2, t ** 2), WHITE, 0.8)
    fx.glow(m, CRIMSON_DEEP, 3, 0.8)
    a = fx.rgba()
    fx = FX(512, 64)
    p = line_pts(200, 32, 480, 32, 32)
    m = fx.strip(p, np.linspace(0.5, 7, 32), np.linspace(0.1, 1, 32))
    fx.add(m, WHITE, 1.2)
    fx.glow(m, CRIMSON, 4, 1.2)
    return [a, fx.rgba()]


@asset('LC_Jifengci_Interrupt', 'ActiveSkills/Jifengci/Special', (512, 512), 1250,
       'Special·Interrupt：银白红边斩线瞬间切断敌方行动轨迹，4 帧（出现→全亮→断开→消散）', fps=24)
def jf_interrupt():
    def frame(t, i):
        fx = FX(1024, 1024)
        ang = -58.0
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        L = 900
        grow = [0.55, 1.0, 1.0, 1.0][i]
        k = [1.0, 1.25, 0.85, 0.4][i]
        gap = [0, 0, 18, 40][i]
        n = 96
        tt = np.linspace(-0.5, 0.5, n) * grow
        pts = np.stack([512 + ux * tt * L, 512 + uy * tt * L], 1)
        # slight crescent bend
        bend = (1 - (tt * 2 / max(grow, 1e-3)) ** 2) * 26
        pts[:, 0] += -uy * bend
        pts[:, 1] += ux * bend
        w = np.sin(np.linspace(0, math.pi, n)) ** 0.6 * (16 if i < 2 else 12) + 0.5
        off = np.stack([-uy, ux]) * 1.0
        for sgn in (1, -1):
            edge = fx.strip(pts + off * sgn * (w.max() * 0.55 + gap * 0.5), w * 0.7, np.ones(n))
            fx.add(edge, CRIMSON, 1.3 * k)
            fx.glow(edge, CRIMSON_DEEP, 12, 0.9 * k)
        if i < 3:
            core = fx.strip(pts, w * (0.55 if i < 2 else 0.25), np.ones(n))
            fx.add(core, WHITE, 1.8 * k)
            fx.glow(core, SILVER, 6, 0.8 * k)
        if i >= 2:
            rng = np.random.default_rng(5 + i)
            for _ in range(10):
                s = rng.uniform(-0.45, 0.45)
                cx, cy = 512 + ux * s * L, 512 + uy * s * L
                d = rng.choice([-1, 1]) * (30 + 60 * t)
                p = line_pts(cx - uy * d, cy + ux * d, cx - uy * d * 1.6, cy + ux * d * 1.6, 12)
                fx.add(fx.strip(p, np.linspace(4, 0.5, 12)), CRIMSON_HOT, 0.9 * k)
        return fx.rgba()
    return seq(4, frame)


@asset('LC_Jifengci_End', 'ActiveSkills/Jifengci/End', (1024, 256), 1300, 'End：残余赤红速度丝消散')
def jf_end():
    fx = FX(2048, 512)
    rng = np.random.default_rng(12)
    for _ in range(14):
        y = 256 + rng.normal(0, 55)
        x0 = rng.uniform(300, 1300); L = rng.uniform(200, 600)
        pts = np.stack([np.linspace(x0, x0 + L, 40), y + np.sin(np.linspace(0, rng.uniform(2, 5), 40)) * rng.uniform(3, 14)], 1)
        m = fx.strip(pts, profile(40, 0.3, 0.3) * rng.uniform(1.5, 4), profile(40, 0.3, 0.4) * rng.uniform(0.3, 0.8))
        fx.add(m, CRIMSON, 0.9)
        fx.glow(m, CRIMSON_DEEP, 8, 0.5)
    return [fx.rgba()]


# =====================================================================================
# 回马枪 Huimaqiang —— 铜橙 / 金白 · 受击 → 回身 → 反刺
# =====================================================================================
def thrust_trail(W, Hh, cy, tip, main, deep, core, seed, n=36, spread=55, field_k=0.7):
    fx = FX(W, Hh)
    rng = np.random.default_rng(seed)
    speed_streaks(fx, rng, n, (200, tip - 30), cy, spread, tip, main, 1.0, (1.2, 5.0), (240, 1000))
    speed_streaks(fx, rng, n // 3, (300, tip - 60), cy, spread * 1.4, tip, deep, 0.9, (3, 8), (300, 800))
    x, y = grid(W, Hh)
    streak = noise(W, Hh, 5, 50, seed + 1, 3)
    cone = np.exp(-((y - cy) / (30 + 110 * np.clip((tip - x) / tip, 0, 1))) ** 2)
    fade = smooth((x - 150) / 600) * smooth((tip + 60 - x) / 100)
    fx.add(blur_dir(cone * fade * (0.2 + streak ** 2 * 1.1), 14, 2), deep, field_k)
    pts = line_pts(220, cy, tip, cy, 96)
    t = np.linspace(0, 1, 96)
    fx.line(pts, 0.8 + 8 * t ** 2, 0.1 + 0.9 * t ** 1.6, core, main, glow_sigma=8, glow_k=0.9, core_k=1.6,
            halo_k=0.6)
    blade, _, _ = spearhead_outline((tip + 40, cy), 150, 46, 0, guard=False)
    b = fx.poly(blade)
    fx.add(b, core, 1.0)
    fx.glow(b, main, 16, 0.9)
    fx.add(fx.radial(tip - 30, cy, 60, sx=2.5), WHITE, 0.8)
    return fx


@asset('LC_Huimaqiang_Ready', 'ActiveSkills/Huimaqiang/Special', (512, 512), 1150,
       'Special·Ready：极淡的铜橙半圆枪势，环绕林冲身后（预备反击，循环低亮度）', loop=True)
def hmq_ready():
    fx = FX(1024, 1024)
    rng = np.random.default_rng(3)
    acc = np.zeros((1024, 1024), np.float32)
    for j in range(7):
        r = 380 - j * rng.uniform(8, 16)
        a0 = 95 + rng.uniform(0, 20); a1 = 265 - rng.uniform(0, 20)
        pts = arc_pts(512, 512, r, r, a0, a1, 96)
        acc += fx.strip(pts, profile(96, 0.3, 0.3) * rng.uniform(2, 7) + 0.3,
                        profile(96, 0.35, 0.35) * rng.uniform(0.35, 0.9))
    fx.add(acc, COPPER, 0.9)
    fx.glow(acc, COPPER_DEEP, 14, 0.9)
    main = fx.strip(arc_pts(512, 512, 392, 392, 100, 260, 96), profile(96, 0.3, 0.3) * 5 + 0.4,
                    profile(96, 0.3, 0.3))
    fx.add(main, GOLD_WHITE, 0.8)
    return [fx.rgba(exposure=0.8)]


@asset('LC_Huimaqiang_Cast', 'ActiveSkills/Huimaqiang/Cast', (512, 512), 1500,
       '出招（未触发反击的 35 版本）：枪锋铜金闪光，3 帧', fps=30)
def hmq_cast():
    def frame(t, i):
        fx = FX(1024, 1024)
        s = [0.6, 1.0, 0.45][i]
        L = 300 * [0.7, 1.0, 1.1][i]
        st = fx.star(512, 512, L, 12, 4, lengths=[L, L * 0.5, L * 0.8, L * 0.5])
        fx.add(st, GOLD_WHITE, 1.4 * s)
        fx.add(fx.radial(512, 512, 45), WHITE, 2.0 * s)
        fx.glow(st, COPPER, 16, 0.8 * s)
        fx.add(fx.radial(512, 512, 140, power=1.4), COPPER_DEEP, 0.4 * s)
        return fx.rgba()
    return seq(3, frame)


@asset('LC_Huimaqiang_Trail', 'ActiveSkills/Huimaqiang/Trail', (1900, 384), 1300,
       'Trail（35 普通版）：金白枪线 + 铜橙速度流；横向 Filled 揭示')
def hmq_trail():
    return [thrust_trail(2048, 768, 384, 1900, COPPER, COPPER_DEEP, GOLD_WHITE, 17, n=30).rgba()]


@asset('LC_Huimaqiang_Trigger', 'ActiveSkills/Huimaqiang/Special', (512, 512), 1250,
       'Special·Trigger：敌方攻击实际命中后，铜金环形气流快速形成，6 帧', fps=30)
def hmq_trigger():
    def frame(t, i):
        fx = FX(1024, 1024)
        rng = np.random.default_rng(40)
        R = 330 * (1.08 - 0.18 * t)
        k = 0.55 + 0.65 * math.sin(min(1, t * 1.3) * math.pi / 2)
        ring_swirl(fx, rng, 512, 512, R, int(10 + 30 * t), 40 + 120 * ease_out(t), 140 * t, COPPER, 1.1 * k,
                   width=(2, 8))
        acc = ring_swirl(fx, rng, 512, 512, R * 0.93, int(4 + 12 * t), 50 + 90 * t, 140 * t + 60, GOLD_WHITE,
                         0.9 * k, width=(1.5, 4), rjit=0.08)
        fx.glow(acc, COPPER, 20, 0.7 * k)
        fx.add(fx.radial(512, 512, R * 1.05, power=6) - fx.radial(512, 512, R * 0.8, power=6), COPPER_DEEP,
               0.25 * k)
        return fx.rgba()
    return seq(6, frame)


def hook_thrust(enhanced):
    W, Hh = 2048, 1024
    fx = FX(W, Hh)
    rng = np.random.default_rng(55 if enhanced else 50)
    cx, cy, R = 520, 420, 230
    arc = arc_pts(cx, cy, R, R, -80, -270, 80)             # sweep back & around (回身)
    straight = line_pts(cx, cy + R, 1900, cy + R, 90)[1:]  # then thrust forward (反刺)
    path = np.vstack([arc, straight])
    n = len(path)
    t = np.linspace(0, 1, n)
    wid = (2 + 14 * smooth(t / 0.55)) * (0.75 + 0.25 * t)
    val = 0.25 + 0.75 * smooth(t / 0.6)
    # copper airflow around the hook (the ring collapsing onto the spear)
    for j in range(26 if enhanced else 18):
        off = rng.normal(0, 26 if enhanced else 20)
        p = path.copy()
        d = np.gradient(p, axis=0); d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-6
        p += np.stack([-d[:, 1], d[:, 0]], 1) * off * (1.2 - t[:, None])
        s0 = rng.uniform(0, 0.4); s1 = rng.uniform(0.55, 0.95)
        m = (t > s0) & (t < s1)
        if m.sum() < 4:
            continue
        pp = p[m]; tt = np.linspace(0, 1, len(pp))
        acc = fx.strip(pp, (0.4 + rng.uniform(2.5, 8) * np.sin(tt * math.pi)), np.sin(tt * math.pi) * rng.uniform(0.5, 1))
        fx.add(acc, COPPER, 1.3)
        fx.glow(acc, COPPER_DEEP, 14, 0.9)
    k = 1.25 if enhanced else 1.0
    core = fx.line(path, wid * 0.45, val, WHITE, GOLD_WHITE, glow_sigma=9, glow_k=1.0 * k, core_k=1.5 * k,
                   halo_k=0.7)
    fx.glow(core, COPPER, 26, 0.7 * k)
    arcpart = fx.strip(arc, 60 * profile(len(arc), 0.4, 0.05), profile(len(arc), 0.5, 0.05) * 0.6, soft=10)
    fx.add(arcpart, COPPER_DEEP, 0.9 * k)
    if enhanced:
        inner = arc_pts(cx, cy, R * 0.82, R * 0.82, -110, -265, 60)
        m = fx.strip(inner, profile(60, 0.3, 0.2) * 4 + 0.3, profile(60, 0.3, 0.2))
        fx.add(m, GOLD_WHITE, 1.0)
        fx.glow(m, COPPER, 12, 0.8)
        speed_streaks(fx, rng, 14, (900, 1860), cy + R, 26, 1900, GOLD_WHITE, 0.9, (1, 3), (200, 600))
    blade, _, _ = spearhead_outline((1940, cy + R), 160, 52 if enhanced else 44, 0, guard=False)
    b = fx.poly(blade)
    fx.add(b, GOLD_WHITE, 1.2 * k)
    fx.glow(b, COPPER, 16, 0.9 * k)
    fx.add(fx.radial(1880, cy + R, 70, sx=2.2), WHITE, 1.0 * k)
    return fx.rgba()


@asset('LC_Huimaqiang_Counter', 'ActiveSkills/Huimaqiang/Special', (1900, 650), 1220,
       'Special·Counter（35→反击基础形态）：铜金气流收向枪身，回身后金白反向枪刺；pivot=枪尖')
def hmq_counter():
    return [hook_thrust(False)]


@asset('LC_Huimaqiang_CounterEnhanced', 'ActiveSkills/Huimaqiang/Special', (1900, 650), 1220,
       'Special·Counter 55 强化：双层回身弧 + 更亮金白枪刺，强于普通版但不爆炸化；pivot=枪尖')
def hmq_counter_enh():
    return [hook_thrust(True)]


def copper_hit(t, enhanced):
    fx = FX(1024, 1024)
    rng = np.random.default_rng(66)
    k = (1 - t) ** 1.2 * (1.2 if enhanced else 1.0)
    fx.add(fx.radial(512, 512, 34 + 30 * ease_out(t, 3)), WHITE, 2.3 * (1 - t) ** 2.2)
    L = (300 if enhanced else 240) * (0.5 + 0.5 * ease_out(t))
    st = fx.star(512, 512, L, 11 * (1 - 0.5 * t), 4, lengths=[L, L * 0.45, L * 0.7, L * 0.45])
    fx.add(st, GOLD_WHITE, 1.3 * k)
    rays = burst_rays(fx, rng, 512, 512, 16 if enhanced else 12, 40 + 150 * ease_out(t, 2), 190 + 200 * ease_out(t, 2),
                      6 * (1 - 0.5 * t), COPPER, 1.2 * k, bias_len=lambda a: 0.7 + 0.5 * max(0, math.cos(a)))
    fx.glow(rays, COPPER_DEEP, 8, 0.8 * k)
    rr = 90 + 230 * ease_out(t, 2.5)
    ring = fx.strip(arc_pts(512, 512, rr, rr * 0.9, 0, 360, 128), 5 * (1 - t) + 1, np.full(128, 1.0))
    fx.add(ring, COPPER, 0.9 * k)
    fx.glow(ring, COPPER_DEEP, 10, 0.6 * k)
    if enhanced:
        rr2 = 60 + 170 * ease_out(t, 2.0)
        ring2 = fx.strip(arc_pts(512, 512, rr2, rr2 * 0.9, 0, 360, 128), 4 * (1 - t) + 1, np.full(128, 1.0))
        fx.add(ring2, GOLD_WHITE, 0.9 * k)
    fx.glow(st, COPPER, 14, 0.6 * k)
    return fx.rgba()


@asset('LC_Huimaqiang_Hit', 'ActiveSkills/Huimaqiang/Hit', (512, 512), 1900,
       'Hit 35：铜金爆点 + 细环冲击，5 帧', fps=25)
def hmq_hit():
    return seq(5, lambda t, i: copper_hit(t * 0.85, False))


@asset('LC_Huimaqiang_HitEnhanced', 'ActiveSkills/Huimaqiang/Hit', (512, 512), 1700,
       'Hit 55 强化：双环 + 更多金白锋线，略大但保持紧凑，5 帧', fps=25)
def hmq_hit_enh():
    return seq(5, lambda t, i: copper_hit(t * 0.85, True))


@asset('LC_Huimaqiang_Particle', 'ActiveSkills/Huimaqiang/Particle', (128, 64), 1600, '粒子：铜橙余烬拖尾')
def hmq_particle():
    fx = FX(256, 128)
    p = line_pts(30, 64, 200, 64, 32)
    m = fx.strip(p, np.linspace(0.5, 9, 32), np.linspace(0.05, 1, 32) ** 1.3)
    fx.add(m, GOLD_WHITE, 1.1)
    fx.glow(m, COPPER, 5, 1.2)
    return [fx.rgba()]


@asset('LC_Huimaqiang_End', 'ActiveSkills/Huimaqiang/End', (512, 512), 1250, 'End：铜金残余气流弧线淡出')
def hmq_end():
    fx = FX(1024, 1024)
    rng = np.random.default_rng(8)
    acc = ring_swirl(fx, rng, 512, 512, 300, 12, 50, 0, COPPER, 0.6, width=(1.5, 4))
    fx.glow(acc, COPPER_DEEP, 12, 0.5)
    return [fx.rgba()]


# =====================================================================================
# 横扫千军 Hengsaoqianjun —— 橙金 / 银白 · 横扫 + 强制变距
# =====================================================================================
@asset('LC_Hengsaoqianjun_Cast', 'ActiveSkills/Hengsaoqianjun/Cast', (512, 512), 1150,
       '出招：橙金短暂蓄势（螺旋气流向枪身收拢），5 帧', fps=20)
def hs_cast():
    def frame(t, i):
        fx = FX(1024, 1024)
        rng = np.random.default_rng(90)
        R = 420 * (1 - 0.5 * ease_out(t))
        k = 0.4 + 0.8 * t
        acc = np.zeros((1024, 1024), np.float32)
        for j in range(26):
            a0 = rng.uniform(0, 360) + 200 * t
            r0 = R * rng.uniform(0.75, 1.0)
            n = 64
            ang = np.radians(np.linspace(a0, a0 + rng.uniform(60, 110), n))
            rad = np.linspace(r0, r0 * 0.55, n)
            pts = np.stack([512 + np.cos(ang) * rad, 512 + np.sin(ang) * rad * 0.55], 1)
            acc += fx.strip(pts, np.sin(np.linspace(0, math.pi, n)) * rng.uniform(1.5, 6) + 0.3,
                            np.linspace(0.2, 1, n) * rng.uniform(0.4, 1))
        fx.add(acc, ORANGE_GOLD, 1.0 * k)
        fx.glow(acc, ORANGE_DEEP, 14, 0.8 * k)
        fx.add(fx.radial(512, 512, 40 + 60 * t, sx=1.6), AMBER, 1.2 * k)
        fx.add(fx.radial(512, 512, 20 + 20 * t, sx=1.6), WHITE, 1.2 * k)
        return fx.rgba()
    return seq(5, frame)


@asset('LC_Hengsaoqianjun_Trail', 'ActiveSkills/Hengsaoqianjun/Trail', (1024, 560), 1450,
       'Trail：_01 巨大但薄的银白枪锋弧 + 橙金横向旋风（左→右，中部最亮，尾端速散）；_02 橙金旋风底层')
def hs_trail():
    W, Hh = 2048, 1024
    cx, cy, rx, ry, rot = 1024, 520, 880, 250, -6
    rng = np.random.default_rng(101)
    # ---- _01 main crescent
    fx = FX(W, Hh)
    n = 140
    a0, a1 = 205, -12
    t = np.linspace(0, 1, n)
    width_prof = smooth(t / 0.45) * smooth((1 - t) / 0.12)
    bright = 0.15 + 0.85 * np.exp(-((t - 0.62) / 0.28) ** 2)
    band = np.zeros((Hh, W), np.float32)
    for j in range(34):
        f = rng.uniform(0.78, 0.985)
        s0 = rng.uniform(0.0, 0.5); s1 = rng.uniform(s0 + 0.3, 1.0)
        pts = arc_pts(cx, cy, rx * f, ry * f, a0 + (a1 - a0) * s0, a0 + (a1 - a0) * s1, 90, rot)
        tt = np.linspace(s0, s1, 90)
        wp = np.interp(tt, t, width_prof)
        bp = np.interp(tt, t, bright)
        band += fx.strip(pts, wp * rng.uniform(3, 12) + 0.3, bp * rng.uniform(0.3, 1.0))
    fx.add(band, ORANGE_GOLD, 1.0)
    fx.glow(band, ORANGE_DEEP, 18, 0.9)
    fx.glow(band, AMBER, 5, 0.5)
    edge = arc_pts(cx, cy, rx, ry, a0, a1, n, rot)
    fx.line(edge, 0.8 + 6 * width_prof, bright * (0.2 + 0.8 * t), WHITE, SILVER_BLUE, glow_sigma=6, glow_k=0.8,
            core_k=1.6, halo_k=0.5)
    # leading spear-point flash on the front of the sweep
    tip = edge[-6]
    fx.add(fx.radial(tip[0], tip[1], 50, sx=2.0), WHITE, 0.8)
    # few sparks along the sweep
    for _ in range(26):
        s = rng.uniform(0.3, 0.95)
        p = arc_pts(cx, cy, rx * rng.uniform(0.85, 1.05), ry * rng.uniform(0.85, 1.05), a0 + (a1 - a0) * s,
                    a0 + (a1 - a0) * (s + 0.02), 6, rot)
        fx.add(fx.strip(p, np.linspace(0.5, 3, 6)), AMBER, 1.2)
    f1 = fx.rgba()
    # ---- _02 whirlwind layer
    fx = FX(W, Hh)
    acc = np.zeros((Hh, W), np.float32)
    for j in range(22):
        f = rng.uniform(0.35, 0.95)
        s = rng.uniform(0, 360)
        pts = arc_pts(cx, cy, rx * f, ry * f * rng.uniform(0.8, 1.1), s, s + rng.uniform(80, 170), 90, rot)
        acc += fx.strip(pts, np.sin(np.linspace(0, math.pi, 90)) * rng.uniform(4, 16) + 0.3,
                        np.sin(np.linspace(0, math.pi, 90)) * rng.uniform(0.2, 0.7))
    fx.add(blur(acc, 2), ORANGE_GOLD, 0.8)
    fx.glow(acc, ORANGE_DEEP, 20, 0.9)
    x, y = grid(W, Hh)
    fx.add(np.exp(-(((x - cx) / (rx * 0.35)) ** 2 + ((y - cy) / (ry * 0.35)) ** 2)), ORANGE_DEEP, 0.35)
    f2 = fx.rgba(exposure=0.9)
    return [f1, f2]


@asset('LC_Hengsaoqianjun_Hit', 'ActiveSkills/Hengsaoqianjun/Hit', (420, 512), 1500,
       'Hit：橙金横向冲击 + 黑色碎屑，5 帧（重攻击：允许极短 HitStop + 小幅屏震）', fps=22)
def hs_hit():
    def frame(t, i):
        fx = FX(1024, 1024)
        rng = np.random.default_rng(120)
        k = (1 - t) ** 1.2
        fx.add(fx.radial(420, 512, 40 + 40 * ease_out(t), sx=2.6), WHITE, 2.2 * (1 - t) ** 2)
        fx.add(fx.radial(460, 512, 110 + 120 * ease_out(t), sx=2.8, power=1.4), ORANGE_GOLD, 0.9 * k)
        rays = burst_rays(fx, rng, 420, 512, 18, 60 + 200 * ease_out(t, 2), 300 + 260 * ease_out(t, 2),
                          8 * (1 - 0.5 * t), AMBER, 1.2 * k, angle_center=0, angle_spread=70)
        fx.glow(rays, ORANGE_DEEP, 8, 0.8 * k)
        # crescent shock front ")"
        rr = 140 + 260 * ease_out(t, 2)
        sh = fx.strip(arc_pts(420, 512, rr, rr * 1.3, -55, 55, 64), profile(64, 0.3, 0.3) * (14 * (1 - t) + 2),
                      profile(64, 0.3, 0.3))
        fx.add(sh, ORANGE_GOLD, 1.2 * k)
        fx.glow(sh, ORANGE_DEEP, 12, 0.7 * k)
        fx.add(fx.star(420, 512, 260 * (0.6 + 0.4 * t), 10 * (1 - 0.5 * t), 2), WHITE, 1.2 * k)
        if i < 4:
            shards(fx, np.random.default_rng(130 + 0), 420 + 280 * ease_out(t), 512, 12,
                   160 + 200 * t, 150 + 100 * t, 30, edge_color=AMBER, edge_k=0.9 * k, alpha=0.95 * (1 - t * 0.6))
        return fx.rgba()
    return seq(5, lambda t, i: frame(t * 0.85, i))


@asset('LC_Hengsaoqianjun_Particle', 'ActiveSkills/Hengsaoqianjun/Particle', (128, 64), 1600,
       '粒子：橙金火星拖尾（配合 LC_Common_Shard 黑色碎屑）')
def hs_particle():
    fx = FX(256, 128)
    p = line_pts(20, 64, 210, 64, 32)
    m = fx.strip(p, np.linspace(0.4, 7, 32), np.linspace(0.05, 1, 32) ** 1.5)
    fx.add(m, WHITE, 1.0)
    fx.glow(m, ORANGE_GOLD, 5, 1.4)
    return [fx.rgba()]


def wind_pressure(t, i, broken):
    W, Hh = 1536, 1024
    fx = FX(W, Hh)
    rng = np.random.default_rng(140)
    base_x = 380
    k = (0.9 if not broken else 1.0 - 0.28 * i) * (1 - 0.15 * t)
    acc = np.zeros((Hh, W), np.float32)
    for j in range(4):
        cx = base_x + j * 150 + (260 * ease_out(t) if not broken else 60 * ease_out(t))
        R = 330 - j * 40
        pts = arc_pts(cx - R, 512, R, R * 1.25, -50, 50, 80)
        prof = profile(80, 0.25, 0.25)
        val = prof * (1.0 - j * 0.18)
        if broken:
            # fragment into shards: carve gaps, offset segments
            gaps = np.ones(80)
            nseg = 3 + i * 2
            cuts = np.sort(rng.uniform(0, 1, nseg))
            for c in cuts:
                gaps *= 1 - np.exp(-((np.linspace(0, 1, 80) - c) / (0.012 + 0.02 * i)) ** 2) * (0.6 + 0.4 * min(1, i))
            val = val * gaps
            segidx = np.floor(np.linspace(0, nseg + 0.999, 80)).astype(int)
            seg_off = rng.normal(0, 4 + 12 * i, (nseg + 2, 2))
            pts = pts + seg_off[segidx] * np.array([1.0, 0.6])
        acc += fx.strip(pts, prof * (16 - j * 3) + 1, np.clip(val, 0, 1))
    fx.add(acc, GOLD_WHITE, 1.0 * k)
    fx.glow(acc, ORANGE_GOLD, 12, 1.0 * k)
    # horizontal wind streaks pushing right
    for _ in range(18):
        y = 512 + rng.normal(0, 150)
        x0 = base_x - 250 + rng.uniform(0, 200) + 300 * ease_out(t) * (0.3 if broken else 1)
        L = rng.uniform(300, 700) * (1 - 0.5 * i / 3 if broken else 1)
        p = np.stack([np.linspace(x0, x0 + L, 32), np.full(32, y)], 1)
        v = np.linspace(0.05, 1, 32) * rng.uniform(0.3, 0.8)
        if broken:
            v = v * (np.sin(np.linspace(0, rng.uniform(10, 20), 32)) > -0.2 + 0.25 * i)
        fx.add(fx.strip(p, np.linspace(0.4, rng.uniform(2, 5), 32), v), ORANGE_GOLD, 0.8 * k)
    if broken and i >= 1:
        shards(fx, np.random.default_rng(150 + i), base_x + 260, 512, 8 + 3 * i, 220, 200, 16,
               edge_color=AMBER, edge_k=0.8, alpha=0.8 * (1 - 0.25 * i))
    return fx.rgba()


@asset('LC_Hengsaoqianjun_ForcedPush', 'ActiveSkills/Hengsaoqianjun/Special', (380, 512), 1300,
       'Special·ForcedPush：Hit 后第二层横向推力风压（强制变距 近→远），4 帧，随目标右移', fps=14)
def hs_push():
    return seq(4, lambda t, i: wind_pressure(t, i, False))


@asset('LC_Hengsaoqianjun_PushBlocked', 'ActiveSkills/Hengsaoqianjun/Special', (380, 512), 1300,
       'Special·PushBlocked：变距被阻止——风压破碎（已造成的 Hit 不回滚），4 帧', fps=14)
def hs_push_blocked():
    return seq(4, lambda t, i: wind_pressure(t, i, True))


@asset('LC_Hengsaoqianjun_End', 'ActiveSkills/Hengsaoqianjun/End', (512, 512), 1300, 'End：橙金余烬消散')
def hs_end():
    fx = FX(1024, 1024)
    rng = np.random.default_rng(160)
    acc = np.zeros((1024, 1024), np.float32)
    for _ in range(40):
        x = 512 + rng.normal(0, 200); y = 512 + rng.normal(0, 90)
        L = rng.uniform(10, 50)
        p = line_pts(x - L, y + L * 0.2, x, y, 8)
        acc += fx.strip(p, np.linspace(0.5, rng.uniform(2, 5), 8), np.linspace(0.1, 1, 8) * rng.uniform(0.3, 1))
    fx.add(acc, AMBER, 1.0)
    fx.glow(acc, ORANGE_DEEP, 6, 0.8)
    return [fx.rgba()]


# =====================================================================================
# 枪阵 Qiangzhen —— 冰蓝 / 银白 · 阵地：Cast → Spawn → Loop → Trigger → Attack/Block → Hit → End
# =====================================================================================
@asset('LC_Qiangzhen_Cast', 'ActiveSkills/Qiangzhen/Cast', (128, 940), 1300,
       '出招：枪尖蓝白光点下落（竖向拖尾，pivot=光点，从 Weapon_Tip 下落至阵心）')
def qz_cast():
    fx = FX(256, 1024)
    p = line_pts(128, 120, 128, 940, 64)
    t = np.linspace(0, 1, 64)
    fx.line(p, 0.5 + 9 * t ** 3, t ** 2, WHITE, ICE, glow_sigma=8, glow_k=1.0, core_k=1.5, halo_k=0.7)
    fx.add(fx.radial(128, 940, 26), WHITE, 2.0)
    fx.add(fx.radial(128, 940, 70), ICE, 0.8)
    return [fx.rgba()]


@asset('LC_Qiangzhen_CastImpact', 'ActiveSkills/Qiangzhen/Cast', (512, 256), 1250,
       '出招：光点落地的小型冰蓝冲击环（地面透视）')
def qz_cast_impact():
    fx = FX(1024, 512)
    ring = fx.strip(arc_pts(512, 256, 300, 100, 0, 360, 160), 6, np.ones(160))
    fx.add(ring, ICE_PALE, 1.0)
    fx.glow(ring, ICE, 12, 1.0)
    fx.add(fx.radial(512, 256, 60, sy=0.35), WHITE, 1.8)
    fx.add(fx.star(512, 250, 200, 8, 2, rot=0), SILVER, 1.0)
    fx.add(fx.star(512, 250, 150, 6, 1, rot=-90), WHITE, 1.1)
    return [fx.rgba()]


QZ_SQ = 0.34  # perspective squash of the ground plane


def qz_rune(mode):
    """Ice-blue spear-formation ground rune. mode: spawn | loop | trigger | end"""
    W, Hh = 2048, 760
    cx, cy = 1024, 380
    fx = FX(W, Hh)
    rng = np.random.default_rng(200)
    def P(pts):
        pts = np.asarray(pts, np.float32).copy()
        pts[:, 0] += cx
        pts[:, 1] = cy + pts[:, 1] * QZ_SQ
        return pts
    k = {'spawn': 1.0, 'loop': 0.42, 'trigger': 1.7, 'end': 0.6}[mode]
    lines = np.zeros((Hh, W), np.float32)
    thin = np.zeros((Hh, W), np.float32)
    for R, w in ((940, 7), (900, 2.5), (600, 3)):
        lines += fx.strip(P(arc_pts(0, 0, R, R, 0, 360, 256)), w, np.ones(256))
    # 12 spear-point glyphs pointing outward, between the rings
    for j in range(12):
        a = math.radians(j * 30 + 15)
        tip = (math.cos(a) * 880, math.sin(a) * 880)
        blade, sock, ridge = spearhead_outline(tip, 230, 70, math.degrees(a))
        lines += np.clip(fx.poly(P(blade)) * 0.35, 0, 1)
        e = fx.poly(P(blade))
        lines += np.clip(e - blur(e, 1.2), 0, 1) * 2.5
        thin += fx.strip(P(ridge), 1.5, np.ones(len(ridge)))
    # crossing-spear formation lines (8-point star)
    pts8 = [(math.cos(math.radians(j * 45 + 22.5)) * 600, math.sin(math.radians(j * 45 + 22.5)) * 600) for j in range(8)]
    for j in range(8):
        a, b = pts8[j], pts8[(j + 3) % 8]
        thin += fx.strip(P(line_pts(a[0], a[1], b[0], b[1], 32)), 2.0, np.ones(32) * 0.8)
    # ice fractures (skip for loop -> keeps loop calm and low-detail)
    if mode != 'loop':
        for j in range(14):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(80, 200)
            pts = []
            for s in range(10):
                pts.append((math.cos(a) * r, math.sin(a) * r))
                a += rng.normal(0, 0.12)
                r += rng.uniform(40, 90)
                if r > 940:
                    break
            pts = np.array(pts)
            thin += fx.strip(P(pts), np.linspace(2.2, 0.6, len(pts)), np.linspace(1, 0.3, len(pts)))
    # frosty fill
    x, y = grid(W, Hh)
    d = np.sqrt(((x - cx) / 940) ** 2 + ((y - cy) / (940 * QZ_SQ)) ** 2)
    frost = noise(W, Hh, 24, 8, 210, 4)
    fill = np.clip(1 - d, 0, 1) ** 0.7 * (0.35 + 0.65 * frost) * (d < 1)
    if mode == 'end':
        # break the rune: angular gaps
        ang = np.arctan2((y - cy) / QZ_SQ, x - cx)
        gapmask = (np.sin(ang * 7 + 1.3) > -0.1) * (np.sin(ang * 13 + 0.4) > -0.35)
        lines *= gapmask
        thin *= gapmask
        fill *= 0.3
    fx.add(fill, ICE_DEEP, 0.35 * k)
    fx.add(lines, ICE_PALE, 0.9 * k)
    fx.add(thin, ICE, 0.9 * k)
    fx.glow(lines + thin, ICE, 10, 0.9 * k)
    if mode == 'trigger':
        fx.glow(lines, ICE_PALE, 26, 0.6)
        fx.add(fx.radial(cx, cy, 520, sy=QZ_SQ, power=1.5), ICE, 0.5)
        # short vertical light rising from the ring glyphs
        for j in range(12):
            a = math.radians(j * 30 + 15)
            px, py = cx + math.cos(a) * 760, cy + math.sin(a) * 760 * QZ_SQ
            h = rng.uniform(80, 180)
            v = fx.strip(line_pts(px, py, px, py - h, 24), np.linspace(6, 0.5, 24), np.linspace(1, 0, 24))
            fx.add(v, ICE_PALE, 1.2)
            fx.glow(v, ICE, 8, 0.8)
    return fx.rgba(exposure=1.0 if mode != 'loop' else 0.85)


@asset('LC_Qiangzhen_Spawn', 'ActiveSkills/Qiangzhen/Status', (1024, 380), 1250,
       'Status·Spawn：_01 冰蓝阵纹出现（地面透视阵，BattleFX_Back 层）')
def qz_spawn():
    return [qz_rune('spawn')]


@asset('LC_Qiangzhen_SpearGhost', 'ActiveSkills/Qiangzhen/Status', (128, 1000), 1500,
       'Status·Spawn：银白半透明枪锋（阵中升起，可复用 3~5 支，pivot=枪杆底部）')
def qz_spear_ghost():
    fx = FX(256, 1024)
    draw_spear_ghost(fx, (128, 40), 250, 76, -90, 720, ICE, SILVER, k=1.0, fill=0.3)
    return [fx.rgba()]


@asset('LC_Qiangzhen_Loop', 'ActiveSkills/Qiangzhen/Status', (1024, 380), 1250,
       'Status·Loop：低亮度蓝光阵纹（持续期，建议透明度 60~80% 呼吸）', loop=True)
def qz_loop():
    return [qz_rune('loop')]


@asset('LC_Qiangzhen_Trigger', 'ActiveSkills/Qiangzhen/Special', (1024, 380), 1250,
       'Special·Trigger：敌方发生 FAR→NEAR Attempt，枪阵瞬间亮起（带竖向光芒）')
def qz_trigger():
    return [qz_rune('trigger')]


@asset('LC_Qiangzhen_Attack', 'ActiveSkills/Qiangzhen/Special', (980, 128), 1500,
       'Special·Attack：单支枪影横向刺出（多支同时播放），pivot=枪尖')
def qz_attack():
    fx = FX(1024, 256)
    rng = np.random.default_rng(230)
    draw_spear_ghost(fx, (980, 128), 200, 60, 0, 520, ICE, SILVER, k=1.0, fill=0.35)
    speed_streaks(fx, rng, 16, (60, 760), 128, 18, 980, ICE, 0.8, (1, 3), (150, 450))
    return [fx.rgba()]


@asset('LC_Qiangzhen_Block', 'ActiveSkills/Qiangzhen/Special', (700, 512), 1300,
       'Special·Block：目标前方形成枪锋封锁（交叉枪锋 + 竖向封锁光幕），pivot=封锁线中心')
def qz_block():
    fx = FX(1024, 1024)
    for j, ang in enumerate([-34, -17, 0, 17, 34]):
        a = math.radians(ang)
        ty = 512 + ang * 7.5
        tip = (700 + 30 * math.cos(a * 2), ty)
        draw_spear_ghost(fx, tip, 180, 56, ang * 0.6, 380, ICE, SILVER, k=0.9 if j != 2 else 1.1, fill=0.3)
    x, y = grid(1024, 1024)
    wall = np.exp(-((x - 740) / 14) ** 2) * smooth((y - 170) / 120) * smooth((860 - y) / 120)
    streak = noise(1024, 1024, 4, 40, 240, 3)
    fx.add(wall * (0.4 + streak), ICE_PALE, 0.9)
    fx.add(blur_dir(wall, 30, 2), ICE, 0.5)
    return [fx.rgba()]


@asset('LC_Qiangzhen_Hit', 'ActiveSkills/Qiangzhen/Hit', (512, 512), 1900,
       'Hit 32×1：蓝白锐利 Hit（针状冰锋放射），5 帧', fps=25)
def qz_hit():
    def frame(t, i):
        fx = FX(1024, 1024)
        rng = np.random.default_rng(250)
        k = (1 - t) ** 1.2
        fx.add(fx.radial(512, 512, 30 + 20 * t), WHITE, 2.4 * (1 - t) ** 2.4)
        L = 320 * (0.5 + 0.5 * ease_out(t))
        st = fx.star(512, 512, L, 9 * (1 - 0.5 * t), 4, rot=0, lengths=[L, L * 0.5, L * 0.7, L * 0.5])
        fx.add(st, SILVER, 1.4 * k)
        needles = burst_rays(fx, rng, 512, 512, 26, 30 + 140 * ease_out(t), 220 + 220 * ease_out(t),
                             4 * (1 - 0.4 * t), ICE_PALE, 1.3 * k, bias_len=lambda a: 0.7 + 0.5 * max(0, -math.cos(a)))
        fx.glow(needles, ICE, 8, 1.0 * k)
        fx.glow(st, ICE, 14, 0.6 * k)
        for _ in range(8):
            a = rng.uniform(0, 2 * math.pi); r = (90 + 250 * ease_out(t)) * rng.uniform(0.6, 1)
            fx.add(fx.star(512 + math.cos(a) * r, 512 + math.sin(a) * r, 18, 3, 4, rot=45), ICE_PALE, 0.9 * k)
        return fx.rgba()
    return seq(5, lambda t, i: frame(t * 0.85, i))


@asset('LC_Qiangzhen_Particle', 'ActiveSkills/Qiangzhen/Particle', (128, 128), 1600, '粒子：冰蓝碎锋闪点')
def qz_particle():
    fx = FX(256, 256)
    s = fx.star(128, 128, 90, 7, 4, rot=0, lengths=[90, 40])
    fx.add(s, ICE_PALE, 1.3)
    fx.glow(s, ICE, 6, 1.2)
    return [fx.rgba()]


@asset('LC_Qiangzhen_End', 'ActiveSkills/Qiangzhen/End', (1024, 380), 1250,
       'End：阵纹断裂、低亮度消散（触发后枪阵消失）')
def qz_end():
    return [qz_rune('end')]


# =====================================================================================
# 固有·豹子头 Baozitou —— 香槟金 / 银灰 · Trigger → Active → Consume
# =====================================================================================
LEOPARD_TOP = [(250, 830), (268, 700), (298, 560), (330, 450), (350, 340), (380, 304), (420, 302), (448, 330), (474, 354),
               (560, 346), (650, 368), (712, 400), (792, 452), (842, 488), (872, 522), (866, 552), (840, 566)]
LEOPARD_LIP = [(840, 566), (826, 596), (792, 622), (746, 636), (706, 640)]
LEOPARD_JAW = [(706, 640), (760, 648), (792, 666), (770, 694), (690, 716), (590, 752), (520, 800), (480, 860)]
LEOPARD_EYE_UP = [(652, 440), (680, 424), (712, 428), (734, 446)]
LEOPARD_EYE_LO = [(652, 440), (684, 454), (734, 446)]
LEOPARD_EAR_IN = [(376, 336), (404, 322), (430, 340)]
LEOPARD_MUZZLE = [(738, 452), (770, 500), (800, 548)]
LEOPARD_CHEEK = [(772, 560), (748, 596), (706, 626)]
LEOPARD_SPOTS = [(520, 420, 20), (590, 470, 16), (470, 520, 24), (560, 560, 20), (420, 620, 26), (640, 540, 14),
                 (500, 670, 22), (380, 720, 24), (620, 420, 12), (440, 440, 18), (340, 560, 22), (600, 640, 16),
                 (330, 800, 22), (420, 780, 18)]


def leopard_mask(fx, reveal=1.0):
    acc = np.zeros((fx.h, fx.w), np.float32)
    def stroke(ctrl, w, v=1.0, n=120):
        p = catmull(ctrl, n)
        m = int(max(2, n * reveal))
        tt = np.linspace(0, 1, m)
        return fx.strip(p[:m], w * (0.35 + 0.65 * np.sin(tt * math.pi) ** 0.4), np.full(m, v))
    acc += stroke(LEOPARD_TOP, 7.5)
    acc += stroke(LEOPARD_LIP, 5.0)
    acc += stroke(LEOPARD_JAW, 6.0)
    acc += stroke(LEOPARD_EYE_UP, 4.0, 1.0, 40)
    acc += stroke(LEOPARD_EYE_LO, 2.5, 0.8, 40)
    acc += stroke(LEOPARD_EAR_IN, 3.0, 0.7, 30)
    acc += stroke(LEOPARD_MUZZLE, 3.0, 0.7, 40)
    acc += stroke(LEOPARD_CHEEK, 2.5, 0.55, 40)
    rng = np.random.default_rng(300)
    for (x, y, r) in LEOPARD_SPOTS:
        for _ in range(3):
            a0 = rng.uniform(0, 360); L = rng.uniform(40, 70)
            p = arc_pts(x, y, r, r * 0.8, a0, a0 + L, 16)
            acc += fx.strip(p, np.sin(np.linspace(0, math.pi, 16)) * 3.0 + 0.3, np.full(16, 0.38))
    return acc


@asset('LC_Baozitou_Trigger', 'PassiveSkills/Baozitou/Trigger', (560, 540), 1150,
       'Trigger：成功打断/截击 → 淡金豹子轮廓 + 香槟金速度线（0.2~0.3s），_01 轮廓，_02 速度线')
def bzt_trigger():
    fx = FX(1024, 1024)
    m = leopard_mask(fx)
    fx.add(m, CHAMPAGNE, 1.2)
    fx.add(m, WHITE, 0.35)
    fx.glow(m, CHAMPAGNE_DEEP, 8, 0.9)
    fx.glow(m, CHAMPAGNE, 26, 0.35)
    fx.add(fx.radial(700, 438, 10), WHITE, 1.6)       # eye glint
    rng = np.random.default_rng(310)
    # speed lines streaming back from the silhouette + two sweeping arcs (icon DNA)
    speed = np.zeros((1024, 1024), np.float32)
    for _ in range(22):
        y = rng.uniform(270, 860)
        x1 = rng.uniform(170, 290); L = rng.uniform(160, 380)
        p = np.stack([np.linspace(x1 - L, x1, 32), np.linspace(y + L * 0.12, y, 32)], 1)
        speed += fx.strip(p, np.linspace(0.4, rng.uniform(2, 5), 32), np.linspace(0, 1, 32) ** 1.5 * rng.uniform(0.3, 0.9))
    for (a0, a1, ry, cy) in ((188, 262, 330, 640), (182, 250, 400, 740)):
        p = arc_pts(560, cy, 520, ry, a0, a1, 96)
        speed += fx.strip(p, profile(96, 0.3, 0.2) * 5 + 0.3, profile(96, 0.3, 0.2) * 0.9)
    fx.add(speed, CHAMPAGNE, 1.0)
    fx.add(speed, SILVER_GREY, 0.3)
    fx.glow(speed, CHAMPAGNE_DEEP, 6, 0.6)
    f1 = fx.rgba()
    fx = FX(1024, 1024)
    s2 = np.zeros((1024, 1024), np.float32)
    for _ in range(30):
        y = rng.uniform(300, 760); x1 = rng.uniform(560, 960); L = rng.uniform(250, 600)
        p = np.stack([np.linspace(x1 - L, x1, 32), np.linspace(y + L * 0.25, y, 32)], 1)   # 向前/向上高速锋线
        s2 += fx.strip(p, np.linspace(0.4, rng.uniform(2, 6), 32), np.linspace(0, 1, 32) ** 1.4 * rng.uniform(0.3, 1))
    fx.add(s2, CHAMPAGNE, 1.1)
    fx.add(s2, WHITE, 0.3)
    fx.glow(s2, CHAMPAGNE_DEEP, 7, 0.7)
    return [f1, fx.rgba()]


@asset('LC_Baozitou_Active', 'PassiveSkills/Baozitou/Active', (512, 48), 1100,
       'Active：枪身淡金高光（沿枪杆，低亮度常驻至消耗；配合 UI/LC_Baozitou_BuffIcon）', loop=True)
def bzt_active():
    fx = FX(1024, 96)
    p = line_pts(40, 48, 984, 48, 96)
    t = np.linspace(0, 1, 96)
    v = 0.25 + 0.75 * np.exp(-((t - 0.72) / 0.12) ** 2)
    m = fx.strip(p, 2.5 + 3 * v, v * profile(96, 0.15, 0.08))
    fx.add(m, CHAMPAGNE, 1.0)
    fx.add(m, WHITE, 0.4 * v.max())
    fx.glow(m, CHAMPAGNE_DEEP, 6, 0.8)
    return [fx.rgba(exposure=0.85)]


@asset('LC_Baozitou_Consume', 'PassiveSkills/Baozitou/Consume', (960, 256), 1250,
       'Consume：下一次攻击开始，金色速度线向枪锋收束后消失（pivot=枪锋），3 帧', fps=16)
def bzt_consume():
    def frame(t, i):
        fx = FX(1024, 512)
        rng = np.random.default_rng(330)
        acc = np.zeros((512, 1024), np.float32)
        for _ in range(26):
            y0 = 256 + rng.normal(0, 110)
            x0 = rng.uniform(40, 500)
            s = ease_out(t) * 0.75
            xs = np.linspace(x0 + (960 - x0) * s, 960, 32)
            ys = y0 + (256 - y0) * ((xs - x0) / (960 - x0)) ** 1.3
            acc += fx.strip(np.stack([xs, ys], 1), np.linspace(0.5, rng.uniform(2, 5), 32),
                            np.linspace(0.1, 1, 32) * rng.uniform(0.4, 1))
        k = [0.9, 1.1, 0.8][i]
        fx.add(acc, CHAMPAGNE, 1.0 * k)
        fx.glow(acc, CHAMPAGNE_DEEP, 6, 0.7 * k)
        g = [0.5, 1.0, 1.6][i]
        fx.add(fx.star(960, 256, 110 * g, 6, 4, lengths=[110 * g, 50 * g]), WHITE, 1.2 * k)
        fx.add(fx.radial(960, 256, 26 * g), CHAMPAGNE, 1.5 * k)
        return fx.rgba()
    return seq(3, frame)


@asset('LC_Baozitou_End', 'PassiveSkills/Baozitou/End', (256, 256), 1500, 'End：枪锋处小型香槟金闪点收尾')
def bzt_end():
    fx = FX(512, 512)
    s = fx.star(256, 256, 110, 6, 4, rot=45, lengths=[110, 60])
    fx.add(s, CHAMPAGNE, 1.2)
    fx.glow(s, CHAMPAGNE_DEEP, 8, 0.8)
    return [fx.rgba()]


# =====================================================================================
# UI  (Battle UI 状态图标 —— 不含文字)
# =====================================================================================
def badge(fx, ring_col, deep_col):
    x, y = grid(fx.w, fx.h)
    d = np.sqrt((x - 128) ** 2 + (y - 128) ** 2)
    disc = np.clip(118 - d, 0, 1)
    fx.over(disc, col('#15171c'), 0.92)
    ring = np.clip(1 - np.abs(d - 112) / 4, 0, 1)
    fx.add(ring, ring_col, 1.2)
    fx.add(np.clip(1 - np.abs(d - 100) / 1.5, 0, 1), deep_col, 0.6)


@asset('LC_Baozitou_BuffIcon', 'UI', (128, 128), 256, 'UI：豹子头 Buff 图标（速度提升：向前/向上锋线），无文字')
def ui_bzt():
    fx = FX(256, 256)
    badge(fx, CHAMPAGNE, CHAMPAGNE_DEEP)
    for dy in (-26, 22):
        p = np.array([(72, 150 + dy), (140, 92 + dy), (196, 118 + dy)], np.float32)
        p = catmull(p, 40)
        m = fx.strip(p, np.linspace(3, 12, 40), np.linspace(0.5, 1, 40))
        fx.add(m, CHAMPAGNE, 1.3)
        fx.add(m, WHITE, 0.3)
        fx.glow(m, CHAMPAGNE_DEEP, 4, 0.6)
    return [fx.rgba()]


@asset('LC_Qiangzhen_StatusIcon', 'UI', (128, 128), 256, 'UI：枪阵状态图标（三枪锋 + 冰蓝环），无文字')
def ui_qz():
    fx = FX(256, 256)
    badge(fx, ICE, ICE_DEEP)
    for dx, h in ((-48, 60), (0, 80), (48, 60)):
        blade, _, ridge = spearhead_outline((128 + dx, 128 - h + 30), 64, 26, -90, guard=False)
        m = fx.poly(blade)
        fx.add(m, SILVER, 0.7)
        fx.add(np.clip(m - blur(m, 1.2), 0, 1) * 2.5, WHITE, 0.8)
        fx.glow(m, ICE, 5, 0.9)
        s = fx.strip(line_pts(128 + dx, 128 - h + 94, 128 + dx, 200, 12), 4, np.linspace(1, 0.3, 12))
        fx.add(s, ICE_PALE, 0.8)
    arc = fx.strip(arc_pts(128, 196, 70, 16, 0, 180, 48), 3, np.ones(48))
    fx.add(arc, ICE, 1.2)
    return [fx.rgba()]


# =====================================================================================
def build(only=None, fmt='webp'):
    manifest = {'character': 'Linchong', 'abbr': 'LC', 'spec': 'DouJiangLuV2 VFX Specification v1.1',
                'unit': 'H = character display height (px). size_H = sprite size / ppu.',
                'format': fmt, 'anchors': ANCHORS, 'layers': LAYERS, 'assets': {}, 'timelines': TIMELINES}
    for a in REG:
        if only and not any(o in a['key'] for o in only):
            continue
        frames = a['fn']()
        out_dir = os.path.join(CHAR, a['dir'])
        meta = save_frames(frames, out_dir, a['key'], a['pivot'], fmt=fmt)
        entry = {
            'dir': 'Characters/Linchong/' + a['dir'],
            'files': meta['files'],
            'size': meta['size'],
            'anchor': meta['anchor'],
            'ppu': a['ppu'],
            'size_H': [round(meta['size'][0] / a['ppu'], 3), round(meta['size'][1] / a['ppu'], 3)],
            'blend': a['blend'],
            'desc': a['desc'],
            'group': a['group'],
        }
        if a['fps']:
            entry['fps'] = a['fps']
        if a['loop']:
            entry['loop'] = True
        manifest['assets'][a['key']] = entry
        print(f"{a['key']:<40} {len(frames)} fr  {meta['size']}  size_H={entry['size_H']}")
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--png', action='store_true')
    ap.add_argument('--only', default='')
    args = ap.parse_args()
    only = [s for s in args.only.split(',') if s]
    m = build(only or None, 'png' if args.png else 'webp')
    mpath = os.path.join(CHAR, 'LC_VFX_Manifest.json')
    if only and os.path.exists(mpath):
        with open(mpath, encoding='utf-8') as f:
            prev = json.load(f)
        prev['assets'].update(m['assets'])
        m['assets'] = {k: prev['assets'][k] for k in [a['key'] for a in REG] if k in prev['assets']}
    with open(mpath, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    with open(os.path.join(CHAR, 'LC_VFX_Manifest.js'), 'w', encoding='utf-8') as f:
        f.write('// Auto-generated by tools/vfx/gen_linchong.py - do not edit\nwindow.LC_VFX_MANIFEST = ')
        json.dump(m, f, ensure_ascii=False)
        f.write(';\n')
    import build_preview
    build_preview.build()
