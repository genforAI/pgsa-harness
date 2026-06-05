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

PGSA 是放进你已有项目仓库里的协议层，不是替代你的主项目目录。你的真实项目代码仍然放在原来的位置，比如 `src/`、`app/`、`packages/`、`docs/`、`tests/`。PGSA 只是在旁边增加两个目录：

```text
your-project/
  pgsa-harness/        # 复制进来的 PGSA 协议和可选工具
  pgsa/                # 当前项目自己的 agent coordination state
  src/                 # 你的真实产品代码，保持原样
  tests/               # 你的现有测试
  docs/                # 你的现有文档
```

下面的 `pgsa/` 指的是“你的项目仓库里的 `pgsa/`”，不是 `pgsa-harness` 仓库本身。

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

  # optional advanced artifacts, 由 init --advanced 创建
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

Advanced mode 需要显式启用：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --advanced --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate --strict-advanced
```

这些 optional folders 不是 import 系统本身，而是内置的高级项目状态分类：

| Advanced folder | 用途 |
| --- | --- |
| `gates/` | verification blueprints 和 readiness gates。 |
| `runtime/` | runtime profiles 和 capability contracts。 |
| `skills/` | 已接受的 skill provenance 或 signed skill manifests。 |
| `evidence/` | 来自外部 runtime / verification tools 的证据记录。 |
| `factory/` | factory-style task DAGs 和 planning artifacts。 |
| `scenarios/` | scenario tests 和 expected evidence。 |
| `audits/` | hypothesis-only cognitive audit notes。 |

Import workflow 是另一条路径。外部 repositories、skill packs、prompt packs 或 protocol folders 先进入 `pgsa/imports/`；只有审查通过后，才把选中的 metadata 或 provenance 提升到 `pgsa/skills/` 等 advanced folders。

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
  --must-read imports/index.json,imports/sources/ \
  --must-update state/research_import.summary.md,ledger/pending/ \
  --handoff-to docs_security_integration \
  --self-registered
```

### Session Agent 文件夹

真正的注册表仍然是 `pgsa/sessions.yaml`。Session agent 文件夹只是给一个新开的
Codex、Claude Code、SDK 或外部 agent session 使用的启动包装器：它给这个 session
一个自己的 `AGENTS.md` / `SKILL.md`，同时指回同一份 PGSA root、harness root、
required reads、required updates 和 accepted skill manifest。

默认内嵌布局：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . session-agent create backend
```

这会写入：

```text
pgsa/session_agents/backend/
  AGENTS.md
  SKILL.md
  PGSA_SESSION.json
```

如果每个长时间运行的 session 有自己的 sibling 文件夹或 worktree：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root target-project   session-agent create backend   --out ../agent-sessions/backend   --harness-root ../pgsa-harness
```

生成的 `PGSA_SESSION.json` 会保存指向 `pgsa_root`、`harness_root`、
`sessions.yaml`、`harness/<session>.md`、`state/<session>.summary.md` 和
`skills/signed_skill_manifest.yaml` 的相对路径。

已接受的外部 skills 通过 `pgsa/skills/signed_skill_manifest.yaml` 被多个 session
复用：session 只能使用 `applies_to` 包含自己 session id 或 `*` 的条目。Raw
`pgsa/imports/sources/<source_id>/` 仍然是 review material，不是 active guidance；
除非当前 session 是 `external_import_review`，或者这个 source 被显式写进该
session 的 `must_read`。

## Session Handoff Snapshot

这里的 recovery 不是回滚代码，也不是恢复文件系统快照，而是让下一轮 agent 不用重放聊天记录也能恢复工作上下文。

每个 `pgsa/state/<session>.summary.md` 都应该保留一个简短的 handoff snapshot：

- current scope；
- last known good state；
- still important failed commands or failed checks；
- touched files；
- open risks、blockers 或 unresolved assumptions；
- recommended next action。

这不是完整 transcript。它的目标是让下一个 Codex / Claude Code / human reviewer 快速判断当前 scope、哪些检查需要重跑、哪些文件被碰过、还有哪些 risk，不再依赖私有聊天记录。

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
-> pgsa import promote <source_id> --accept-import --applies-to <sessions>
-> accepted provenance in pgsa/skills/signed_skill_manifest.yaml
-> optional promotion into contracts, roles, capabilities, or ledger
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
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import promote external_pack --accept-import --applies-to backend,frontend_components
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . import stats
```

`process-inbox` 会索引 inbox item，复制到 `pgsa/imports/sources/<source_id>/`，写入 `pgsa/imports/index.json`，并默认清理已处理的 inbox item。只有调试时才建议传 `--keep`。

`import review <source_id>` 会扫描复制后的来源，识别 `SKILL.md`、README 和 schema 文件，把 import 记录更新为 `reviewed`，并把审查结果写入 `harness/<session>.md`、`state/<session>.summary.md` 和 `ledger/pending/`。这仍然不会自动安装或信任外部内容。

`import promote <source_id> --accept-import` 是 accepted provenance 步骤。它会把已审查 skill metadata 写入 `pgsa/skills/signed_skill_manifest.yaml`，并把 import 标记为 accepted。它仍然不会安装全局 skills、执行外部代码，也不会把 raw external instructions 直接复制进随仓库发布的 `protocol/`。

使用 `--applies-to` 可以声明这份 accepted provenance 后续允许哪些 PGSA sessions 使用。例如同一个外部 package 可以被批准给 `backend`、`frontend_components` 或 `docs_security_integration` 使用，但不会获得整个项目的全局权威。

专门的 import-review 配置：

- `pgsa/sessions.yaml` 默认包含 `external_import_review`。
- `pgsa/harness/external_import_review.md` 会在 init 时生成，作为这个 session 的操作文件。
- `protocol/imports/external_import_review_agent.md` 包含启动 prompt 和逐步 review workflow。
- `protocol/roles/examples/external-import-review.role.yaml` 是需要更强 role 文件时可复用的示例。

要运行真实外部导入验证：

```bash
python3 tools/scripts/verify_external_skill_imports.py
```

这个脚本会把公共外部 skills clone 到临时项目，放入 `pgsa/imports/inbox/`，运行 `process-inbox`，对每个来源运行 `import review`，确认 inbox 已清理、review artifacts 和 pending ledger events 已生成，并运行 `pgsa validate`。

## Codex 和 Claude Code 使用方式

对 Codex，把 PGSA 指导写进你的项目仓库 `AGENTS.md`。对 Claude Code，把等价指导写进 `CLAUDE.md`。本仓库包含这两个文件作为示例。

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

## 原生 Codex 和 Codex SDK 的区别

默认路径是原生 Codex / Claude Code：在你的项目仓库里打开 agent，给它一个 PGSA session identity，并要求它读取 `AGENTS.md` 或 `CLAUDE.md`、`pgsa-harness/protocol/SKILL.md`、`pgsa/sessions.yaml` 和当前 session 的 `must_read` artifacts。它完成工作后更新自己的 `must_update` artifacts。

SDK 路径只在你需要“可重复、程序化启动多个已注册 session”时使用。SDK 不会比文件协议产生更强的记忆；它只是读取同一份 `pgsa/sessions.yaml`，自动构造 prompts 并启动 Codex SDK threads。

## Optional Codex SDK Demo

`sdk/` 文件夹面向想使用 Codex SDK 的用户，展示如何用 SDK 启动多个已注册 PGSA session。它是 userland demo，不是 PGSA 核心路径，也不代表 OpenAI/Codex 官方集成或背书。

SDK 参考文档：<https://developers.openai.com/codex/sdk#python-library>

PGSA 支持两种 Codex 使用模式：

| 模式 | 工作方式 | 适合场景 | 取舍 |
| --- | --- | --- | --- |
| 原生 Codex / 不使用 SDK | 用户在项目仓库里手动启动 Codex，并给出 PGSA session prompt。 | 日常交互式工作、一次性 session、人工控制和最高透明度。 | 用户需要自己启动和协调每个 session。 |
| 使用 Codex SDK | `sdk/codex_pgsa_runner.py` 读取 `pgsa/sessions.yaml`，为每个 session 构造 PGSA-aware prompt，并在 `--root` 指向的项目仓库里启动 Codex SDK threads。 | 程序化编排、重复的长时间检查、CI/internal tools、稳定启动多个已注册 sessions。 | 需要可选 Codex SDK；仍然是 userland orchestration，不绕过 Codex sandbox 或 approvals。 |

SDK dry-run：

```bash
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json --dry-run
```

SDK 使用流程：

1. 在你的项目仓库初始化 PGSA。
2. 检查 `pgsa/sessions.yaml`，确认每个 session 有 role、`must_read` 和 `must_update`。
3. 先运行 SDK dry-run，查看它将要启动的 prompts。
4. 单独安装官方 SDK。
5. 用 `--start-only` 创建 threads，或直接运行配置里的 session prompts。

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --force
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json --dry-run
pip install openai-codex
python3 sdk/codex_pgsa_runner.py --start-only
python3 sdk/codex_pgsa_runner.py --root . --config sdk/codex-runner.config.example.json
```

## 快速开始

把 `pgsa-harness/` 作为普通文件夹复制到你已有的项目仓库：

```text
your-project/
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
| 外部材料主要靠约定引用。 | 外部 packages 先复制、索引、审查、总结；通过 `import promote` 写入 accepted skill provenance 后，才允许进入项目状态。 |
| signed skill provenance 是 advanced artifact shape。 | 已接受 import metadata 可以提升到 `pgsa/skills/`；未审查 raw external content 不进入随仓库发布的 `protocol/`。 |
| 已有 recovery 和 conflict artifacts。 | README 明确 daily-use 路径：recovery snapshots、`must_read` / `must_update`、semantic conflicts、ledger boundaries、SDK vs non-SDK 使用，以及 import-package review。 |

## 边界

PGSA 不替代 PR、worktree、测试、code review、CI、security tooling、sandboxing 或 integration agent。它增加的是仓库本地项目状态层，让跨 session 的共享假设可见、可恢复。

PGSA Harness Core v1.2 是本地协议版本。Advanced packs 和 import package management 都是可选项目状态文件和工作流，不是强制服务。当前证据只是本地 architecture-protocol 和 embedded-example evidence，不是 Codex、Claude Code、Grok、OpenAI、Anthropic 或任何托管产品的 benchmark。

## License

Apache License 2.0. See `LICENSE`.
