# Branches

Extra steps per branch. Every branch still follows the SKILL.md spine:
collect, file, validate, dry-run, confirm, upsert, read-back.

## Onboard (new tenant)

1. Pick a `tenantId` slug with the user. Check it does not exist:
   `tenant.py get --id <slug>` should exit 2 (not found).
2. Pick `templateId` from the live registry (factory admin Templates tab or
   `templates:ids`). Never guess; an unknown id fails at Convex with 422.
3. Fill the payload from `references/data-model.md`. Sensible defaults allowed
   only for optional fields; required fields need real values.
4. Follow the spine. After read-back, offer next steps in factory admin:
   Peek for preview, Generate for the preview site, Promote for production.

## Manage (edit existing tenant)

1. Read first: `tenant.py get --id <tenantId> --output current.json`.
   Exit 2 means the id is wrong; stop and ask.
2. Merge the requested change into `current.json`. Touch only the fields the
   user asked about. Keep ids of products, testimonials, and outlets stable
   unless the user asked to add or remove entries.
3. Validate, dry-run, confirm, upsert, read-back per the spine. The dry-run
   step matters most here: show the user what changed before writing.

## Clone (existing tenant as template)

1. `get` the source tenant to `clone.json`.
2. Replace identity fields: new `tenantId` slug (verify exit 2 first),
   `businessName`, contact details. Review theme and content with the user;
   defaults carry over anything not explicitly changed.
3. Treat the result as onboard from step 4 of that branch.

## Delete

1. Confirm the exact `tenantId` with the user. State what delete does: removes
   the tenant data row. Preview/prod repos are cleaned by the separate
   delete-site op in factory admin, not by this call.
2. Run `tenant.py delete --id <tenantId> --force`. The script refuses without
   `--force`. Done when the API returns `{"ok": true}`.
3. Verify: `get` the same id, expect exit 2.
