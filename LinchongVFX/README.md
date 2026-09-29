# 林冲 VFX 素材与动效预览

依据《斗将录：梁山篇》VFX 制作规范 v1.1 制作，覆盖四个主动技能与「豹子头」被动。

**美术硬约束：武侠风格，禁止魔法、科技感特效。**冷钢、风压、沙土、金属火星承载技能辨识度；不得使用魔法阵、符文、电弧、激光、能量光环或霓虹粒子。详见 [美术方向](docs/ART-DIRECTION.md)。

## 直接预览

- 双击 `preview/index.html`，可离线运行，无需安装依赖。
- `preview/Linchong-VFX-showcase.mp4`：约 21 秒、1920×1080、30fps H.264 演示视频。`preview/Qiangzhen-Gather-Thrust.mp4` 展示枪阵贴地聚拢、弧线突刺；`preview/Hengsao-Trail-Push-End.mp4` 展示左向镜像的横扫千军命中、推远和受阻分支。视频包含演示背景与文字；**透明游戏素材只从 Characters 目录取用**。
- 预览支持五技能、十个机制分支、暂停、重播、0.25× / 0.5× / 1×、时间轴、深色 / 浅色 / 棋盘验收背景、隐藏标靶、全屏。
- 空格可切换播放；选择技能卡切换演出。状态等待时间经过演示压缩，不能作为正式战斗的自动触发计时器。

## 交付内容

| 内容 | 位置 |
|---|---|
| 38 个独立 RGBA PNG 组件 | `Characters/Linchong/`（不含 UI 的五枚参考图标） |
| 疾风刺 | `ActiveSkills/Jifengci/`：Cast、Trail、Hit、Interrupt、End |
| 回马枪 | `ActiveSkills/Huimaqiang/`：Ready、Cast、Trigger、Counter、Hit、End |
| 横扫千军 | `ActiveSkills/Hengsaoqianjun/`：Cast、Trail、Hit、Push、Blocked、End |
| 枪阵 | `ActiveSkills/Qiangzhen/`：Cast、Ground、Spawn、Loop、Trigger、GatherSpear、ArcTrail、Attack、Block、Hit、End |
| 豹子头 | `PassiveSkills/Baozitou/`：Trigger、Active、Consume、End |
| 通用组件 | `CommonFX/`：WeaponFlash、HitFlash、Dust、Spark、Wind、Shard |
| 图层、Anchor、尺寸、Alpha 元数据 | `manifest.json` |
| 完整演示时间轴 | `timelines.json` |
| 正式接入事件库 / 播放组件模板 | `Cocos/vfx-events.json`、`Cocos/LinchongVfxPlayer.ts` |
| 可编辑辅助素材源文件 | `sources/`，30 个 SVG 源文件 |
| AI 生图提示词 | `docs/generation-prompts.json` |
| 验证报告 | `docs/alpha-report.json`、`docs/preview-check.json`、`docs/video-check.json` |

目录按规范拆分。未使用 Projectile，未创建空目录。Special / Status 内按文件阶段名区分 Spawn、Trigger、Push、Blocked 等模块。

## 图标视觉来源

来自用户指定的 [DJLWiki](https://github.com/shigujie8327-dev/DJLWiki)，读取提交 `6d0dad6aa0fe7454a532940cf29a418505a70286` 的 `data.js` 与 `skills/icons/linchong-*.webp`。

| 技能 | 视觉 DNA | 动效机制 |
|---|---|---|
| 疾风刺 | 赤红气流 + 银白细枪锋 | 26×1；成功打断时切断行动轨迹，触发豹子头 |
| 回马枪 | 铜橙风沙 + 金白枪线 | 35×1 普通 / 实际受击后 55×1；回身风沙收束后反刺 |
| 横扫千军 | 橙金横风 + 银白薄锋 | 左向镜像锋端对准左侧 Target_HitPoint；62×1 后播放独立横向风压，受阻时风压截断破碎，末尾只保留低亮残风；伤害不撤销 |
| 枪阵 | 地面沙土 + 冷钢枪锋 | FAR→NEAR 尝试触发，五杆实体枪贴地聚拢，沿上扬弧线刺向对方；32×1 后消失；到期不命中 |
| 豹子头 | 香槟金速度弧 + 银灰豹纹 | Trigger 0.25s；低亮枪光持续；下一次攻击开始时收束消耗 |

关键兵器组件使用内置 imagegen，逐组件生成，定稿技能图标作为造型参考；原始透明 Alpha 保留。枪阵 Spawn、GatherSpear、Attack 已替换为实体钢枪和泥土、灰白风痕，新增可单独复用的 ArcTrail。回马枪 Ready、Trigger 改为不闭合的物理风沙弧。横扫千军的 Trail 已按用户指定水平镜像，尖端向左；Push、End 在播放时同步水平镜像。指定的旧版图片镜像备份位于 `sources/variants/LC_Hengsaoqianjun_Trail_v1_Left_01.png`，正式播放使用 `Characters` 下的修订版 Trail。原始透明 PNG 源文件保存在 `sources/imagegen/`，本轮定稿提示词保存于 `docs/qiangzhen-wuxia-prompts.json` 和 `docs/hengsao-revision-prompts.json`。辅助组件以可编辑 SVG 制作并导出 RGBA PNG，未使用背景抠除。生成图片的原始分辨率随工具输出保留，实际尺寸记录于 manifest；辅助素材为 1024 / 512 / 256 像素。

## 时间与尺度

基准为 1920×1080、角色高度 H=400。主动演出为疾风刺 0.46s、回马枪 0.66s、横扫 0.88s；枪阵施放与拦截是两个独立短演出，持续等待由状态管理。Hit 0.22s、状态消失 0.22–0.28s。

预览中 Trail 最大展示宽度 590px（1.475H），普通 Hit 可见核心约 0.3–0.5H；豹子头 Trigger 占 115px（0.288H），持续亮度 0.22。完整图片画布包含透明边距，不能把图片画布大小等同于可见亮区。

施放端微动在 16–21px 范围内并回到原点。强制变距的敌方布局变化单独保存，区别于受击微动。参考 Wiki 当前没有林冲独立立绘，预览采用抽象施放标记与受击标靶；交付素材无人物、文字、UI、棋盘格或不透明背景。

## 验证与限制

- 38/38 PNG 均为四通道，具有透明与半透明像素；在浅底、深底、棋盘背景上检查。
- 十个分支均无缺失组件，无浏览器脚本错误；攻击分支均只有一次伤害事件，枪阵到期无伤害。
- 横扫千军左向镜像预览中，Trail 锋端于命中时落在约 `(745.9,584.3)`，左侧目标受击点为 `(740,585)`；Push 与 End 是两张不同的透明素材，播放时水平镜像。正式 Cocos 工程须以实际 Anchor 校准。
- 验证了施放端归位、慢放、拖动时间轴、暂停以及 file:// 离线加载；视频全片解码完成，并验证八处跳转（含 20.8s 末尾）。
- Cocos 3.8 组件为可接入模板；当前工作区没有完整 Cocos 游戏工程，**尚未进行 Cocos 引擎内编译、真机性能或正式 Battle UI 遮挡验收**。最终层级、人物锚点与贴图压缩请在工程内校准。
- 浏览器 Canvas 与 Cocos 并非同一渲染器。本包共用图片、主要轨迹和时序；枪阵的地面起点、贝塞尔弧线、朝向和风痕逐步显露已在两个播放器内同步。浏览器附加的标靶、伤害数字、微动、少量程序化沙尘由展示页绘制；Cocos 接入时需接到项目的角色、UI 和粒子系统。不能据此宣称像素级一致，也不能假定导入 Cocos 自动提高画质。
- 该包以分层 Sprite 的平移、缩放、旋转、透明度以及粒子组合成动效，未烘焙为逐帧序列图或 Spine 人物动画。

## 重建

`tools/build.mjs` 生成辅助素材、manifest、离线预览数据与 Alpha 报告；`tools/export-events.mjs` 导出时间轴与事件库；`tools/server.mjs` 提供仅本机访问的 4173 端口服务；`tools/check.mjs` 进行浏览器验证；`tools/record.mjs` 导出演示视频。

脚本使用当前工作站的 Node、Sharp、Playwright 与 Edge。迁移机器时修改工具顶部依赖路径。现成预览和 PNG 的使用不需要这些依赖。
