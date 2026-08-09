---
title: 进程内沙箱模式（仅可信扩展）
type: pattern
created: 2024-03-15
updated: 2026-08-08
tags:
  - pattern/isolation
  - pattern/plugin
status: active
maturity: deprecated
confidence: 60
relations:
  supports: []
  contradicts:
    - "[[pattern/process-level-isolation]]"
  evolves: []
  supersedes: []
context: 仅适用于扩展代码完全可信（自有团队、CI 验证过）；性能敏感场景
value:
  reuse: 0
  impact: 3
  uniqueness: 2
---

# 进程内沙箱模式（仅可信扩展）

> ⚠ 此模式已被 [[pattern/process-level-isolation]] 在不可信场景下取代。

## 解决什么问题

性能敏感且扩展完全可信时，避免跨进程通信开销。

## 模式描述

- 扩展以 .so/.dll 或 V8 isolate 形式加载到宿主进程
- 通过运行时（V8 / Luau / WASM）隔离
- 共享宿主内存空间，但限制系统调用

## 适用条件

- **必须**：扩展代码完全可信（自有团队/CI 验证）
- **必须**：性能损失（30%+）不可接受
- **必须**：明确文档化此选择的风险

## 反模式（不要这样用）

- ❌ 对第三方/不可信代码用此模式 → 见 [[experience/2024-plugin-sandbox-escape]]

## 已应用案例

- BI 引擎插件体系（2024 Q1 之前）· 后被废弃
- 自家 Lua 脚本（可信）· 仍可用

## 相关模式

- [[pattern/process-level-isolation]] · 不可信场景的对立选择

## 待抽象

- [ ] 可信/不可信边界的判定标准可抽象为更高层模式？
