#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建dashboard.py
扫描整个 vault，把所有笔记内容内嵌到一个自包含的 dashboard.html 中。
- 点击笔记 → 在右侧阅读面板直接查看渲染后的 Markdown
- 数据保存在 dashboard.html 内部，打开就是最新内容
- Obsidian 里的 .md 文件保持不变，双向同步

使用方法：
    python _系统/03-脚本/重建dashboard.py
"""
import json
import re
import sys
import io
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# vault 根目录 = 脚本所在目录的上两级（_系统/03-脚本/xxx.py → 上两级）
VAULT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = VAULT_ROOT / "dashboard.html"

# 要扫描的笔记目录（按 pillar 分类）
PILLARS = {
    "python": {"path": "语言学习", "emoji": "🐍", "name": "Python 编程", "color": "#3776ab"},
    "ai": {"path": "AI学习", "emoji": "🤖", "name": "AI 学习", "color": "#7c3aed"},
    "devops": {"path": "运维学习", "emoji": "🖥️", "name": "运维学习", "color": "#06b6d4"},
    "projects": {"path": "简历项目实战", "emoji": "🚀", "name": "简历项目实战", "color": "#f59e0b"},
    "linux": {"path": "Linux学习", "emoji": "🐧", "name": "Linux 学习", "color": "#e05c5c"},
}

# 跳过的目录（系统目录、收件箱、归档等）
SKIP_DIRS = {".obsidian", ".vscode", ".workbuddy", "_系统", "99-归档", "00-收件箱"}
SKIP_FILES = {"README.md", "dashboard.html"}


def parse_frontmatter(text: str) -> dict:
    """解析 YAML frontmatter"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def get_first_paragraph(body: str) -> str:
    """提取第一个非空段落作为摘要"""
    for para in body.split("\n\n"):
        p = para.strip()
        if p and not p.startswith("#") and not p.startswith("---"):
            # 去掉 Markdown 语法，只留纯文本
            clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', p)  # 链接
            clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)    # 粗体
            clean = re.sub(r'\*([^*]+)\*', r'\1', clean)        # 斜体
            clean = re.sub(r'`([^`]+)`', r'\1', clean)          # 行内代码
            clean = re.sub(r'^#+\s*', '', clean)                # 标题
            return clean[:150]
    return ""


def scan_vault() -> list:
    """扫描所有 pillar 目录下的 Markdown 笔记"""
    notes = []
    for pillar_id, cfg in PILLARS.items():
        pillar_dir = VAULT_ROOT / cfg["path"]
        if not pillar_dir.exists():
            continue
        for md in sorted(pillar_dir.rglob("*.md")):
            relative_parts = md.relative_to(pillar_dir).parts
            if any(part in SKIP_DIRS for part in relative_parts):
                continue
            if md.name in SKIP_FILES:
                continue
            # 跳过 MOC 文件本身
            if md.stem.endswith("-MOC"):
                continue
            rel = md.relative_to(VAULT_ROOT).as_posix()
            raw = md.read_text(encoding="utf-8")
            fm = parse_frontmatter(raw)
            # 提取 frontmatter 之后的正文
            body = raw
            if raw.startswith("---"):
                end = raw.find("\n---", 3)
                if end != -1:
                    body = raw[end + 4:].strip()
            notes.append({
                "title": fm.get("title", md.stem),
                "path": rel,
                "pillar": pillar_id,
                "status": fm.get("status", "seedling"),
                "summary": get_first_paragraph(body),
                "content": body,  # 完整内容，用于阅读面板
                "created": fm.get("created", ""),
            })
    return notes


def build_html(notes: list, pillars_meta: dict) -> str:
    """生成自包含 dashboard.html"""

    # 转义 JSON 中的特殊字符（防止 </script> 破坏）
    notes_json = json.dumps(notes, ensure_ascii=False).replace("</", "<\\/")
    pillars_json = json.dumps(pillars_meta, ensure_ascii=False).replace("</", "<\\/")

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>知识库仪表盘</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.0/marked.min.js"></script>
<style>
  :root {{
    --bg: #f8f9fc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --border: #e2e8f0;
    --python: #3776ab; --ai: #7c3aed; --devops: #06b6d4; --projects: #f59e0b;
    --seedling: #10b981; --evergreen: #6366f1; --permanent: #f59e0b; --project: #ef4444;
    --radius: 14px; --radius-sm: 8px;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); line-height:1.65; padding:24px; max-width:1200px; margin:0 auto; }}

  /* Header */
  .header {{ text-align:center; margin-bottom:32px; padding:32px 24px; background:linear-gradient(135deg,#1e293b,#334155); border-radius:var(--radius); color:white; }}
  .header h1 {{ font-size:28px; font-weight:700; }}
  .header p {{ opacity:.85; margin-top:8px; font-size:15px; }}
  .header .tagline {{ display:inline-block; background:rgba(255,255,255,.15); padding:4px 16px; border-radius:20px; font-size:13px; margin-top:12px; }}

  /* Stats */
  .stats-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin-bottom:28px; }}
  .stat-card {{ background:var(--card); border-radius:var(--radius-sm); padding:18px; border:1px solid var(--border); }}
  .stat-icon {{ font-size:24px; display:block; margin-bottom:8px; }}
  .stat-label {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; font-weight:600; }}
  .stat-value {{ font-size:28px; font-weight:800; margin-top:2px; }}
  .stat-card.python .stat-value {{ color:var(--python); }}
  .stat-card.ai .stat-value {{ color:var(--ai); }}
  .stat-card.devops .stat-value {{ color:var(--devops); }}
  .stat-card.projects .stat-value {{ color:var(--projects); }}

  /* Pillars */
  .section-title {{ font-size:18px; font-weight:700; margin:26px 0 14px; display:flex; align-items:center; gap:8px; }}
  .pillar-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; margin-bottom:28px; }}
  .pillar-card {{ border-radius:var(--radius); padding:24px; color:white; cursor:pointer; transition:transform .2s, box-shadow .2s; position:relative; overflow:hidden; }}
  .pillar-card:hover {{ transform:scale(1.02) translateY(-2px); box-shadow:0 12px 32px rgba(0,0,0,.15); }}
  .pillar-card h3 {{ font-size:20px; font-weight:700; margin-bottom:4px; }}
  .pillar-card .desc {{ font-size:13px; opacity:.9; max-width:280px; }}
  .pillar-card .count-badge {{ position:absolute; top:14px; right:14px; background:rgba(255,255,255,.2); padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600; }}
  .pillar-card.python {{ background:linear-gradient(135deg,#1a365d,#3776ab); }}
  .pillar-card.ai {{ background:linear-gradient(135deg,#4c1d95,#7c3aed); }}
  .pillar-card.devops {{ background:linear-gradient(135deg,#134e4a,#06b6d4); }}
  .pillar-card.projects {{ background:linear-gradient(135deg,#78350f,#f59e0b); }}

  /* Layout: list + reader side by side */
  .browser-wrap {{ display:grid; grid-template-columns: 1fr; gap:20px; margin-bottom:28px; }}
  @media (min-width:900px) {{ .browser-wrap {{ grid-template-columns: 380px 1fr; }} }}

  .notes-list-panel {{ background:var(--card); border-radius:var(--radius); border:1px solid var(--border); overflow:hidden; display:flex; flex-direction:column; max-height:80vh; }}
  .notes-toolbar {{ padding:14px 16px; border-bottom:1px solid var(--border); display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
  .notes-toolbar input {{ flex:1; min-width:140px; padding:9px 14px; border:1px solid var(--border); border-radius:var(--radius-sm); font-size:14px; outline:none; }}
  .notes-toolbar input:focus {{ border-color:#6366f1; }}
  .filter-btn {{ padding:7px 12px; border:1px solid var(--border); border-radius:16px; background:transparent; font-size:12px; cursor:pointer; color:var(--muted); transition:all .15s; }}
  .filter-btn:hover {{ border-color:#6366f1; color:#6366f1; }}
  .filter-btn.active {{ background:#6366f1; color:white; border-color:#6366f1; }}
  #notesList {{ overflow-y:auto; flex:1; }}
  .note-item {{ display:flex; align-items:center; gap:12px; padding:12px 16px; border-bottom:1px solid var(--border); cursor:pointer; transition:background .1s; }}
  .note-item:hover {{ background:#f8fafc; }}
  .note-item.active {{ background:#eef2ff; border-left:3px solid #6366f1; padding-left:13px; }}
  .note-pillar-dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
  .note-info {{ flex:1; min-width:0; }}
  .note-title {{ font-size:14px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .note-path {{ font-size:11.5px; color:var(--muted); margin-top:1px; }}
  .note-status-tag {{ padding:2px 8px; border-radius:10px; font-size:10.5px; font-weight:600; flex-shrink:0; }}

  /* Reader panel */
  .reader-panel {{ background:var(--card); border-radius:var(--radius); border:1px solid var(--border); padding:28px 32px; max-height:80vh; overflow-y:auto; }}
  .reader-empty {{ text-align:center; padding:60px 20px; color:var(--muted); }}
  .reader-empty .icon {{ font-size:48px; margin-bottom:12px; }}
  .reader-header {{ border-bottom:1px solid var(--border); padding-bottom:16px; margin-bottom:20px; }}
  .reader-title {{ font-size:22px; font-weight:700; margin-bottom:8px; }}
  .reader-meta {{ display:flex; gap:12px; flex-wrap:wrap; align-items:center; }}
  .reader-meta .tag {{ padding:3px 10px; border-radius:12px; font-size:11.5px; font-weight:600; }}
  .reader-meta .path {{ font-size:12px; color:var(--muted); }}
  .reader-actions {{ margin-top:12px; display:flex; gap:10px; }}
  .btn-obsidian {{ padding:7px 14px; border-radius:8px; border:1px solid var(--border); background:transparent; font-size:12.5px; cursor:pointer; color:var(--muted); }}
  .btn-obsidian:hover {{ border-color:#6366f1; color:#6366f1; }}
  .reader-body {{ font-size:14.5px; line-height:1.8; }}
  .reader-body h1 {{ font-size:20px; margin:24px 0 10px; }}
  .reader-body h2 {{ font-size:17px; margin:22px 0 8px; }}
  .reader-body h3 {{ font-size:15px; margin:18px 0 6px; }}
  .reader-body p {{ margin:10px 0; }}
  .reader-body code {{ background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:13px; font-family:"Consolas","Monaco",monospace; }}
  .reader-body pre {{ background:#1e293b; color:#e2e8f0; padding:16px; border-radius:8px; overflow-x:auto; margin:14px 0; }}
  .reader-body pre code {{ background:transparent; color:inherit; padding:0; }}
  .reader-body ul,.reader-body ol {{ padding-left:24px; margin:10px 0; }}
  .reader-body li {{ margin:4px 0; }}
  .reader-body blockquote {{ border-left:3px solid #6366f1; padding:10px 16px; background:#f8fafc; margin:14px 0; border-radius:0 8px 8px 0; }}
  .reader-body table {{ width:100%; border-collapse:collapse; margin:14px 0; font-size:13.5px; }}
  .reader-body th {{ background:#f1f5f9; padding:8px 12px; text-align:left; font-weight:600; }}
  .reader-body td {{ padding:8px 12px; border-top:1px solid var(--border); }}

  /* Charts */
  .charts-row {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:28px; }}
  .chart-card {{ background:var(--card); border-radius:var(--radius); border:1px solid var(--border); padding:22px; }}
  .chart-card h3 {{ font-size:15px; font-weight:700; margin-bottom:14px; }}
  .chart-card canvas {{ max-height:260px; }}

  /* Footer */
  .footer {{ text-align:center; padding:20px; color:var(--muted); font-size:13px; }}

  .empty-state {{ text-align:center; padding:48px 24px; color:var(--muted); }}
  .empty-state .icon {{ font-size:42px; margin-bottom:12px; }}

  @media (max-width:900px) {{
    body {{ padding:12px; }}
    .charts-row {{ grid-template-columns:1fr; }}
    .notes-list-panel {{ max-height:50vh; }}
    .reader-panel {{ max-height:none; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>Knowledge Base Dashboard</h1>
  <p>自生长知识库 — 捕获 / 处理 / 链接 / 回顾</p>
  <span class="tagline">点击笔记即可阅读 · Obsidian 同步更新</span>
</div>

<div class="stats-grid" id="statsGrid"></div>

<h2 class="section-title">🗂️ 三大支柱</h2>
<div class="pillar-grid" id="pillarGrid"></div>

<h2 class="section-title">📝 笔记浏览器 <span style="font-size:12px;font-weight:400;color:var(--muted)">（点击左侧笔记在右侧阅读）</span></h2>
<div class="browser-wrap">
  <div class="notes-list-panel">
    <div class="notes-toolbar">
      <input type="text" id="searchInput" placeholder="搜索笔记...">
      <button class="filter-btn active" data-filter="all">全部</button>
      <button class="filter-btn" data-filter="python">🐍</button>
      <button class="filter-btn" data-filter="ai">🤖</button>
      <button class="filter-btn" data-filter="devops">🖥️</button>
      <button class="filter-btn" data-filter="projects">🚀</button>
    </div>
    <div id="notesList"></div>
  </div>
  <div class="reader-panel" id="readerPanel">
    <div class="reader-empty">
      <div class="icon">📖</div>
      <p>点击左侧任意笔记<br>在这里直接阅读内容</p>
    </div>
  </div>
</div>

<div class="charts-row">
  <div class="chart-card"><h3>各支柱笔记分布</h3><canvas id="pillarChart" role="img" aria-label="Pillar distribution"></canvas></div>
  <div class="chart-card"><h3>笔记状态分布</h3><canvas id="statusChart" role="img" aria-label="Status distribution"></canvas></div>
</div>

<div class="footer">最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M")} · 共 <strong id="totalNotesFooter">0</strong> 条笔记 · 与 Obsidian 双向同步</div>

<script>
const notes = {notes_json};
const pillars = {pillars_json};

const statusColors = {{
  seedling:   {{ bg:"rgba(16,185,129,.12)", color:"#059669", label:"🌱 seedling" }},
  evergreen:  {{ bg:"rgba(99,102,241,.12)", color:"#4338ca", label:"🌳 evergreen" }},
  permanent:  {{ bg:"rgba(245,158,11,.12)", color:"#d97706", label:"⚡ permanent" }},
  project:    {{ bg:"rgba(239,68,68,.12)",  color:"#dc2626", label:"🎯 project" }},
}};

let currentFilter = "all", searchQuery = "", activeNote = null;

// ======== 渲染 ========
function renderStats() {{
  const total = notes.length;
  const bp = {{}}; notes.forEach(n => bp[n.pillar]=(bp[n.pillar]||0)+1);
  document.getElementById("statsGrid").innerHTML = `
    <div class="stat-card"><span class="stat-icon">📝</span><div class="stat-label">总笔记</div><div class="stat-value">${{total}}</div></div>
    <div class="stat-card python"><span class="stat-icon">🐍</span><div class="stat-label">Python</div><div class="stat-value">${{bp.python||0}}</div></div>
    <div class="stat-card ai"><span class="stat-icon">🤖</span><div class="stat-label">AI</div><div class="stat-value">${{bp.ai||0}}</div></div>
    <div class="stat-card devops"><span class="stat-icon">🖥️</span><div class="stat-label">运维</div><div class="stat-value">${{bp.devops||0}}</div></div>
    <div class="stat-card projects"><span class="stat-icon">🚀</span><div class="stat-label">简历项目</div><div class="stat-value">${{bp.projects||0}}</div></div>`;
  document.getElementById("totalNotesFooter").textContent = total;
}}

function renderPillars() {{
  document.getElementById("pillarGrid").innerHTML = Object.entries(pillars).map(([id,p]) => {{
    const count = notes.filter(n=>n.pillar===id).length;
    return `<div class="pillar-card ${{id}}" onclick="filterByPillar('${{id}}')">
      <h3>${{p.emoji}} ${{p.name}}</h3><div class="desc">${{p.desc}}</div>
      <div class="count-badge">${{count}} 篇</div></div>`;
  }}).join("");
}}

function renderNotes() {{
  let filtered = notes;
  if (currentFilter !== "all") filtered = filtered.filter(n=>n.pillar===currentFilter);
  if (searchQuery) {{ const q=searchQuery.toLowerCase();
    filtered = filtered.filter(n=>n.title.toLowerCase().includes(q)||n.summary.toLowerCase().includes(q)); }}
  if (!filtered.length) {{ document.getElementById("notesList").innerHTML=`<div class="empty-state"><div class="icon">🔍</div><p>没有匹配的笔记</p></div>`; return; }}
  document.getElementById("notesList").innerHTML = filtered.map((n,i) => {{
    const sc=statusColors[n.status]||statusColors.seedling;
    const isActive = activeNote===n.path;
    return `<div class="note-item ${{isActive?'active':''}}" onclick="openNote('${{encodeURIComponent(n.path)}}')">
      <div class="note-pillar-dot" style="background:${{pillars[n.pillar]?.color||'#999'}}"></div>
      <div class="note-info"><div class="note-title">${{n.title}}</div><div class="note-path">${{n.path}}</div></div>
      <div class="note-status-tag" style="background:${{sc.bg}};color:${{sc.color}}">${{sc.label}}</div></div>`;
  }}).join("");
}}

// ======== 打开笔记 ========
function openNote(encodedPath) {{
  const path = decodeURIComponent(encodedPath);
  const note = notes.find(n=>n.path===path);
  if (!note) return;
  activeNote = path;
  renderNotes();
  const sc = statusColors[note.status]||statusColors.seedling;
  const html = marked.parse(note.content||"*暂无内容*");
  document.getElementById("readerPanel").innerHTML = `
    <div class="reader-header">
      <div class="reader-title">${{note.title}}</div>
      <div class="reader-meta">
        <span class="tag" style="background:${{sc.bg}};color:${{sc.color}}">${{sc.label}}</span>
        <span class="path">${{note.path}}</span>
      </div>
      <div class="reader-actions">
        <button class="btn-obsidian" onclick="event.stopPropagation();openInObsidian('${{encodeURIComponent(path)}}')">在 Obsidian 中编辑 ↗</button>
      </div>
    </div>
    <div class="reader-body">${{html}}</div>`;
  // 滚动到顶部
  document.getElementById("readerPanel").scrollTop = 0;
}}

function openInObsidian(encodedPath) {{
  const path = decodeURIComponent(encodedPath).replace(/\\.md$/,"");
  window.location.href = `obsidian://open?vault=${{encodeURIComponent("知识库")}}&file=${{encodeURIComponent(path)}}`;
}}

// ======== 筛选 ========
document.querySelectorAll(".filter-btn").forEach(btn=>{{
  btn.addEventListener("click",()=>{{
    document.querySelectorAll(".filter-btn").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active"); currentFilter=btn.dataset.filter; renderNotes();
  }});
}});
document.getElementById("searchInput").addEventListener("input",e=>{{ searchQuery=e.target.value; renderNotes(); }});
function filterByPillar(id){{ currentFilter=id;
  document.querySelectorAll(".filter-btn").forEach(b=>b.classList.toggle("active",b.dataset.filter===id));
  renderNotes(); document.getElementById("notesList").scrollIntoView({{behavior:"smooth",block:"start"}}); }}

// ======== 图表 ========
function renderCharts() {{
  const bp={{}}; notes.forEach(n=>bp[n.pillar]=(bp[n.pillar]||0)+1);
  new Chart(document.getElementById("pillarChart"),{{type:"bar",data:{{labels:["Python","AI学习","运维学习","简历项目"],datasets:[{{data:[bp.python||0,bp.ai||0,bp.devops||0,bp.projects||0],backgroundColor:["#3776ab","#7c3aed","#06b6d4","#f59e0b"],borderRadius:8,barThickness:32}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,ticks:{{stepSize:1}},grid:{{color:"#f1f5f9"}}}},x:{{grid:{{display:false}}}}}}}}}});
  const bs={{}}; notes.forEach(n=>bs[n.status]=(bs[n.status]||0)+1);
  new Chart(document.getElementById("statusChart"),{{type:"doughnut",data:{{labels:["Seedling 🌱","Evergreen 🌳","Permanent ⚡","Project 🎯"],datasets:[{{data:[bs.seedling||0,bs.evergreen||0,bs.permanent||0,bs.project||0],backgroundColor:["#10b981","#6366f1","#f59e0b","#ef4444"],borderWidth:0,hoverOffset:6}}]}},options:{{responsive:true,cutout:"62%",plugins:{{legend:{{position:"bottom",labels:{{padding:14,usePointStyle:true,pointStyleWidth:10}}}}}}}}}});
}}

// ======== 初始化 ========
renderStats(); renderPillars(); renderNotes(); renderCharts();
</script>
</body>
    </html>'''


def refresh_existing_dashboard(output_file: Path, notes: list, pillars_meta: dict) -> None:
    """只刷新现有仪表盘的数据，避免自动任务覆盖手工维护的界面。"""
    html = output_file.read_text(encoding="utf-8")
    notes_json = json.dumps(notes, ensure_ascii=False).replace("</", "<\\/")
    pillars_json = json.dumps(pillars_meta, ensure_ascii=False).replace("</", "<\\/")
    replacement = f"const notes = {notes_json};\nconst pillars = {pillars_json};"
    updated, count = re.subn(
        r"const notes = .*?;\r?\nconst pillars = .*?;",
        lambda _match: replacement,
        html,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError(f"{output_file.name} 中未找到可刷新的 notes/pillars 数据块")
    updated = re.sub(
        r"最后更新: \d{4}-\d{2}-\d{2}(?= · 共)",
        f"最后更新: {datetime.now().strftime('%Y-%m-%d')}",
        updated,
        count=1,
    )
    output_file.write_text(updated, encoding="utf-8")


def main():
    print(f"扫描 vault: {VAULT_ROOT}")
    notes = scan_vault()
    print(f"找到 {len(notes)} 条笔记")

    pillars_meta = {pid: {"emoji": c["emoji"], "name": c["name"], "desc": "", "color": c["color"]}
                    for pid, c in PILLARS.items()}
    # 从实际笔记动态生成描述
    for pid in pillars_meta:
        pillar_notes = [n for n in notes if n["pillar"] == pid]
        pillars_meta[pid]["desc"] = " / ".join(n["title"] for n in pillar_notes[:5])

    # 主仪表盘和部署站点共用同一份扫描数据；只替换数据块，保留当前 UI、登录和打卡功能。
    output_files = [OUTPUT_FILE, VAULT_ROOT / "部署站点" / "index.html"]
    for output_file in output_files:
        if output_file.exists():
            refresh_existing_dashboard(output_file, notes, pillars_meta)
            size_kb = output_file.stat().st_size // 1024
            print(f"已刷新: {output_file}  ({size_kb} KB, {len(notes)} 条笔记内嵌)")
        elif output_file == OUTPUT_FILE:
            html = build_html(notes, pillars_meta)
            output_file.write_text(html, encoding="utf-8")
            print(f"已生成: {output_file}  ({len(notes)} 条笔记内嵌)")


if __name__ == "__main__":
    main()
