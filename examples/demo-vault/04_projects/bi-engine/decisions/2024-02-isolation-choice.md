---
title: "Decision 001：BI 引擎插件隔离方案选型"
type: decision
created: 2024-02-15
updated: 2024-12-20
tags:
  - decision/bi-engine
  - decision/isolation
status: archived
maturity: teachable
confidence: 95
deadline: 2024-02-29
domain: ai-engineering
relations:
  supports: []
  contradicts: []
  evolves: []
  supersedes: []
context: 8 人 BI 团队；内部工具；支持业务方自定义指标插件；性能敏感（数据计算量大）
value:
  reuse: 0
  impact: 5
  uniqueness: 4
derived_to:
  - "[[experience/2024-plugin-sandbox-escape]]"
---

# Decision 001：BI 引擎插件隔离方案选型

## Problem

BI 引擎需要支持业务方上传自定义指标计算插件。问题：
- 插件代码不完全可信（业务方团队，安全审计水平参差）
- 性能敏感（数据计算量大，30% 性能损失难以接受）
- 团队 8 人，运维带宽有限

## Options

| 方案 | 隔离强度 | 性能损失 | 复杂度 |
|------|---------|---------|--------|
| A. 进程内 V8 isolate | 中 | <5% | 低 |
| B. 子进程 + IPC | 高 | ~30% | 中 |
| C. WebAssembly + WASI | 高 | ~15% | 高 |
| D. 容器 + gRPC | 极高 | ~40% | 高 |

## Chosen

**方案 A：进程内 V8 isolate**

## Reason

- 性能损失最低（< 5%）
- 团队熟悉 V8 API，落地快
- 当时认为 V8 isolate 已足够隔离（CVE 关注度不足）

## Rejected

- **B 子进程**：30% 性能损失认为不可接受
- **C WASM**：团队无经验，落地周期 > 1 季度
- **D 容器**：运维复杂度过高，8 人团队难以承担

## Expected

- V8 isolate 提供足够沙箱
- 性能损失可控
- 1 个月内可上线

## Actual

- **2024-07 沙箱逃逸**：业务方某插件利用 V8 已知 CVE 完成 OOB 读，泄露宿主 token
- 紧急回滚插件机制，3 周内重写为方案 B（子进程）
- 1 个客户数据泄露事件

## Lesson

> **派生为 [[experience/2024-plugin-sandbox-escape]]**

对不可信代码，进程级隔离的代价（30% 性能）远低于沙箱逃逸的代价（数据泄露）。边界契约缺失时，运行时沙箱只是延迟不可避免的失败。性能优化应基于「可接受的最强隔离」，而非「可接受的最弱隔离」。

---

## 派生

- → [[experience/2024-plugin-sandbox-escape]]（lesson 字段已派生为独立 experience 笔记）
- → [[principle/boundary-over-reuse]]（教训升格为原则）
- → [[pattern/process-level-isolation]]（教训抽象为模式）
