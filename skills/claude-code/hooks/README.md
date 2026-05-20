# Claude Code Hook Examples

These are documentation-level examples for Claude Code-style lifecycle hooks.

They are not enabled automatically and do not modify Claude Code internals.

Recommended mapping:

- session start: read `pgsa/harness/<session>.md`;
- post tool use: check contract and summary impact;
- stop: run validation and drift reporting.

