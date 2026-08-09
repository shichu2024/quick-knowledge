---
title: 进程级隔离模式（不可信扩展）
type: pattern
created: 2026-08-08
updated: 2026-08-08
tags:
  - pattern/isolation
  - pattern/plugin
status: active
maturity: applied
confidence: 80
relations:
  supports:
    - "[[principle/boundary-over-reuse]]"
  contradicts:
    - "[[pattern/in-process-sandbox]]"
  evolves: []
  supersedes:
    - "[[pattern/in-process-sandbox]]"
context: 内部工具需支持第三方/不可信扩展；性能可接受 30% 内损失
value:
  reuse: 0
  impact: 5
  uniqueness: 4
---

# 进程级隔离模式（不可信扩展）

## 解决什么问题

当宿主工具需要支持第三方/不可信扩展时，如何在保留扩展能力的同时避免沙箱逃逸与权限提升。

## 模式描述

- 扩展运行在独立进程（子进程 / 容器 / Web Worker）
- 宿主与扩展通过序列化消息（IPC / postMessage）通信
- 扩展能力（文件/网络/系统调用）通过显式 capability 列表授权
- 接口 schema 版本化，扩展声明所兼容版本

## 关键步骤

1. 定义消息协议（请求/响应/事件）
2. 启动扩展进程，注入 capability
3. 宿主代理所有副作用（文件/网络）
4. 扩展崩溃可恢复，宿主不受影响
5. 性能监控 + 慢扩展熔断

## 适用条件

- **必须**：扩展代码不完全可信（第三方/用户脚本）
- **必须**：扩展可用性的损失在可接受范围
- **加分**：扩展数量可控（< 50）

## 反模式（不要这样用）

- ❌ 进程内 V8 isolate / QuickJS 隔离 → 见 [[experience/2024-plugin-sandbox-escape]]，逃逸风险高
- ❌ 把宿主对象直接暴露给扩展 → 破坏边界
- ❌ 不版本化协议 → 升级即破坏

## 已应用案例

- [[04_projects/plugin-system/_readme|插件系统项目]] · 进程级方案落地
- BI 引擎插件体系 · 重构为进程级（2024 Q4）

## 相关模式

- [[pattern/in-process-sandbox]] · 互斥（仅适用于可信扩展）
- pattern/capability-based-security（待 Capture）· 可组合

## 待抽象

- [ ] 是否可抽象出「跨进程 React 渲染」共享模式？
