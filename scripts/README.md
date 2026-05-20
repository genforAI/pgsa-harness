# PGSA Scripts

This folder contains small release and local-adoption helpers.

- `install_pgsa_harness.py`: initialize a target repository with `pgsa/`
  artifacts.
- `validate_release.py`: scan the release tree for common hygiene issues.
- `package_release.py`: build a GitHub-ready zip whose root is
  `pgsa-harness/`.
- `smoke_test.sh`: run a local CLI smoke test against a temporary project.

These scripts are helpers. The protocol remains the repo-local `pgsa/` artifact
layer.

