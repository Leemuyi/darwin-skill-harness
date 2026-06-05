#!/usr/bin/env python3
"""Validate the Hermes-native Darwin skill bundle."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "README_EN.md",
    "references/hermes-tool-mapping.md",
    "references/hermes-safety-policy.md",
    "references/hermes-results-ledger.md",
    "templates/results.tsv.template",
    "templates/skill-evolution-report.md",
    "templates/cron-evaluation-prompt.md",
    "scripts/screenshot.mjs",
]

REQUIRED_SKILL_REFERENCES = [
    "references/hermes-tool-mapping.md",
    "references/hermes-safety-policy.md",
    "references/hermes-results-ledger.md",
    "templates/results.tsv.template",
    "templates/skill-evolution-report.md",
    "templates/cron-evaluation-prompt.md",
]

REQUIRED_SKILL_TERMS = [
    "9-dim",
    "full_test",
    "delegate_task",
    "skill_manage",
    "session_search",
    "todo",
    "results.tsv",
    "keep/revert",
    "STOP/CHECKPOINT",
    "cron",
]

FORBIDDEN_PRIMARY_RESIDUE = [
    re.compile(r"~/\.claude/skills"),
    re.compile(r"raw\s+SKILL\.md", re.IGNORECASE),
    re.compile(r"/Users/[^ \n\t]+"),
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with frontmatter at byte 0")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter closing marker not found")
    block = text[4:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")


def check_frontmatter() -> None:
    data = parse_frontmatter(read("SKILL.md"))
    if not data.get("name"):
        fail("frontmatter missing name")
    description = data.get("description", "")
    if not description:
        fail("frontmatter missing description")
    if len(description) > 1024:
        fail(f"description exceeds 1024 chars: {len(description)}")


def check_skill_content() -> None:
    text = read("SKILL.md")
    for ref in REQUIRED_SKILL_REFERENCES:
        if ref not in text:
            fail(f"SKILL.md does not reference {ref}")
    for term in REQUIRED_SKILL_TERMS:
        if term not in text:
            fail(f"SKILL.md missing required Hermes workflow term: {term}")


def check_ledger_template() -> None:
    header = read("templates/results.tsv.template").strip()
    expected = (
        "timestamp\tskill\tround\tmode\tbase_score\tnew_score\tdelta\tdecision\t"
        "commit_sha\tbranch\truntime_warn\tdry_run_ratio\tnote"
    )
    if header != expected:
        fail("results.tsv template header does not match Hermes ledger schema")


def check_forbidden_residue() -> None:
    scanned = ["SKILL.md", "README.md", "README_EN.md"]
    for path in scanned:
        text = read(path)
        for pattern in FORBIDDEN_PRIMARY_RESIDUE:
            if pattern.search(text):
                fail(f"forbidden primary runtime residue in {path}: {pattern.pattern}")


def check_markdown_fences() -> None:
    markdown_paths = [
        "SKILL.md",
        "README.md",
        "README_EN.md",
        "references/hermes-tool-mapping.md",
        "references/hermes-safety-policy.md",
        "references/hermes-results-ledger.md",
        "templates/skill-evolution-report.md",
        "templates/cron-evaluation-prompt.md",
    ]
    for path in markdown_paths:
        count = read(path).count("```")
        if count % 2:
            fail(f"unbalanced markdown fences in {path}")


def check_node_screenshot_syntax() -> None:
    node = shutil.which("node")
    if not node:
        print("WARN: node not found; skipped screenshot syntax check")
        return
    result = subprocess.run(
        [node, "--check", str(ROOT / "scripts/screenshot.mjs")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        fail("node --check scripts/screenshot.mjs failed")


def main() -> None:
    check_required_files()
    check_frontmatter()
    check_skill_content()
    check_ledger_template()
    check_forbidden_residue()
    check_markdown_fences()
    check_node_screenshot_syntax()
    print("Hermes skill bundle validation passed.")


if __name__ == "__main__":
    main()
