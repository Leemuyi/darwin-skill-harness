# Hermes Tool Mapping

This table maps Darwin's original optimization mechanics to Hermes-native execution.

| Darwin Mechanic | Hermes Tool or Practice | Execution Rule |
|---|---|---|
| 9-dim rubric | Static scoring plus isolated judge prompt | Score dim1-7 and dim9 from the skill text; score dim8 only after prompt execution |
| full_test first | `delegate_task` | Run `with_skill`, `baseline`, and isolated `judge` before any dry_run fallback |
| Independent judge | `delegate_task` | Judge receives prompt, expected behavior, and anonymized outputs only |
| keep/revert ratchet | git branch plus score comparison | Keep only strict score improvement; otherwise revert and ledger the failed attempt |
| results ledger | `results.tsv` | Record every baseline, keep, revert, error, and dry_run decision |
| User checkpoint | Hermes conversation checkpoint | Stop before scope, prompt approval, patch, commit, cron, and high-risk action |
| High-risk blacklist | Safety policy | Block secrets, external side effects, cron mutation, config mutation, destructive git, deletion, rename |
| Batch state | `todo` | Track scope, prompts, baseline, patch rounds, verification, report, and commit status |
| Historical evidence | `session_search` | Retrieve prior failures and user preferences; never copy private text into skills |
| Safe installed-skill edit | `skill_manage` | Prefer patching installed Hermes skills through managed skill operations |
| Development-tree edit | Patch/write operation | Keep diff minimal and scoped when working in a repo checkout |
| Git audit | terminal git commands | Record branch, commit SHA, diff stat, and whitespace checks |
| Periodic evaluation | Optional cron prompt | Report-only; never patches, commits, publishes, or changes cron by itself |

## Required Tool Order

1. `todo`: create batch state.
2. `session_search`: collect evidence after scope is known.
3. git audit: record branch and worktree state.
4. `delegate_task`: execute full_test baseline.
5. `skill_manage`: patch installed Hermes skill only after user checkpoint.
6. `delegate_task`: rerun full_test.
7. git audit: diff, ledger, commit proposal.

## Failure Rules

| Failure | Required Behavior |
|---|---|
| `delegate_task` unavailable | Mark affected prompts `dry_run`; if dry-run ratio exceeds 30%, report only |
| `session_search` unavailable | Continue without historical evidence and record the gap |
| `skill_manage` unavailable | Use repo-local patch only when target is a development checkout |
| git unavailable | Ask user before using file backups; do not pretend the ratchet is git-backed |
