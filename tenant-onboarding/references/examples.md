# Examples

## Full valid payload

Save as a file, then `validate_payload.py` it before any write.

```json
{
  "tenantId": "kopi-sore",
  "templateId": "template-2",
  "includedTemplates": ["template-2"],
  "businessName": "Kopi Sore",
  "tagline": "Ngopi santai tiap sore",
  "description": "Kedai kopi rumahan dengan biji pilihan petani lokal.",
  "theme": {
    "primaryColor": "#6F4E37",
    "secondaryColor": "#F5EFE6",
    "fontFamily": "Inter"
  },
  "contact": {
    "whatsapp": "6281234567890",
    "address": "Jl. Sore No. 8, Bandung",
    "gmapsUrl": "https://maps.google.com/?q=Kopi+Sore",
    "instagram": "kopi.sore",
    "openHours": "Mon-Sat 09:00-21:00"
  },
  "features": { "enableCart": true, "enableSearch": true },
  "heroImage": "/images/hero.jpg",
  "products": [
    {
      "id": "espresso",
      "name": "Espresso",
      "description": "Single origin arabika, diseduh pekat.",
      "price": 18000,
      "category": "Minuman",
      "image": "/images/espresso.jpg"
    },
    {
      "id": "kopi-susu",
      "name": "Kopi Susu Sore",
      "description": "Espresso, susu segar, gula aren.",
      "price": 22000,
      "category": "Minuman"
    }
  ],
  "testimonials": [
    {
      "id": "t1",
      "customerName": "Sinta",
      "comment": "Kopinya konsisten enak.",
      "rating": 5
    }
  ],
  "cta": { "text": "Pesan via WhatsApp" },
  "footer": { "copyrightText": "Kopi Sore 2026" },
  "isDraft": true
}
```

Notes: `isDraft: true` keeps a new tenant out of the way until Peek confirms
it. Drop `includedTemplates` only for legacy tenants. Prices are bare numbers.

## Manage edit example

User says: change Espresso price to 20000. Agent runs `get`, edits only
`products[espresso].price`, then spine: validate, dry-run, confirm, upsert,
read-back. Everything else stays byte-identical.
