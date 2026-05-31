from __future__ import annotations

import argparse
import shutil
from pathlib import Path


BANNED_PATH_PARTS = {"__pycache__", ".pytest_cache"}
BANNED_SUFFIXES = {".pyc", ".zip"}
BANNED_FILENAMES = {".DS_Store"}
# Split strings that are also release-scan needles so this validator does not
# become a false positive in simple grep-based audits.
BANNED_TEXT = [
    "".join(parts)
    for parts in [
        ("C:", "\\Users"),
        ("/", "Users", "/"),
        ("PGSA_", "FULL_RESTORE"),
        ("FINAL_", "DELIVERABLE"),
        ("HARNESS_", "REPO_READY"),
        ("ECC_", "ALIGNED"),
        ("ARCHITECTURE_", "CLARIFIED"),
        ("PGSA improves", " Codex by"),
        ("PGSA beats", " Codex"),
        ("PGSA is inside", " Codex"),
    ]
]

ALLOWED_BOUNDARY_PATH_PARTS = {
    "AGENTS.md",
    "claim-boundary.md",
    "claim_boundary.md",
    "rules",
    "protocol",
}

ALLOWED_ROOT_ENTRIES = {
    ".git",
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "README.zh-CN.md",
    "SECURITY.md",
    "VERSION",
    "examples",
    "protocol",
    "tools",
}


def clean_generated(root: Path) -> None:
    for path in sorted(root.rglob("__pycache__")):
        if path.is_dir():
            shutil.rmtree(path)
    for path in sorted(root.rglob("*.egg-info")):
        if path.is_dir():
            shutil.rmtree(path)
    pytest_cache = root / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache)
    for path in root.rglob("*.pyc"):
        if path.is_file():
            path.unlink()
    for path in root.rglob(".DS_Store"):
        if path.is_file():
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PGSA release hygiene.")
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()
    root = Path(args.root)
    clean_generated(root)
    issues: list[str] = []

    for entry in root.iterdir():
        if entry.name not in ALLOWED_ROOT_ENTRIES:
            issues.append(f"unexpected root entry: {entry.name}")

    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if ".git" in rel.parts:
            continue
        parts = set(rel.parts)
        if path.is_dir() and path.name.endswith(".egg-info"):
            issues.append(f"banned generated path: {rel}")
        if parts & BANNED_PATH_PARTS:
            issues.append(f"banned generated path: {rel}")
        if path.name in BANNED_FILENAMES:
            issues.append(f"banned generated file: {rel}")
        if path.is_file() and path.suffix in BANNED_SUFFIXES:
            issues.append(f"banned generated file: {rel}")
        if path.is_file() and path.suffix in {".md", ".py", ".toml", ".yaml", ".json", ".sh", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            boundary_context = bool(set(rel.parts) & ALLOWED_BOUNDARY_PATH_PARTS)
            if path.name == "validate_release.py":
                boundary_context = True
            for needle in BANNED_TEXT:
                if needle in text and not boundary_context:
                    issues.append(f"banned phrase outside claim-boundary context: {needle} in {rel}")

    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("release hygiene checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
