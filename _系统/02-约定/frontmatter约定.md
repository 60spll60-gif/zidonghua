# Frontmatter 约定

所有长期笔记都应该包含 YAML frontmatter：

```yaml
---
title: 笔记标题
created: 2026-07-17T13:00:00
modified: 2026-07-17T13:00:00
tags: [tag1, tag2]
status: seedling
type: permanent
pillar: AI学习
---
```

## 字段说明

| 字段 | 说明 | 可选值 |
|------|------|--------|
| title | 标题 | 任意 |
| created | 创建时间 | ISO 8601 |
| modified | 修改时间 | ISO 8601 |
| tags | 标签数组 | 见 [[_系统/02-约定/命名与标签约定|命名与标签约定]] |
| status | 笔记成熟度 | `draft`, `seedling`, `evergreen`, `archived` |
| type | 笔记类型 | `fleeting`, `literature`, `permanent`, `project`, `moc` |
| pillar | 所属支柱 | `AI学习`, `语言学习`, `运维学习`, `Linux学习`, `meta` |

## 状态说明

- **draft**：刚捕获，未整理
- **seedling**：已整理，需要继续生长
- **evergreen**：成熟、可随时复用的原子笔记
- **archived**：过时或不再活跃的笔记

## 为什么要有 frontmatter？

1. 让脚本可以统计、筛选、生成报告。
2. 与 Obsidian Dataview / 搜索 / 标签系统天然兼容。
3. 在 VSCode 中也能直接阅读和维护。
