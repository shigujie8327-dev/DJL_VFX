# imagegen source notes

这里保存本轮透明清理后的关键视觉母版。正式游戏资源位于 `Characters/Huarong/`。

流程：VFX v1.1 拆组件 → 生成单一主体 → 去背景 → 视觉复核 → 复用到规范目录 → Cocos 通过位移 / 缩放 / Alpha / Reveal 组合。

Git 会对重复二进制内容去重；目录阶段语义仍由 manifest / vfx-events 定义。
