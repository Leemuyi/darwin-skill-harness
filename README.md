<div align="right">

**[English](README_EN.md)** | 中文

</div>

![达尔文.skill](assets/banner.svg)

<p align="center">
  <img src="assets/hero.gif" alt="Darwin Skill Animation" />
</p>

<div align="center">

# Hermes Native Darwin Skill Harness

**用 Hermes 工作流安全演化 Agent Skills。**

Darwin Skill Harness 保留达尔文 2.0 的 9 维 rubric、`full_test` 优先、独立 judge、keep/revert 棘轮、`results.tsv` ledger、用户 checkpoint 和 high-risk blacklist，并迁移为 Hermes-native 的可执行工作流：`todo` 管状态，`session_search` 找证据，`delegate_task` 跑 full_test 和盲评，`skill_manage` 做安全 patch，git 负责可追踪审计。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0--hermes-blue.svg)](#hermes-native-迁移)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Compatible-blueviolet)](https://skills.sh)

</div>

---

## Hermes Native 迁移

这次迁移把原来的通用 Darwin Skill 优化方法论，改造成 Hermes 生态里的安全执行 harness。

| 保留机制 | Hermes 落地 |
|---|---|
| 9 维 rubric | `SKILL.md` 内完整保留 100 分权重 |
| `full_test` 优先 | `delegate_task` 先跑 with_skill / baseline / judge |
| 独立 judge | judge 子任务只看匿名输出，不共享编辑上下文 |
| keep/revert 棘轮 | 分数严格上升才 keep，否则 git revert/恢复 |
| `results.tsv` ledger | 新增字段模板和字段说明 |
| 用户 checkpoint | scope、测试 prompt、patch、commit、cron 前都 STOP |
| high-risk blacklist | secrets、外部副作用、cron、config、删除/重命名都受控 |

新增资源：

- [references/hermes-tool-mapping.md](references/hermes-tool-mapping.md)
- [references/hermes-safety-policy.md](references/hermes-safety-policy.md)
- [references/hermes-results-ledger.md](references/hermes-results-ledger.md)
- [templates/results.tsv.template](templates/results.tsv.template)
- [templates/skill-evolution-report.md](templates/skill-evolution-report.md)
- [templates/cron-evaluation-prompt.md](templates/cron-evaluation-prompt.md)
- [scripts/validate_hermes_skill_bundle.py](scripts/validate_hermes_skill_bundle.py)

## 快速开始

安装时复制完整目录。这个 bundle 依赖 `references/`、`templates/` 和 `scripts/`，单独拿主 skill 文件会缺资源。

```bash
git clone https://github.com/Leemuyi/darwin-skill-harness.git
mkdir -p ~/.hermes/skills
cp -R darwin-skill-harness ~/.hermes/skills/darwin-skill-harness
```

在 Hermes 会话里重新加载 skills 后使用：

```text
优化 huashu-research 这个 skill
```

或只评估不修改：

```text
评估所有 Hermes skills 的质量
```

## 单 Skill 优化流程

1. **Scope discovery**：`todo` 建批次状态，读取目标 skill，`session_search` 查历史证据，git 创建审计分支。
2. **测试 prompt 确认**：为目标 skill 设计 2-3 个 happy path / ambiguous / failure mode prompt，用户确认后继续。
3. **Baseline full_test**：`delegate_task` 跑 with_skill、baseline、独立 judge，生成 9 维基线分。
4. **安全 patch**：已安装 Hermes skill 优先走 `skill_manage`；开发目录走小 patch。
5. **重测和棘轮**：重跑 full_test。分数严格上升才 keep，否则 revert。
6. **报告和审计**：更新 `results.tsv`，输出 report，跑 git diff audit，用户确认后再 commit。

## 安全 Checkpoints

这些动作必须暂停等用户确认：

- 优化范围不明确或包含多个 skills
- 测试 prompt 进入 baseline 前
- 任何 patch 前，尤其是涉及权限、配置、cron、外部副作用
- 创建、删除、重命名 skill
- commit 前
- 真实 cron 创建或修改前

明令禁止：写入或泄露 token/API key/password，自动发布，自动发送外部消息，自动改 Hermes config，`git reset --hard`，force push，同一上下文自改自评。

## Cron 只做报告

[templates/cron-evaluation-prompt.md](templates/cron-evaluation-prompt.md) 只是 report-only 模板。它用于周期性发现候选问题，不自动 patch、不自动 commit、不自动创建或修改 cron。真实 cron 需要用户另行确认。

## 结果卡片

截图 helper 保留为轻量 Playwright 脚本：

```bash
cd ~/.hermes/skills/darwin-skill-harness
npm ci
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-result-card.png
```

## 本地验证

```bash
python3 scripts/validate_hermes_skill_bundle.py
node --check scripts/screenshot.mjs
npm ci
npm run check:screenshot
node scripts/screenshot.mjs templates/result-card.html /tmp/darwin-hermes-card.png
git diff --check
```

## 研究来源

Darwin 的评分和验证机制来自：

- Microsoft Research, *From Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills*, arXiv:2605.23899.
- Microsoft Research, *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*, arXiv:2605.23904.
- Andrej Karpathy, *autoresearch*.

更多证据见 [references/skilllens-evidence.md](references/skilllens-evidence.md)。

## 许可证

MIT
