# Changelog

## v1.0.0 (2026-10-07)

- Initial release. Onboard, manage, clone, delete tenant rows via the edge API.
- Contract: tenantId slug, template-N ids, theme `#rrggbb`, caps
  products 500, testimonials 200, instagramImages 100, edge body 512KB.
- Scripts: `validate_payload.py`, `tenant.py` (validate/get/upsert/delete,
  `--dry-run`, exit codes 0/1/2/3).
