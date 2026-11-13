#!/usr/bin/env python3
"""
Validate a Automation project, or a whole workspace of projects.

Errors (exit 1):
  - required docs, root files or project skills missing or empty
  - leftover {{PLACEHOLDERS}} or <!-- AUTO: --> guidance comments
  - a automation project nested inside this project
  - .env tracked by git or not ignored
  - open Critical/High findings in docs/SECURITY_REPORT.md
  - unticked boxes in AUTOMATION_STATUS.md (unless --allow-incomplete)
  - command-contract scripts missing from package.json (once package.json exists)
  - workspace mode: any folder at workspace level that is not a project

Warnings (reported, exit 0): leftover git worktrees, TODO/FIXME in source.

Usage:
  python validate_project.py ./work/event-management-system
  python validate_project.py ./work/event-management-system --allow-incomplete
  python validate_project.py --workspace ./work
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Windows consoles default to a legacy code page; print the arrows and ticks safely.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


MARKER = "AUTOMATION_STATUS.md"
REQUIRED_ROOT = ["README.md", "AGENTS.md", "CLAUDE.md", MARKER, ".env.example", ".gitignore"]
REQUIRED_DOCS = ["PRD.md", "DESIGN_SYSTEM.md", "ARCHITECTURE.md", "DATABASE.md", "API.md", "SECURITY_REPORT.md"]
PROJECT_SKILLS = [
    "project-implementation", "setup-initialization", "feature-development", "auth-security",
    "mcp-connection", "integrations", "testing-qa", "debugging", "compound-ask", "compound-plan",
    "compound-analysis", "compound-work", "compound-fix", "pr-reviewer",
]
CONTRACT = ["dev", "infra:up", "infra:down", "lint", "typecheck", "test", "test:e2e", "test:security",
            "build", "verify", "db:migrate", "db:seed", "db:reset", "audit:deps"]
SKIP_DIRS = {"node_modules", ".git", ".worktrees", ".next", ".turbo", "dist", "build", "coverage", "out"}
WORKSPACE_ALLOWED_FILES = {"AUTOMATION_SUMMARY.md"}
PLACEHOLDER = re.compile(r"\{\{[A-Z_]+\}\}")
GUIDE_COMMENT = re.compile(r"<!--\s*AUTO\b")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SOURCE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".java", ".kt", ".swift", ".dart"}


def walk(root):
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = list(current.iterdir())
        except (PermissionError, FileNotFoundError):
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in SKIP_DIRS:
                    stack.append(entry)
            else:
                yield entry


def check_project(project, allow_incomplete):
    errors, warnings = [], []
    rel = lambda p: str(p.relative_to(project))

    if not (project / MARKER).exists():
        return [f"{project} is not a automation project (no {MARKER})"], []

    for name in REQUIRED_ROOT:
        path = project / name
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty: {name}")
    for name in REQUIRED_DOCS:
        path = project / "docs" / name
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty: docs/{name}")

    for skill in PROJECT_SKILLS:
        path = project / ".claude" / "skills" / skill / "SKILL.md"
        if not path.exists():
            errors.append(f"missing project skill: .claude/skills/{skill}/SKILL.md")
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:600]
        if not head.startswith("---") or f"name: {skill}" not in head:
            errors.append(f"bad frontmatter in .claude/skills/{skill}/SKILL.md")

    # Leftover placeholders and guidance comments in markdown files.
    for path in walk(project):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if PLACEHOLDER.search(text):
            errors.append(f"unrendered {{{{PLACEHOLDER}}}} in {rel(path)}")
        count = len(GUIDE_COMMENT.findall(text))
        if count:
            errors.append(f"{count} unfilled <!-- AUTO --> section(s) in {rel(path)}")

    # No nested projects.
    for path in walk(project):
        if path.name == MARKER and path.parent != project:
            errors.append(f"nested project found: {rel(path.parent)} (projects must not live inside projects)")

    # .env safety.
    gitignore = (project / ".gitignore").read_text(encoding="utf-8", errors="replace") if (project / ".gitignore").exists() else ""
    if not re.search(r"^\.env\s*$", gitignore, re.MULTILINE):
        errors.append(".gitignore does not ignore .env")
    if (project / ".git").exists():
        tracked = subprocess.run(["git", "ls-files"], cwd=project, capture_output=True, text=True).stdout.splitlines()
        leaked = [f for f in tracked if re.search(r"(^|/)\.env(\.[^/]+)?$", f) and not f.endswith(".env.example")]
        if leaked:
            errors.append("env files tracked by git: " + ", ".join(leaked))
        worktrees = subprocess.run(["git", "worktree", "list"], cwd=project, capture_output=True, text=True).stdout.strip().splitlines()
        if len(worktrees) > 1:
            warnings.append(f"{len(worktrees) - 1} git worktree(s) still present; remove merged ones")

    # Security report: no open Critical/High.
    report = project / "docs" / "SECURITY_REPORT.md"
    if report.exists():
        text = HTML_COMMENT.sub("", report.read_text(encoding="utf-8", errors="replace"))
        for block in re.split(r"\n(?=###\s+SEC-)", text):
            if not block.lstrip().startswith("### SEC-"):
                continue
            title = block.strip().splitlines()[0].lstrip("# ").strip()
            sev = re.search(r"Severity:\s*\**\s*(Critical|High|Medium|Low)", block, re.IGNORECASE)
            status = re.search(r"Status:\s*\**\s*(Open|Fixed|Verified|Accepted)", block, re.IGNORECASE)
            if sev and sev.group(1).lower() in {"critical", "high"}:
                if not status or status.group(1).lower() == "open":
                    errors.append(f"open {sev.group(1)} finding: {title}")
                elif status.group(1).lower() == "accepted":
                    warnings.append(f"{sev.group(1)} finding accepted rather than fixed: {title}")

    # Status file.
    status_file = project / MARKER
    if status_file.exists():
        unticked = [line.strip() for line in status_file.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- [ ]")]
        if unticked:
            msg = f"{len(unticked)} unticked item(s) in {MARKER}, first: {unticked[0]}"
            (warnings if allow_incomplete else errors).append(msg)

    # Command contract (only once the code exists).
    pkg = project / "package.json"
    if pkg.exists():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
            missing = [s for s in CONTRACT if s not in scripts]
            if missing:
                (warnings if allow_incomplete else errors).append("package.json missing command-contract scripts: " + ", ".join(missing))
        except json.JSONDecodeError:
            errors.append("package.json is not valid JSON")

    # TODO/FIXME in source.
    todo = 0
    for folder in ("apps", "packages", "src"):
        base = project / folder
        if base.exists():
            for path in walk(base):
                if path.suffix in SOURCE_EXT:
                    todo += len(re.findall(r"\b(TODO|FIXME|XXX)\b", path.read_text(encoding="utf-8", errors="replace")))
    if todo:
        warnings.append(f"{todo} TODO/FIXME marker(s) in source; link each to a plan or remove")

    return errors, warnings


def check_workspace(workspace, allow_incomplete):
    results, ws_errors = {}, []
    for entry in sorted(workspace.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            if (entry / MARKER).exists():
                results[entry.name] = check_project(entry, allow_incomplete)
            else:
                ws_errors.append(f"'{entry.name}/' is not a project; workspace must hold only project folders (no add-on or shared folders)")
        elif entry.name not in WORKSPACE_ALLOWED_FILES:
            ws_errors.append(f"unexpected file at workspace level: {entry.name}")
    if not results:
        ws_errors.append("no automation projects found in workspace")
    return ws_errors, results


def report(name, errors, warnings):
    state = "PASS" if not errors else "FAIL"
    print(f"[{state}] {name}")
    for e in errors:
        print(f"   ✗ {e}")
    for w in warnings:
        print(f"   ! {w}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", nargs="?", help="project folder")
    parser.add_argument("--workspace", help="validate every project in this workspace folder")
    parser.add_argument("--allow-incomplete", action="store_true", help="treat unticked status boxes and missing scripts as warnings")
    args = parser.parse_args()

    if not args.project and not args.workspace:
        parser.error("give a project folder or --workspace")

    failed = False
    if args.workspace:
        ws = Path(args.workspace).expanduser().resolve()
        ws_errors, results = check_workspace(ws, args.allow_incomplete)
        report(f"workspace {ws}", ws_errors, [])
        failed |= bool(ws_errors)
        for name, (errors, warnings) in results.items():
            report(name, errors, warnings)
            failed |= bool(errors)
    if args.project:
        project = Path(args.project).expanduser().resolve()
        errors, warnings = check_project(project, args.allow_incomplete)
        report(project.name, errors, warnings)
        failed |= bool(errors)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
