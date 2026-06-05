# Hermes Native Darwin Skill Migration Implementation Plan

> **For Hermes:** 等用户确认后，再使用 subagent-driven-development / 本地实现 + Codex review 分阶段执行本计划。当前文件只是开发计划，不包含功能实现。

**Goal:** 将 `darwin-skill-harness` 从通用/Claude 风格的 Agent Skill 优化方法论，迁移为 Hermes-native 的可执行 skill 演化工作流。

**Architecture:** 保留 Darwin Skill 的 9 维 rubric、full_test 优先、独立 judge、keep/revert 棘轮、results ledger、用户 checkpoint 和 high-risk blacklist；新增 Hermes 工具编排层，把 `skill_manage`、`delegate_task`、`session_search`、`todo`、git 审计、可选 cron 周期性评估写入 workflow，使它从“说明如何优化”升级成“在 Hermes 中可持续执行的安全演化流程”。

**Tech Stack:** Markdown `SKILL.md`、Hermes tools/skills、Node Playwright helper、Git、可选 cronjob、Codex CLI code review。

---

## Scope & Non-goals

### In Scope

- 重构 `SKILL.md` 为 Hermes-native 执行型 workflow。
- 保留并清晰映射 Darwin 原核心机制：
  - 9 维 rubric
  - `full_test` 优先
  - 独立 judge
  - keep/revert 棘轮
  - `results.tsv` ledger
  - 用户 checkpoint
  - high-risk blacklist
- 新增 Hermes 工具编排：
  - `todo`：当前优化批次状态机
  - `session_search`：从历史会话提取证据
  - `delegate_task`：独立测试者 / judge / reviewer
  - `skill_manage`：安全 patch / create / write_file 工作流
  - git branch/commit 审计：每轮可回滚、可追踪
  - 可选 `cronjob`：周期性候选提取/评分，但默认只生成报告，不自动 patch
- 建立 Hermes 专属安全边界：隐私、凭证、外部发布、cron、自修改限制。
- 更新 README 中的定位与使用说明。
- 增加可验证的辅助 reference / template / script。

### Out of Scope for First Migration

- 不直接安装到 `~/.hermes/skills/`，除非用户另行确认。
- 不创建真实 cron job，只提供模板/说明。
- 不自动修改用户其他 skill 库。
- 不发布到 Hermes skill hub。
- 不引入复杂 Python/Node 后端服务；保持 skill bundle 轻量。

---

## Proposed File Changes

### Modify

- `SKILL.md`
  - 改造成 Hermes-native 主工作流。
  - 明确各阶段调用哪些 Hermes tool。
  - 删除残余单 runtime 风格。
- `README.md`
  - 中文说明改成 Hermes 迁移版定位。
  - 加入使用流程、安装完整 bundle、确认机制。
- `README_EN.md`
  - 英文同步。
- `references/runtime-neutrality.md`
  - 保留多 runtime 审查，但把 Hermes-native 模式列为本 fork 的主线。

### Create

- `references/hermes-tool-mapping.md`
  - Darwin 原机制 → Hermes tool 映射表。
- `references/hermes-safety-policy.md`
  - 自进化、隐私、外部副作用、cron、git 的安全规则。
- `references/hermes-results-ledger.md`
  - `results.tsv` 字段定义与示例。
- `templates/results.tsv.template`
  - ledger 模板。
- `templates/skill-evolution-report.md`
  - 用户确认前的报告模板。
- `templates/cron-evaluation-prompt.md`
  - 可选 cron job 的自包含 prompt 模板，仅报告不自动改。
- `scripts/validate_hermes_skill_bundle.py`
  - 校验 bundle 结构、frontmatter、resource 引用、ledger 模板、runtime 残留。

---

## Phase 1: Information Architecture Refactor

### Task 1: Define Hermes-native identity in `SKILL.md`

**Objective:** 把 skill 的身份从 “Darwin Skill 2.0” 调整为 “Hermes Native Darwin Skill Harness”，但保留 Darwin 方法论来源。

**Files:**
- Modify: `SKILL.md:1-30`

**Steps:**
1. 更新 frontmatter `name`，建议：`darwin-skill-harness`。
2. 将 description 缩短到 Hermes validator 安全范围内，包含：做什么、何时用、核心工具。
3. 在正文开头加一句定位：
   - “这是用于 Hermes 生态的 skill 演化 harness，不是单纯的评分 rubric。”
4. 保留 GitHub 地址。

**Verification:**
- `SKILL.md` 从 byte 0 开始为 `---`。
- frontmatter 有 `name` / `description`。
- description ≤ 1024 chars。

---

### Task 2: Add Darwin → Hermes mapping section

**Objective:** 让用户一眼看到保留了什么、Hermes 新增了什么。

**Files:**
- Modify: `SKILL.md`
- Create: `references/hermes-tool-mapping.md`

**Content outline:**

```markdown
## Hermes Native Mapping

| Darwin Core | Hermes Implementation |
|---|---|
| 9-dim rubric | Static scoring section + judge prompt |
| full_test first | delegate_task test runners before dry_run |
| independent judge | delegate_task isolated judge, no shared context |
| keep/revert ratchet | git branch + score comparison + rollback rule |
| results ledger | results.tsv in target skill directory or report dir |
| user checkpoint | STOP/CHECKPOINT before apply, commit, cron |
| high-risk blacklist | safety policy + forbidden actions |
```

**Verification:**
- 新 reference 被 `SKILL.md` 明确引用。
- 表格覆盖用户列出的 7 个核心保留项和 6 个 Hermes 新增项。

---

## Phase 2: Hermes Execution Workflow

### Task 3: Rewrite Phase 0 as Hermes scope discovery

**Objective:** 用 Hermes 工具定义优化范围，而不是假设某个固定 skill 目录。

**Files:**
- Modify: `SKILL.md` Phase 0

**Workflow:**
1. `todo` 建立当前优化批次。
2. 若用户指定 skill：直接读取目标。
3. 若用户说“优化全部 skills”：扫描 `$HERMES_HOME/skills/` / `~/.hermes/skills/`，但先展示列表给用户确认。
4. `session_search` 查询最近相关修正/失败经验，作为 evidence，不直接写入 skill。
5. 创建 git 分支：`skill-evolve/YYYYMMDD-HHMM-<scope>`。

**Checkpoint:**
- 🔴 STOP：展示 scope、候选 skill、风险等级，用户确认后进入评估。

**Verification:**
- 不要求当前 session 能真的解析 `$HERMES_HOME`；文档中写明执行时以 `hermes-agent` skill/docs 为准。
- 没有硬编码 `.claude`。

---

### Task 4: Rewrite Phase 0.5 as test prompt design + user checkpoint

**Objective:** 把测试 prompt 设计变成 Hermes 可执行的前置门槛。

**Files:**
- Modify: `SKILL.md` Phase 0.5
- Create: `templates/skill-evolution-report.md`

**Workflow:**
1. 为每个 skill 生成 2-3 个 prompt。
2. prompt 分类：happy path / ambiguous / failure mode。
3. 写入目标 skill 的 `test-prompts.json` 或本次 report 临时区。
4. 展示给用户确认。

**Checkpoint:**
- 🔴 STOP：测试 prompt 未确认，不得进入 full_test。

**Verification:**
- 模板中有 prompt table。
- 模板中有“用户确认状态”。

---

### Task 5: Rewrite Phase 1 as baseline full_test-first evaluation

**Objective:** 强制 `delegate_task` full_test 优先，dry_run 只能作为降级路径。

**Files:**
- Modify: `SKILL.md` Phase 1

**Workflow:**
1. 静态评分：主 agent 按 dim1-7、dim9 打分。
2. 效果评分：对每个 prompt 调用 `delegate_task`：
   - `with_skill` 子 agent：加载/读取目标 skill 后执行。
   - `baseline` 子 agent：不加载目标 skill，只按普通能力执行。
   - `judge` 子 agent：盲评二者输出，产出 dim8 分数与理由。
3. 如果 delegate_task 失败：标记 `dry_run`，并在 ledger 记录失败原因。
4. dry_run 比例 > 30%：本轮不能自动 keep，只能生成报告。

**Verification:**
- `SKILL.md` 明确 full_test > dry_run。
- `dry_run` 降级有阈值与后果。

---

### Task 6: Rewrite Phase 2 as skill_manage-safe improvement loop

**Objective:** 把“改 skill”限定在 Hermes 安全可审计路径内。

**Files:**
- Modify: `SKILL.md` Phase 2
- Create: `references/hermes-safety-policy.md`

**Workflow:**
1. 根据低分维度选择一个最小改动目标。
2. 对已安装 skill：优先 `skill_manage(action='patch')`。
3. 对 dev tree：使用 `patch` / `write_file`，但必须保持 diff 小。
4. 每轮只改一个 skill 的一个小主题。
5. 修改后立刻重跑相关 full_test。
6. 分数严格上升才 keep；否则 git revert / restore。

**High-risk blacklist:**
- 不得写入/泄露 token、API key、密码、私聊原文。
- 不得自动发布、发送外部消息、改 cron、改 Hermes config。
- 不得删除/重命名 skill。
- 不得创建新 skill，除非用户确认。
- 不得把短期任务状态写入 memory。

**Checkpoint:**
- 🔴 STOP：涉及新 skill、cron、外部副作用、删除/重命名、权限/安全规则，必须用户确认。

**Verification:**
- safety policy 有 blacklist 表。
- `SKILL.md` 明确 `skill_manage` 的适用场景和限制。

---

### Task 7: Rewrite Phase 3 as report + commit audit

**Objective:** 每轮输出可审计结果，而不是只给自然语言总结。

**Files:**
- Modify: `SKILL.md` Phase 3
- Create: `references/hermes-results-ledger.md`
- Create: `templates/results.tsv.template`

**Ledger fields proposal:**

```tsv
timestamp	skill	round	mode	base_score	new_score	delta	decision	commit_sha	branch	runtime_warn	dry_run_ratio	note
```

**Workflow:**
1. 写入/更新 `results.tsv`。
2. 输出 `skill-evolution-report.md`。
3. `git diff --stat` + `git diff --check`。
4. 可选 Codex review。
5. 用户确认后 commit。
6. commit message 建议：`skill: evolve <name> via Hermes harness`。

**Verification:**
- ledger 模板字段齐全。
- `SKILL.md` 明确 commit 前后验证步骤。

---

## Phase 3: Optional Cron Evaluation Design

### Task 8: Add cron proposal template, not active cron

**Objective:** 支持周期性评估，但默认只生成报告，不自动修改。

**Files:**
- Create: `templates/cron-evaluation-prompt.md`
- Modify: `SKILL.md` optional cron section

**Cron constraints:**
1. cron prompt 必须自包含。
2. 默认 `no_agent=false`，agent 负责总结脚本输出。
3. 不自动 patch skill。
4. 不自动创建/删除 cron。
5. 输出候选报告，等待用户确认。
6. 可限制 `enabled_toolsets`: `session_search,file,terminal,skills`。

**Verification:**
- 模板中明确“report-only”。
- `SKILL.md` 写明创建 cron 需要用户确认。

---

## Phase 4: Validation & Tooling

### Task 9: Add bundle validator script

**Objective:** 给这个 skill bundle 一个轻量校验器，避免文档/资源断链。

**Files:**
- Create: `scripts/validate_hermes_skill_bundle.py`

**Checks:**
1. `SKILL.md` frontmatter valid。
2. description ≤ 1024。
3. referenced files exist：
   - `references/hermes-tool-mapping.md`
   - `references/hermes-safety-policy.md`
   - `references/hermes-results-ledger.md`
   - `templates/results.tsv.template`
   - `templates/skill-evolution-report.md`
   - `templates/cron-evaluation-prompt.md`
4. scan forbidden residue：
   - `~/.claude/skills` as primary install path
   - raw `SKILL.md` primary install command
   - `/Users/` hardcoded script path
5. Node screenshot helper syntax check if node exists。

**Verification command:**

```bash
python3 scripts/validate_hermes_skill_bundle.py
node --check scripts/screenshot.mjs
npm ci
npm run check:screenshot
```

Expected: all pass.

---

### Task 10: Update README / README_EN for Hermes-native use

**Objective:** README 不只是安装说明，还要解释 Hermes-native harness 如何使用。

**Files:**
- Modify: `README.md`
- Modify: `README_EN.md`

**Content:**
1. “What changed in Hermes migration”。
2. “Quick Start”。
3. “Run a one-skill optimization”。
4. “Safety checkpoints”。
5. “Cron is optional/report-only”。
6. “Resources included”。

**Verification:**
- Markdown fences balanced。
- 不出现 raw `SKILL.md` 作为 bundle 主安装方式。

---

## Phase 5: Review, Commit, and Push

### Task 11: Run full local verification

**Commands:**

```bash
python3 scripts/validate_hermes_skill_bundle.py
node --check scripts/screenshot.mjs
npm ci
npm run check:screenshot
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-hermes-card.png
git diff --check
git status --short
```

**Expected:**
- validator pass
- screenshot script syntax pass
- screenshot PNG generated
- no whitespace errors

---

### Task 12: Run local Codex review

**Command:**

```bash
codex exec review --base master --dangerously-bypass-approvals-and-sandbox --output-last-message /tmp/darwin-hermes-migration-codex-review.md
```

**Expected:**
- No P0/P1 findings。
- P2 findings either fixed or explicitly accepted by user。

---

### Task 13: Commit and push only after user approval

**Command:**

```bash
git add SKILL.md README.md README_EN.md references/ templates/ scripts/
git commit -m "feat: migrate Darwin skill harness to Hermes-native workflow"
git push origin dev
```

**Checkpoint:**
- 🔴 STOP：用户确认计划后才执行实现；用户确认实现结果后再决定是否推向主分支/发布。

---

## Acceptance Criteria

- [ ] `SKILL.md` 是 Hermes-native workflow，而不是 `.claude/skills` 路径迁移版。
- [ ] 9 维 rubric 保留且权重不丢失。
- [ ] `full_test` 优先写成强规则，dry_run 是降级且有阈值。
- [ ] 独立 judge 通过 `delegate_task` 明确建模。
- [ ] keep/revert 棘轮绑定 git diff/branch/commit。
- [ ] `results.tsv` ledger 有字段定义与模板。
- [ ] 用户 checkpoint 在 scope、test prompts、apply、commit、cron 处显式标记。
- [ ] high-risk blacklist 覆盖 secrets、外部副作用、cron、config、删除/重命名 skill。
- [ ] Hermes 工具：`skill_manage`、`delegate_task`、`session_search`、`todo` 都有明确使用时机。
- [ ] 可选 cron 只是 report-only 模板，不自动创建任务。
- [ ] README 中不再把 raw `SKILL.md` 单文件安装作为主路径。
- [ ] validator / screenshot / diff check / Codex review 通过。

---

## Recommended Execution Strategy

建议拆成 3 个 PR-sized commits：

1. `feat: define Hermes-native Darwin workflow`
   - `SKILL.md`
   - `references/hermes-tool-mapping.md`
   - `references/hermes-safety-policy.md`

2. `feat: add Hermes ledger and report templates`
   - `references/hermes-results-ledger.md`
   - `templates/results.tsv.template`
   - `templates/skill-evolution-report.md`
   - `templates/cron-evaluation-prompt.md`

3. `chore: add validation and documentation for Hermes migration`
   - `scripts/validate_hermes_skill_bundle.py`
   - `README.md`
   - `README_EN.md`
   - verification + Codex review fixes

这样每一步都可回滚，避免一口气把 skill 写成巨型不可审 diff。
