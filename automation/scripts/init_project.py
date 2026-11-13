#!/usr/bin/env python3
"""
Scaffold one Automation project folder.

Creates <workspace>/<slug>/ with doc templates, the 14 project skills in
.claude/skills/, AGENTS.md, CLAUDE.md, README.md, AUTOMATION_STATUS.md, .env.example,
.gitignore and an empty git repository. Each project gets its own ports from
--index so several projects can run at the same time.

Safety rules enforced here:
  - refuses to create a project inside another project (no nesting)
  - refuses to write into an existing non-empty folder that is not a automation project
  - if the folder is already a automation project, prints RESUME and changes nothing

Usage:
  python init_project.py --workspace ./work --name "Event Management System" --platform web --index 0
  python init_project.py --workspace ./work --name "Restaurant Management System" --platform web-mobile --index 2

Platforms: web, web-mobile, mobile, desktop, api
"""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Windows consoles default to a legacy code page; print the arrows and ticks safely.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
MARKER = "AUTOMATION_STATUS.md"
PLATFORMS = {
    "web": "Web",
    "web-mobile": "Web + Mobile",
    "mobile": "Mobile",
    "desktop": "Desktop",
    "api": "API only",
}
PROJECT_SKILLS = [
    "project-implementation", "setup-initialization", "feature-development", "auth-security",
    "mcp-connection", "integrations", "testing-qa", "debugging", "compound-ask", "compound-plan",
    "compound-analysis", "compound-work", "compound-fix", "pr-reviewer",
]
DOCS_IN_DOCS_DIR = ["PRD.md", "DESIGN_SYSTEM.md", "ARCHITECTURE.md", "DATABASE.md", "API.md", "SECURITY_REPORT.md"]
ROOT_FILES = ["README.md", "AGENTS.md", "CLAUDE.md", "AUTOMATION_STATUS.md"]
DOC_SUBDIRS = ["adr", "plans", "solutions", "research"]
PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")

GITIGNORE = """# dependencies and builds
node_modules/
dist/
build/
.next/
.turbo/
out/
coverage/
*.tsbuildinfo

# env and secrets
.env
.env.*
!.env.example
*.pem
*.key

# parallel feature worktrees (inside this project only)
.worktrees/

# test output
playwright-report/
test-results/
tests/security/zap/*.html
tests/security/zap/*.json

# logs and OS files
*.log
.DS_Store
Thumbs.db
"""


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:60].rstrip("-")


def ports_for(index):
    return {
        "WEB_PORT": 3000 + index * 10,
        "API_PORT": 4000 + index * 10,
        "DB_PORT": 55432 + index,
        "REDIS_PORT": 56379 + index,
        "MAIL_PORT": 51025 + index,
        "MAIL_UI_PORT": 58025 + index,
    }


def display_path(path):
    """Show paths under the home folder as ~/... so usernames are not written into project files."""
    home = Path.home()
    try:
        return "~/" + str(Path(path).resolve().relative_to(home))
    except ValueError:
        return str(path)


def render(text, values):
    return PLACEHOLDER.sub(lambda m: str(values.get(m.group(1), m.group(0))), text)


def enclosing_project(path):
    for parent in path.parents:
        if (parent / MARKER).exists():
            return parent
    return None


def enclosing_git(path):
    for parent in path.parents:
        if (parent / ".git").exists():
            return parent
    return None


def env_example(values):
    slug = values["PROJECT_SLUG"].replace("-", "_")
    return f"""# {values['PROJECT_NAME']} — environment variables
# Copy to .env and fill values marked REQUIRED. Never commit .env.
# Ports are unique to this project so several automation projects can run at once.

NODE_ENV=development
APP_URL=http://localhost:{values['WEB_PORT']}
API_URL=http://localhost:{values['API_PORT']}
WEB_PORT={values['WEB_PORT']}
API_PORT={values['API_PORT']}
# Comma-separated allowlist for CORS (no wildcards)
CORS_ORIGINS=http://localhost:{values['WEB_PORT']}
# Number of trusted reverse proxies in front of the API (0 locally) — used to read the real client IP
TRUST_PROXY_HOPS=0

# --- Database (Docker Compose project: {values['PROJECT_SLUG']}) ---
DB_PORT={values['DB_PORT']}
POSTGRES_DB={slug}
POSTGRES_USER={slug}_app
# REQUIRED: long random value
POSTGRES_PASSWORD=
# REQUIRED: postgresql://{slug}_app:<POSTGRES_PASSWORD>@localhost:{values['DB_PORT']}/{slug}
DATABASE_URL=
# Read-only role used by reporting and the dev MCP database server
DATABASE_READONLY_URL=

# --- Redis (sessions, rate limits, IP bans, queues) ---
REDIS_PORT={values['REDIS_PORT']}
REDIS_URL=redis://localhost:{values['REDIS_PORT']}

# --- Auth ---
# REQUIRED: at least 32 random bytes, e.g. `openssl rand -base64 48`
SESSION_SECRET=
# REQUIRED if JWTs are used
JWT_ACCESS_SECRET=
JWT_REFRESH_SECRET=
ACCESS_TOKEN_TTL_SECONDS=900
REFRESH_TOKEN_TTL_DAYS=14

# --- CAPTCHA (use the provider's official test keys in development) ---
CAPTCHA_PROVIDER=turnstile
CAPTCHA_SITE_KEY=
CAPTCHA_SECRET_KEY=

# --- Email (Mailpit locally) ---
SMTP_HOST=localhost
SMTP_PORT={values['MAIL_PORT']}
MAIL_UI_PORT={values['MAIL_UI_PORT']}
MAIL_FROM="{values['PROJECT_NAME']} <no-reply@example.test>"

# --- Seed (development and test only; seed refuses to run in production) ---
# REQUIRED for db:seed
SEED_PASSWORD=
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", required=True, help="folder that holds all projects")
    parser.add_argument("--name", required=True, help='clean project name, e.g. "Event Management System"')
    parser.add_argument("--slug", help="folder name (default: derived from --name)")
    parser.add_argument("--platform", default="web", choices=sorted(PLATFORMS))
    parser.add_argument("--index", type=int, default=0, help="project position (0, 1, 2…) used to allocate ports")
    parser.add_argument("--no-git", action="store_true", help="skip git init")
    args = parser.parse_args()

    if args.index < 0 or args.index > 50:
        sys.exit("error: --index must be between 0 and 50")

    workspace = Path(args.workspace).expanduser().resolve()
    slug = slugify(args.slug or args.name)
    if not slug:
        sys.exit("error: could not derive a folder name; pass --slug")
    project = workspace / slug

    # Rule: never nest a project inside another project.
    outer = enclosing_project(project)
    if outer:
        sys.exit(f"error: {project} would be inside the automation project {outer}. Projects must not be nested; choose another workspace.")

    if project.exists():
        if (project / MARKER).exists():
            print(f"RESUME: {project} is already a automation project. Read AUTOMATION_STATUS.md and continue from the first unticked box.")
            return
        if any(project.iterdir()):
            sys.exit(f"error: {project} exists and is not empty. Refusing to overwrite someone's work; ask the user.")

    parent_git = enclosing_git(project)
    if parent_git and not args.no_git:
        print(f"warning: the workspace is inside the git repository {parent_git}. Each project will still get its own repository.")

    values = {
        "PROJECT_NAME": args.name.strip(),
        "PROJECT_SLUG": slug,
        "PLATFORM": PLATFORMS[args.platform],
        "DATE": dt.date.today().isoformat(),
        "SKILL_DIR": display_path(SKILL_DIR),
        "KNOWLEDGE_DIR": display_path(os.environ.get("AUTOMATION_KNOWLEDGE_DIR") or SKILL_DIR / "knowledge"),
        **{k: str(v) for k, v in ports_for(args.index).items()},
    }

    project.mkdir(parents=True, exist_ok=True)
    docs = project / "docs"
    for sub in DOC_SUBDIRS:
        (docs / sub).mkdir(parents=True, exist_ok=True)
        (docs / sub / ".gitkeep").touch()

    for name in DOCS_IN_DOCS_DIR:
        src = ASSETS / "docs" / name
        (docs / name).write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")

    for name in ROOT_FILES:
        src = ASSETS / "root" / name
        (project / name).write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")

    skills_root = project / ".claude" / "skills"
    for skill in PROJECT_SKILLS:
        src_dir = ASSETS / "project-skills" / skill
        if not src_dir.is_dir():
            sys.exit(f"error: missing skill template {src_dir}")
        for src in src_dir.rglob("*"):
            if src.is_dir():
                continue
            rel = src.relative_to(src_dir)
            if rel.name == "SKILL.md.tmpl":
                rel = rel.with_name("SKILL.md")
            dest = skills_root / skill / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(render(src.read_text(encoding="utf-8"), values), encoding="utf-8")

    (project / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (project / ".env.example").write_text(env_example(values), encoding="utf-8")

    if not args.no_git and shutil.which("git"):
        result = subprocess.run(["git", "init", "-b", "main"], cwd=project, capture_output=True, text=True)
        if result.returncode != 0:  # older git without -b
            subprocess.run(["git", "init"], cwd=project, capture_output=True, text=True)
            subprocess.run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], cwd=project, capture_output=True, text=True)

    print(f"Created {project}")
    print(f"  platform  {values['PLATFORM']}")
    print(f"  ports     web {values['WEB_PORT']} · api {values['API_PORT']} · db {values['DB_PORT']} · redis {values['REDIS_PORT']} · mail {values['MAIL_PORT']}/{values['MAIL_UI_PORT']}")
    print(f"  skills    {len(PROJECT_SKILLS)} installed in .claude/skills/")
    print(f"  knowledge {values['KNOWLEDGE_DIR']}  (run learn.py suggest before decisions)")
    print("Next: Phase 1 research notes → docs/research/notes.md, then fill docs in order (PRD first).")


if __name__ == "__main__":
    main()
