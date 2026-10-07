# Tenant data model

Contract version: v1.0.0 (2026-10-07). Mirrored in the factory dev repo;
when the Convex tenantFields change, bump the version in both places.

Single source of truth for the JSON payload the skill builds. Mirrors
`convex/convex/schema.ts` (tenantFields), `workers/api/src/schemas.ts`
(tenantDoc), and `convex/convex/validate.ts` (guards). If this file and those
three disagree, the code wins; update this file.

## Identity

- `tenantId`: string, required. Slug: 1 to 64 chars, lowercase letters, digits,
  hyphens, must start with a letter or digit (`^[a-z0-9][a-z0-9-]{0,63}$`).
  Interpolated into Pages project names and preview hostnames, so keep it
  URL-safe and stable. Never rename a live tenant; create a new id instead.
- `templateId`: string, required. Shape `template-N`. Must be a known id in the
  `templates` registry table (Convex enforces membership on write).
- `includedTemplates`: optional array of `template-N` strings, 1 to 5 items.
  The picker set the tenant may use. Omit for legacy behavior.

## Business profile

- `businessName`: string, required.
- `tagline`: string, required.
- `description`: string, required.

## theme (required object)

- `primaryColor`: `#rrggbb` hex, required. Lands in inline style, strictly validated.
- `secondaryColor`: `#rrggbb` hex, required.
- `fontFamily`: optional string.

## contact (required object)

- `whatsapp`: string, required (digits with country code, no `+`).
- `address`: string, required.
- `gmapsUrl`: optional. Empty or absolute `https://`, site path `/`, or `#`.
  No `javascript:`, `data:`, or bare words. Same URL rule applies to every
  URL field below.
- `instagram`: optional string (handle or URL).
- `email`: optional string.
- `openHours`: optional string (free text, e.g. `Mon-Sat 09:00-21:00`).
- `outlets`: optional array of `{id, name, address, gmapsUrl?}`.

## features (required object)

- `enableCart`: boolean, required.
- `enableSearch`: boolean, required.

## Content

- `heroImage`: string, required. URL rule applies (absolute https, `/` path,
  or `#`). Empty string allowed only when the template tolerates no hero.
- `products`: required array of
  `{id, name, description, price, category, image?, link?}`. `price` is a
  number (no currency symbols). `image` and `link` follow the URL rule.
  Max 500 items.
- `testimonials`: required array of `{id, customerName, comment, rating}`.
  `rating` is a number. Max 200 items. Empty array allowed.
- `instagramImages`: optional string array, URL rule each. Max 100 items.
- `cta`: optional `{text, link?}`. `link` follows the URL rule.
- `footer`: optional `{shortDescription?, copyrightText?}`.
- `isDraft`: optional boolean. Marks the row as draft content.

## Caps summary

products 500, testimonials 200, instagramImages 100, body cap 512KB at the edge.

## Minimal viable payload

Identity, business profile, theme, contact (whatsapp + address), features,
heroImage, one product, empty testimonials. See `references/examples.md` for a
full valid payload.
