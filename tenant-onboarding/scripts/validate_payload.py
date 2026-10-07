"""Local contract check for tenant payloads. Mirrors convex/validate.ts.

Reads one JSON file, prints problems to stderr, exits 0 when valid.
Importable: from validate_payload import validate(doc) -> list[str].
stdlib only.
"""

import json
import re
import sys

TENANT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
TEMPLATE_RE = re.compile(r"^template-\d+$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
URL_RE = re.compile(r"^(https?://|/|#)")

MAX_PRODUCTS = 500
MAX_TESTIMONIALS = 200
MAX_INSTAGRAM = 100

REQUIRED_STR = ["tenantId", "businessName", "tagline", "description", "heroImage"]


def _url(value, what, problems):
    if value is None or value == "":
        return
    if not isinstance(value, str) or not URL_RE.match(value):
        problems.append(f"bad {what} {value!r}: use https://, /, #, or empty")


def validate(doc):
    """Return a list of problem strings. Empty means valid."""
    problems = []
    if not isinstance(doc, dict):
        return ["payload must be a JSON object"]

    for key in REQUIRED_STR:
        if not isinstance(doc.get(key), str) or not doc[key]:
            problems.append(f"missing or empty required string: {key}")
    if "tenantId" in doc and isinstance(doc["tenantId"], str):
        if not TENANT_ID_RE.match(doc["tenantId"]):
            problems.append(
                f"bad tenantId {doc['tenantId']!r}: 1-64 lowercase, digits, hyphens"
            )
    tid = doc.get("templateId")
    if not isinstance(tid, str) or not TEMPLATE_RE.match(tid):
        problems.append(f"bad templateId {tid!r}: use template-N shape")
    inc = doc.get("includedTemplates")
    if inc is not None:
        if not isinstance(inc, list) or not 1 <= len(inc) <= 5:
            problems.append("includedTemplates must hold 1 to 5 items")
        else:
            for t in inc:
                if not isinstance(t, str) or not TEMPLATE_RE.match(t):
                    problems.append(f"bad includedTemplates entry {t!r}")

    theme = doc.get("theme")
    if not isinstance(theme, dict):
        problems.append("missing required object: theme")
    else:
        for key in ("primaryColor", "secondaryColor"):
            val = theme.get(key)
            if not isinstance(val, str) or not COLOR_RE.match(val):
                problems.append(f"bad {key} {val!r}: use #rrggbb")

    contact = doc.get("contact")
    if not isinstance(contact, dict):
        problems.append("missing required object: contact")
    else:
        for key in ("whatsapp", "address"):
            if not isinstance(contact.get(key), str) or not contact[key]:
                problems.append(f"missing or empty contact.{key}")
        _url(contact.get("gmapsUrl"), "contact.gmapsUrl", problems)
        outlets = contact.get("outlets")
        if outlets is not None:
            if not isinstance(outlets, list):
                problems.append("contact.outlets must be an array")
            else:
                for o in outlets:
                    if not isinstance(o, dict) or not all(
                        isinstance(o.get(k), str) and o[k] for k in ("id", "name", "address")
                    ):
                        problems.append(f"bad outlet entry {o!r}: need id, name, address")
                    _url(o.get("gmapsUrl") if isinstance(o, dict) else None,
                          "outlet gmapsUrl", problems)

    features = doc.get("features")
    if not isinstance(features, dict):
        problems.append("missing required object: features")
    else:
        for key in ("enableCart", "enableSearch"):
            if not isinstance(features.get(key), bool):
                problems.append(f"features.{key} must be boolean")

    _url(doc.get("heroImage"), "heroImage", problems)
    _url(doc.get("cta", {}).get("link") if isinstance(doc.get("cta"), dict) else None,
         "cta.link", problems)

    products = doc.get("products")
    if not isinstance(products, list):
        problems.append("missing required array: products")
    else:
        if len(products) > MAX_PRODUCTS:
            problems.append(f"too many products (max {MAX_PRODUCTS})")
        for p in products:
            if not isinstance(p, dict) or not all(
                k in p for k in ("id", "name", "description", "price", "category")
            ):
                problems.append(f"bad product entry {p!r}: need id, name, description, price, category")
                continue
            if not isinstance(p["price"], (int, float)) or isinstance(p["price"], bool):
                problems.append(f"bad product {p.get('id')!r} price: must be a number")
            _url(p.get("image"), f"product {p.get('id')!r} image", problems)
            _url(p.get("link"), f"product {p.get('id')!r} link", problems)

    testimonials = doc.get("testimonials")
    if not isinstance(testimonials, list):
        problems.append("missing required array: testimonials")
    elif len(testimonials) > MAX_TESTIMONIALS:
        problems.append(f"too many testimonials (max {MAX_TESTIMONIALS})")

    insta = doc.get("instagramImages")
    if insta is not None:
        if not isinstance(insta, list) or len(insta) > MAX_INSTAGRAM:
            problems.append(f"instagramImages must be an array of max {MAX_INSTAGRAM}")
        else:
            for u in insta:
                _url(u, "instagram image", problems)

    return problems


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("usage: validate_payload.py <payload.json>", file=sys.stderr)
        print("exit 0 valid, 1 invalid. Problems go to stderr.", file=sys.stderr)
        return 0 if len(argv) == 2 else 1
    try:
        with open(argv[1], encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read payload: {e}", file=sys.stderr)
        return 1
    problems = validate(doc)
    for p in problems:
        print(p, file=sys.stderr)
    if not problems:
        print("payload valid", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
