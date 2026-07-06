#!/usr/bin/env python3
# ruff: noqa: E501
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"

CHAPTERS = [
    (1, "Why a task queue — and why Postgres", "What background jobs actually are, and how a database becomes a broker with SELECT FOR UPDATE and LISTEN/NOTIFY."),
    (2, "Setup: your first job, end to end", "Install, connect, apply the schema, defer one job, and watch a worker pick it up."),
    (3, "Defining and deferring tasks", "Task anatomy, configure(), batch deferring, JSON argument limits, and blueprints for larger codebases."),
    (4, "Workers up close", "Queues, concurrency, how jobs are fetched the instant they're deferred — and the polling that backs it up."),
    (5, "Retries and failure", "The job lifecycle, built-in retry strategies, and writing a custom one that changes queue or priority on retry."),
    (6, "Scheduling: later and every hour", "One-off future jobs with schedule_at/schedule_in, and periodic tasks with cron — including who defers them when you run five workers."),
    (7, "Locks, queueing locks, priorities", "Serialize jobs that touch the same resource, stop duplicate jobs from piling up, and decide who goes first."),
    (8, "Context, cancellation, middleware", "Reach into the running job with JobContext, abort jobs that are already executing, and wrap every task with middleware."),
    (9, "Sync and async together", "Sync connectors, deferring from synchronous code, and the RuntimeError waiting for you at the boundary."),
    (10, "Procrastinate in FastAPI", "Defer jobs from endpoints, embed a worker in the lifespan — and why production usually wants a separate worker process."),
    (11, "Testing your tasks", "InMemoryConnector, asserting on deferred jobs, and running a real worker inside a test when it's worth it."),
    (12, "Operating in production", "Schema migrations without downtime, monitoring, graceful shutdown, stalled-job recovery, and keeping the jobs table small."),
    (13, "Deploying workers on AWS ECS", "Containerize the worker, map SIGTERM to procrastinate's graceful shutdown, and size stopTimeout so jobs survive deploys."),
]

PARTS = [
    ("I", "Foundations", [1, 2, 3, 4]),
    ("II", "Controlling execution", [5, 6, 7, 8]),
    ("III", "Sync and the web", [9, 10]),
    ("IV", "Production", [11, 12, 13]),
]


def pad(n: int) -> str:
    return f"{n:02d}"


def replace_in_tree(directory: Path, mapping: dict[str, str]) -> None:
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".html", ".md", ".txt", ".xml"}:
            continue
        text = path.read_text()
        new = text
        for old, new_val in mapping.items():
            new = new.replace(old, new_val)
        if new != text:
            path.write_text(new)


def build_has_part(pages_url: str, og_image: str) -> str:
    entries = []
    for num, title, desc in CHAPTERS:
        entries.append(
            "    "
            + json.dumps(
                {
                    "@type": "Chapter",
                    "position": num,
                    "name": title,
                    "description": desc,
                    "url": f"{pages_url}chapters/ch{pad(num)}.html",
                },
                ensure_ascii=False,
            )
        )
    return ",\n".join(entries)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <owner/repo>", file=sys.stderr)
        sys.exit(1)
    owner_repo = sys.argv[1]
    owner = owner_repo.split("/")[0]
    pages_url = f"https://{owner}.github.io/{owner_repo.split('/')[1]}/"
    pages_host = f"{owner}.github.io/{owner_repo.split('/')[1]}"
    repo_url = f"https://github.com/{owner_repo}"
    codespaces_url = f"https://codespaces.new/{owner_repo}"
    what_running = "Postgres is already running there"
    author_url = f"https://github.com/{owner}"
    og_image = f"{pages_url}assets/screenshots/homepage.png"
    shot = BOOK / "assets/screenshots/homepage.png"
    width = height = "1200"
    if shot.exists():
        try:
            import struct

            with shot.open("rb") as f:
                f.seek(16)
                width, height = struct.unpack(">II", f.read(8))
                width, height = str(width), str(height)
        except Exception:
            pass

    mapping = {
        "{{PAGES_URL}}": pages_url,
        "{{PAGES_HOST_PATH}}": pages_host,
        "{{REPO_URL}}": repo_url,
        "{{CODESPACES_URL}}": codespaces_url,
        "{{WHAT_S_ALREADY_RUNNING}}": what_running,
        "{{AUTHOR_URL}}": author_url,
        "{{OG_IMAGE_URL}}": og_image,
        "{{OG_IMAGE_WIDTH}}": width,
        "{{OG_IMAGE_HEIGHT}}": height,
    }
    replace_in_tree(ROOT, mapping)
    replace_in_tree(BOOK, mapping)

    index = BOOK / "index.html"
    text = index.read_text()
    has_part = build_has_part(pages_url, og_image)
    text = re.sub(
        r'"hasPart": \[\s*\{[^]]+\}\s*\]',
        f'"hasPart": [\n{has_part}\n  ]',
        text,
        count=1,
        flags=re.DOTALL,
    )
    index.write_text(text)

    lastmod = date.today().isoformat()
    sitemap_urls = [f"  <url>\n    <loc>{pages_url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>1.0</priority>\n  </url>"]
    for num, _, _ in CHAPTERS:
        sitemap_urls.append(
            f"  <url>\n    <loc>{pages_url}chapters/ch{pad(num)}.html</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>0.8</priority>\n  </url>"
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (BOOK / "sitemap.xml").write_text(sitemap)
    (BOOK / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + pages_url + "sitemap.xml\n"
    )

    tagline = (
        "A hands-on course on Procrastinate 3, the Python task queue built on PostgreSQL — "
        "thirteen chapters with runnable examples, failing-test challenges, and citations to the real docs."
    )
    llms = [
        "# Procrastinate: Task Queues on Postgres",
        "",
        f"> {tagline}",
        "",
        "Every example was run against a real Postgres database; load-bearing claims link to official docs.",
        "",
    ]
    for roman, part_title, nums in PARTS:
        llms.append(f"## Part {roman} · {part_title}")
        llms.append("")
        for num in nums:
            title, desc = CHAPTERS[num - 1][1], CHAPTERS[num - 1][2]
            llms.append(f"- [{title}]({pages_url}chapters/ch{pad(num)}.html): {desc}")
        llms.append("")
    llms.extend(
        [
            "## Optional",
            "",
            f"- [Source repo]({repo_url}): runnable examples, failing-test challenges, and reference solutions",
            f"- [Open in GitHub Codespaces]({codespaces_url}): zero-install environment with {what_running}",
            "",
        ]
    )
    (BOOK / "llms.txt").write_text("\n".join(llms))


if __name__ == "__main__":
    main()
