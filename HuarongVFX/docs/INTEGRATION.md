# Cocos Creator 3.8 接入说明

1. 将 `Characters/Huarong/` 放入项目 resources 对应目录，并绑定 `manifest.json` 与 `Cocos/vfx-events.json`。
2. Battle 场景提供 `Caster_WeaponPoint / Attack_MidPoint / Target_HitPoint / Target_Feet`。
3. 图层名称按 manifest 固定。
4. Battle Core 先提交结果，再发 VFX 事件；VFX 不反推判定。
5. 连珠箭每段分别调用 Arrow / Hit，禁止一次大爆炸替代 4 Hit。
6. 退身箭 Hit 已发生后，才根据 DistanceChangeResult 调用 Success 或 Blocked。
7. 定身 CostPulse 仅提示 ACTIVE 变距成本 +20，不消耗状态；FORCED 变距不得调用。
8. 小李广由当前 FAR 状态调用 `setFarPassive(true/false)`。

素材按左→右制作。反向阵营统一通过播放器镜像。
