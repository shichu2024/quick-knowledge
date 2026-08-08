# Inbox · 采集入口

> 所有未经整理的素材先进这里。用 quick-kb-capture 写入，用 quick-kb-ingest 入库。

## 子目录

| 目录 | 用途 |
|------|------|
| `ideas/` | 临时灵感、想法 |
| `clips/` | 网页摘录（原始抓取在 `clips/_raw/`） |
| `meetings/` | 会议记录（v0.2 启用） |
| `ai-dialogs/` | AI 对话精华（v0.2 启用） |
| `reading/` | 阅读笔记（v0.2 启用） |

## 工作流

1. `quick-kb-capture "想记的东西"` → 写入 inbox 子目录
2. `quick-kb-ingest inbox/clips/某条.md` → 入库到 areas/resources
3. inbox 原始素材**永不删除**，由 review 闭环统一清理（v0.2 启用）
