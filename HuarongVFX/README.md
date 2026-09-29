# 花荣 VFX 素材与动效预览

依据《斗将录：梁山篇》VFX 制作规范 v1.1，并复用 `LinchongVFX/` 的交付结构制作。规则与技能图标来源锁定 DJLWiki 提交 `6d0dad6aa0fe7454a532940cf29a418505a70286`。

## 视觉核心
花荣靠 **弓箭、箭迹、精准** 统一角色辨识，不强行统一为单一角色主色。

| 技能 | 视觉 DNA | 机制演出 |
|---|---|---|
| 连珠箭 | 翠绿 + 银白 | 同一实体箭母版连续四次；四次小 Hit 可数 |
| 穿云箭 | 冰蓝 + 银白 | 单发重箭 + 压缩空气 + 集中穿透 Hit |
| 退身箭 | 月夜蓝 + 白蓝运动弧 | 命中后再尝试 Near→Far；成功完整显露，受阻截断 |
| 定身箭 | 冰蓝链环 + 淡紫节点 | 脚踝低亮链环；主动变距 +20 Energy；强制变距不受影响 |
| 小李广 | 翠绿准星 / 弓形 | 进入 FAR 短暂提示，持续阶段低亮 |

**硬约束：武侠弓术，不做魔法师。** 禁止魔法阵、符文、电弧、激光、霓虹爆炸和长期覆盖角色的大型状态特效。

## 交付
- 正式透明 PNG：`Characters/Huarong/`
- 通用组件：`Characters/Huarong/CommonFX/`
- 图层 / Anchor / Alpha 元数据：`manifest.json`
- 机制演示时间轴：`timelines.json`
- Cocos 事件库 + 播放器：`Cocos/`
- 离线 HTML 预览：`preview/index.html`
- 清理后的 imagegen 母版：`sources/imagegen/`
- 美术与接入规范：`docs/`

## 规则绑定
- 连珠箭：远｜30气｜11×4｜S8；FAR 下小李广使最终速度为 9。四段分别计算护甲。
- 穿云箭：远｜45气｜55×1｜S5；FAR 下最终速度为 6。
- 退身箭：近｜25气｜18×1｜S9；造成伤害后发起 Near→Far 主动变距尝试，受阻不回滚伤害。
- 定身箭：远｜30气｜20×1｜S6；命中施加定身至下一回合结束；目标主动变距 +20 Energy，强制变距不受影响。
- 小李广：处于 FAR 时所有攻击技能 Speed +1。

## Cocos 推荐事件顺序
```text
连珠箭: Cast -> (Arrow -> Hit) × 4
穿云箭: Cast -> Arrow -> Hit
退身箭: Cast -> Arrow -> Hit -> DistanceSuccess / DistanceBlocked
定身箭: Cast -> Arrow -> Hit -> Apply -> [CostPulse...] -> End
小李广: FAR entered -> Activate ; FAR left -> Deactivate
```

VFX 不计算伤害、护甲、命中、Speed、Energy 或变距合法性，只消费 Battle Core 已确定的结果。

## Anchor
需要 `Caster_WeaponPoint`、`Attack_MidPoint`、`Target_HitPoint`、`Target_Feet`。其中 `Target_Feet` 专供定身链环，避免状态贴胸或遮挡主体。

母版方向为左→右；反向站位由统一战斗 VFX 层镜像，不复制资源。
