# quick-knowledge

> Base de conocimiento personal × Framework de habilidades IA — destila información fragmentada en activos personales reutilizables con un conjunto de habilidades.

[中文](./README.md) · [English](./README_EN.md) · [日本語](./README_JA.md) · [한국어](./README_KO.md)

---

## Qué es

`quick-knowledge` es un conjunto de habilidades de base de conocimiento basado en el [protocolo Agent Skills](https://agentskills.io). En cualquier runtime compatible (Claude Code / Codex / Cursor / OpenCode, etc.), completa **Capture → Ingest → Connect → Review** con una sola frase.

Resuelve tres problemas:

| Problema | Enfoque de quick-knowledge |
|----------|----------------------------|
| **Descomposición** —— las notas se acumulan pero nunca se revisan | Bucle de Review obligatorio + decaimiento de confianza |
| **Islas** —— registrado pero no recuperable, no interconectado | Bucle de Connect + enlaces bidireccionales + MOC |
| **Alta fricción** —— categorizar, nombrar, plantillar agota | Sin categorización en Capture; IA maneja Normalize |

---

## Instalación

### Opción 1 · Comando universal (Recomendado, todos los runtimes)

```bash
npx skills add shichu2024/quick-knowledge
```

### Opción 2 · Claude Code marketplace

Dentro de Claude Code:

```
/plugin marketplace add shichu2024/quick-knowledge
/plugin install quick-knowledge
```

### Opción 3 · Instalación manual (por runtime)

| Runtime | Ruta |
|---------|------|
| Claude Code | `~/.claude/skills/quick-knowledge/` |
| Codex CLI | `~/.codex/skills/quick-knowledge/` |
| Cursor | `~/.cursor/skills/quick-knowledge/` |
| OpenCode | `~/.opencode/skills/quick-knowledge/` |

La inicialización del vault se realiza tras la instalación, en cualquier directorio vacío: di `初始化我的知识库` (chino) / `Initialize my knowledge base` (inglés).

---

## Inicio rápido en 5 minutos

1. **Inicializar**: "Initialize my knowledge base"
2. **Capture**: "Grab https://example.com/article"
3. **Ingest**: "Ingest this inbox note"
4. **Query**: "What do my notes say about X?"
5. **Advisor** (v0.3+): "I want to do X, how?"

Más detalles en [docs/quick-start.md](./docs/quick-start.md).

---

## Cómo funciona

### Seis bucles cerrados

```
Capture → Ingest → Normalize → Connect → Query → Review → (volver a Capture)
```

### Tres Agentes (dominios de entrada no superpuestos)

- **manager-agent** —— gestor de estructura de la biblioteca
- **research-agent** —— procesador de materiales externos
- **memory-agent** —— recuperación de memoria a largo plazo (diferenciador central)

### Knowledge Score

```
KS = confidence × log2(1 + reuse) × impact
```

---

## Hoja de ruta

| Fase | Estado | Contenido principal |
|------|--------|---------------------|
| v0.1 mvp | ✅ | init/capture/ingest/daily + plantillas chinas |
| v0.2 loops | ✅ | connect/query/review + manager/research-agent + plantillas inglesas |
| v0.3 assistant | ✅ | memory-agent + advisor/project/goal + plantillas de activos cognitivos |
| v0.4 extensions | ✅ | normalize/archive/stats/import + kb.config + README multilingüe |
| v1.0 release | ✅ | CONTRIBUTING/LICENSE + CI + publicación demo-vault |
| v1.1 flow-restructure | ✅ | Prefijo `NN_` en nivel superior + prohibición de rutas absolutas (⚠️ BREAKING) |
| v1.2 ai-polish | ✅ | Propuesta de pulido por IA para entradas de capture / daily escritas por el usuario (3 opciones) |
| v1.3 skillopt-integration | ✅ | Pruebas de comportamiento + optimización de texto de habilidades (SkillOpt × 51 casos golden × workflow nocturno mock) |

---

## Pruebas de comportamiento (v1.3+)

El CI de v0.1–v1.2 era puramente estructural (frontmatter / wikilinks / placeholders) — **no podía responder "¿esta edición de SKILL.md regresionó el comportamiento de capture?"**. v1.3 introduce [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) como motor de pruebas de comportamiento:

- Benchmark personalizado `bench/quickkb/` (dataloader + rollout + adapter + 4 scorers)
- 51 casos golden: 45 casos puntuales × 9 dimensiones + 6 transiciones de flujo J end-to-end
- Workflow nocturno con backend mock, **nunca bloquea el merge de PR** (señal no bloqueante)
- Nunca auto-despliega — el `best_skill.md` de SkillOpt se revisa manualmente antes de cualquier commit

Ver [`docs/dev/v1.3-skillopt-integration.md`](./docs/dev/v1.3-skillopt-integration.md).

---

## Documentación

- [DESIGN.md](./docs/DESIGN.md) —— diseño completo (fuente de verdad)
- [SKILLS_SPEC.md](./docs/SKILLS_SPEC.md) —— especificación de habilidades
- [AGENTS_SPEC.md](./docs/AGENTS_SPEC.md) —— especificación de agentes (con fórmula de ranking)

---

## Agradecimientos

- [Agent Skills Protocol](https://agentskills.io)
- [Obsidian](https://obsidian.md)
- [Zettelkasten](https://zettelkasten.de)
- [alchaincyf/nuwa-skill](https://github.com/alchaincyf/nuwa-skill)

---

## License

Se definirá en el lanzamiento v1.0 (propuesta: MIT o Apache 2.0).
