# Nono Runtime Adapter Spec

Purpose: translate Nono-style cage/profile/audit/capability events into PGSA runtime evidence.

Minimum event mapping:

- cage/profile start -> `runtime.session_started`
- file/network/command denial -> `runtime.capability_denied`
- capability request -> file under `pgsa/runtime/capability_requests/` plus evidence event
- approved grant -> `runtime.capability_granted`
- rollback point -> `runtime.rollback_snapshot`

PGSA consumes these as governance evidence; Nono remains the enforcement layer.
