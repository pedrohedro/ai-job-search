import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import codex_job_search  # noqa: E402


def test_build_linkedin_command_includes_remote_filter():
    command = codex_job_search.build_linkedin_command(
        query="AI engineer",
        location="Brazil",
        jobage=14,
        limit=10,
        remote="remote",
    )

    assert command[:3] == ["bun", "run", ".agents/skills/linkedin-search/cli/src/cli.ts"]
    assert command[3] == "search"
    assert command[command.index("--query") + 1] == "AI engineer"
    assert command[command.index("--location") + 1] == "Brazil"
    assert command[command.index("--remote") + 1] == "remote"
    assert command[-2:] == ["--remote", "remote"]


def test_build_freehire_command_uses_region_facets():
    command = codex_job_search.build_freehire_command(
        query="data engineer",
        region="latam,global,none",
        jobage=30,
        limit=5,
        remote=None,
    )

    assert command[:3] == ["bun", "run", ".agents/skills/freehire-search/cli/src/cli.ts"]
    assert command[3] == "search"
    assert command[command.index("--query") + 1] == "data engineer"
    assert command[command.index("--region") + 1] == "latam,global,none"
    assert "--remote" not in command


def test_normalize_results_accepts_url_or_id():
    payload = {
        "results": [
            {"title": "AI Engineer", "company": "Acme", "location": "Remote", "date": "2026-07-15", "url": "https://example.com/job"},
            {"title": "Data Engineer", "company": "Beta", "location": None, "date": None, "id": "beta-data"},
        ]
    }

    results = codex_job_search.normalize_results("test", payload)

    assert results[0].url == "https://example.com/job"
    assert results[1].location == "—"
    assert results[1].date == "—"
    assert results[1].url == "beta-data"


def test_dedupe_keeps_first_matching_title_company_url():
    result = codex_job_search.JobResult("LinkedIn", "AI Engineer", "Acme", "Remote", "2026-07-15", "https://example.com/job")
    duplicate = codex_job_search.JobResult("freehire", "ai engineer", "acme", "Remote", "2026-07-15", "https://example.com/job")

    assert codex_job_search.dedupe([result, duplicate]) == [result]


def test_markdown_table_escapes_pipes():
    table = codex_job_search.markdown_table([
        codex_job_search.JobResult("LinkedIn", "2026-07-15", "AI | ML Engineer", "Acme | Labs", "Remote", "https://example.com/job")
    ])

    assert "AI \\| ML Engineer" in table
    assert "Acme \\| Labs" in table
