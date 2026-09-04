---
title: 知识库仪表盘
created: 2026-07-17T00:00:00
modified: 2026-07-20T13:50:00
tags: [MOC, dashboard]
type: moc
status: evergreen
---

# 🧠 知识库仪表盘

> **自生长知识库** — 捕获 → 处理 → 链接 → 回顾，每周自动迭代

---

## 📊 本周概览

<div class="dashboard-grid">

<div class="stat-card">

<div class="stat-emoji">📝</div>
<div class="stat-label">总笔记数</div>
<div class="stat-value">64</div>

</div>

<div class="stat-card">

<div class="stat-emoji">🌱</div>
<div class="stat-label">生长中 (seedling)</div>
<div class="stat-value">23</div>

</div>

<div class="stat-card">

<div class="stat-emoji">🌳</div>
<div class="stat-label">已成熟 (evergreen)</div>
<div class="stat-value">7</div>

</div>

<div class="stat-card">

<div class="stat-emoji">⚡</div>
<div class="stat-label">永久笔记</div>
<div class="stat-value">20</div>

</div>

</div>

> [!note] 🤖 自动化
> - **每周五 18:00** 自动运行：知识汇出 + 周回顾 + 统计报告
> - 报告位置：`_系统/04-工作流/`

## 🗂️ 五大支柱

<div class="pillar-container">

<div class="pillar-card python">

**🐍 Python 编程**
<div class="pillar-count">6 篇</div>
<div class="pillar-desc">
数据类型 · 函数与作用域 · 面向对象 · 装饰器 · 异步编程
</div>
[[语言学习/语言学习-MOC|进入 →]]

</div>

<div class="pillar-card ai">

**🤖 AI 学习**
<div class="pillar-count">5 篇</div>
<div class="pillar-desc">
大语言模型 · 提示工程 · RAG · AI Agent
</div>
[[AI学习/AI学习-MOC|进入 →]]

</div>

<div class="pillar-card devops">

**🖥️ 运维学习**
<div class="pillar-count">11 篇</div>
<div class="pillar-desc">
Linux · 网络 · Docker · K8s · CI/CD · 监控 · 容器化部署
</div>
[[运维学习/运维学习-MOC|进入 →]]

</div>

<div class="pillar-card projects">

**🚀 简历项目实战**
<div class="pillar-count">10 篇</div>
<div class="pillar-desc">
CI/CD · K8s · 监控 · Ansible · HTTPS自动化 · ELK日志平台 · RAG · 私有化LLM · Agent · 微调
</div>
[[简历项目实战/简历项目实战-MOC|进入 →]]

</div>

<div class="pillar-card linux">

**🐧 Linux 学习**
<div class="pillar-count">5 篇</div>
<div class="pillar-desc">
文件系统 · 权限 · 进程 · 网络排错 · 练习题 · 迭代任务
</div>
[[Linux学习/Linux学习-MOC|进入 →]]

</div>

</div>

## ⚡ 快速操作

| 操作 | 方式 |
|------|------|
| 📥 **快速捕获** | 把闪念丢进 [[00-收件箱/00-收件箱说明\|收件箱]] |
| ✨ **新建规范笔记** | 运行 `python _系统/03-脚本/新建笔记.py` |
| 🔍 **搜索知识库** | 对我说「搜一下 XX」或用 `Ctrl+Shift+F` |
| 📈 **查看统计** | 运行 `python _系统/03-脚本/vault统计.py` |
| 📋 **本周总结** | 查看 [[_系统/04-工作流/知识汇出-2026-07-17]] |
| 🐧 **Linux 练习** | 查看 [[Linux学习/03-练习题/20260905-Linux练习题-基础篇]] |
| 🚀 **迭代并部署** | 运行 `python _系统/03-脚本/自动迭代并推送.py` |

## 🔄 工作流（5 分钟上手）

<ol class="workflow-steps">
<li><strong>捕获</strong> — 任何想法、链接、片段先丢进收件箱，不用整理</li>
<li><strong>处理</strong> — 每周整理，把有价值的转成永久笔记，链接到 MOC</li>
<li><strong>生长</strong> — 新笔记用脚本生成，自动带 frontmatter 和标准格式</li>
<li><strong>回顾</strong> — 每周五自动跑汇出，发现孤儿笔记并升级 seedling；Linux 任务沿用同一流程</li>
</ol>

> [!tip] 💡 工具分工
> - **Obsidian** — 可视化图谱、双向链接、Daily Notes、CSS 样式预览
> - **VSCode** — 批量编辑、运行 Python 脚本、Git 版本管理

## 🏷️ 常用标签速查

`#Python` `#Python/基础` `#Python/异步` `#Python/OO`
`#AI` `#AI/LLM` `#AI/Prompt` `#AI/RAG` `#AI/Agent`
`#运维` `#运维/Linux` `#运维/Docker` `#运维/K8s` `#运维/监控`
`#Linux` `#Linux/基础` `#Linux/权限` `#Linux/进程` `#Linux/网络` `#Linux/练习` `#Linux/迭代`
`#简历` `#项目/运维` `#项目/AI` `#实操` `#面试`
`#seedling` `#evergreen` `#permanent` `#project`

---

*最后更新: 2026-09-05 · 下次自动化: 周五 18:00*
