# Vendor Outreach Note

Subject: PGSA Harness Core v0.1: repo-local project-coherence layer for coding-agent workflows

Hi,

I am building PGSA Harness Core, a repo-local project-coherence layer for coding-agent workflows.

The focus is not agent speed. It is project recoverability: contracts, session summaries, semantic merge proposals, review state, integration reports, and a coherence ledger that survive across sessions.

The current v0.1 package includes:

- a small Python CLI;
- repo-local artifact templates;
- validators and drift reporting;
- per-session harness Markdown files;
- an optional context export helper;
- a Codex workflow adapter scaffold;
- Claude Code, Grok Build, and generic CLI adapter notes;
- agent-readable commands, hooks, templates, rules, and skills;
- a lightweight PGSA artifact example and smoke tests;
- local generated git-worktree evidence.

In local generated git-worktree suites, PGSA-gated artifacts surfaced semantic contract drift as review / merge blockers while not over-blocking the included no-drift controls.

The boundary is important: this is not a Codex, Claude Code, Grok, OpenAI, Anthropic, or hosted product benchmark. I am not making product-performance claims. The next step would be a Level 3 evaluation with real tool transcripts, diffs, tests, versions, timing metadata, and a shared evaluator.

I am interested in feedback on whether this kind of repo-local project layer could integrate cleanly with coding-agent workflows, especially around session lifecycle, artifact capture, review gates, and final integration.

I would especially value feedback on three points:

1. Could repo-local project artifacts fit naturally into your coding-agent workflow?
2. Are skills, hooks, wrappers, or generic CLI adapters the right integration surface?
3. Is semantic contract drift a failure mode you see in multi-session agent use?

Best,
