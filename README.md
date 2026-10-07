# web-factory-tenant-skill

Public agent skill: onboard new tenants and edit existing tenant data in
Web Factory admin via the edge API. Pairs with any repo; the agent running
it only needs this folder plus two env vars.

Contract version: v1.0.0 (2026-10-07). Matches the factory `tenantFields`
schema of the same date. If writes start failing with 422 on payloads that
used to work, check CHANGELOG for a contract bump first.

## Layout

```
tenant-onboarding/
  SKILL.md                  # workflow the agent follows
  references/data-model.md  # the valid JSON payload contract
  references/branches.md    # onboard, manage, clone, delete details
  references/examples.md    # full valid payload example
  scripts/validate_payload.py  # local contract check, stdlib only
  scripts/tenant.py            # validate/get/upsert/delete CLI, stdlib only
```

## Setup

1. Wire this folder into the agent repo, one of:
   - Submodule (recommended):
     `git submodule add <this-repo-url> .opencode/skills/tenant-onboarding`
   - Manual: clone beside your work and point the agent at the path.
2. Set env vars on the machine running the agent (never commit them):
   - `FACTORY_API_URL`: edge API base URL (ask the factory admin).
   - `FACTORY_ADMIN_SECRET`: admin secret (ask the factory admin over a
     secure channel, rotate on the worker if it ever leaks).
3. Invoke: `skill({ name: "tenant-onboarding" })`, or tell the agent to
   onboard or edit a tenant.

## Notes

- This repo holds procedure only. No secrets, no customer data.
- Writes preview with `--dry-run` and need user confirmation; delete needs
  `--force`. Peek, generate, and promote stay in factory admin.
- Python 3 stdlib only, no installs. Windows and Unix shells.
