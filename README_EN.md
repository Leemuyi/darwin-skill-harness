<div align="right">

English | **[中文](README.md)**

</div>

![darwin.skill](assets/banner-en.svg)

<div align="center">

# Hermes Native Darwin Skill Harness

**Safely evolve Agent Skills with a Hermes-native workflow.**

Darwin Skill Harness preserves the Darwin 2.0 method: a 9-dimension rubric, `full_test` first, independent judges, a keep/revert ratchet, `results.tsv` ledger, user checkpoints, and a high-risk blacklist. This migration makes it executable in Hermes: `todo` tracks state, `session_search` gathers evidence, `delegate_task` runs full tests and blind judging, `skill_manage` applies safe patches, and git provides auditability.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0--hermes-blue.svg)](#hermes-native-migration)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Compatible-blueviolet)](https://skills.sh)

</div>

---

## Hermes Native Migration

This migration turns the original Darwin skill optimization method into a Hermes-native safety and execution harness.

| Preserved Mechanic | Hermes Implementation |
|---|---|
| 9-dimension rubric | Full 100-point rubric remains in `SKILL.md` |
| `full_test` first | `delegate_task` runs with_skill / baseline / judge first |
| Independent judge | Judge task only sees anonymized outputs, not edit context |
| keep/revert ratchet | Strict score improvement keeps the patch; otherwise revert |
| `results.tsv` ledger | New schema template and field reference |
| User checkpoint | STOP before scope, prompts, patch, commit, and cron |
| High-risk blacklist | Secrets, external side effects, cron, config, delete/rename are gated |

Included resources:

- [references/hermes-tool-mapping.md](references/hermes-tool-mapping.md)
- [references/hermes-safety-policy.md](references/hermes-safety-policy.md)
- [references/hermes-results-ledger.md](references/hermes-results-ledger.md)
- [templates/results.tsv.template](templates/results.tsv.template)
- [templates/skill-evolution-report.md](templates/skill-evolution-report.md)
- [templates/cron-evaluation-prompt.md](templates/cron-evaluation-prompt.md)
- [scripts/validate_hermes_skill_bundle.py](scripts/validate_hermes_skill_bundle.py)

## Quick Start

Install the complete directory. This bundle depends on `references/`, `templates/`, and `scripts/`; a single main skill file is not enough.

```bash
git clone https://github.com/Leemuyi/darwin-skill-harness.git
mkdir -p ~/.hermes/skills
cp -R darwin-skill-harness ~/.hermes/skills/darwin-skill-harness
```

Then reload skills in Hermes and ask:

```text
Optimize the huashu-research skill.
```

For evaluation only:

```text
Evaluate all Hermes skills for quality.
```

## One-Skill Optimization Flow

1. **Scope discovery**: `todo` creates batch state, the target skill is read, `session_search` retrieves historical evidence, and git records the audit branch.
2. **Prompt confirmation**: Generate 2-3 happy path / ambiguous / failure mode prompts and wait for user approval.
3. **Baseline full_test**: `delegate_task` runs with_skill, baseline, and independent judge tasks to produce a 9-dimension baseline score.
4. **Safe patch**: Installed Hermes skills prefer `skill_manage`; development trees use minimal scoped patches.
5. **Retest and ratchet**: Rerun full_test. Keep only strict score improvement; otherwise revert.
6. **Report and audit**: Update `results.tsv`, produce a report, run git diff checks, then commit only after confirmation.

## Safety Checkpoints

These actions require a user checkpoint:

- Scope is unclear or includes multiple skills
- Test prompts are about to enter baseline testing
- Any patch, especially one touching permissions, config, cron, or external side effects
- Creating, deleting, or renaming a skill
- Committing changes
- Creating or editing a real cron job

Forbidden: writing or revealing tokens/API keys/passwords, auto-publishing, sending external messages, modifying Hermes config without approval, `git reset --hard`, force push, and letting the same context edit and judge the final score.

## Cron Is Report-Only

[templates/cron-evaluation-prompt.md](templates/cron-evaluation-prompt.md) is only a report-only prompt. It can periodically identify candidate issues, but it does not patch, commit, create cron, or modify cron. Real cron setup needs separate user confirmation.

## Result Cards

The screenshot helper remains a lightweight Playwright script:

```bash
cd ~/.hermes/skills/darwin-skill-harness
npm ci
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-result-card.png
```

## Local Verification

```bash
python3 scripts/validate_hermes_skill_bundle.py
node --check scripts/screenshot.mjs
npm ci
npm run check:screenshot
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-hermes-card.png
git diff --check
```

## Research Basis

Darwin's scoring and validation method builds on:

- Microsoft Research, *From Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills*, arXiv:2605.23899.
- Microsoft Research, *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*, arXiv:2605.23904.
- Andrej Karpathy, *autoresearch*.

See [references/skilllens-evidence.md](references/skilllens-evidence.md) for details.

## License

MIT
