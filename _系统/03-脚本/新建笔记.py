#!/usr/bin/env python3
"""
新建笔记.py —— 为知识库生成规范化 Markdown 笔记

用法：
    python _系统/03-脚本/新建笔记.py

说明：
    交互式输入标题、类型、支柱，自动生成文件名和 YAML frontmatter。
"""
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]  # _系统/03-脚本 -> _系统 -> vault root

TEMPLATES = {
    "fleeting": "闪念笔记",
    "literature": "文献笔记",
    "permanent": "永久笔记",
    "project": "项目笔记",
    "moc": "MOC模板",
}

PILLARS = {
    "ai": "AI学习",
    "lang": "语言学习",
    "ops": "运维学习",
    "linux": "Linux学习",
    "meta": "_系统",
}


def slugify(title: str) -> str:
    """去掉 Windows 文件名非法字符。"""
    return re.sub(r'[\\/:*?"<>|]', "", title).strip()


def choose(prompt, options):
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        try:
            idx = int(input("输入编号: ").strip()) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print("无效输入，请重试。")


def parse_template(path: Path, title: str, now: str) -> str:
    if not path.exists():
        return f"# {title}\n\n"
    content = path.read_text(encoding="utf-8")
    return content.replace("{{title}}", title).replace("{{created}}", now).replace("{{modified}}", now)


def main():
    title = input("笔记标题: ").strip()
    if not title:
        print("标题不能为空")
        sys.exit(1)

    note_type = choose("笔记类型", list(TEMPLATES.keys()))
    pillar_key = choose("所属支柱", list(PILLARS.keys()))
    pillar = PILLARS[pillar_key]

    now = datetime.now().isoformat(timespec="seconds")
    safe_title = slugify(title)
    filename = f"{now.split('T')[0].replace('-', '')}-{safe_title}.md"

    if pillar == "_系统":
        folder = VAULT_ROOT / "_系统/04-工作流"
    else:
        folder = VAULT_ROOT / pillar
        if note_type == "permanent":
            folder = folder / "02-基础概念"
        elif note_type == "literature":
            folder = folder / "03-工具与实践"
        elif note_type == "project":
            folder = folder / "04-项目与案例"
        elif note_type == "moc":
            folder = folder
        else:
            folder = VAULT_ROOT / "00-收件箱"

    folder.mkdir(parents=True, exist_ok=True)
    file_path = folder / filename

    template_path = VAULT_ROOT / "_系统/01-笔记模板" / f"{TEMPLATES[note_type]}.md"
    content = parse_template(template_path, title, now)

    file_path.write_text(content, encoding="utf-8")
    print(f"已创建: {file_path.relative_to(VAULT_ROOT)}")


if __name__ == "__main__":
    main()
