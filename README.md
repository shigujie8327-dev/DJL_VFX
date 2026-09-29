# 斗将录 VFX 素材

本仓库保存《斗将录：梁山篇》的特效交付素材及动效预览。

## 林冲

- [素材与接入说明](LinchongVFX/README.md)
- [交互预览](LinchongVFX/preview/index.html)：下载仓库后双击即可离线打开，包含五个技能、十个机制分支。
- [完整演示视频](LinchongVFX/preview/Linchong-VFX-showcase.mp4)、[枪阵演示](LinchongVFX/preview/Qiangzhen-Gather-Thrust.mp4)、[横扫千军演示](LinchongVFX/preview/Hengsao-Trail-Push-End.mp4)
- [透明 PNG](LinchongVFX/Characters/Linchong/)、[Cocos Creator 接入模板](LinchongVFX/Cocos/)
- [下载完整离线素材包](https://github.com/shigujie8327-dev/DJL_VFX/releases/tag/v1.1-r5)

当前版本为 `v1.1-r5`：枪阵贴地聚拢后沿弧线刺向敌人；横扫千军使用左向水平镜像，锋端对准左侧受击点。全部特效遵守[武侠风格、禁止魔法特效](LinchongVFX/docs/ART-DIRECTION.md)。

交互预览采用浏览器 Canvas。Cocos 模板共用素材、锚点和主要时序，尚未在正式游戏工程内编译验收。

## 花荣

- [素材与接入说明](HuarongVFX/README.md)
- [离线交互预览](HuarongVFX/preview/index.html)、[图标与拆分组件总览](HuarongVFX/preview/overview.png)
- [透明 PNG 素材](HuarongVFX/Characters/Huarong/)、[Cocos Creator 事件模板](HuarongVFX/Cocos/)

花荣素材以已定稿的五张技能图标为视觉母版，包含 27 张透明 PNG 和 22 个事件。连珠箭分四段命中；退身箭区分变距成功和受阻；定身箭只表示主动变距费用增加。Cocos 模板尚未在正式游戏工程内编译验收。
