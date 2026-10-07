"""Edge API client for the tenant-onboarding skill. stdlib only.

Subcommands: validate, get, upsert, delete. Data to stdout (JSON),
diagnostics to stderr. Exit codes: 0 ok, 1 invalid payload or args,
2 not found, 3 auth or network failure.

Auth: Basic admin:<secret>. Both values from env only:
  FACTORY_API_URL (default https://web-factory-api.langitkode1001.workers.dev)
  FACTORY_ADMIN_SECRET (required for every call, reads included)
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from validate_payload import validate

DEFAULT_API_URL = "https://web-factory-api.langitkode1001.workers.dev"


def _client():
    base = os.environ.get("FACTORY_API_URL", DEFAULT_API_URL).rstrip("/")
    secret = os.environ.get("FACTORY_ADMIN_SECRET", "")
    if not secret:
        print("FACTORY_ADMIN_SECRET is not set", file=sys.stderr)
        sys.exit(3)
    token = base64.b64encode(f"admin:{secret}".encode()).decode()
    return base, {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def _request(method, path, body=None):
    base, headers = _client()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return 0, json.loads(res.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode() or "{}")
        except (ValueError, OSError):
            detail = {"error": f"HTTP {e.code}"}
        code = 2 if e.code == 404 else 3 if e.code in (401, 403) else 1
        return code, detail
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 3, {"error": f"network failure: {e}"}


def _load_payload(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read payload: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_validate(args):
    doc = _load_payload(args.file)
    problems = validate(doc)
    for p in problems:
        print(p, file=sys.stderr)
    if problems:
        sys.exit(1)
    print("payload valid", file=sys.stderr)


def cmd_get(args):
    code, out = _request("GET", "/api/tenants")
    if code != 0:
        print(json.dumps(out), file=sys.stderr)
        sys.exit(code)
    rows = out if isinstance(out, list) else []
    row = next((r for r in rows if r.get("tenantId") == args.id), None)
    if row is None:
        print(f"unknown tenant {args.id!r}", file=sys.stderr)
        sys.exit(2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(row, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(row, ensure_ascii=False, indent=2))


def cmd_upsert(args):
    doc = _load_payload(args.file)
    problems = validate(doc)
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "tenantId": doc.get("tenantId"),
                          "templateId": doc.get("templateId"),
                          "products": len(doc.get("products", []))}, indent=2))
        return
    code, out = _request("POST", "/api/tenants", doc)
    if code != 0:
        print(json.dumps(out), file=sys.stderr)
        sys.exit(code)
    print(json.dumps(out))


def cmd_delete(args):
    if not args.force:
        print("refusing: delete needs --force plus user confirmation", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "delete": args.id}, indent=2))
        return
    code, out = _request("DELETE", "/api/tenants?id=" + urllib.parse.quote(args.id))
    if code != 0:
        print(json.dumps(out), file=sys.stderr)
        sys.exit(code)
    print(json.dumps(out))


def main(argv=None):
    p = argparse.ArgumentParser(prog="tenant.py",
                                description="Tenant rows via the factory edge API.")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="local contract check only, no HTTP")
    v.add_argument("--file", required=True, help="payload JSON file")
    v.set_defaults(func=cmd_validate)

    g = sub.add_parser("get", help="read one tenant row")
    g.add_argument("--id", required=True, help="tenantId slug")
    g.add_argument("--output", help="write row to FILE instead of stdout")
    g.set_defaults(func=cmd_get)

    u = sub.add_parser("upsert", help="create or update a tenant row")
    u.add_argument("--file", required=True, help="payload JSON file")
    u.add_argument("--dry-run", action="store_true", help="validate and preview, no HTTP")
    u.set_defaults(func=cmd_upsert)

    d = sub.add_parser("delete", help="remove a tenant data row")
    d.add_argument("--id", required=True, help="tenantId slug")
    d.add_argument("--force", action="store_true", help="required for real delete")
    d.add_argument("--dry-run", action="store_true", help="preview, no HTTP")
    d.set_defaults(func=cmd_delete)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
