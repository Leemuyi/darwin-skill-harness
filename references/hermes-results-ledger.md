# Hermes Results Ledger

`results.tsv` is the audit trail for Darwin skill evolution. Store it in the target skill directory when optimizing one skill. For batch or read-only evaluations, store it in the report directory.

## Schema

```tsv
timestamp	skill	round	mode	base_score	new_score	delta	decision	commit_sha	branch	runtime_warn	dry_run_ratio	note
```

| Field | Required | Meaning |
|---|---|---|
| `timestamp` | yes | ISO-8601 local or UTC timestamp |
| `skill` | yes | Skill name or relative path |
| `round` | yes | `baseline`, `r1`, `r2`, `r3`, `report`, or `error` |
| `mode` | yes | `full_test`, `dry_run`, `mixed`, or `static_only` |
| `base_score` | yes | Previous best score; `-` for first baseline |
| `new_score` | yes | New measured score; `-` for non-score rows |
| `delta` | yes | `new_score - base_score`; `-` for baseline |
| `decision` | yes | `baseline`, `keep`, `revert`, `report_only`, `blocked`, or `error` |
| `commit_sha` | yes | Commit SHA, `pending`, or `-` |
| `branch` | yes | Current branch or `no_git` |
| `runtime_warn` | yes | Count of runtime neutrality warnings |
| `dry_run_ratio` | yes | Decimal from `0.00` to `1.00` |
| `note` | yes | Short note without secrets or private text |

## Example

```tsv
timestamp	skill	round	mode	base_score	new_score	delta	decision	commit_sha	branch	runtime_warn	dry_run_ratio	note
2026-06-05T12:00:00+08:00	huashu-research	baseline	full_test	-	78.4	-	baseline	-	skill-evolve/20260605-1200-research	0	0.00	initial baseline
2026-06-05T12:20:00+08:00	huashu-research	r1	full_test	78.4	84.1	5.7	keep	pending	skill-evolve/20260605-1200-research	0	0.00	added failure fallback table
2026-06-05T12:35:00+08:00	huashu-research	r2	mixed	84.1	83.6	-0.5	revert	a1b2c3d	skill-evolve/20260605-1200-research	0	0.33	overfit ambiguous prompt
```

## Rules

1. Append one row for every baseline, keep, revert, blocked state, and error.
2. Keep notes short enough to scan in terminal output.
3. Never record secrets, private identifiers, or raw private session text.
4. If `dry_run_ratio > 0.30`, the batch is report-only unless the user explicitly approves continuing.
5. If a change is reverted, record the reverted score and the revert commit or pending revert status.
