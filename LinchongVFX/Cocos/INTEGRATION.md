# Cocos Creator 3.8 接入

本目录为接入模板，尚未在实际游戏工程中编译验证。不要把演示时间轴中的等待时间当成战斗规则。

全套素材遵守 [武侠美术方向](../docs/ART-DIRECTION.md)：禁用魔法阵、符文、电弧、激光和霓虹粒子。

## 导入与绑定

1. 把 `Characters` 完整目录复制到 `assets/resources/Characters`。UI 中五张 Wiki 参考图标可按项目现有 UI 系统复用。
2. 导入 `manifest.json` 与本目录的 `vfx-events.json` 为 JsonAsset，挂载 `LinchongVfxPlayer.ts` 并绑定这两个字段。
3. 纹理类型设为 SpriteFrame；保留 Alpha，默认普通透明混合。使用中心 pivot (0.5, 0.5)。为保持提供的画布尺寸和锚点，先关闭自动裁切；若自行打图集裁切，应保留 originalSize / offset 信息。
4. 按规范从后到前建立 UI 图层并绑定 layers：BattleFX_Back → Status_Back → Character → WeaponTrail → SkillFX → Projectile → HitFX → Status_Front → BattleUI。图层节点须有 UITransform，设置一致缩放，BattleUI 置顶。
5. 绑定 anchors，节点名必须匹配：Caster_WeaponPoint、Caster_PassivePoint、Target_HitPoint、Ground、Attack_MidPoint。Attack_MidPoint 位于攻防锚点之间，Ground 为阵地落地点。
6. 等待 `await player.prepare()` 完成后再开始战斗。资源加载按官方 [动态加载 SpriteFrame 的方式](https://docs.cocos.com/creator/3.8/manual/en/asset/dynamic-load-resources.html) 使用无扩展名路径加 `/spriteFrame`。

默认基准宽高 1920×1080，H=400。JSON cue 中 w/h 是场景显示尺寸，x/y 是相对锚点偏移，Y 向下；组件已把它转换为 Cocos UI 的 Y 向上坐标。SpriteFrame 使用普通透明材质，勿直接叠加为纯 Additive，否则黑色碎屑消失、银白边过曝。

## 事件对照

| 战斗事件 | 调用 |
|---|---|
| 疾风刺 ActionStarted | `emit('Jifengci.Cast')` |
| 疾风刺伤害命中结算 | `emit('Jifengci.Hit')` |
| 打断成功 | `emit('Jifengci.Interrupt')`，同时停止被打断的敌方攻击轨迹，然后 `triggerPassive()` |
| 回马枪待机 | `emit('Huimaqiang.Ready')` |
| 敌方非攻击行为，普通出枪 | `emit('Huimaqiang.Normal')` |
| 敌方攻击实际命中且该次攻击全部结算后 | `counterAfterActualHit(actionId)`，相同 actionId 只触发一次 |
| 回马枪伤害命中 | 按结果调用 `emit('Huimaqiang.Hit35')` 或 `emit('Huimaqiang.Hit55')` |
| 横扫开始 | `emit('Hengsaoqianjun.Cast')` |
| 横扫命中 | `emit('Hengsaoqianjun.Hit')` |
| 命中后的强制变距尝试 | `emit('Hengsaoqianjun.Push')` |
| 变距被阻止 | `emit('Hengsaoqianjun.Blocked')`，终止推力 tag；不得撤销已结算伤害 |
| 枪阵施放 | `activateField()`，循环保持至外部事件 |
| 敌方 FAR→NEAR 尝试，规则系统判定触发枪阵 | `interceptField()`，移除阵地并播放单次拦截 Hit |
| 林冲下一次战斗行动结束、枪阵仍在 | `expireField()`，不播放 Hit |
| 成功打断 / 截击后获得豹子头 | `triggerPassive()` |
| 下一次攻击 ActionStarted | `consumePassiveOnAttackStarted()` |
| 换场 / 战斗结束 | `resetBattle()` |

`interceptField()` 内已包含枪阵 Hit 视觉，不要再额外调用另一个枪阵 Hit。枪阵是否属于可触发豹子头的“截击”由正式规则系统判断；播放器不会推断或附赠被动。

播放器只处理视觉，不计算伤害、30% 概率、费用、合法距离或速度。也不自动移动人物、更新 UI 或自动取消敌方技能。角色微动、受击后退、状态图标、真实距离布局由现有 Battle UI / 角色控制器处理，并在微动结束时恢复既定 Anchor。强制距离改变后的新布局是独立的逻辑锚点。

## 演出基准

- 疾风刺：Cast 0.00s；Trail 0.07s；预览命中 0.17s；结尾 0.46s。
- 回马枪强化：敌方命中结算后回身风沙 0.00s；反刺 0.20s；预览命中 0.30s。待机不自动触发。
- 横扫：Cast 0.00s；Trail 0.20s；预览命中 0.37s；推力从命中后 0.09s 开始。
- 横扫 r5：Trail 使用水平镜像后的银白弯钩纹理，面向左侧敌人。预览中林冲位于右侧，Attack_MidPoint=(970,585)、Target_HitPoint=(740,585)，相对偏移 `(58,−18)` 使锋端落在受击点。项目中的攻击间距若不同，应依相同端点校准方式调整 Attack_MidPoint 或 cue 的 x/y。Push 和 End 的 `mirrorX` 随左向轨迹同步，强制推远朝左；变距受阻时 Push 长度缩至 0.13s，再切换碎裂。若生产战斗还需右向版本，应分别提供右向纹理和 cue，不能只修改一个贴图而保留左向锚点。
- 枪阵 r4：施放与待机独立于拦截；五个 GatherSpear 实例先从土中立枪位置**降至地面附近聚拢**（0.00–0.30s），然后 Attack 从 Ground 出发按二次贝塞尔曲线向上刺到 Target_HitPoint（0.28–0.53s），0.50s 播放唯一一次 32×1 Hit。ArcTrail 是灰白风痕与细沙，按进度显露；没有发射高度或法术地纹。枪身沿路径切线旋转，目标终点随 Target_HitPoint 锚点变化。到期分支不会聚枪或攻击。移动、旋转、透明度和风痕显露逻辑在 Canvas 与 Cocos 模板中采用同一 cue 参数。
- 豹子头：Trigger 0.25s；Active 无限低亮等待；Consume 0.23s 后消失。

上述命中时间只用于镜头同步建议；生产环境中以真实战斗事件为准。Hit 与 Trail 分开调用可避免未命中也闪出命中特效。
