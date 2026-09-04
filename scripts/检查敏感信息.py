#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阻止明显的密钥、私钥和密码误提交到公开仓库。"""

import io
import re
import sys
from pathlib import Path


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".workbuddy", "__pycache__"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".ico", ".gif", ".woff", ".woff2", ".ttf", ".bin"}
SENSITIVE_NAMES = re.compile(
    r"(^|\.)(env(?:\..*)?|pem|key|p12|pfx)$|(^|/)(id_rsa|id_ed25519)$",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr|github_pat)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?key|secret[_-]?key|password)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{16,}"
    ),
)


def iter_text_files():
    """遍历可安全读取的文本文件。"""
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if SENSITIVE_NAMES.search(path.name):
            yield path, "文件名可能包含凭证"
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path, None


def main() -> None:
    findings: list[str] = []
    for path, name_warning in iter_text_files():
        relative = path.relative_to(ROOT).as_posix()
        if name_warning:
            findings.append(f"{relative}：{name_warning}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(f"{relative}：读取失败（{exc}）")
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings.append(f"{relative}:{line_number}：疑似敏感信息")

    if findings:
        print("❌ 敏感信息检查失败，停止提交：")
        for finding in findings[:20]:
            print(f"  - {finding}")
        if len(findings) > 20:
            print(f"  - 其余 {len(findings) - 20} 条未展开")
        sys.exit(1)

    print("✅ 敏感信息检查通过")


if __name__ == "__main__":
    main()
