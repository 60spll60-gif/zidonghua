#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""执行知识库迭代任务，并将结果推送到 GitHub 触发自动部署。"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = VAULT_ROOT / "_系统" / "03-脚本"


def run(command: list[str]) -> None:
    """在知识库根目录执行命令，失败时立即停止。"""
    print(f"执行：{' '.join(command)}")
    subprocess.run(command, cwd=VAULT_ROOT, check=True)


def main() -> None:
    for script in ("知识汇出.py", "周回顾.py", "vault统计.py", "重建dashboard.py"):
        run([sys.executable, str(SCRIPTS / script)])

    run([sys.executable, str(VAULT_ROOT / "scripts" / "验证部署包.py")])
    run(["git", "add", "-A"])

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=VAULT_ROOT,
        check=False,
    )
    if diff.returncode == 0:
        print("没有新的知识库变更，不执行提交和推送。")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    run(["git", "commit", "-m", f"chore: 自动迭代知识库 {date}"])
    run(["git", "push", "origin", "main"])
    print("✅ 已推送到 GitHub，GitHub Actions 将继续部署网站。")


if __name__ == "__main__":
    main()
