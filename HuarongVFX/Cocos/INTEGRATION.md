# 花荣 VFX · Cocos Creator 3.8 接入

`HuarongVfxPlayer.ts` 是与林冲模板同结构的事件播放器。它负责分层贴图、淡入淡出、位移和循环停止，不计算伤害、费用、距离、命中或状态时长。尚未在正式游戏工程编译验收。

1. 把 `Characters` 目录复制到 `assets/resources/Characters`。PNG 导入为 SpriteFrame，保留原始 RGBA、中心 pivot `(0.5,0.5)`。关闭自动裁切；若使用图集裁切，保留 originalSize/offset。
2. 把 `manifest.json` 与 `Cocos/vfx-events.json` 导入为 JsonAsset，并绑定到 `HuarongVfxPlayer` 的对应字段。
3. 按前后顺序建立 `BattleFX_Back → Status_Back → Character → WeaponTrail → SkillFX → Projectile → HitFX → Status_Front → BattleUI`。播放器用到的每个图层都要有 `UITransform`。
4. 绑定 `Caster_WeaponPoint`、`Caster_PassivePoint`、`Attack_MidPoint`、`Target_HitPoint`、`Target_FeetPoint` 五个锚点。`Target_FeetPoint` 应位于目标脚踝附近。`Attack_MidPoint` 位于双方之间。所有图层与锚点使用同一坐标缩放。
5. 在战斗开始前等待 `await player.prepare()`。切换战斗或角色时调用 `resetBattle()`。

基准画面 1920×1080，参考人物高度 H=400。JSON 的 `w/h` 为场景显示尺寸，`x/y/dx/dy` 采用向下为正的编排坐标，播放器会转换为 Cocos UI 坐标。角色镜像朝向需要项目按攻防左右位置同步处理；当前素材与预览默认花荣在左侧、向右射箭。

## 规则事件绑定

| 规则时点 | 视觉调用 |
|---|---|
| 连珠箭出招 | `emit('LianzhuJian.Cast')` |
| 四次独立发箭 | 每次调用 `emit('LianzhuJian.Shot')` |
| 每段实际命中 | 依次 `hitVolley(1)` 到 `hitVolley(4)`；未命中段不发 Hit |
| 穿云箭出招、发箭、命中 | 分别 `ChuanyunJian.Cast`、`.Shot`、`.Hit` |
| 退身箭出招、发箭、命中 | 分别 `TuishenJian.Cast`、`.Shot`、`.Hit` |
| 退身箭命中后主动近→远成功 | `emit('TuishenJian.RetreatSuccess')`，人物微动由角色控制器完成 |
| 退身箭的主动变距被阻止 | `emit('TuishenJian.RetreatBlocked')`；已结算伤害保留 |
| 定身箭出招、发箭、命中 | 分别 `DingshenJian.Cast`、`.Shot`、`.Hit` |
| 定身实际施加 | `emit('DingshenJian.Apply')`；只在规则判定命中并施加后调用 |
| 目标主动变距增加费用时 | 可选 `emit('DingshenJian.CostPulse')`；UI 显示 +20 气力 |
| 定身到期或被移除 | `emit('DingshenJian.Expire')` |
| 进入远距 | `enterFar()`；规则系统另外设置速度 +1 和 UI Buff |
| 离开远距 | `leaveFar()`；规则系统另外移除速度 +1 和 UI Buff |

`DingshenJian.Apply` 的 Active 链纹循环只表示费用上升，不拦截强制变距，也不能把目标动画冻结。`TuishenJian.Hit` 与两个退身分支是不同事件，便于受阻时保留已结算伤害。四段连珠箭的 `Hit1..Hit4` 使用相同命中纹理但不同小幅落点，避免合并成一次大爆点。

所有人物微动结束后应恢复既定角色 Anchor。Hit 绑定 `Target_HitPoint`，链纹绑定 `Target_FeetPoint`，BattleUI 始终在 VFX 上方。透明素材按普通 Alpha 混合；不要统一改为加法混合。
