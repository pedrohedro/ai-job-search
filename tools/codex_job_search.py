#!/usr/bin/env python3
"""Run a small, Codex-friendly job search using the repo's portal CLIs.

The script is intentionally a thin wrapper around the existing Bun CLIs so Codex
can perform a real first-pass search without memorising each portal's flags. It
prints Markdown for quick review and does not write personal tracking data.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LINKEDIN_CLI = ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
FREEHIRE_CLI = ROOT / ".agents" / "skills" / "freehire-search" / "cli" / "src" / "cli.ts"

DEFAULT_QUERIES = [
    "AI engineer",
    "software engineer",
    "data engineer",
]


@dataclass(frozen=True)
class JobResult:
    source: str
    title: str
    company: str
    location: str
    date: str
    url: str


def build_linkedin_command(
    query: str,
    location: str,
    jobage: int,
    limit: int,
    remote: str | None,
) -> list[str]:
    command = [
        "bun",
        "run",
        str(LINKEDIN_CLI.relative_to(ROOT)),
        "search",
        "--query",
        query,
        "--location",
        location,
        "--jobage",
        str(jobage),
        "--limit",
        str(limit),
        "--format",
        "json",
    ]
    if remote:
        command.extend(["--remote", remote])
    return command


def build_freehire_command(
    query: str,
    region: str,
    jobage: int,
    limit: int,
    remote: str | None,
) -> list[str]:
    command = [
        "bun",
        "run",
        str(FREEHIRE_CLI.relative_to(ROOT)),
        "search",
        "--query",
        query,
        "--region",
        region,
        "--jobage",
        str(jobage),
        "--limit",
        str(limit),
        "--format",
        "json",
    ]
    if remote:
        command.extend(["--remote", remote])
    return command


def run_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


def normalize_results(source: str, payload: dict[str, Any]) -> list[JobResult]:
    normalized: list[JobResult] = []
    for item in payload.get("results", []):
        normalized.append(
            JobResult(
                source=source,
                title=str(item.get("title") or "—").strip(),
                company=str(item.get("company") or "—").strip(),
                location=str(item.get("location") or "—").strip(),
                date=str(item.get("date") or "—").strip(),
                url=str(item.get("url") or item.get("applyUrl") or item.get("id") or "—").strip(),
            )
        )
    return normalized


def dedupe(results: list[JobResult]) -> list[JobResult]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[JobResult] = []
    for result in results:
        key = (result.title.lower(), result.company.lower(), result.url.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique


def markdown_table(results: list[JobResult]) -> str:
    lines = [
        "| Source | Date | Title | Company | Location | URL |",
        "|---|---|---|---|---|---|",
    ]
    for result in results:
        lines.append(
            "| "
            + " | ".join(
                [
                    result.source,
                    result.date,
                    result.title.replace("|", "\\|"),
                    result.company.replace("|", "\\|"),
                    result.location.replace("|", "\\|"),
                    result.url,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a first-pass Codex job search.")
    parser.add_argument("--query", action="append", dest="queries", help="Role keyword. Repeatable.")
    parser.add_argument("--location", default="Brazil", help="LinkedIn location string.")
    parser.add_argument("--region", default="latam,global,none", help="freehire region facet list.")
    parser.add_argument("--jobage", type=int, default=14, help="Only include jobs posted within N days.")
    parser.add_argument("--limit", type=int, default=10, help="Results per query/source.")
    parser.add_argument("--remote", choices=["remote", "hybrid", "onsite"], default="remote")
    parser.add_argument("--source", choices=["all", "linkedin", "freehire"], default="all")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if shutil.which("bun") is None:
        print("error: bun is required to run the job-search CLIs", file=sys.stderr)
        return 1

    queries = args.queries or DEFAULT_QUERIES
    results: list[JobResult] = []
    failures: list[str] = []

    for query in queries:
        if args.source in {"all", "linkedin"}:
            command = build_linkedin_command(query, args.location, args.jobage, args.limit, args.remote)
            try:
                results.extend(normalize_results("LinkedIn", run_json(command)))
            except (RuntimeError, json.JSONDecodeError) as exc:
                failures.append(f"LinkedIn query {query!r}: {exc}")
        if args.source in {"all", "freehire"}:
            command = build_freehire_command(query, args.region, args.jobage, args.limit, args.remote)
            try:
                results.extend(normalize_results("freehire", run_json(command)))
            except (RuntimeError, json.JSONDecodeError) as exc:
                failures.append(f"freehire query {query!r}: {exc}")

    unique = dedupe(results)
    print(f"# Codex Job Search Results\n")
    print(f"Queries: {', '.join(queries)}")
    print(f"LinkedIn location: {args.location}")
    print(f"freehire region: {args.region}")
    print(f"Remote filter: {args.remote}")
    print(f"Posted within: {args.jobage} days")
    print(f"Results: {len(unique)}\n")
    if unique:
        print(markdown_table(unique))
    else:
        print("No results returned.")

    if failures:
        print("\n## Warnings", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
    return 0 if unique else 1


if __name__ == "__main__":
    sys.exit(main())
