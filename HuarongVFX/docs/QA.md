# QA 记录

## 已检查
- 10 个独立视觉母版均经过透明背景清理，输出为 PNG。
- 正式目录通过 Git blob 复用相同母版，不使用程序化 Graphics 代替主体。
- 连珠箭时间轴存在 4 个 Projectile + 4 个 Hit。
- 退身箭事件顺序为 Hit → Distance Attempt → Success/Blocked；Blocked 不撤销 Hit。
- 定身状态持续层与 CostPulse 分离；CostPulse 不 End 状态。
- 小李广只有 FAR 激活 / 离开 FAR 关闭。
- BattleUI 图层始终位于 VFX 之上。

## 尚需工程内验收
Cocos 真机编译、角色实际 Anchor、左右阵营统一镜像、Battle UI 遮挡、贴图压缩与移动端性能。
