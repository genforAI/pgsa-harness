# Level 3 Real Agent Benchmark

Level 3 requires actual external agent/tool execution.

Required evidence per run:

1. Real installed tool command and version.
2. Captured prompt and exact context sent to the tool.
3. Raw stdout/stderr or tool transcript.
4. Before/after diffs or artifact snapshots.
5. Test logs.
6. `pgsa validate` output where PGSA artifacts exist.
7. Timing metadata.
8. Run manifest per task.
9. Same fixed task schedule across conditions.
10. Explicit labeling of missing-transcript runs as `protocol run` or `dry-run`.

Product-level claims remain blocked until these artifacts exist.
