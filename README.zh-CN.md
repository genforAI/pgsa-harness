# PGSA Harness Core

[English README](README.md)

PGSA Harness Core 是一个 agent-first 的仓库本地项目一致性协议。它不是聊天记录、不是 PR merge agent、不是 CI 或 sandbox，而是一组放在项目里的 Markdown / YAML / JSON artifacts，让 Codex、Claude Code 或其他 coding agent 在多个 session 之间恢复项目语义状态。

当前版本：1.2.0。

v1.2 在 v1.1 的 core protocol 和 advanced packs 基础上，补充了两个实际使用层：

- review-first 的外部 skill / harness 包管理路径；
- 可选 Codex SDK runner，用于可重复启动多个已注册 PGSA session。

## 核心思想

一次 session 可以完成局部任务，但大型项目的真实状态通常跨越很多 session：

- 谁负责哪个 scope；
- 哪些 contracts 是当前假设；
- 哪些命令失败过；
- 哪些文件被碰过；
- 哪些 review / integration risk 仍未关闭；
- 下一轮 agent 必须读什么、更新什么。

PGSA 把这些状态写进仓库本地 `pgsa/` 文件夹，而不是依赖私有、易丢失的聊天历史。

```text
agent reads repo-local PGSA artifacts
-> agent performs scoped work
-> agent updates contracts, summaries, reviews, integration state, merge proposals, or ledger drafts
-> next agent resumes from project state, not from chat replay
```

## 核心目录

```text
pgsa/
  project.yaml
  sessions.yaml
  harness/
  contracts/
  state/
  merge_proposals/
  reviews/
  integration/
  ledger/
  imports/
    inbox/
    sources/
  reports/

  # optional advanced mode
  gates/
  runtime/
  skills/
  evidence/
  factory/
  scenarios/
  audits/
```

## 关键 artifacts

| Artifact | 用途 |
| --- | --- |
| `project.yaml` | 项目身份、目标、模块和验收标准。 |
| `sessions.yaml` | session 注册表：role、owner scope、produces、consumes、must_read、must_update、handoff。 |
| `harness/<session>.md` | 单个 session 的操作说明。 |
| `contracts/*.json` | producer/consumer 共享假设、review 状态、验证状态和 breaking-change 状态。 |
| `state/*.summary.md` | session recovery snapshot：scope、last known good state、failed commands、touched files、open risks、next actions。 |
| `merge_proposals/*.md` | 语义冲突或假设漂移的可审查记录。 |
| `reviews/*` | review gate 状态和阻塞问题。 |
| `integration/integration_report.json` | integration readiness、blockers、open merge proposals 和 contract review state。 |
| `ledger/pending/*.json` | 并行 session 写入的 draft event records，等待 review/integration 接受。 |
| `ledger/coherence_ledger.jsonl` | append-only 的已接受项目一致性事件。 |
| `imports/index.json` | 外部 skill / harness / protocol 的导入索引。 |

## 多 Session 注册

PGSA 是 registration-based 的。每个项目 session 都在 `pgsa/sessions.yaml` 中声明身份和边界。

示例：

```text
backend
  owns API contracts and backend summary

frontend_components
  consumes API contracts and owns UI review state

docs_security_integration
  reads contracts, summaries, reviews, merge proposals, integration state, and ledger before deciding readiness

external_import_review
  triages imported harnesses, skill packs, protocols, and docs before promotion
```

这些注册信息告诉 Codex、Claude Code 或其他 agent：当前 session 拥有什么、必须读什么、handoff 前必须更新什么。注册不会扩大文件权限，也不会让 session 获得整个仓库的全局权威。

用户也可以显式注册自定义 session：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . session register research_import \
  --role external-skill-review \
  --scope "triage imported skills and protocols" \
  --must-read imports/index.json,imports/sources/external_pack/ \
  --must-update state/research_import.summary.md,ledger/pending/ \
  --handoff-to docs_security_integration \
  --self-registered
```

## 下一轮 Session 恢复

每个 `pgsa/state/<session>.summary.md` 都应该保留一个 recovery snapshot：

- current scope；
- last known good state；
- still important failed commands or failed checks；
- touched files；
- open risks、blockers 或 unresolved assumptions；
- recommended next action。

这不是完整 transcript。它的目标是让下一个 Codex / Claude Code / human reviewer 快速判断哪些检查需要重跑，避免重复执行已经失败的命令。

## 冲突和 Ledger 边界

PGSA 不会静默自动合并冲突写入，也不是 PR merge agent。Git、PR、CI 和 code review 仍然负责代码 diff、文本冲突、实现审查和最终 merge。

PGSA 记录的是更早一层的 project-state drift：语义、假设、contracts、handoff 和 readiness 的漂移。这些漂移不一定会表现为 Git 冲突。

```text
session finds semantic drift
-> create or update merge_proposal
-> record evidence, affected contracts, resolution options
-> producer / consumer / integration review
-> update editable current-state artifacts
-> append accepted ledger event
```

边界：

| 层 | 文件 | 含义 |
| --- | --- | --- |
| 当前可编辑状态 | `sessions.yaml`, `contracts/`, `state/`, `merge_proposals/`, `reviews/`, `integration/` | roles、assumptions、open conflicts、review state、integration readiness。 |
| 待接受历史 | `ledger/pending/*.json` | 并行 session 写入的 draft event records。 |
| 已接受历史 | `ledger/coherence_ledger.jsonl` | append-only 的已接受 project-coherence events 和 decisions 时间线。 |

如果一个 session 发现 contract 变了但 consumer 仍然依赖旧假设，它应该创建或更新 `pgsa/merge_proposals/*.md`，写清 evidence、affected contracts、resolution options 和 decision owner。只有 review / integration 接受 resolution 后，才追加正式 ledger event。

## 外部 Skill 和 Harness 包管理

这是 v1.2 的主要新增内容之一。

外部 harnesses、skills、prompt packs、protocol folders 或 docs 应作为可审查 package 管理：先进入 import index，再由专门 session 审查，最后才决定是否提升为项目状态。

推荐流程：

```text
external source
-> pgsa/imports/inbox/
-> pgsa import process-inbox
-> pgsa/imports/sources/<source_id>/ + imports/index.json
-> external_import_review session
-> review artifacts + ledger/pending/
-> accepted promotion into pgsa/skills, contracts, roles, capabilities, or ledger
```

默认的 `external_import_review` session 是专门负责包审查的 session。它和其他 PGSA session 一样，有明确的 `must_read`、`must_update`、handoff 和 ledger 义务。

直接导入：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import add external_pack \
  --path ../external-pack \
  --kind skill_pack \
  --session external_import_review
```

inbox 工作流：

```bash
cp -R ../external-pack pgsa/imports/inbox/external_pack
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import process-inbox
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import review external_pack
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import stats
```

`process-inbox` 会索引 inbox item，复制到 `pgsa/imports/sources/<source_id>/`，写入 `pgsa/imports/index.json`，并默认清理已处理的 inbox item。只有调试时才建议传 `--keep`。

`import review <source_id>` 会扫描复制后的来源，识别 `SKILL.md`、README 和 schema 文件，把 import 记录更新为 `reviewed`，并把审查结果写入 `harness/<session>.md`、`state/<session>.summary.md` 和 `ledger/pending/`。这仍然不会自动安装或信任外部内容。

要运行真实外部导入验证：

```bash
python3 tools/scripts/verify_external_skill_imports.py
```

这个脚本会把公共外部 skills clone 到临时项目，放入 `pgsa/imports/inbox/`，运行 `process-inbox`，对每个来源运行 `import review`，确认 inbox 已清理、review artifacts 和 pending ledger events 已生成，并运行 `pgsa validate`。

## Codex 和 Claude Code 使用方式

对 Codex，把 PGSA 指导写进目标仓库的 `AGENTS.md`。对 Claude Code，把等价指导写进 `CLAUDE.md`。本仓库包含这两个文件作为示例。

Codex 最小 prompt：

```text
Use PGSA session backend. Read AGENTS.md, pgsa-harness/protocol/SKILL.md,
pgsa/sessions.yaml, and the backend must_read artifacts before editing. Work
inside the backend owner_scope unless a merge proposal is needed. Update backend
must_update artifacts before handoff.
```

Claude Code 最小 prompt：

```text
Use PGSA session frontend_components. Read CLAUDE.md,
pgsa-harness/protocol/SKILL.md, pgsa/sessions.yaml, and the frontend_components
must_read artifacts before editing. If UI assumptions no longer match a
contract, create or update a merge proposal instead of relying on conversation
memory.
```

多个 session 可以来自不同终端、不同 worktree 或不同 agent thread。给每个 session 一个独立 PGSA identity。

## Optional Codex SDK Demo

`sdk/` 文件夹面向想使用 Codex SDK 的用户，展示如何用 SDK 启动多个已注册 PGSA session。它是 userland demo，不是 PGSA 核心路径，也不代表 OpenAI/Codex 官方集成或背书。

SDK 参考文档：<https://developers.openai.com/codex/sdk#python-library>

PGSA 支持两种 Codex 使用模式：

| 模式 | 工作方式 | 适合场景 | 取舍 |
| --- | --- | --- | --- |
| 不使用 SDK | 用户手动启动 Codex，并给出 PGSA session prompt。 | 日常交互式工作、一次性 session、人工控制和最高透明度。 | 用户需要自己启动和协调每个 session。 |
| 使用 SDK | `sdk/codex_pgsa_runner.py` 读取 `pgsa/sessions.yaml`，为每个 session 构造 PGSA-aware prompt，并启动 Codex SDK threads。 | 程序化编排、重复的长时间检查、CI/internal tools、稳定启动多个已注册 sessions。 | 需要可选 Codex SDK；仍然是 userland orchestration。 |

SDK dry-run：

```bash
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json --dry-run
```

真实运行前需要单独安装官方 SDK：

```bash
pip install openai-codex
python3 sdk/codex_pgsa_runner.py --start-only
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json
```

## 快速开始

把 `pgsa-harness/` 作为普通文件夹复制到目标项目：

```text
target-project/
  pgsa-harness/
  pgsa/
  src/
  tests/
```

初始化和验证：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . export-context --session backend
```

Advanced artifacts 是可选的：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --advanced --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate --strict-advanced
```

可选 Python CLI 也可以安装：

```bash
python3 -m pip install -e tools/python
pgsa --root examples/teamtask-projectboard validate
pgsa --root examples/teamtask-projectboard drift-report
```

## v1.2 新增内容

| v1.1 baseline | v1.2 improvement |
| --- | --- |
| core protocol plus optional advanced packs。 | 通过 `imports/inbox/`、`imports/sources/`、`imports/index.json` 和专门的 `external_import_review` session 管理外部 skill / harness packages。 |
| agents 可以手动读取 PGSA 文件。 | 增加具体非 SDK prompts 和可选 Codex SDK runner，可根据 `pgsa/sessions.yaml` 重复启动已注册 PGSA sessions。 |
| 外部材料主要靠约定引用。 | 外部 packages 先复制、索引、审查、总结，并写入 pending ledger events 后才允许提升。 |
| signed skill provenance 是 advanced artifact shape。 | 已接受 import metadata 可以提升到 `pgsa/skills/`；未审查 raw external content 不进入随仓库发布的 `protocol/`。 |
| 已有 recovery 和 conflict artifacts。 | README 明确 daily-use 路径：recovery snapshots、`must_read` / `must_update`、semantic conflicts、ledger boundaries、SDK vs non-SDK 使用，以及 import-package review。 |

## 边界

PGSA 不替代 PR、worktree、测试、code review、CI、security tooling、sandboxing 或 integration agent。它增加的是仓库本地项目状态层，让跨 session 的共享假设可见、可恢复。

PGSA Harness Core v1.2 是本地协议版本。Advanced packs 和 import package management 都是可选项目状态文件和工作流，不是强制服务。当前证据只是本地 architecture-protocol 和 embedded-example evidence，不是 Codex、Claude Code、Grok、OpenAI、Anthropic 或任何托管产品的 benchmark。

## License

Apache License 2.0. See `LICENSE`.
