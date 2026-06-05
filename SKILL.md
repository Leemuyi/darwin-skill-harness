---
name: darwin-skill-harness
description: "Hermes-native Darwin Skill Harness: safely evaluates and evolves Agent Skills with todo, session_search, delegate_task, skill_manage, git audit, a 9-dimension rubric, full_test-first validation, independent judges, keep/revert ratchet, results.tsv ledger, user checkpoints, and high-risk action blacklists. Use when the user asks to optimize, score, review, migrate, or continuously improve one skill or a skill bundle."
---

# Hermes Native Darwin Skill Harness

This is a Hermes-native skill evolution harness, not just a scoring rubric. It preserves the Darwin method: **evaluate -> improve -> full_test -> independent judge -> user checkpoint -> keep or revert -> ledger**.

GitHub: https://github.com/Leemuyi/darwin-skill-harness

Read these references when executing the workflow:

- [references/hermes-tool-mapping.md](references/hermes-tool-mapping.md) for Darwin core to Hermes tool mapping
- [references/hermes-safety-policy.md](references/hermes-safety-policy.md) for safety gates and high-risk blacklist
- [references/hermes-results-ledger.md](references/hermes-results-ledger.md) for `results.tsv` schema
- [references/runtime-neutrality.md](references/runtime-neutrality.md) for runtime wording checks
- [references/skilllens-evidence.md](references/skilllens-evidence.md) for rubric evidence and high-leverage examples

## Hermes Native Mapping

| Darwin Core | Hermes Implementation |
|---|---|
| 9-dim rubric | Static scoring section plus isolated judge prompts |
| full_test first | `delegate_task` runs test prompts before any dry_run fallback |
| independent judge | `delegate_task` judge receives isolated outputs, not edit context |
| keep/revert ratchet | git branch, score comparison, keep/revert rule, commit audit |
| results ledger | `results.tsv` in the target skill directory or batch report directory |
| user checkpoint | STOP/CHECKPOINT before scope, prompts, edits, commit, cron |
| high-risk blacklist | Safety policy plus forbidden actions table |
| batch state | `todo` tracks every phase, skill, round, decision, and blocker |
| historical evidence | `session_search` retrieves prior failures and fixes as evidence |
| safe edits | `skill_manage` patches installed Hermes skills when available |
| full-test execution | `delegate_task` creates with_skill, baseline, judge, and reviewer agents |
| auditability | git branch/commit checks plus `git diff --check` before commit |
| optional periodic eval | cron prompt template is report-only and never auto-patches |

## Evaluation Rubric: 9 Dimensions, 100 Points

The rubric is based on SkillLens and local Darwin controlled studies. Dim1-7 and dim9 are static or structural. Dim8 requires live testing whenever Hermes can run `delegate_task`.

### Structural Dimensions: 59 Points

| # | Dimension | Weight | Scoring Standard |
|---|---:|---:|---|
| 1 | Frontmatter quality | 7 | Valid `name`, concise `description`, clear purpose, trigger conditions, <=1024 characters, no vague ending filler |
| 2 | Workflow clarity | 12 | Ordered executable steps with explicit inputs, outputs, and phase transitions |
| 3 | Failure mode encoding | 12 | Explicit if-then fallback branches; missing failure branches subtract at least 3 rubric points |
| 4 | Checkpoint design | 6 | Visible `STOP` or `CHECKPOINT` markers before irreversible or high-risk decisions |
| 5 | Actionable specificity | 17 | Concrete commands, paths, formats, thresholds, and examples; no vague hedge language |
| 6 | Resource integration | 4 | Referenced files, templates, scripts, and evidence paths exist and are used correctly |

### Effectiveness Dimensions: 35 Points

| # | Dimension | Weight | Scoring Standard |
|---|---:|---:|---|
| 7 | Overall architecture | 12 | Clean structure, no padding, no duplicated flow, compatible with the target ecosystem |
| 8 | Measured performance | 23 | `with_skill` output beats or usefully changes `baseline` output across confirmed prompts |

### Meta-Skill Dimension: 6 Points

| # | Dimension | Weight | Scoring Standard |
|---|---:|---:|---|
| 9 | Counterexamples and high-risk blacklist | 6 | Has explicit "do not do" actions, risk triggers, and forbidden anti-patterns |

### Score Rules

1. Score each dimension from 1 to 10.
2. Compute `total = sum(dimension_score * dimension_weight) / 10`.
3. Keep one decimal place for reports, but compare unrounded totals.
4. A changed skill is kept only when the new total is strictly higher than the current best total.
5. Important decisions still require user review because LLM judging remains noisy. See [references/skilllens-evidence.md](references/skilllens-evidence.md).

## Phase 0: Scope Discovery

Use `todo` immediately to create a batch state:

```text
batch_id: YYYYMMDD-HHMM-scope
status: scope_discovery
skills: pending list
branch: pending
ledger: pending
```

1. Determine scope from the user request.
   - One named skill: read that skill directory.
   - Multiple named skills: read only those directories.
   - "All skills": discover candidates from `$HERMES_HOME/skills/` first, then `~/.hermes/skills/`.
2. If discovery returns more than one candidate, show the list and risk level before continuing.
3. Use `session_search` for recent fixes, failures, scoring disputes, and prior user preferences. Treat results as evidence, not as content to copy into a skill.
4. Confirm git state:
   - Run `git status --short`.
   - Record current branch and latest commit.
   - Create `skill-evolve/YYYYMMDD-HHMM-<scope>` if the target is in a git repo.
5. Initialize or locate `results.tsv`. Use [templates/results.tsv.template](templates/results.tsv.template) if a new ledger is needed.

**STOP/CHECKPOINT:** Show scope, candidate skill paths, branch name, current git state, ledger path, and risk level. Do not design prompts or edit files until the user confirms the scope.

Failure handling:

| Trigger | Action |
|---|---|
| No `SKILL.md` in a candidate | Mark `decision=error` in ledger and skip that candidate |
| Not a git repo | Ask user whether to continue with file backups; no automatic patch until confirmed |
| Dirty worktree | Show changed paths; continue only if user confirms they are unrelated or intentional |
| Skill list too large | Batch by lowest-confidence or user-selected subset; keep remaining skills in `todo` |

## Phase 0.5: Test Prompt Design

Dim8 is invalid without prompts. Before scoring:

1. For each target skill, write 2-3 prompts:
   - `happy_path`: common intended use
   - `ambiguous`: under-specified or mixed intent
   - `failure_mode`: likely boundary or unsafe request
2. Store prompts in `{skill}/test-prompts.json` when the target skill owns tests. For a read-only or batch evaluation, store them in the report workspace.
3. Include expected behavior, not exact expected wording.
4. Show the prompt table using [templates/skill-evolution-report.md](templates/skill-evolution-report.md).

**STOP/CHECKPOINT:** Test prompts must be confirmed by the user before Phase 1 full_test. If the user rejects a prompt, revise prompts before any scoring.

Failure handling:

| Trigger | Action |
|---|---|
| Existing `test-prompts.json` | Show existing prompts; ask whether to reuse, replace, or append |
| User declines prompt design | Stop with `decision=blocked`; do not fabricate a dim8 score |
| Prompt is high-risk | Replace it with a safe expected-refusal or safe-boundary prompt |

## Phase 1: Baseline Evaluation, Full-Test First

Run baseline before editing. `full_test` is mandatory when `delegate_task` is available.

1. Static scoring:
   - Main agent scores dim1-7 and dim9 with short evidence.
   - Run runtime wording checks from [references/runtime-neutrality.md](references/runtime-neutrality.md).
2. Effectiveness scoring:
   - For every confirmed prompt, run `delegate_task` as `with_skill`.
   - Run the same prompt through `delegate_task` as `baseline` without loading the target skill.
   - Run `delegate_task` as isolated `judge`; give it only the prompt, expected behavior, and the two outputs in randomized labels.
   - The judge returns dim8 score, winning output, confidence, and failure notes.
3. Aggregate score and write a baseline ledger row.
4. Update `todo` with score, weak dimensions, dry_run ratio, and runtime warnings.

Dry-run fallback:

| Trigger | Action |
|---|---|
| `delegate_task` unavailable or fails | Mark that prompt `mode=dry_run`; simulate execution only enough to identify likely behavior |
| A judge has context leakage | Discard judge result and rerun with a new isolated judge |
| `dry_run_ratio > 0.30` | This batch cannot auto-keep edits; generate report only unless user explicitly approves continuing |

**STOP/CHECKPOINT:** After baseline, show score card, dim weaknesses, dry-run ratio, runtime warnings, and proposed first edit target. Do not patch until the user confirms.

## Phase 2: skill_manage-Safe Improvement Loop

Each round changes one skill and one small theme.

1. Choose the weakest actionable target:
   - Runtime drift is P0.
   - Dim3, dim4, and dim5 weaknesses usually beat cosmetic edits.
   - Consider dim2/3/4 as a correlated cluster but keep the patch minimal.
2. Draft a change proposal:
   - exact file and section
   - target dimension
   - expected score movement
   - safety policy check
3. Apply the patch:
   - Installed Hermes skill: prefer `skill_manage(action="patch")`.
   - Development tree: use a minimal patch/write operation appropriate to the environment.
   - Never edit more than one skill per round.
4. Rerun relevant Phase 1 tests with `delegate_task`.
5. Compare new total with current best.
   - If `new_total > best_total`: keep, update best score, append ledger row.
   - If `new_total <= best_total`: revert with `git revert` when the change was committed, or restore the pre-edit file snapshot when not committed; append ledger row.
6. Stop optimizing a skill when two consecutive kept rounds have `delta < 2.0`, or after `MAX_ROUNDS=3`.

**STOP/CHECKPOINT:** Before applying a patch, stop for user confirmation if the change involves any high-risk policy item, new skill creation, deletion or rename, external side effects, cron, Hermes config, credentials, or permission changes.

**STOP/CHECKPOINT:** After each skill, show diff summary, score delta, test comparison, ledger rows, and commit plan. Wait for user confirmation before moving to another skill or committing.

## Phase 2.5: Exploratory Rewrite

Use this only when normal hill-climbing is stuck.

Trigger: two consecutive skills fail in round 1 or two consecutive rounds return `delta < 1.0`.

Workflow:

1. Save current best state with git or file backup.
2. Propose a structural rewrite plan with expected rubric benefits.
3. Run full Phase 1 tests after the rewrite.
4. Keep only if the rewrite strictly beats current best.

**STOP/CHECKPOINT:** Exploratory rewrites require explicit user approval before any file edit.

## Phase 3: Report, Ledger, Git Audit

Every batch ends with an auditable report.

1. Append or update `results.tsv` using the schema in [references/hermes-results-ledger.md](references/hermes-results-ledger.md).
2. Generate a Markdown report from [templates/skill-evolution-report.md](templates/skill-evolution-report.md).
3. Run:
   - `git status --short`
   - `git diff --stat`
   - `git diff --check`
4. If the implementation is complete and verified, propose a commit:
   - `skill: evolve <name> via Hermes harness`
   - or `feat: migrate <name> to Hermes-native skill workflow`
5. Commit only after the user confirms the report and commit scope.

**STOP/CHECKPOINT:** Do not commit unverified changes, unrelated user changes, or report-only cron proposals without user confirmation.

## Optional Cron Evaluation: Report-Only

Cron is only for periodic candidate discovery and report generation.

1. Use [templates/cron-evaluation-prompt.md](templates/cron-evaluation-prompt.md).
2. The cron prompt must be self-contained.
3. It may use `session_search`, file reading, terminal checks, and skills discovery.
4. It must not patch, create, delete, rename, publish, commit, or modify Hermes config.
5. It outputs a candidate report and waits for a user-run Hermes session to act.

**STOP/CHECKPOINT:** Creating, editing, enabling, or deleting a real cron job requires explicit user confirmation. This skill never creates cron automatically.

## High-Risk Blacklist

Apply [references/hermes-safety-policy.md](references/hermes-safety-policy.md) before every edit.

| Forbidden Action | Reason | Safe Alternative |
|---|---|---|
| Write, reveal, summarize, or store tokens, API keys, passwords, or private chat text | Secrets and privacy risk | Redact and mark as unavailable evidence |
| Auto-publish a skill or send external messages | External side effect | Generate a local report |
| Create, edit, enable, or delete cron without confirmation | Persistent automation risk | Use report-only template |
| Modify Hermes config, permissions, or global memory without confirmation | Runtime integrity risk | Ask user and record decision |
| Delete or rename a skill without confirmation | Irreversible workflow impact | Propose in report only |
| Create a new skill without confirmation | Expands scope | Ask user and create only after approval |
| Use `git reset --hard`, force push, or destructive cleanup | Can destroy user work | Use `git revert`, targeted restore, or ask |
| Let the same context edit and judge the final score | Self-evaluation bias | Use isolated `delegate_task` judge |
| Skip full_test when it is available | Dim8 becomes unreliable | Run full_test first; mark fallback as dry_run |
| Keep a change when score does not strictly improve | Breaks the ratchet | Revert and ledger the failed attempt |

## Result Card

After a completed skill or batch, generate a visual card when useful:

```bash
npm ci
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-result-card.png
```

Resources:

| Path | Purpose |
|---|---|
| `templates/result-card.html` | Main visual result card |
| `templates/result-card-dark.html` | Dark variant |
| `templates/result-card-white.html` | White variant |
| `scripts/screenshot.mjs` | Cross-platform Playwright screenshot helper |

## User Commands

| User Request | Workflow |
|---|---|
| "Optimize this skill" | Phase 0 through Phase 3 for the named skill |
| "Evaluate all skills" | Phase 0 through Phase 1, report only |
| "Improve all Hermes skills" | Scope discovery, checkpoint, then batched Phase 0.5 through Phase 3 |
| "Show optimization history" | Read `results.tsv` and summarize decisions, scores, dry-run ratio, and commits |
| "Set up periodic evaluation" | Produce a report-only cron proposal; no real cron creation |

## Constraints

1. Preserve the target skill's purpose; improve how it executes and validates, not what it claims to do.
2. Keep patches small and attributable to one weak dimension or one correlated cluster.
3. Do not introduce server frameworks, background services, or heavyweight dependencies.
4. Do not install this bundle into `~/.hermes/skills/` unless the user asks.
5. Do not push. Commit only when implementation is complete, verified, and in scope.
6. Keep short-term batch state in `todo` and reports, not in long-term memory.
