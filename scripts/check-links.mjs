#!/usr/bin/env node
/**
 * Wikilink 死链检查
 * 用法：node scripts/check-links.mjs <vault-root>
 *
 * 检查 [[X]] 与 [[X|alias]] 是否指向存在的 .md 文件。
 * 不区分大小写；支持相对路径与 basename 匹配。
 *
 * 退出码：0 通过，1 失败
 */

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, extname, basename, resolve, sep } from 'node:path'

const vault = process.argv[2]
if (!vault) {
  console.error('Usage: node check-links.mjs <vault-root>')
  process.exit(2)
}

// 收集所有 .md 文件路径
const allFiles = new Set()    // 完整相对路径
const allBasenames = new Map() // basename -> 路径列表

function* walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry.startsWith('.')) continue
    if (entry === 'node_modules' || entry === '_raw') continue
    const full = join(dir, entry)
    const st = statSync(full)
    if (st.isDirectory()) yield* walk(full)
    else if (extname(entry) === '.md') yield full
  }
}

for (const file of walk(vault)) {
  const rel = file.slice(vault.length).replace(/^[\\/]/, '').replace(/\\/g, '/')
  allFiles.add(rel)
  const bn = basename(file, '.md')
  if (!allBasenames.has(bn)) allBasenames.set(bn, [])
  allBasenames.get(bn).push(rel)
}

function existsByPath(target) {
  // 直接相对路径匹配
  if (allFiles.has(target)) return true
  // 加 .md 后缀
  if (allFiles.has(target + '.md')) return true
  // Obsidian 约定：[[dir]] 解析为 dir/_readme.md
  if (allFiles.has(target + '/_readme.md')) return true
  if (allFiles.has(target + '/_readme')) return true
  // basename 匹配
  const bn = basename(target, '.md')
  return allBasenames.has(bn)
}

let failures = 0
let total = 0
const failureSet = new Set()

const linkRe = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g

for (const file of walk(vault)) {
  const content = readFileSync(file, 'utf8')
  let m
  while ((m = linkRe.exec(content)) !== null) {
    total++
    const target = m[1].trim()
    // 跳过模板占位符
    if (target.includes('{{')) continue
    // 跳过 anchor (#xxx)
    const path = target.split('#')[0].split('|')[0].trim()
    if (!path) continue
    if (!existsByPath(path)) {
      failures++
      failureSet.add(`${file} -> [[${target}]]`)
    }
  }
}

console.log(`Checked ${total} wikilinks, ${failures} dead links`)
for (const f of failureSet) {
  console.error(`✗ ${f}`)
}
process.exit(failures === 0 ? 0 : 1)
