# Codex Instructions for AI Job Search

This repository is a personal job-search workspace adapted for Codex. Treat the existing Claude-oriented files as the source workflow documentation, but execute the steps with Codex tools.

## How to Use This Repo with Codex

- Start with `CLAUDE.md` for the candidate-facing workflow, profile expectations, and document verification checklist.
- Use `.claude/commands/*.md` as command playbooks. When the user asks for `/setup`, `/scrape`, `/apply`, `/rank`, `/interview`, `/outcome`, `/expand`, `/upskill`, `/add-template`, `/add-portal`, or `/reset`, read the matching file and follow its workflow manually in Codex.
- Use `.claude/skills/job-application-assistant/SKILL.md` and its referenced files as the canonical application workflow for evaluating job fit, tailoring CVs, writing cover letters, and preparing interviews.
- Use `.claude/skills/job-scraper/SKILL.md` plus `.agents/skills/*/SKILL.md` for job search workflows. Prefer `python tools/codex_job_search.py` for a first-pass Codex search, then use the local portal CLIs directly for deeper searches; use web search only when the relevant workflow calls for it or when live data is needed.
- Use `.claude/skills/upskill/SKILL.md` for skill-gap and learning-plan workflows.

## Candidate Documents

- Personal documents belong under `documents/` as described in `documents/README.md`.
- The user's current CVs are expected to be copied into `documents/cv/` before profile extraction:
  - English: `CV Pedro Hedro 2026 Eng.pdf`
  - Portuguese: `CV-Pedro-Hedro-2026-pt.pdf`
- Do not commit personal CVs, LinkedIn exports, diplomas, references, generated application drafts, salary data, tracker rows, or scrape results. These paths are intentionally ignored by `.gitignore`.
- If referenced local files are outside the container or missing, say that clearly and continue with the available repository context rather than inventing candidate details.

## Application Workflow Rules

- Always evaluate fit before drafting application documents.
- Never fabricate skills, dates, employers, education, achievements, salary data, references, or company research.
- Verify live or company-specific claims with web sources before using them in a CV or cover letter.
- When mentioning agentic coding or AI tooling in candidate-facing documents, explicitly name **Codex** when describing work performed in this environment, and preserve **Claude Code** only when the candidate actually used Claude Code.
- Generated CVs must be LaTeX files under `cv/` and generated cover letters must be LaTeX files under `cover_letters/`, following the templates and verification checklist in `CLAUDE.md`.
- Compile generated PDFs when LaTeX tooling is available. If tooling is missing, report the exact missing command and perform all non-compile checks possible.

## Repository Hygiene

- Before editing, check `git status --short` and do not overwrite user changes.
- Prefer `rg`/`rg --files` for searching; do not use recursive `grep -R` or `ls -R`.
- Keep reusable workflow changes in tracked documentation or template files. Keep personal outputs in ignored folders.
- Run relevant tests after changes, at minimum `python -m pytest` for repository-level documentation or tooling updates when dependencies are available.
