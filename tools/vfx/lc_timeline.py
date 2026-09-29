"""Linchong VFX timelines — event data shared by the HTML preview and Cocos integration.

Coordinates / units
  * H          : character display height in px (preview uses 520 px on a 1920x1080 stage)
  * anchors    : offsets in H from the actor root (feet); y < 0 is up
  * tracks     : [[normalised_time, value], ...] linearly interpolated over the event's `dur`
  * x / y      : extra offset in H;  sx / sy / scale : multiplier of the asset's native size_H
  * reveal     : 0..1 horizontal fill (Cocos Sprite FILLED / HORIZONTAL, fillRange)
  * frame      : fixed frame index (0-based); omitted => the sequence plays across `dur`
"""

LAYERS = ['BattleFX_Back', 'Status_Back', 'Character', 'WeaponTrail', 'SkillFX', 'Projectile', 'HitFX',
          'Status_Front', 'BattleUI']

ANCHORS = {
    'H': 520,
    'stage': [1920, 1080],
    'LC_root': [560, 880],
    'Target_root': {'NEAR': [1270, 880], 'FAR': [1580, 880]},
    'LC': {
        'Root': [0, 0], 'Ground': [0, 0], 'Body': [0, -0.55], 'Cast': [0.1, -0.6], 'Back': [-0.15, -0.55],
        'Weapon_Tip': [0.5, -0.6], 'Spear_Mid': [0.07, -0.58], 'Sweep': [0.7, -0.5], 'Field': [0.98, -0.1],
    },
    'Target': {'Root': [0, 0], 'Ground': [0, 0], 'HitPoint': [0, -0.55], 'Front': [-0.3, -0.5]},
    'spear': {'from': [-0.36, -0.56], 'to': [0.5, -0.6]},
}

FADE_OUT = [[0, 1], [0.6, 1], [1, 0]]
QZ = 0.82  # field display scale (keeps the rune clear of the bottom Battle UI band)
FLASH = [[0, 0], [0.15, 1], [0.6, 1], [1, 0]]


def fx(t, asset, anchor, dur, layer, **kw):
    e = {'t': round(t, 3), 'type': 'fx', 'asset': asset, 'anchor': anchor, 'dur': dur, 'layer': layer}
    e.update(kw)
    return e


def move(t, actor, dur, x=None, rot=None, y=None):
    e = {'t': round(t, 3), 'type': 'move', 'actor': actor, 'dur': dur}
    if x: e['x'] = x          # px (spec §7 is expressed in px)
    if y: e['y'] = y
    if rot: e['rot'] = rot    # degrees
    return e


def particles(t, asset, anchor, count, angle, speed, life, size, frame=0, gravity=0.0, layer='HitFX', align=True,
              spread=0.03):
    return {'t': round(t, 3), 'type': 'particles', 'asset': asset, 'frame': frame, 'anchor': anchor,
            'count': count, 'angle': angle, 'speed': speed, 'life': life, 'size': size, 'gravity': gravity,
            'layer': layer, 'align': align, 'spread': spread}


def dmg(t, actor, text, style='normal'):
    return {'t': round(t, 3), 'type': 'dmg', 'actor': actor, 'text': text, 'style': style}


def tag(t, actor, text, kind='mech'):
    return {'t': round(t, 3), 'type': 'tag', 'actor': actor, 'text': text, 'kind': kind}


def shake(t, dur, amp):
    return {'t': round(t, 3), 'type': 'shake', 'dur': dur, 'amp': amp}


def hitstop(t, dur):
    return {'t': round(t, 3), 'type': 'hitstop', 'dur': dur}


def shift(events, dt):
    out = []
    for e in events:
        e = dict(e)
        e['t'] = round(e['t'] + dt, 3)
        out.append(e)
    return out


# ------------------------------------------------------------------ 疾风刺
def jifengci_core(interrupt=False, speed_tag=None):
    ev = [
        move(0, 'LC', 0.45, x=[[0, 0], [0.12, -6], [0.3, 18], [0.62, 18], [1, 0]]),
        fx(0, 'LC_Jifengci_Cast', 'LC.Weapon_Tip', 0.14, 'SkillFX'),
        fx(0.07, 'LC_Jifengci_Trail', 'Target.HitPoint', 0.3, 'WeaponTrail', frame=1,
           reveal=[[0, 0], [0.25, 1]], alpha=[[0, 0], [0.1, 1], [0.45, 1], [1, 0]], x=[[0, -0.04], [1, 0.03]]),
        fx(0.07, 'LC_Jifengci_Trail', 'Target.HitPoint', 0.26, 'WeaponTrail', frame=0,
           reveal=[[0, 0], [0.3, 1]], alpha=FADE_OUT, x=[[0, -0.03], [1, 0.02]]),
        fx(0.15, 'LC_Jifengci_Hit', 'Target.HitPoint', 0.2, 'HitFX'),
        move(0.15, 'Target', 0.25, x=[[0, 0], [0.2, 10], [1, 0]]),
        particles(0.15, 'LC_Jifengci_Particle', 'Target.HitPoint', 8, [-18, 18], [1.6, 3.2], [0.12, 0.24],
                  [0.6, 1.1], frame=0),
        particles(0.15, 'LC_Jifengci_Particle', 'Target.HitPoint', 6, [-70, 70], [1.0, 2.2], [0.1, 0.2],
                  [0.4, 0.8], frame=1),
        dmg(0.16, 'Target', '26'),
        fx(0.33, 'LC_Jifengci_End', 'Target.HitPoint', 0.2, 'SkillFX', x=[[0, -0.55], [1, -0.4]],
           alpha=[[0, 0.8], [1, 0]]),
    ]
    if speed_tag:
        ev.append(tag(0.0, 'LC', speed_tag, 'buff'))
    if interrupt:
        ev += [
            {'t': 0.0, 'type': 'intent', 'action': 'show'},
            fx(0.15, 'LC_Jifengci_Interrupt', 'Target.Front', 0.2, 'HitFX', x=[[0, -0.1], [1, -0.1]]),
            {'t': 0.17, 'type': 'intent', 'action': 'break'},
            tag(0.2, 'Target', '打断'),
        ]
    return ev


# ------------------------------------------------------------------ 回马枪
def huimaqiang_normal():
    return [
        move(0, 'LC', 0.5, x=[[0, 0], [0.15, -6], [0.35, 16], [0.65, 16], [1, 0]]),
        fx(0, 'LC_Huimaqiang_Cast', 'LC.Weapon_Tip', 0.12, 'SkillFX'),
        fx(0.08, 'LC_Huimaqiang_Trail', 'Target.HitPoint', 0.3, 'WeaponTrail', reveal=[[0, 0], [0.3, 1]],
           alpha=FADE_OUT),
        fx(0.17, 'LC_Huimaqiang_Hit', 'Target.HitPoint', 0.2, 'HitFX'),
        move(0.17, 'Target', 0.25, x=[[0, 0], [0.2, 9], [1, 0]]),
        particles(0.17, 'LC_Huimaqiang_Particle', 'Target.HitPoint', 10, [-50, 50], [1.0, 2.4], [0.15, 0.3],
                  [0.6, 1.1]),
        dmg(0.18, 'Target', '35'),
        tag(0.18, 'Target', '未触发反击 · 35×1', 'info'),
    ]


def huimaqiang_counter():
    return [
        fx(0, 'LC_Huimaqiang_Ready', 'LC.Body', 0.62, 'Status_Back', alpha=[[0, 0], [0.25, 0.5], [0.6, 0.35],
                                                                          [0.85, 0.5], [1, 0.2]], x=[[0, -0.12], [1, -0.12]]),
        tag(0.0, 'LC', '回马枪 · 预备', 'info'),
        move(0.3, 'Target', 0.5, x=[[0, 0], [0.35, -70], [0.6, -70], [1, 0]]),
        {'t': 0.3, 'type': 'intent', 'action': 'show'},
        {'t': 0.48, 'type': 'intent', 'action': 'hide'},
        fx(0.48, 'LC_Common_HitFlash', 'LC.Body', 0.16, 'HitFX', scale=[[0, 0.5], [1, 0.8]], alpha=[[0, 1], [1, 0]],
           x=[[0, 0.1], [1, 0.1]]),
        move(0.48, 'LC', 0.2, x=[[0, 0], [0.3, -10], [1, 0]]),
        dmg(0.49, 'LC', '28', 'taken'),
        fx(0.54, 'LC_Huimaqiang_Trigger', 'LC.Body', 0.2, 'SkillFX'),
        tag(0.56, 'LC', '反击触发'),
        fx(0.74, 'LC_Huimaqiang_Trigger', 'LC.Cast', 0.1, 'SkillFX', frame=5, scale=[[0, 1], [1, 0.3]],
           alpha=[[0, 1], [1, 0]], x=[[0, -0.1], [1, 0.25]]),
        move(0.76, 'LC', 0.4, x=[[0, 0], [0.15, -12], [0.35, 22], [0.7, 22], [1, 0]]),
        fx(0.8, 'LC_Huimaqiang_CounterEnhanced', 'Target.HitPoint', 0.32, 'WeaponTrail',
           reveal=[[0, 0], [0.35, 1]], alpha=[[0, 1], [0.55, 1], [1, 0]]),
        fx(0.91, 'LC_Huimaqiang_HitEnhanced', 'Target.HitPoint', 0.24, 'HitFX'),
        hitstop(0.91, 0.05),
        shake(0.91, 0.12, 5),
        move(0.91, 'Target', 0.3, x=[[0, 0], [0.2, 14], [1, 0]]),
        particles(0.91, 'LC_Huimaqiang_Particle', 'Target.HitPoint', 14, [-60, 60], [1.2, 2.8], [0.18, 0.34],
                  [0.6, 1.2]),
        dmg(0.92, 'Target', '55', 'crit'),
        fx(1.1, 'LC_Huimaqiang_End', 'Target.HitPoint', 0.25, 'SkillFX', scale=[[0, 0.8], [1, 1.1]],
           alpha=[[0, 0.7], [1, 0]]),
    ]


# ------------------------------------------------------------------ 横扫千军
def hengsao(blocked):
    ev = [
        move(0, 'LC', 0.9, x=[[0, 0], [0.3, -12], [0.45, 20], [0.75, 20], [1, 0]],
             rot=[[0, 0], [0.3, -1.5], [0.45, 1.5], [0.8, 1.5], [1, 0]]),
        fx(0, 'LC_Hengsaoqianjun_Cast', 'LC.Cast', 0.3, 'SkillFX', alpha=[[0, 1], [0.85, 1], [1, 0]]),
        fx(0.22, 'LC_Hengsaoqianjun_Trail', 'LC.Sweep', 0.45, 'WeaponTrail', frame=1,
           scale=[[0, 0.85], [1, 1.05]], alpha=[[0, 0], [0.2, 0.85], [0.7, 0.6], [1, 0]]),
        fx(0.28, 'LC_Hengsaoqianjun_Trail', 'LC.Sweep', 0.3, 'WeaponTrail', frame=0,
           reveal=[[0, 0], [0.4, 1]], alpha=FADE_OUT),
        fx(0.4, 'LC_Hengsaoqianjun_Hit', 'Target.HitPoint', 0.25, 'HitFX'),
        hitstop(0.4, 0.04),
        shake(0.4, 0.14, 6),
        particles(0.4, 'LC_Common_Shard', 'Target.HitPoint', 9, [-45, 15], [1.0, 2.3], [0.3, 0.5], [0.5, 1.1],
                  gravity=4.0, align=False),
        particles(0.4, 'LC_Hengsaoqianjun_Particle', 'Target.HitPoint', 12, [-40, 40], [1.2, 2.8],
                  [0.15, 0.3], [0.6, 1.1]),
        dmg(0.41, 'Target', '62'),
    ]
    if not blocked:
        ev += [
            fx(0.5, 'LC_Hengsaoqianjun_ForcedPush', 'Target.HitPoint', 0.34, 'SkillFX', follow=True,
               x=[[0, -0.35], [1, -0.35]], alpha=[[0, 1], [0.7, 1], [1, 0]]),
            {'t': 0.5, 'type': 'distance', 'to': 'FAR', 'dur': 0.34, 'result': 'success'},
            tag(0.55, 'Target', '强制变距 近→远'),
            fx(0.84, 'LC_Hengsaoqianjun_End', 'Target.HitPoint', 0.25, 'SkillFX', alpha=[[0, 0.8], [1, 0]]),
        ]
    else:
        ev += [
            fx(0.5, 'LC_Hengsaoqianjun_ForcedPush', 'Target.HitPoint', 0.12, 'SkillFX', frame=0, follow=True,
               x=[[0, -0.35], [1, -0.3]]),
            {'t': 0.5, 'type': 'distance', 'to': 'FAR', 'dur': 0.34, 'result': 'blocked'},
            fx(0.6, 'LC_Hengsaoqianjun_PushBlocked', 'Target.HitPoint', 0.3, 'SkillFX', x=[[0, -0.3], [1, -0.3]]),
            tag(0.62, 'Target', '变距受阻 · 伤害不回滚'),
            fx(0.84, 'LC_Hengsaoqianjun_End', 'Target.HitPoint', 0.25, 'SkillFX', alpha=[[0, 0.6], [1, 0]]),
        ]
    return ev


# ------------------------------------------------------------------ 枪阵
def qiangzhen():
    ev = [
        move(0, 'LC', 0.4, x=[[0, 0], [0.3, 8], [1, 0]]),
        fx(0, 'LC_Common_WeaponFlash', 'LC.Weapon_Tip', 0.12, 'SkillFX', alpha=[[0, 1], [1, 0]],
           scale=[[0, 0.6], [1, 1]]),
        fx(0.04, 'LC_Qiangzhen_Cast', 'LC.Field', 0.2, 'SkillFX', x=[[0, -0.48], [1, 0]], y=[[0, -0.6], [1, 0]],
           alpha=[[0, 0], [0.2, 1], [1, 1]], scale=[[0, 0.6], [1, 0.6]]),
        fx(0.24, 'LC_Qiangzhen_CastImpact', 'LC.Field', 0.25, 'BattleFX_Back', scale=[[0, 0.4], [1, 1.05]],
           alpha=[[0, 1], [1, 0]]),
        fx(0.26, 'LC_Qiangzhen_Spawn', 'LC.Field', 0.45, 'BattleFX_Back', scale=[[0, 0.3], [0.5, QZ], [1, QZ]],
           alpha=[[0, 0], [0.3, 1], [1, 1]]),
        fx(0.71, 'LC_Qiangzhen_Loop', 'LC.Field', 0.72, 'BattleFX_Back', scale=[[0, QZ], [1, QZ]],
           alpha=[[0, 1], [0.35, 0.7], [0.7, 0.9], [1, 0.75]]),
        {'t': 0.72, 'type': 'ui_status', 'action': 'add', 'icon': 'LC_Qiangzhen_StatusIcon', 'label': '枪阵'},
        tag(0.72, 'LC', '枪阵 · 持续至林冲下次行动结束', 'info'),
    ]
    xs = [-0.43, -0.21, 0.0, 0.21, 0.43]
    ys = [0.03, -0.03, 0.02, -0.02, 0.03]
    for i, (dx, dy) in enumerate(zip(xs, ys)):
        t0 = 0.32 + i * 0.03
        ev.append(fx(t0, 'LC_Qiangzhen_SpearGhost', 'LC.Field', 0.35, 'SkillFX', x=[[0, dx], [1, dx]],
                     y=[[0, dy + 0.3], [1, dy]], alpha=[[0, 0], [0.5, 0.85], [1, 0.85]], scale=[[0, 0.62], [1, 0.62]]))
        ev.append(fx(t0 + 0.35, 'LC_Qiangzhen_SpearGhost', 'LC.Field', 1.43 - (t0 + 0.35), 'SkillFX',
                     x=[[0, dx], [1, dx]], y=[[0, dy], [1, dy]], alpha=[[0, 0.85], [0.2, 0.4], [0.6, 0.55], [1, 0.45]],
                     scale=[[0, 0.62], [1, 0.62]]))
    ev += [
        {'t': 1.25, 'type': 'distance', 'to': 'NEAR', 'dur': 0.5, 'result': 'blocked', 'attacker': 'Target'},
        tag(1.25, 'Target', '远→近 尝试'),
        fx(1.4, 'LC_Qiangzhen_Trigger', 'LC.Field', 0.22, 'BattleFX_Back', scale=[[0, QZ], [1, QZ]], alpha=[[0, 0], [0.12, 1], [1, 0.2]]),
    ]
    for i, (dy, d) in enumerate([(-0.14, 0.0), (0.0, 0.02), (0.14, 0.04)]):
        ev.append(fx(1.43 + d, 'LC_Qiangzhen_Attack', 'Target.HitPoint', 0.18, 'SkillFX',
                     x=[[0, -0.95], [1, -0.12]], y=[[0, dy], [1, dy * 0.4]], alpha=[[0, 0], [0.3, 1], [0.8, 1], [1, 0]]))
    for i, dx in enumerate(xs):
        ev.append(fx(1.43, 'LC_Qiangzhen_SpearGhost', 'LC.Field', 0.12, 'SkillFX', x=[[0, dx], [1, dx]],
                     y=[[0, 0], [1, -0.05]], alpha=[[0, 0.9], [1, 0]], scale=[[0, 0.62], [1, 0.62]]))
    ev += [
        fx(1.5, 'LC_Qiangzhen_Block', 'Target.Front', 0.42, 'SkillFX', alpha=[[0, 0], [0.1, 1], [0.6, 1], [1, 0]],
           x=[[0, 0.02], [1, 0.02]]),
        tag(1.52, 'Target', '变距被阻止'),
        fx(1.56, 'LC_Qiangzhen_Hit', 'Target.HitPoint', 0.2, 'HitFX'),
        shake(1.56, 0.1, 4),
        particles(1.56, 'LC_Qiangzhen_Particle', 'Target.HitPoint', 10, [-80, 80], [0.8, 2.0], [0.15, 0.3],
                  [0.5, 1.0], align=False),
        dmg(1.57, 'Target', '32'),
        fx(1.66, 'LC_Qiangzhen_End', 'LC.Field', 0.35, 'BattleFX_Back', scale=[[0, QZ], [1, QZ * 1.04]], alpha=[[0, 0.9], [1, 0]]),
        {'t': 1.7, 'type': 'ui_status', 'action': 'remove', 'icon': 'LC_Qiangzhen_StatusIcon'},
    ]
    return ev


# ------------------------------------------------------------------ 豹子头 (固有)
def baozitou():
    ev = jifengci_core(interrupt=True)
    ev += [
        fx(0.34, 'LC_Baozitou_Trigger', 'LC.Body', 0.3, 'Status_Back', frame=0, x=[[0, -0.46], [1, -0.38]],
           y=[[0, -0.1], [1, -0.1]],
           scale=[[0, 0.92], [1, 1.04]], alpha=[[0, 0], [0.2, 1], [0.6, 0.9], [1, 0]]),
        fx(0.36, 'LC_Baozitou_Trigger', 'LC.Body', 0.26, 'Status_Front', frame=1, x=[[0, -0.1], [1, 0.1]],
           alpha=[[0, 0], [0.25, 0.9], [1, 0]]),
        tag(0.36, 'LC', '豹子头 触发'),
        fx(0.62, 'LC_Baozitou_Active', 'LC.Spear_Mid', 1.03, 'WeaponTrail', rot=-2.7, sy=[[0, 2.2], [1, 2.2]],
           alpha=[[0, 0], [0.1, 1], [0.45, 0.65], [0.8, 1], [1, 1]]),
        {'t': 0.62, 'type': 'ui_status', 'action': 'add', 'icon': 'LC_Baozitou_BuffIcon', 'label': '豹子头 · 速度+2'},
        {'t': 1.45, 'type': 'caption', 'text': '— 下一回合 · 林冲再次攻击 —'},
        fx(1.65, 'LC_Baozitou_Consume', 'LC.Weapon_Tip', 0.22, 'SkillFX'),
        tag(1.65, 'LC', '豹子头 消耗 · 速度+2', 'buff'),
        {'t': 1.8, 'type': 'ui_status', 'action': 'remove', 'icon': 'LC_Baozitou_BuffIcon'},
        fx(1.86, 'LC_Baozitou_End', 'LC.Weapon_Tip', 0.14, 'SkillFX', alpha=[[0, 1], [1, 0]]),
    ]
    ev += shift(jifengci_core(), 1.87)
    return ev


TIMELINES = {
    'Jifengci_Hit': {'skill': 'Jifengci', 'name': '疾风刺 · 命中', 'category': '快速技能', 'std': [0.30, 0.50],
                     'setup': {'distance': 'NEAR'}, 'duration': 0.6, 'events': jifengci_core()},
    'Jifengci_Interrupt': {'skill': 'Jifengci', 'name': '疾风刺 · 打断成功', 'category': '快速技能',
                           'std': [0.30, 0.50], 'setup': {'distance': 'NEAR'}, 'duration': 0.65,
                           'events': jifengci_core(interrupt=True)},
    'Huimaqiang_Normal': {'skill': 'Huimaqiang', 'name': '回马枪 · 35×1 普通', 'category': '普通技能',
                          'std': [0.45, 0.75], 'setup': {'distance': 'NEAR'}, 'duration': 0.6,
                          'events': huimaqiang_normal()},
    'Huimaqiang_Counter': {'skill': 'Huimaqiang', 'name': '回马枪 · 受击反击 55×1', 'category': '反击',
                           'std': [0.70, 1.10], 'note': 'Ready → 受击 → Trigger → Counter → Hit；反击段 0.54→1.35s',
                           'setup': {'distance': 'NEAR'}, 'duration': 1.45, 'events': huimaqiang_counter()},
    'Hengsaoqianjun_Push': {'skill': 'Hengsaoqianjun', 'name': '横扫千军 · 击退成功 近→远', 'category': '重攻击',
                            'std': [0.70, 1.10], 'setup': {'distance': 'NEAR'}, 'duration': 1.15,
                            'events': hengsao(False)},
    'Hengsaoqianjun_Blocked': {'skill': 'Hengsaoqianjun', 'name': '横扫千军 · 变距受阻', 'category': '重攻击',
                               'std': [0.70, 1.10], 'setup': {'distance': 'NEAR'}, 'duration': 1.15,
                               'events': hengsao(True)},
    'Qiangzhen_Field': {'skill': 'Qiangzhen', 'name': '枪阵 · 布阵 → 阻止接近', 'category': '阵地技能',
                        'std': [0.45, 0.75], 'note': '布阵 0→0.71s；之后为持续期与敌方回合的触发演示',
                        'setup': {'distance': 'FAR'}, 'duration': 2.1, 'events': qiangzhen()},
    'Baozitou_Passive': {'skill': 'Baozitou', 'name': '固有·豹子头 · 触发 → 生效 → 消耗', 'category': '被动',
                         'std': [0.20, 0.40], 'note': 'Trigger 0.3s；Active 常驻至下一次攻击；Consume 于攻击开始',
                         'setup': {'distance': 'NEAR'}, 'duration': 2.6, 'events': baozitou()},
}
