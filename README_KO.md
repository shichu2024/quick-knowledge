# quick-knowledge

> 개인 지식 베이스 × AI 스킬 프레임워크 —— 하나의 스킬 세트로 파편화된 정보를 재사용 가능한 개인 자산으로 증류합니다.

[中文](./README.md) · [English](./README_EN.md) · [日本語](./README_JA.md) · [Español](./README_ES.md)

---

## 이것은 무엇인가

`quick-knowledge`는 [Agent Skills 프로토콜](https://agentskills.io) 기반의 지식 베이스 스킬 모음입니다. 호환되는 런타임(Claude Code / Codex / Cursor / OpenCode 등)에서 **Capture → Ingest → Connect → Review**를 한 문장으로 완료합니다.

세 가지 문제를 해결합니다:

| 문제 | quick-knowledge의 접근 |
|------|------------------------|
| **부패** —— 노트가 쌓이지만 검토되지 않음 | Review 루프 + 신뢰도 감쇠 |
| **고립** —— 기록했지만 찾을 수 없음 | Connect 루프 + 양방향 링크 + MOC |
| **고마찰** —— 분류/이름/템플릿이 피곤 | Capture 단계에서 분류 생략, AI가 Normalize |

---

## 설치

### 방식 1 · 범용 원라이너 (권장, 모든 runtime)

```bash
npx skills add shichu2024/quick-knowledge
```

### 방식 2 · Claude Code marketplace

Claude Code 안에서:

```
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

### 방식 3 · 수동 설치 (runtime별)

| Runtime | 경로 |
|---------|------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

vault 초기화는 설치 후 임의의 빈 디렉토리에서 `初始化我的知识库`(중국어) / `Initialize my knowledge base`(영어)로 호출하면 됩니다.

---

## 5분 퀵스타트

1. **초기화**: "Initialize my knowledge base"
2. **Capture**: "Grab https://example.com/article"
3. **Ingest**: "Ingest this inbox note"
4. **Query**: "What do my notes say about X?"
5. **Advisor** (v0.3+): "I want to do X, how?"

자세한 내용은 [docs/quick-start.md](./docs/quick-start.md).

---

## 작동 원리

### 6개의 폐쇄 루프

```
Capture → Ingest → Normalize → Connect → Query → Review → (Capture로)
```

### 3개의 Agent (입력 도메인 비중복)

- **quick-kb-manager-agent** —— 라이브러리 구조 관리
- **quick-kb-research-agent** —— 외부 자료 처리
- **quick-kb-memory-agent** —— 장기 기억 호출 (핵심 차별화)

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## 로드맵

| 단계 | 상태 | 주요 내용 |
|------|------|---------|
| v0.1 mvp | ✅ | init/capture/ingest/daily + 중국어 템플릿 |
| v0.2 loops | ✅ | connect/query/review + manager/quick-kb-research-agent + 영어 템플릿 |
| v0.3 assistant | ✅ | quick-kb-memory-agent + advisor/project/goal + 인지 자산 템플릿 |
| v0.4 extensions | ✅ | normalize/archive/stats/import + kb.config + 다국어 README |
| v1.0 release | ✅ | CONTRIBUTING/LICENSE + CI + demo-vault 공개 |
| v1.1 flow-restructure | ✅ | 최상위 `NN_` 접두사 + 절대 경로 하드 제약 (⚠️ BREAKING) |
| v1.2 ai-polish | ✅ | capture / daily 사용자 직접 입력에 대한 AI 윤문 제안 (3선택) |
| v1.3 skillopt-integration | ✅ | 동작 테스트 + 스킬 텍스트 최적화 (SkillOpt × 51 golden cases × 야간 mock workflow) |
| v1.4 nested-domain + hardening | ✅ | 중첩 domain_taxonomy + 템플릿 전량 배포(12→14) + schema 검증 |
| v1.5–v1.6 consistency + 규범화 | ✅ | confidence 0-100 통일 · JSON Schema 검증 · archive copy+stub · wikilink 명명 규약 · canvas 규범 |
| v1.7 automation & integration | ✅ | agent §0 계약 · polish_mode 3단계 · 유사/순환 검출 · 저하 관측성 |
| v1.8 e2e-calibration | ✅ | init 리소스 자족(템플릿+schema+지문) · 전 스킬 쓰기 전 검증 · 지표 통일 |
| v1.8.1–v1.9.3 테스트 캘리브레이션 시리즈 | ✅ | 13라운드 외부 테스트 보고서 캘리브레이션: schema/어휘 정렬 · 저하 임계값표 · 콜드스타트 정렬 · source 포맷 object 통일 · 구조 드리프트 방어 |

---

## 동작 테스트 (v1.3+)

v0.1–v1.2의 CI는 순수 구조 검사(frontmatter / wikilink / placeholder)였습니다 — **"이 SKILL.md 편집이 capture 동작을 퇴화시켰는가?"에 답할 수 없었습니다**. v1.3은 [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)를 동작 테스트 엔진으로 도입합니다:

- 커스텀 benchmark `bench/quickkb/` (dataloader + rollout + adapter + 4 scorers)
- 51 golden cases: 45 단일 케이스 × 9 차원 + 6 J 클래스 엔드투엔드 흐름 전환
- 야간 mock 백엔드 workflow, **PR 병합을 절대 차단하지 않음** (논블로킹 신호)
- 자동 배포 안 함 — SkillOpt의 `best_skill.md`는 모든 커밋 전에 사람이 검토
- **릴리스 회귀**: 매 릴리스 전 capture / flow 벤치 실행, 결과는 [CHANGELOG](./docs/CHANGELOG.md) 각 버전의「评测」섹션에 기록

v1.8부터는**테스트 캘리브레이션 루프**도 운영: 외부 테스트 보고서(13+ 라운드)를 주장별로 저장소 신뢰 원천과 대조 검증하고, 검증된 실제 결함만 수정하며 허위 주장은 근거와 함께 거부 — 캘리브레이션 결론·거부 목록·방법론 제약은 [docs/dev/](./docs/dev/)의 각 버전 캘리브레이션 문서와 CHANGELOG에 기록.

자세한 내용은 [`docs/dev/v1.3-skillopt-integration.md`](./docs/dev/v1.3-skillopt-integration.md).

---

## 문서

- [DESIGN.md](./docs/DESIGN.md) —— 전체 설계 (신뢰 원천)
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) —— 스킬 상세
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) —— Agent 상세 (랭킹 공식 포함)
- [CHANGELOG.md](./docs/CHANGELOG.md) —— 버전 이력 (각 버전 벤치 결과 포함)
- [dev/](./docs/dev/) —— 단계별 개발 문서 및 캘리브레이션 문서

---

## 감사

- [Agent Skills Protocol](https://agentskills.io)
- [Obsidian](https://obsidian.md)
- [Zettelkasten](https://zettelkasten.de)
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

---

## License

[MIT](./LICENSE)
