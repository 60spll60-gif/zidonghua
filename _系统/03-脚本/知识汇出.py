#!/usr/bin/env python3
"""
知识汇出.py —— 生成结构化每周迭代总结

用法：
    python _系统/03-脚本/知识汇出.py

输出：_系统/04-工作流/知识汇出-YYYY-MM-DD.md
    一份按 pillar 分组的周报，含每个新/改笔记的关键摘要。
"""
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = VAULT_ROOT / "_系统/04-工作流"


def parse_frontmatter(path: Path) -> dict:
    """简单解析 YAML frontmatter。"""
    text = path.read_text(encoding="utf-8")
    data = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def extract_digest(path: Path) -> str:
    """从笔记内容中提取第一段有意义的摘要。"""
    text = path.read_text(encoding="utf-8")
    # 跳过 frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        body = text[end + 3 :] if end != -1 else text
    else:
        body = text

    # 跳过标题行（# 开头）
    lines = body.strip().split("\n")
    paragraphs = []
    for line in lines:
        stripped = line.strip()
        # 跳过空行、标题、列表和代码块
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue
        # 收集直到遇到空行（一个段落结束）
        paragraphs.append(stripped)
        # 遇到空行表示段落结束，取前两句话
        if len(" ".join(paragraphs)) > 60:
            break

    digest = " ".join(paragraphs).strip()
    # 截断到 200 字符
    if len(digest) > 200:
        digest = digest[:200].rsplit("。", 1)[0] + "。"
    return digest or "（无摘要）"


def get_pillar(path: Path, fm: dict) -> str:
    """确定笔记的 pillar 归属。"""
    pillar = fm.get("pillar", "")
    if pillar:
        return pillar
    # 从路径推断
    parts = path.relative_to(VAULT_ROOT).parts
    known = {"AI学习", "语言学习", "运维学习", "Linux学习", "00-收件箱", "99-归档", "_系统"}
    for p in parts:
        if p in known:
            return p
    return "其他"


def get_note_title(path: Path, fm: dict) -> str:
    """从 frontmatter 或文件名取标题。"""
    title = fm.get("title", "")
    if title and title not in ("{{title}}", ""):
        return title
    # 从文件名取
    stem = path.stem
    # 去掉 YYYYMMDD- 前缀
    return re.sub(r"^\d{8}-", "", stem)


def note_sort_key(path: Path):
    """按修改时间排序，最新的在前。"""
    return -path.stat().st_mtime


def main():
    now = datetime.now()
    this_week = now - timedelta(days=7)

    # 找到本周新增/修改的笔记
    notes = [
        p
        for p in VAULT_ROOT.rglob("*.md")
        if p.stat().st_mtime > this_week.timestamp()
    ]
    # 排除系统元文件和模板占位符
    notes = [
        p
        for p in notes
        if not (".workbuddy" in p.parts)
        and not (".obsidian" in p.parts)
        and not ("_系统/01-笔记模板" in str(p.relative_to(VAULT_ROOT)))
    ]
    notes.sort(key=note_sort_key)

    # 按 pillar 分组
    groups = defaultdict(list)
    stats = defaultdict(lambda: {"count": 0, "seedling": 0, "evergreen": 0})
    for p in notes:
        fm = parse_frontmatter(p)
        pillar = get_pillar(p, fm)
        groups[pillar].append((p, fm))
        stats[pillar]["count"] += 1
        s = fm.get("status", "unknown")
        if s == "seedling":
            stats[pillar]["seedling"] += 1
        elif s == "evergreen":
            stats[pillar]["evergreen"] += 1

    report_date = now.strftime("%Y-%m-%d")
    report_path = REPORT_DIR / f"知识汇出-{report_date}.md"

    lines = [
        "---",
        "title: 知识汇出",
        f"created: {report_date}T00:00:00",
        f"modified: {report_date}T00:00:00",
        "tags: [meta, summary, report]",
        "status: draft",
        "type: project",
        "pillar: meta",
        "---",
        "",
        f"# 知识汇出 {report_date}",
        "",
        f"> 统计周期：{this_week.strftime('%Y-%m-%d')} ~ {report_date}",
        "",
        "## 📊 本周概览",
        "",
        f"- 总活跃笔记：{len(notes)}",
    ]
    # Pillar order
    for pillar_name in ["AI学习", "语言学习", "运维学习", "Linux学习", "00-收件箱", "99-归档", "_系统", "其他"]:
        if pillar_name in stats:
            s = stats[pillar_name]
            lines.append(
                f"- **{pillar_name}**：{s['count']} 条（seedling: {s['seedling']}, evergreen: {s['evergreen']}）"
            )

    lines.extend(["", "---", ""])

    # 按 pillar 详细列出
    pillar_order = ["AI学习", "语言学习", "运维学习", "Linux学习"]
    for pillar in pillar_order:
        items = groups.get(pillar, [])
        if not items:
            continue
        emoji = {"AI学习": "🤖", "语言学习": "🐍", "运维学习": "🖥️", "Linux学习": "🐧"}.get(pillar, "📌")
        lines.append(f"## {emoji} {pillar}")
        lines.append("")
        for p, fm in items:
            title = get_note_title(p, fm)
            status = fm.get("status", "unknown")
            note_type = fm.get("type", "unknown")
            rel_path = p.relative_to(VAULT_ROOT)
            digest = extract_digest(p)
            status_tag = "🌱" if status == "seedling" else "🌳" if status == "evergreen" else "📝"
            lines.append(f"### {status_tag} [[{p.stem}]]")
            lines.append(f"*类型: {note_type} | 状态: {status}*")
            lines.append("")
            lines.append(f"> {digest}")
            lines.append("")

    # 其他 pillar
    for pillar in groups:
        if pillar in pillar_order:
            continue
        items = groups[pillar]
        lines.append(f"## 📌 {pillar}")
        lines.append("")
        for p, fm in items:
            title = get_note_title(p, fm)
            rel_path = p.relative_to(VAULT_ROOT)
            lines.append(f"- [[{p.stem}]] — *{fm.get('type', '?')}*")
        lines.append("")

    # 知识地图 — 本周概念关联
    lines.extend([
        "---",
        "",
        "## 🔗 本周概念关联",
        "",
        "建议在 Obsidian 图谱中查看以下笔记的链接网络：",
        "",
    ])
    for p in notes:
        fm = parse_frontmatter(p)
        if fm.get("type") in ("permanent", "literature"):
            # 统计链接数
            text = p.read_text(encoding="utf-8")
            link_count = len(re.findall(r"\[\[([^\]]+)\]\]", text))
            if link_count > 0:
                lines.append(f"- [[{p.stem}]] — {link_count} 个链接")

    lines.extend([
        "",
        "---",
        "",
        "## 📋 下周计划",
        "",
        "- [ ] 将至少 1 篇 `seedling` 升级为 `evergreen`",
        "- [ ] 补充孤儿笔记的链接",
        "- [ ] 更新对应 MOC",
        "- [ ] 检查 Linux 学习迭代任务并记录本周练习结果",
        "- [ ] 归档过时笔记",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成: {report_path.relative_to(VAULT_ROOT)}")


if __name__ == "__main__":
    main()
