# PGSA Harness Core

[English README](README.md)

PGSA Harness Core 是一个 agent-first 的仓库本地项目一致性协议。v1.1 保持核心协议文件化、可嵌入，同时增加可选 advanced artifact packs，用于更严格的 verification、review、runtime evidence 和 planning 记录。

它不是 Python 框架，也不在模型内部运行。它存在于代码仓库中，用一组 Markdown、JSON、YAML 和 JSONL 文件，让 coding agent 可以读取、更新、diff、审查，并在多个 session 之间交接项目状态。

## 它是什么

coding agent 可以完成局部任务，但项目整体仍然漂移。backend session 改了 API，frontend session 可能还保留旧假设；docs 可能描述旧行为；局部检查通过，但项目已经对不上。

PGSA 把这些共享项目状态写进仓库：

```text
agent 读取仓库本地 PGSA artifacts
-> agent 执行任务
-> agent 更新 contracts、summaries、reviews、integration state 或 ledger drafts
-> 下一个 agent 从可检查的项目状态继续
```

交流媒介是仓库，不是私有聊天记录。

适合使用 PGSA 的场景：任务很长、多个 agent session 并行或接力、共享假设容易变化。对于一次性小修改，PGSA 可能没有必要。

## 文件模型

协议源文件在 `protocol/`：

- `protocol/SKILL.md`：给 agent 的工作流。
- `protocol/artifact-map.md`：每类 PGSA artifact 的含义。
- `protocol/templates/`：复制到目标仓库 `pgsa/` 层的起始模板。
- `protocol/schemas/`：结构化 artifact 的 JSON schema。
- `protocol/rules/`：agent 应遵守的短规则和边界。
- `protocol/roles/`：可选 role 示例和 role schema。
- `protocol/capabilities/`：可选高级能力包说明。
- `protocol/adapters/`：runtime/security/interpretability 工具的可选 adapter spec。

使用 PGSA 的目标项目会有一个 `pgsa/` 文件夹：

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
  reports/

  # 可选 advanced mode
  gates/
  runtime/
  skills/
  evidence/
  factory/
  scenarios/
  audits/
```

核心 artifact 职责：

| Artifact | 职责 |
| --- | --- |
| `project.yaml` | 项目身份、目标、模块和验收标准。 |
| `sessions.yaml` | session 身份、职责、必须读取、必须更新和 handoff 目标。 |
| `harness/<session>.md` | 单个 session 的操作说明。 |
| `contracts/*.json` | producer/consumer 共享假设、review state、验收测试和 breaking-change state。 |
| `state/*.summary.md` | 压缩后的 session memory，并包含 recovery snapshot：scope、失败命令、触碰文件、开放风险和下一步。 |
| `merge_proposals/*.md` | 开放中的语义冲突记录，包含 evidence、options 和 decision owner。 |
| `reviews/*` | review gate 状态和阻塞问题。 |
| `integration/integration_report.json` | 当前 integration readiness、blockers、open merge proposals 和 contract review state。 |
| `ledger/coherence_ledger.jsonl` | append-only 的已接受项目一致性事件。 |
| `ledger/pending/*.json` | 并行 session 的事件草稿，由 review/integration session 接受后提升到正式 ledger。 |

## 核心流程

每个 agent session 遵循同一套流程：

1. 读取 `pgsa/project.yaml`。
2. 读取 `pgsa/sessions.yaml`。
3. 确认当前 session，并检查它的 `role`、`owner_scope`、`produces`、`consumes`、`must_read`、`must_update` 和 `handoff_to`。
4. 读取 `pgsa/harness/<session>.md`。
5. 读取相关 contracts、summaries、reviews、integration reports、merge proposals 和 ledger events。
6. 执行任务。
7. 在 handoff 前更新受影响的 PGSA artifacts。
8. 如果共享假设改变，更新 contract 或创建 merge proposal。
9. 如果决策已被接受，追加 ledger event，或先提交 pending event 等待 review。

## 下一轮 Session 恢复

仓库本地状态只有在下一轮不需要重放聊天记录时才真正有用。因此每个
`pgsa/state/<session>.summary.md` 都应该保留一个短的 recovery snapshot：

- 当前 scope；
- last known good state；
- 仍然重要的失败命令或失败检查；
- touched files，包括已经检查过或部分修改过的文件；
- open risks、blockers 或未解决假设；
- 下一步建议动作。

这个 snapshot 不是聊天记录，也不是完整 transcript。它的目标是让下一个
Codex、Claude Code 或人工 reviewer 能够恢复工作、判断哪些检查必须重跑，
并避免重复执行已经失败的命令。

## 多 Session 注册

PGSA 是 registration-based 的。每个项目 session 都在 `pgsa/sessions.yaml` 中声明 role、ownership scope、produced artifacts、consumed artifacts、required reads、required updates、handoff targets 和 escalation policy。

示例 session：

```text
backend
  owns API contracts and backend summary

frontend_components
  consumes API contracts and owns UI review state

docs_security_integration
  reads contracts, summaries, reviews, merge proposals, integration state,
  and ledger before deciding readiness
```

这个注册信息告诉 Codex、Claude Code 或其他 coding-agent session：它拥有什么、必须检查什么、handoff 前必须更新什么。

## 冲突生命周期和 Ledger 边界

PGSA 不会静默自动合并冲突写入，也不是 PR merge agent。Git、PR、CI 和 code review 仍然负责代码 diff、文本冲突、实现审查和最终 merge。

PGSA 工作在更早的一层：记录跨 session 的项目语义状态，而这些语义漂移不一定会表现为 Git 冲突。

冲突生命周期：

```text
session 发现语义漂移
-> 创建或更新 merge_proposal
-> 记录 evidence、affected contracts、resolution options
-> producer / consumer / integration review
-> 更新可编辑的当前状态
-> 追加已接受 ledger event
```

边界：

| 层 | 文件 | 含义 |
| --- | --- | --- |
| 当前可编辑状态 | `sessions.yaml`, `contracts/`, `state/`, `merge_proposals/`, `reviews/`, `integration/` | 可编辑的当前项目状态：roles、assumptions、open conflicts、review state、integration readiness。 |
| 待接受历史 | `ledger/pending/*.json` | 并行 session 写入的 draft event records，尚未被接受。 |
| 已接受历史 | `ledger/coherence_ledger.jsonl` | append-only 的已接受 project-coherence events 和 decisions 时间线。 |

当一个 session 发现语义漂移，比如 contract 改了但 consumer 仍然使用旧假设，它应该创建或更新 `pgsa/merge_proposals/*.md`，写清 evidence、affected contracts、resolution options 和 decision owner。

只有在 review 或 integration 接受 resolution 后，才应该向 `pgsa/ledger/coherence_ledger.jsonl` 追加事件。ledger 应该引用可编辑 artifacts；它不应该变成 raw context、未接受结论或完整聊天记录的堆放处。

并行运行时，session 应先写 `pgsa/ledger/pending/*.json`。review/integration session 再把已接受事件提升到正式 coherence ledger。

## 为什么它不是 PR 自动化

PGSA 不替代 pull request。PR 仍然适合 review 代码 diff、运行 CI、讨论实现和 merge 变更。

PGSA 记录的是 agent session 在 PR 准备好之前就需要知道的 project-state：

- 哪个 session 拥有项目的哪一部分；
- 编辑前必须读取哪些 contracts 和 summaries；
- handoff 前必须更新哪些 artifacts；
- 哪些语义假设改变了，即使 Git 没有文本冲突；
- integration 为什么 ready 或 blocked。

相比单纯 PR review，PGSA 的主要优势是 semantic continuity。backend session 可以改变 API，代码仍然能编译，但 frontend session 还保留旧假设。Git 可能没有冲突，PR 也可能直到 late review 才暴露漂移。PGSA 把这种漂移记录为仓库本地项目状态，让下一个 agent 不依赖私有聊天记录。

## 快速开始

把 `pgsa-harness/` 作为普通文件夹复制到目标项目：

```text
target-project/
  pgsa-harness/
  pgsa/
  src/
  tests/
```

面向 agent 的协议入口是 `pgsa-harness/protocol/SKILL.md`。目标项目的持久协作状态放在 `pgsa/`。

可选初始化和校验可以直接从嵌入后的文件夹运行，不需要全局安装：

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

Python 被放在主路径之外。协议本体是文件。

## Codex 和 Claude Code 使用方式

对于 Codex，把 PGSA 指导写进目标仓库的 `AGENTS.md`。对于 Claude Code，把等价指导写进 `CLAUDE.md`。本仓库包含这两个文件作为示例。

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

多个 session 可以来自不同终端、不同 worktree 或不同 agent thread。给每个 session 一个独立 PGSA identity：

```bash
codex "Use PGSA session backend. Read AGENTS.md, pgsa-harness/protocol/SKILL.md, pgsa/sessions.yaml, and the backend must_read artifacts. Update backend must_update artifacts before handoff."

codex "Use PGSA session frontend_components. Read AGENTS.md, pgsa-harness/protocol/SKILL.md, pgsa/sessions.yaml, frontend_components must_read artifacts, and backend contract state. Update frontend must_update artifacts before handoff."

codex "Use PGSA session docs_security_integration. Read AGENTS.md, pgsa-harness/protocol/SKILL.md, all summaries, reviews, contracts, merge proposals, integration state, and ledger. Decide readiness and block integration if unresolved semantic drift remains."
```

Claude Code 可以用同样方式启动：`claude "Use PGSA session ..."`。

对于 Codex subagent workflow，建议让 parent session 作为 integrator，让 subagents 返回 PGSA-ready summaries，而不是让每个 subagent 都直接写所有 artifacts。

## 可选 Python 工具

可选 CLI 可以帮助用户初始化和校验 PGSA artifacts：

```bash
python3 -m pip install -e tools/python
pgsa --root examples/teamtask-projectboard validate
pgsa --root examples/teamtask-projectboard drift-report
pgsa --root /tmp/pgsa-demo init --force
```

不安装也可以运行：

```bash
PYTHONPATH=tools/python python3 -m pgsa_cli.main --root examples/teamtask-projectboard status
```

`--root` 可以放在 subcommand 前或后：

```bash
pgsa --root examples/teamtask-projectboard validate
pgsa validate --root examples/teamtask-projectboard
```

CLI 只是 helper automation。它不决定语义真相，不自动解决冲突，也不替代 agent 判断。

## v1.1 新增内容

v1.1 保持核心协议小而清晰，同时增加可选 project-state 层：

| Area | Files | 新增能力 |
| --- | --- | --- |
| Session registry | `pgsa/sessions.yaml` | 清晰的 session identity、ownership、`must_read`、`must_update`、handoff 和 escalation rules。 |
| Semantic conflicts | `pgsa/merge_proposals/` | 可审查的 assumption drift 记录，即使 Git 没有冲突。 |
| Verification planning | `pgsa/gates/`, `pgsa/scenarios/` | 描述 integration 前应该具备哪些 evidence 的 verification blueprints 和 scenario tests。 |
| Review routing | `pgsa/reviews/` | risk-aware review-routing artifacts。 |
| Runtime evidence | `pgsa/runtime/`, `pgsa/evidence/` | 外部 runtime/security 工具记录；不声明 PGSA 自己执行 runtime policy。 |
| Capability contracts | `pgsa/runtime/` | session 或 tool 的 capability 与 approval expectations。 |
| Signed skills | `pgsa/skills/` | 可选 skill provenance、digest 和 trust metadata。 |
| Factory-style planning | `pgsa/factory/` | task DAG 和 decomposition plans；不是 autonomous factory 或 hosted orchestrator。 |
| Cognitive audit notes | `pgsa/audits/` | hypothesis-only research notes；不是模型可解释性证据本身。 |

所有 advanced packs 都是可选的。它们是仓库本地 artifact shapes，不是 services、daemons、CI、sandboxing、merge automation 或 security enforcement。

## 分层

Advanced packs 被组织成可选层，使 PGSA 保持 project-state protocol 的定位：

| Layer | Status | Purpose |
| --- | --- | --- |
| Core protocol | Required, stable | Project contracts、sessions、state、reviews、integration、ledger 和 merge proposals。 |
| Advanced packs | Optional, draft | Verification、scenario、review-routing、runtime evidence、signed skills 和 factory-style planning artifacts。 |
| Runtime adapters | Specs only | 外部工具可能提供 runtime/security evidence 的接口。 |
| Research notes | Hypothesis only | Cognitive audit notes 和相关观察；不能强于 tests、runtime evidence、contracts 或 review decisions。 |

Advanced schemas 描述 artifact shapes 和 references。它们不会让 PGSA 自己执行 runtime policy。

## 示例

`examples/teamtask-projectboard/` 包含一套完整 PGSA artifact 层。想理解文件模型，先看这里，不需要先读 Python 代码。

## 边界

PGSA 不替代 PR、worktree、测试、code review、CI、security tooling、sandboxing 或 integration agent。它增加的是仓库本地项目状态层，让跨 session 的共享假设可见、可恢复。

PGSA Harness Core v1.1 是本地协议版本。Advanced packs 是可选项目状态文件，不是强制服务。当前证据只是本地 architecture-protocol 和 embedded-example evidence。它不是 Codex、Claude Code、Grok、OpenAI、Anthropic 或任何托管产品的 benchmark。

## License

Apache License 2.0. See `LICENSE`.
