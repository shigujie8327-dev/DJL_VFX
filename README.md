# DJL_VFX

《斗将录：梁山篇》战斗特效素材库，遵循 [`DouJiangLuV2 VFX Specification.md`](DouJiangLuV2%20VFX%20Specification.md)（v1.1）。

| 角色 | 状态 | 位置 |
|---|---|---|
| 林冲 LC | 四主动 + 固有·豹子头，47 组 / 101 张 RGBA WebP，8 段演出时间轴 | [`Characters/Linchong`](Characters/Linchong/README.md) |

**预览**：用浏览器打开 [`LC_VFX_Preview.html`](LC_VFX_Preview.html)，可逐帧播放全部技能演出，并查看素材清单和验收项。

`preview/wiki_icons/` 是从 DJLWiki 复制的林冲定稿技能图标，只用作视觉母版参照和预览页技能栏，不属于 VFX 素材。

生成工具在 `tools/vfx/`（Python，依赖 `pillow`、`numpy`）。
