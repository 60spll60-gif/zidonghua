#!/usr/bin/env python3
"""
周回顾.py —— 生成每周回顾报告

用法：
    python _系统/03-脚本/周回顾.py
"""
from datetime import datetime, timedelta
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[3:end].strip()
            for line in fm.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def main():
    now = datetime.now()
    this_week = now - timedelta(days=7)
    notes = [p for p in VAULT_ROOT.rglob("*.md") if p.stat().st_mtime > this_week.timestamp()]

    inbox_path = VAULT_ROOT / "00-收件箱"
    unprocessed = []
    if inbox_path.exists():
        for p in inbox_path.rglob("*.md"):
            if p.stem != "00-收件箱说明":
                unprocessed.append(p)

    report_date = now.strftime("%Y-%m-%d")
    report_path = VAULT_ROOT / "_系统" / "04-工作流" / f"周回顾-{report_date}.md"

    lines = [
        "---",
        "title: 周回顾",
        f"created: {report_date}T00:00:00",
        f"modified: {report_date}T00:00:00",
        "tags: [meta, review]",
        "status: draft",
        "type: project",
        "pillar: meta",
        "---",
        "",
        f"# 周回顾 {report_date}",
        "",
        "## 本周新增笔记",
        "",
    ]

    if notes:
        for p in notes:
            lines.append(f"- [[{p.stem}]]")
    else:
        lines.append("（本周没有新增笔记）")

    lines.extend([
        "",
        "## 待处理收件箱",
        "",
        f"当前收件箱有 {len(unprocessed)} 条未处理。",
        "",
    ])

    if unprocessed:
        for p in unprocessed:
            lines.append(f"- [[{p.stem}]]")
    else:
        lines.append("收件箱已清空 🎉")

    lines.extend([
        "",
        "## Linux 学习迭代",
        "",
        "本周沿用知识库原有自动化回顾流程，同时检查独立 Linux 学习支柱：",
        "- [ ] 查看 [[Linux学习/Linux学习-MOC]]，补充新知识链接",
        "- [ ] 执行 [[Linux学习/04-迭代任务/Linux学习迭代任务]] 中的本周任务",
        "- [ ] 完成一组 [[Linux学习/03-练习题/20260905-Linux练习题-基础篇]] 并记录错题",
        "",
        "## 下周行动",
        "",
        "- [ ] 处理收件箱",
        "- [ ] 检查孤儿笔记并建立链接",
        "- [ ] 更新 MOC",
        "",
        "## 反思",
        "",
        "（写几句话）",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成: {report_path.relative_to(VAULT_ROOT)}")


if __name__ == "__main__":
    main()
