# 花荣 VFX 素材包

依据仓库的《斗将录：梁山篇》战斗特效制作规范 v1.1，以及 2026-09-26 定稿的五张花荣技能图标制作。规范中写作“花荣”，用户消息中的“花容”按同一角色处理。素材按林冲包的目录、透明 PNG、manifest、事件表和离线预览方式交付。

## 交付内容

- `Characters/Huarong/`：27 张 RGBA 透明 PNG；包括 4 个主动技能、1 个固有能力及 2 个通用小粒子。`UI/` 保存五张 512×512 定稿图标副本，未改绘。
- `sources/`：25 个可编辑 SVG 源文件与 2 张图像生成的原始箭矢纹理。
- `manifest.json`：每张素材的路径、尺寸、锚点、图层、持续时间和来源。
- `Cocos/vfx-events.json`：22 个视觉事件；`Cocos/HuarongVfxPlayer.ts` 为 Cocos Creator 3.8 接入模板。
- `preview/index.html`：双击即可打开的离线交互预览；`preview/overview.png` 是图标与关键组件总览。
- `docs/alpha-report.json`：每张素材的透明通道检查。

## 图标视觉与机制

| 技能 | 图标视觉母版 | 演出重点 |
|---|---|---|
| 连珠箭 | 翠绿风迹、银白箭头 | 四支独立箭、四次独立 Hit；复用一张 Projectile 素材四次 |
| 穿云箭 | 冰蓝风压、银白重箭 | 单发高速穿透；空气锥与集中 Hit 分层 |
| 退身箭 | 月夜蓝、白蓝月弧 | 先结算箭的 Hit，再按规则分别播放完整或截断退身弧 |
| 定身箭 | 冰蓝链纹、淡紫中心 | 目标脚踝低亮链纹；表示主动变距额外 +20 气力 |
| 小李广 | 翠绿弓、准星 | 进入远距短促准星，持续只留弱弓身高光；离开远距熄灭 |

箭矢是可辨识的实体箭。翠绿和冰蓝主要附着于风压、箭迹或短暂反光。状态 Active 控制为小范围低亮显示；UI 状态图标、速度和费用数字仍由战斗 UI 负责。

## 预览与构建

直接打开 [`preview/index.html`](preview/index.html) 选择技能。预览按图标的五种技能演示机制分支；时间仅是视觉建议，正式命中必须由战斗规则事件触发。

构建工具需要 Node.js 和 `sharp`。安装 `sharp` 后运行：

```text
node HuarongVFX/tools/build.mjs
node HuarongVFX/tools/build-events.mjs
node HuarongVFX/tools/check.mjs
node HuarongVFX/tools/overview.mjs
```

图像生成的箭矢原图保存在 `sources/imagegen/`，重新运行构建不会再调用图像服务。其余组件从 `sources/*.svg` 源稿导出。检查结果为 27/27 张透明 PNG、22/22 个事件有合法素材引用。接入细节见 [`Cocos/INTEGRATION.md`](Cocos/INTEGRATION.md)。

## 尚需项目内验收

Cocos 模板和预览使用同一组贴图、锚点与主要时长，但未在正式游戏工程编译。接入时应按角色像素高度、左右朝向、实际命中点和战斗 UI 安全区校准缩放与位置；远距速度加成和定身费用仍由规则系统处理。
