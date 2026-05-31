# PGSA Harness Core

PGSA Harness Core 是一个 agent-first 的仓库本地项目一致性协议。v1.1 增加可选 advanced capability packs，同时保持核心协议仍是文件化、可嵌入、轻量的。

它不是 Python 框架，也不在模型内部运行。它存在于代码仓库中，用一组
Markdown、JSON、YAML 和 JSONL 文件，让 coding agent 可以读取、更新、
diff、审查，并在多个 session 之间交接项目状态。

## PGSA 解决什么

coding agent 可以完成局部任务，但项目整体仍然漂移。backend session 改了
API，frontend session 可能还保留旧假设；docs 可能描述旧行为；局部检查通过，
但项目已经对不上。

PGSA 把这些共享假设写进仓库：

```text
agent 读取 PGSA artifacts
-> agent 执行任务
-> agent 更新 contract、summary、review、integration 或 ledger
-> 下一个 agent 从可检查的项目状态继续
```

交流媒介是仓库，不是聊天记录。

## 核心文件

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

agent 的核心流程是：

1. 读取 `pgsa/project.yaml`。
2. 读取 `pgsa/sessions.yaml`。
3. 确认当前 session，并检查它的 `role`、`produces`、`consumes`、
   `must_read`、`must_update` 和 `handoff_to`。
4. 读取 `pgsa/harness/<session>.md`。
5. 读取相关 contracts、summaries、reviews、integration reports、merge proposals 和 ledger events。
6. 执行任务。
7. 在交接前更新受影响的 PGSA artifacts。
8. 如果共享假设改变，更新 contract 或创建 merge proposal。

## 仓库结构

```text
protocol/   面向 agent 的 PGSA 协议、模板、schema、规则和 role
examples/   带完整 pgsa/ artifact 层的小示例项目
tools/      可选用户工具；不是协议本体
```

Python 被放在主路径之外。协议本体是文件。

## 嵌入式使用

把 `pgsa-harness/` 作为普通文件夹复制到任意目标项目：

```text
target-project/
  pgsa-harness/
  pgsa/
  src/
  tests/
```

面向 agent 的协议入口是 `pgsa-harness/protocol/SKILL.md`。目标项目的持久协作
状态放在 `pgsa/`。

可选初始化和校验可以直接从嵌入后的文件夹运行，不需要全局安装：

```bash
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --force
# 可选 advanced capability artifacts：
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . init --advanced --force
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . validate
PYTHONPATH=pgsa-harness/tools/python python3 -m pgsa_cli.main --root . export-context --session backend
```

agent 通过读取和更新 `pgsa/` artifacts 协作。嵌入的 `pgsa-harness/` 文件夹只承担
协议和可选 helper package 的职责。

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

CLI 只是 helper automation。它不决定语义真相，不自动解决冲突，也不替代 agent 判断。

## 示例

`examples/teamtask-projectboard/` 包含一套完整 PGSA artifact 层。想理解文件模型，
先看这里，不需要先读 Python 代码。

## 协作模型

PGSA 通过仓库本地 artifacts 对接多个 agent：

- sessions 注册职责、依赖和 handoff 目标；
- contracts 定义 producer/consumer 边界；
- merge proposals 记录语义冲突；
- review 和 integration artifacts 接受或阻断项目状态；
- ledger 记录决策。

## 边界

PGSA 不替代 PR、worktree、测试、code review 或 integration agent。它增加的是
仓库本地项目状态层，让跨 session 的共享假设可见、可恢复。

PGSA Harness Core v1.1 是本地协议版本。Advanced packs 是可选项目状态文件，不是强制服务。当前证据只是本地 architecture-protocol
和 embedded-example evidence。它不是 Codex、Claude Code、Grok、OpenAI、
Anthropic 或任何托管产品的 benchmark。

## License

Apache License 2.0. See `LICENSE`.
