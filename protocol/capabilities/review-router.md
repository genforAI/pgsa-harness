# Review Router

Review Router assigns review strength based on contract impact, changed files, tests, runtime evidence, permission requests, and risk tier.

It helps avoid sending every agent change through the same review path. Low-risk
changes can be routed to lightweight review, while contract-breaking,
security-sensitive, or high-permission changes can require human or specialized
session review. PGSA records the routing decision; repository policy and
reviewers still enforce it.

Reference artifact: `pgsa/gates/review_router.yaml`.
