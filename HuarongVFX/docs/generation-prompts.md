# 原始位图生成提示词

本包使用内置 imagegen 生成两张透明箭矢原图，并复制到 `sources/imagegen/`。最终战斗尺寸由 `tools/build.mjs` 导出；同一张连珠箭 Projectile 在时序中独立复用四次。其余 25 张素材为项目可编辑 SVG 绘制。

## 连珠箭 · Projectile

> Use case: stylized-concept. Asset type: isolated 2D game VFX texture for Huarong's Lianzhu Jian (four consecutive arrows), one reusable single arrow projectile component. Reference visual style: classic Chinese wuxia action, emerald green thin wind streaks and a physically recognizable silver-white arrow with steel arrowhead and dark shaft, from the finalized skill icon showing four parallel silver arrows flying through green wind. One arrow only, pointing exactly right, full side profile, centered horizontally, long narrow silhouette, sharp metal glint, delicate curved jade-green air streaks behind the shaft, a few tiny wind flecks. Transparent RGBA background, ample alpha padding, no character, no landscape, no UI, no words, no border, no frame, no white or black backdrop. Must read at game scale and avoid magical laser/neon effects.

## 穿云箭 · Projectile

> Use case: stylized-concept. Asset type: isolated 2D game VFX texture for Huarong's Chuanyun Jian. Reference style: finalized icon of one heavy silver Chinese arrow piercing dark clouds in icy blue wind. ONE physical silver-white heavy arrow, pointed exactly right in side profile, larger triangular steel head, dark shaft and fletching, very narrow ice-blue compressed air wake trailing to the left and a thin conical bow shock just behind the arrowhead; concentrated single-shot piercing force. Wide horizontal composition, transparent RGBA background with alpha padding. Wuxia metal-and-wind material, crisp and readable at small game size. No character, no clouds/scene backdrop, no text, no UI, no frame, no magic circles, no electricity, no lasers, no fire.
