#!/usr/bin/env python3
"""
vault统计.py —— 统计知识库状态

用法：
    python _系统/03-脚本/vault统计.py
"""
from collections import Counter
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]


def parse_frontmatter(path: Path) -> dict:
    """简单解析 YAML frontmatter，不需要 PyYAML 依赖。"""
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
    notes = [p for p in VAULT_ROOT.rglob("*.md")]
    # 排除 _系统 下非 MOC 类元笔记（只统计知识内容）
    notes = [p for p in notes if not ("_系统" in p.parts and p.name.startswith("_"))]

    statuses = Counter()
    types = Counter()
    pillars = Counter()
    orphans = []

    note_names = {p: p.stem for p in notes}

    for p in notes:
        fm = parse_frontmatter(p)
        statuses[fm.get("status", "unknown")] += 1
        types[fm.get("type", "unknown")] += 1
        pillars[fm.get("pillar", "unknown")] += 1

        # 检查反向链接：是否被其他笔记引用
        if fm.get("type") in ("moc", "fleeting"):
            continue
        title = note_names[p]
        refs = sum(
            1
            for q in notes
            if p != q and f"[[{title}]]" in q.read_text(encoding="utf-8")
        )
        if refs == 0:
            orphans.append(p.relative_to(VAULT_ROOT))

    print(f"总笔记数: {len(notes)}")
    print(f"按状态: {dict(statuses)}")
    print(f"按类型: {dict(types)}")
    print(f"按支柱: {dict(pillars)}")
    print(f"\n孤儿笔记（无反向链接）: {len(orphans)}")
    for o in orphans[:10]:
        print(f"  - {o}")
    if len(orphans) > 10:
        print(f"  ... 还有 {len(orphans) - 10} 条")


if __name__ == "__main__":
    main()
