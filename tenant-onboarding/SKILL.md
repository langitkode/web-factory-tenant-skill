---
name: tenant-onboarding
description: Onboard new tenants and edit existing tenant data in factory admin via the edge API. Use when adding a tenant, updating products, theme, or contact info, cloning a tenant, or deleting one.
license: MIT
compatibility: opencode, python3 stdlib only, Windows and Unix shells
metadata:
  audience: maintainers
  workflow: factory-admin
---

## What I do

Write tenant rows to factory admin through the edge API (`POST /api/tenants` upsert,
`DELETE /api/tenants?id=` remove). Two branches: onboard a new tenant, or manage
an existing one. Clone is manage with a new id.

## Workflow

1. Collect the tenant data from wherever the user has it (chat answers, document,
   existing tenant to clone). Flexible source, fixed contract: the payload must
   match `references/data-model.md`. Done when every required field has a value.
2. Write the payload to a temp JSON file. Never inline large JSON in commands.
3. Run local validation first, always:
   `py .opencode/skills/tenant-onboarding/scripts/validate_payload.py <file>`
   Done when exit 0. Fix and retry on nonzero, max 2 rounds, then ask the user.
4. Preview the write:
   `py .opencode/skills/tenant-onboarding/scripts/tenant.py upsert --file <file> --dry-run`
   Done when the preview shows the exact diff the user expects.
5. Confirm with the user, then run without `--dry-run`. Done when the API
   returns `{"ok": true}`.
6. Verify with a read-back:
   `py .opencode/skills/tenant-onboarding/scripts/tenant.py get --id <tenantId>`
   Done when the returned row matches what was sent.

## Branches

Onboard, manage, clone, and delete each have extra steps. Read
`references/branches.md` when the run needs one of them. The workflow above is
the spine every branch follows.

## Rules

- Credentials come from env only: `FACTORY_API_URL` (default
  `https://web-factory-api.langitkode1001.workers.dev`) and
  `FACTORY_ADMIN_SECRET` (required for every call, reads included). Never print
  them, never write them to disk, never paste them into chat.
- Never invent `UMKMConfig` fields. Unknown keys are rejected; check
  `references/data-model.md` first.
- Manage branch is read-modify-write: `get` first, merge the change, then
  upsert. Never blind-overwrite a live tenant.
- Delete requires explicit user confirmation plus `--force`. It removes the
  data row; repo cleanup is the separate delete-site op in factory admin.
- Peek, generate, and promote are NOT this skill. After a successful upsert,
  point at factory admin for preview and deploy.
- Script exit codes: 0 ok, 1 invalid payload or args, 2 not found, 3 auth or
  network failure. Never treat nonzero as success.
