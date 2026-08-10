#!/usr/bin/env node
/**
 * clone-vault.mjs — Copy examples/demo-vault/ to a tmpdir for SkillOpt rollouts.
 *
 * Used by the exec backend (real Claude Code) so the gate ground-truth
 * vault is never mutated. For MVP chat backend this script is not invoked
 * (chat backend produces text-only, no filesystem side effects).
 *
 * Usage:
 *   node bench/harness/clone-vault.mjs /tmp/quickkb-vault-<run-id>
 */
import { cpSync, mkdirSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'

const target = process.argv[2]
if (!target) {
  console.error('Usage: clone-vault.mjs <target-dir>')
  process.exit(1)
}

const repoRoot = resolve(import.meta.dirname, '..', '..')
const source = resolve(repoRoot, 'examples', 'demo-vault')

if (!existsSync(source)) {
  console.error(`Source demo-vault not found: ${source}`)
  process.exit(1)
}

const targetAbs = resolve(target)
mkdirSync(targetAbs, { recursive: true })
cpSync(source, targetAbs, { recursive: true, force: true })

console.log(`[clone-vault] ${source} → ${targetAbs}`)
