"""Check project-owned text for personal absolute home paths before publishing.

Dependency environments, model caches, Git internals and binary artifacts are
excluded. Reports and intermediate project text are included, even if ignored.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", ".cache", "__pycache__", ".pytest_cache"}
PATTERN = re.compile(r"/(?:Users|home)/[^/\s\"'`]+")


def personal_paths(root=ROOT):
    matches = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file() or EXCLUDED.intersection(relative.parts) or path.name.startswith(".env"):
            continue
        if path.suffix.lower() in {".wav", ".mp3", ".aiff", ".png", ".jpg", ".pdf", ".pyc"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        if PATTERN.search(content):
            matches.append(str(relative))
    return matches


if __name__ == "__main__":
    found = personal_paths()
    if found:
        print("Personal absolute home paths found in: " + ", ".join(found))
        raise SystemExit(1)
    print("PASS: project-owned text contains no personal absolute home paths")
