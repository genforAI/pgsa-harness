# CLI Boundary

The CLI is optional helper automation, not the semantic authority.

PGSA's project truth lives in repo-local artifacts and in review/integration
synthesis performed by agents or humans.

## The CLI Can

- initialize PGSA artifact folders;
- check that required files exist;
- lint obvious schema or structure issues;
- export context;
- package context for agents;
- detect obvious missing artifacts;
- run mechanical validation;
- call an external agent command and capture transcript if configured by a
  downstream integration.

## The CLI Cannot

- decide semantic merge;
- authoritatively resolve project conflicts;
- generate final project synthesis without an agent or human review;
- prove maintainability;
- replace review or integration session agents.

## Drift Report Boundary

`pgsa drift-report` is a mechanical artifact/status report.

Authoritative project synthesis should be produced by review or integration
session agents using PGSA artifacts.

If a drift report says no mechanical issues are found, that does not prove the
project is semantically correct. It only means current validators did not detect
known artifact problems.

