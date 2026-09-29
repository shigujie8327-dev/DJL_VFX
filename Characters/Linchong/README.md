# 林冲 · 战斗特效素材包（VFX v1.1）

按《斗将录：梁山篇》战斗特效制作规范 v1.1 制作。每个技能以 Wiki 定稿技能图标为视觉母版，拆成 Cast / Trail / Hit / Particle / Status / Special / End。**没有给林冲统一配一种颜色**。

| 技能 | Wiki 视觉 DNA | 机制表达 |
|---|---|---|
| 疾风刺 Jifengci | 赤红 / 银白 | 银白细枪线 + 赤红速度场（非火焰）；打断时用银白红边斩线切断敌方行动轨迹 |
| 回马枪 Huimaqiang | 铜橙 / 金白 | Ready 半圆枪势 → 受击 → 铜金环形气流 → 回身弧 + 金白反刺；55 强化版更亮但不爆炸化 |
| 横扫千军 Hengsaoqianjun | 橙金 / 银白 | 薄而大的银白枪锋弧 + 橙金旋风；Hit 后第二层横向风压（强制变距），受阻时风压破碎，伤害不回滚 |
| 枪阵 Qiangzhen | 冰蓝 / 银白 | 光点落地 → 冰蓝阵纹 + 枪锋升起 → 低亮度 Loop → 远→近尝试时亮起 → 多枪影刺出 + 枪锋封锁 → 32×1 Hit → 阵纹断裂 |
| 固有·豹子头 Baozitou | 香槟金 / 银灰 | Trigger：淡金豹子轮廓 + 速度线；Active：枪身淡金高光 + Buff 图标；Consume：金色速度线收束至枪锋 |

## 目录

```text
Characters/Linchong/
├─ ActiveSkills/
│  ├─ Jifengci/        Cast · Trail · Hit · Particle · Special(Interrupt) · End
│  ├─ Huimaqiang/      Cast · Trail · Hit · Particle · Special(Ready/Trigger/Counter) · End
│  ├─ Hengsaoqianjun/  Cast · Trail · Hit · Particle · Special(ForcedPush/PushBlocked) · End
│  └─ Qiangzhen/       Cast · Status(Spawn/SpearGhost/Loop) · Special(Trigger/Attack/Block) · Hit · Particle · End
├─ PassiveSkills/
│  └─ Baozitou/        Trigger · Active · Consume · End
├─ CommonFX/           WeaponFlash · HitFlash · Spark · Dust · Wind · CommonParticles
├─ UI/                 LC_Baozitou_BuffIcon · LC_Qiangzhen_StatusIcon（无文字）
├─ LC_VFX_Manifest.json   素材元数据 + 演出时间轴（Cocos 接入用）
└─ LC_VFX_Manifest.js     同上，供预览页离线加载
```

阵地技能的阶段按 §4 标准目录归位：Spawn / Loop 放进 `Status/`（持续存在的地面阵），Trigger / Attack / Block 放进 `Special/`（阻挡变距）。反击的 Ready / Trigger / Counter 放进 `Special/`。

## 文件规范

- 命名：`LC_技能_阶段_编号.webp`，如 `LC_Jifengci_Hit_01.webp`。多帧序列按 `_01…_NN` 顺序播放，manifest 中带 `fps`。没有 `fps` 的多文件素材是变体或分层（如 `LC_Jifengci_Trail_01` 主体 + `_02` 赤红速度场层）。
- 格式：WebP，RGBA 32-bit 真透明，无黑底 / 白底 / 棋盘格，无人物、文字、UI 或环境。已紧裁切。需要 PNG 时运行 `python tools/vfx/gen_linchong.py --png`。
- 发光素材的透明度取自亮度，所以用普通 Alpha 混合（Normal）即可得到发光效果，也能叠在亮色背景上。

## 尺寸与 Anchor

manifest 中每个素材都有：

| 字段 | 含义 |
|---|---|
| `size` | 裁切后像素尺寸 |
| `anchor` | pivot，已换算为 Cocos `anchorPoint`（左下角为 0,0） |
| `ppu` | 每 1H 对应的源像素 |
| `size_H` | 推荐显示尺寸，以角色画面高度 H 为单位 |

在 Cocos 里显示：`node.scale = (H_px × size_H[0]) / size[0]`。所有素材都按 §8 控制：普通 Hit 0.37–0.44H，横扫千军（重攻击）Hit 0.68H，Cast ≤0.72H，枪类 Trail ≤1.5H。只有阵地 / 变距类（枪阵阵纹 1.56H 按 0.82 缩放显示，横扫风压）超过普通范围，符合 §8 的例外。

挂点（manifest `anchors`，单位 H，y 向上为负）：

| 挂点 | 用途 |
|---|---|
| `LC.Weapon_Tip` | Cast 闪光、Consume 收束点 |
| `LC.Body` / `LC.Cast` | 回马枪 Ready / Trigger、豹子头轮廓 |
| `LC.Spear_Mid` | 豹子头 Active 枪身高光（沿枪杆方向旋转） |
| `LC.Sweep` | 横扫千军弧心 |
| `LC.Field` | 枪阵阵心（地面） |
| `Target.HitPoint` | 所有 Hit；枪刺类 Trail 的 pivot 在枪尖，也挂这里 |
| `Target.Front` | 打断斩线、枪阵封锁 |

## 时间轴（manifest `timelines`）

8 段演出，全部事件驱动，时长按 §9：

| 演出 | 类型 | 时长 |
|---|---|---|
| 疾风刺 · 命中 / 打断成功 | 快速技能 | 0.45 s 核心 |
| 回马枪 · 35×1 普通 | 普通技能 | 0.5 s |
| 回马枪 · 受击反击 55×1 | 反击 | 反击段 0.54→1.35 s（含 0.05 s HitStop） |
| 横扫千军 · 击退成功 / 变距受阻 | 重攻击 | 1.1 s（含 0.04 s HitStop + 小幅屏震） |
| 枪阵 · 布阵 → 阻止接近 | 阵地技能 | 布阵 0.71 s，之后为持续期和触发演示 |
| 固有·豹子头 | 被动 | Trigger 0.3 s，Active 常驻，Consume 0.22 s |

事件类型：`fx`（素材、挂点、图层、时长，以及 alpha / scale / x / y / reveal 关键帧）、`particles`、`move`（角色微动，px，符合 §7 且回到 Anchor）、`distance`（success / blocked）、`hitstop`、`shake`、`dmg`、`tag`、`ui_status`、`intent`（敌方行动轨迹，打断演示用）。

`reveal` 对应 Cocos `Sprite.Type.FILLED` + `FillType.HORIZONTAL` 的 `fillRange`，枪刺 Trail 由此从林冲一侧推向枪尖。

图层严格使用 §15 冻结的顺序：`BattleFX_Back → Status_Back → Character → WeaponTrail → SkillFX → Projectile → HitFX → Status_Front → BattleUI`。

## 预览

用浏览器打开仓库根目录的 `LC_VFX_Preview.html`（可以离线打开，不需要服务器）。页面包含：

- 8 段演出逐帧播放，支持 0.1× 慢放、逐帧步进、拖动时间轴
- 按图层分行的时间轴，以及命中 / 顿帧标记
- 验收面板：Wiki 配色、演出时长与 §9 标准对比、命中段数、峰值尺寸、使用图层
- 战场 / 亮底 / 棋盘格三种背景，用来检查透明边
- Anchor 与 Battle UI 安全区叠加显示
- 全部素材清单，逐帧动画、尺寸、anchor、说明

人物为占位剪影（林冲定稿立绘还没接入 Wiki），H = 520 px，舞台 1920×1080。

## 重新生成

```bash
pip install pillow numpy
python tools/vfx/gen_linchong.py                 # 全部素材 + manifest + 预览页（约 7 分钟）
python tools/vfx/gen_linchong.py --only Jifengci # 只重做部分素材，manifest 合并更新
python tools/vfx/build_preview.py                # 只重建预览页
```

- 调色板：`tools/vfx/lc_common.py`
- 各素材的绘制函数：`tools/vfx/gen_linchong.py`
- 时间轴：`tools/vfx/lc_timeline.py`
