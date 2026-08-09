#!/usr/bin/env node
/**
 * Frontmatter 基础校验
 * 用法：node scripts/check-frontmatter.mjs <dir1> [dir2] ...
 *
 * 校验规则：
 * - 所有 .md 文件含 YAML frontmatter（--- ... ---）
 * - frontmatter 含 title + type
 * - type 在 14 种枚举内（concept/resource/idea/daily/review/decision/goal/project/moc
 *   + principle/belief/pattern/experience）
 *
 * 退出码：0 通过，1 失败
 */

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, extname } from 'node:path'

const VALID_TYPES = new Set([
  'concept', 'resource', 'idea', 'daily', 'review', 'decision', 'goal', 'project', 'moc',
  'principle', 'belief', 'pattern', 'experience'
])

const REQUIRED_FIELDS = ['title', 'type']

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry.startsWith('.')) continue
    if (entry === 'node_modules' || entry === '_raw') continue
    // 跳过模板（占位符 frontmatter）与 inbox 原始素材（无 type）与 _readme.md（meta 文档）
    if (entry === 'templates' || entry === 'inbox') continue
    if (entry === '_readme.md') continue
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) {
      yield* walk(full)
    } else if (extname(entry) === '.md') {
      yield full
    }
  }
}

function parseFrontmatter(content) {
  const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!m) return null
  const lines = m[1].split(/\r?\n/)
  const fm = {}
  let currentKey = null
  for (const line of lines) {
    if (!line.trim() || line.trim().startsWith('#')) continue
    const kv = line.match(/^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$/)
    if (kv) {
      currentKey = kv[1]
      fm[currentKey] = kv[2].trim().replace(/^['"]|['"]$/g, '')
    }
  }
  return fm
}

const dirs = process.argv.slice(2)
if (dirs.length === 0) {
  console.error('Usage: node check-frontmatter.mjs <dir1> [dir2] ...')
  process.exit(2)
}

let failures = 0
let total = 0

for (const dir of dirs) {
  for (const file of walk(dir)) {
    total++
    const content = readFileSync(file, 'utf8')
    const fm = parseFrontmatter(content)
    if (!fm) {
      console.error(`✗ ${file}: no frontmatter`)
      failures++
      continue
    }
    for (const f of REQUIRED_FIELDS) {
      if (!fm[f]) {
        console.error(`✗ ${file}: missing required field "${f}"`)
        failures++
      }
    }
    if (fm.type && !VALID_TYPES.has(fm.type)) {
      console.error(`✗ ${file}: invalid type "${fm.type}"`)
      failures++
    }
  }
}

console.log(`\nChecked ${total} files, ${failures} failures`)
process.exit(failures === 0 ? 0 : 1)
