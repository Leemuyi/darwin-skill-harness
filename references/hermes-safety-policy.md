# Hermes Safety Policy

This policy constrains Hermes-native skill evolution. Apply it before scope confirmation, every patch, every commit, and every cron proposal.

## Safety Gates

| Gate | Stop Condition | Required Action |
|---|---|---|
| Scope | More than one skill, unclear target, or all-skills request | Show candidate list and wait for confirmation |
| Privacy | Prompt, evidence, or session result contains secrets or private chat text | Redact; do not write into skill files, ledger notes, or reports |
| External side effect | Publish, send message, open network write, alter remote service | Generate local proposal only |
| Persistence | Cron, Hermes config, permissions, memory, global settings | Stop and ask user |
| Destructive edit | Delete, rename, overwrite large content, destructive shell, force push | Stop and ask user |
| Commit | Unverified changes, unrelated dirty files, or failed checks | Do not commit |

## High-Risk Blacklist

| Forbidden | Rationale | Safe Path |
|---|---|---|
| Store or reveal tokens, API keys, passwords, cookies, private messages, or private identifiers | Credential and privacy exposure | Redact as `[REDACTED]` and cite only the category |
| Auto-publish skills, push branches, send emails, post messages, or update remote systems | External side effect | Produce a local report and ask user |
| Create, edit, enable, or delete cron automatically | Persistent unattended automation | Use `templates/cron-evaluation-prompt.md` as report-only proposal |
| Modify Hermes config, enabled tools, permissions, memory, or global state without approval | Runtime integrity risk | Ask user and record approval in the report |
| Delete, rename, or create skills without approval | Scope expansion or data loss | Propose and wait |
| Use `git reset --hard`, `git clean -fd`, force push, or broad checkout restore | Can destroy user work | Use `git revert`, targeted patch reversal, or ask |
| Let the editing context be the final judge | Self-evaluation bias | Use isolated `delegate_task` judge |
| Keep a change without strict score improvement | Breaks Darwin ratchet | Revert and ledger |
| Convert a failed full_test into an unmarked score | Misleading dim8 result | Mark `mode=dry_run` and include failure reason |

## Data Handling

1. `session_search` results are evidence, not source text for skill files.
2. Ledger notes must be short and free of secrets.
3. Reports may reference categories of failures, not private raw conversations.
4. Generated prompts must avoid requiring real credentials, private accounts, or irreversible actions.

## Commit Policy

Commit only when all are true:

1. The user approved the scope and patch direction.
2. `full_test` ran, or dry-run limitations are explicit and accepted.
3. `results.tsv` or the report records the decision.
4. `git diff --check` passes.
5. The commit contains only relevant files.
