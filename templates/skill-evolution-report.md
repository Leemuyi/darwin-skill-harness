# Hermes Skill Evolution Report

## Batch

| Field | Value |
|---|---|
| Batch ID | `<batch_id>` |
| Scope | `<single skill / selected skills / all skills>` |
| Branch | `<branch>` |
| Ledger | `<results.tsv path>` |
| User confirmation status | `<pending / confirmed / blocked>` |

## Candidate Skills

| Skill | Path | Risk Level | Runtime Warnings | Status |
|---|---|---:|---:|---|
| `<skill>` | `<path>` | `<low/medium/high>` | `<count>` | `<pending>` |

## Test Prompts

| Skill | Prompt ID | Type | Prompt | Expected Behavior | User Confirmation |
|---|---|---|---|---|---|
| `<skill>` | `p1` | `happy_path` | `<prompt>` | `<expected>` | `<pending>` |
| `<skill>` | `p2` | `ambiguous` | `<prompt>` | `<expected>` | `<pending>` |
| `<skill>` | `p3` | `failure_mode` | `<prompt>` | `<expected>` | `<pending>` |

## Baseline Scores

| Skill | Total | Weak Dimensions | Dim8 Mode | Dry-Run Ratio | Notes |
|---|---:|---|---|---:|---|
| `<skill>` | `<score>` | `<dim list>` | `<full_test/dry_run/mixed>` | `<0.00>` | `<note>` |

## Evolution Rounds

| Skill | Round | Change | Before | After | Delta | Decision | Commit |
|---|---|---|---:|---:|---:|---|---|
| `<skill>` | `r1` | `<summary>` | `<score>` | `<score>` | `<delta>` | `<keep/revert>` | `<sha/pending>` |

## Full-Test Evidence

| Skill | Prompt ID | With Skill Result | Baseline Result | Judge Verdict | Dim8 Score |
|---|---|---|---|---|---:|
| `<skill>` | `p1` | `<short summary>` | `<short summary>` | `<winner and reason>` | `<score>` |

## Git Audit

| Check | Result |
|---|---|
| `git status --short` | `<result>` |
| `git diff --stat` | `<result>` |
| `git diff --check` | `<pass/fail>` |

## Decisions Needed

| Decision | Options | Current Status |
|---|---|---|
| Continue to patch | `yes/no/revise scope` | `<pending>` |
| Commit verified changes | `yes/no` | `<pending>` |
| Cron report-only proposal | `yes/no` | `<pending>` |
