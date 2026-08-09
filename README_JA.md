# quick-knowledge

> 個人ナレッジベース × AI スキルフレームワーク —— 一連のスキルで、断片的な情報を再利用可能な個人資産に蒸留します。

[中文](./README.md) · [English](./README_EN.md) · [한국어](./README_KO.md) · [Español](./README_ES.md)

---

## これは何

`quick-knowledge` は [Agent Skills プロトコル](https://agentskills.io) に基づくナレッジベーススキル群です。任意の互換ランタイム（Claude Code / Codex / Cursor / OpenCode など）で、**Capture → Ingest → Connect → Review** を一文で完結します。

3 つの課題を解決します：

| 課題 | quick-knowledge のアプローチ |
|------|------------------------------|
| **腐敗** —— ノートが蓄積されるが振り返らない | Review ループ + 信頼度減衰 |
| **孤島** —— 記録したが見つからない、繋がらない | Connect ループ + 双方向リンク + MOC |
| **高摩擦** —— 分類・命名・テンプレで疲れる | Capture 段階では分類しない、AI が Normalize |

---

## インストール

### 方式 1 ・ 汎用ワンライナー（推奨・全 runtime 対応）

```bash
npx skills add shichu2024/quick-knowledge
```

### 方式 2 ・ Claude Code marketplace

Claude Code 内で：

```
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

### 方式 3 ・ 手動インストール（runtime 別）

| Runtime | パス |
|---------|------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

vault の初期化はインストール後、任意の空ディレクトリで `初始化我的知识 base`（中国語）/ `Initialize my knowledge base`（英語）と呼びかけるだけです。

---

## 5 分クイックスタート

1. **初期化**：「初始化我的知识库」/「Initialize my knowledge base」
2. **Capture**：「抓 https://example.com/article」
3. **Ingest**：「入库 inbox 这条」
4. **Query**：「我笔记里关于 X 怎么说？」
5. **Advisor** (v0.3+)：「我要做 X，怎么做？」

詳細は [docs/quick-start.md](./docs/quick-start.md)。

---

## 仕組み

### 6 つのクローズドループ

```
Capture → Ingest → Normalize → Connect → Query → Review → (Capture へ)
```

### 3 つの Agent（入力ドメイン非重複）

- **manager-agent** —— ライブラリ構造管理
- **research-agent** —— 外部資料処理
- **memory-agent** —— 長期記憶呼び出し（コア差別化）

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## ロードマップ

| フェーズ | 状態 | 主な内容 |
|----------|------|---------|
| v0.1 mvp | ✅ | init/capture/ingest/daily + 中国語テンプレ |
| v0.2 loops | ✅ | connect/query/review + manager/research-agent + 英語テンプレ |
| v0.3 assistant | ✅ | memory-agent + advisor/project/goal + 認知資産テンプレ |
| v0.4 extensions | ✅ | normalize/archive/stats/import + kb.config + 多言語 README |
| v1.0 release | 🚧 | CONTRIBUTING/LICENSE + CI + demo-vault 公開 |

---

## ドキュメント

- [DESIGN.md](./docs/DESIGN.md) —— 完全設計（信源）
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) —— スキル詳細
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) —— Agent 詳細（ランキング式含む）

---

## 謝辞

- [Agent Skills Protocol](https://agentskills.io)
- [Obsidian](https://obsidian.md)
- [Zettelkasten](https://zettelkasten.de)
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

---

## License

v1.0 リリース時に決定（MIT または Apache 2.0 想定）。
