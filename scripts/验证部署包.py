#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证部署站点是否包含完整的 Linux 学习内容和必要资源。"""

import json
import io
import sys
from pathlib import Path


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "部署站点"
EXPECTED_LINUX_TITLES = {
    "Linux文件系统与权限",
    "Linux进程与服务",
    "Linux网络与排错",
    "Linux练习题-基础篇",
    "Linux学习迭代任务",
}
REQUIRED_FILES = (
    "index.html",
    "checkin.html",
    "login.html",
    "manifest.json",
    "sw.js",
    "libs/chart.umd.js",
    "libs/marked.min.js",
)


def fail(message: str) -> None:
    """输出中文错误并终止校验。"""
    print(f"❌ 部署包校验失败：{message}")
    sys.exit(1)


def load_embedded_json(html: str, prefix: str) -> object:
    """从仪表盘脚本中读取单行 JSON 数据。"""
    line = next((item for item in html.splitlines() if item.startswith(prefix)), None)
    if line is None:
        fail(f"index.html 中缺少数据块：{prefix}")
    try:
        return json.loads(line[len(prefix) : -1])
    except json.JSONDecodeError as exc:
        fail(f"index.html 数据块无法解析：{exc}")


def markdown_body(path: Path) -> str:
    """去掉 Markdown frontmatter，返回正文。"""
    raw = path.read_text(encoding="utf-8")
    end = raw.find("\n---", 3)
    return raw[end + 4 :].strip() if end != -1 else raw.strip()


def main() -> None:
    missing = [name for name in REQUIRED_FILES if not (SITE / name).is_file()]
    if missing:
        fail(f"缺少文件：{', '.join(missing)}")

    index_html = (SITE / "index.html").read_text(encoding="utf-8")
    notes = load_embedded_json(index_html, "const notes = ")
    pillars = load_embedded_json(index_html, "const pillars = ")
    linux_notes = [note for note in notes if note.get("pillar") == "linux"]
    actual_titles = {note.get("title") for note in linux_notes}

    if "linux" not in pillars:
        fail("index.html 未配置 Linux 支柱")
    if actual_titles != EXPECTED_LINUX_TITLES:
        fail(f"Linux 笔记不完整，当前为：{sorted(actual_titles)}")
    if 'data-filter="linux"' not in index_html:
        fail("index.html 缺少 Linux 筛选按钮")

    # 确认内嵌正文和源 Markdown 没有脱节。
    for note in linux_notes:
        source = ROOT / note["path"]
        if not source.is_file():
            fail(f"找不到 Linux 源笔记：{note['path']}")
        if markdown_body(source) != note.get("content", ""):
            fail(f"内嵌正文与源笔记不一致：{note['title']}")

    checkin_html = (SITE / "checkin.html").read_text(encoding="utf-8")
    markers = {
        'value="linux"': "打卡任务缺少 Linux 选项",
        "Linux 学习日": "打卡模板缺少 Linux 学习日",
        "Linux 练习题 1～6 题": "打卡模板缺少 Linux 练习任务",
        "linux:'Linux'": "打卡页面缺少 Linux 标签映射",
    }
    for marker, message in markers.items():
        if marker not in checkin_html:
            fail(message)

    print(f"✅ 部署包校验通过：{len(notes)} 条笔记，{len(linux_notes)} 条 Linux 笔记")


if __name__ == "__main__":
    main()
