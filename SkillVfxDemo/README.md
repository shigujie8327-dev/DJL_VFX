# 斗将录 · 技能特效演示

在浏览器里直接播放《斗将录》V2 六位角色、二十四个技能的战斗特效。页面运行的是 Cocos 工程里的原始 VFX 代码（`SkillVfxRegistry.ts` 及其引用的全部 Effect），经 TypeScript 编译后，由一层模拟 `cc.Graphics` / `Sprite` / `resources` 的 Canvas 2D 适配层驱动，所以时序、顿帧、震屏、分层和音效与游戏一致。

## 打开

下载仓库后双击 `dist/djl-skill-vfx.html` 即可离线打开（美术、音效都已内嵌）。

- 顶部切换出招角色，下拉框选对手。
- 点技能卡播放；距离不符时先按项目的 0.3 秒滑步换距。
- 有分支的技能（疾风刺打断、回马枪反击、枪阵拦截、震地震慑、羽扇策回气、奇谋未中、空城受击减伤、回风斩回风、退身被拦、被闪避等）在右侧切换，对应 Core 事件给出的 `variant`。
- 0.1× 到 1× 慢放；拖动时间轴会用同一随机种子静默重放到该时刻，可逐帧查看。
- 技能结束后的状态光环（枪阵、定身、缚足、震慑、空城、醉步、回风等）和距离变化也会演出。

`dist/huarong-graphics-demo.html` 是花荣四技的旧版 cc.Graphics 手工移植，现在的注册表已改用帧动画占位版，保留作对照。

## 当前各角色的特效实现

| 角色 | 实现 |
| --- | --- |
| 林冲 | 帧动画，DJL_VFX 1.1-r5（正式交付） |
| 花荣 | 帧动画占位，按原 Graphics 编排 |
| 吴用 | 帧动画占位 1.1-wy-cocos-r2，按原 Graphics 编排；乱阵、空城为帧动画状态循环 |
| 鲁智深、扈三娘、武松 | 程序化 cc.Graphics |

`dist/` 里的页面对应 2026-09-30 的工程快照（含花荣退身箭、定身箭改用穿云箭箭矢贴图，退身箭近距离改为从弓直射胸口；吴用帧动画素材）。

## 重新构建

工程里的特效更新后，按下面步骤重建。需要 Node.js（全局或本地装 `typescript`）、Python 3 + Pillow，林冲的 `.wav` 音效需要 ffmpeg 转码。

```bash
# 参数是 DouJiangLuV2 工程根目录（包含 assets/ 的那一层）
node tools/bundle.js "Y:/Cocos Project/DouJiangLu_V2/DouJiangLuV2"         # → build/djl-vfx.js
python tools/encode_assets.py "Y:/Cocos Project/DouJiangLu_V2/DouJiangLuV2" # → build/assets.js
node tools/assemble.js                                                    # → dist/djl-skill-vfx.html
node tools/smoke_test.js                                                  # 可选：需要 playwright，逐个播放全部技能与分支
```

## 文件

| 路径 | 作用 |
| --- | --- |
| `src/cc-shim.js` | Cocos 运行时适配：小型节点树；Graphics 录制绘制指令并回放到 Canvas，按 Cocos 的路径语义处理 fill/stroke；Sprite 支持锚点、缩放、旋转、透明度和横向填充；resources/AudioSource 走内嵌素材 |
| `src/entry.ts` | 打包入口，导出注册表、状态光环、帧动画状态追踪器、音效表、角色定义和出手点配置 |
| `src/template.html` | 演示页：舞台、层级顺序（BattleFX_Back / Status_Back → 角色 → WeaponTrail … Status_Front）、滑步残影、受击反馈、分支与状态演出、界面 |
| `tools/bundle.js` | 用 `ts.transpileModule` 逐个编译工程 TS，并用极简 CommonJS 包装合成一个脚本；`cc` 指向适配层 |
| `tools/encode_assets.py` | 把舞台、立绘、技能图标、帧动画贴图（长边缩到 1024）和音效编码为 data URI |
| `tools/assemble.js` | 拼出单文件成品页 |
| `tools/smoke_test.js` | 无头浏览器冒烟测试 |

## 与游戏内的差异

- 飘字是技能面板伤害，未计护甲；重击判定用面板伤害 ≥ 40（游戏里按实际伤害）。
- 只演示我方出招；敌方受击为红闪加击退，闪避用项目的 DodgeEffect。
- HUD、血条、气条、回合流程不在演示范围内。
