"""Read-only NovaComp deployment smoke test.

Usage:
  NOVACOMP_BASE_URL=https://novacomp.vercel.app python scripts/smoke_test.py

This checks only public, non-mutating endpoints. It never prints secrets and does
not write memory or enqueue tasks. Vercel SSO/deployment protection may block it.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin

BASE_URL = os.getenv("NOVACOMP_BASE_URL", "https://novacomp.vercel.app").rstrip("/")
TIMEOUT_SECONDS = 12


def get_json(path: str) -> tuple[int, object]:
    request = urllib.request.Request(
        urljoin(BASE_URL + "/", path.lstrip("/")),
        headers={"Accept": "application/json", "User-Agent": "NovaComp-SmokeTest/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(1_000_000).decode("utf-8")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as exc:
        # Do not print response bodies: proxies may include deployment details.
        return exc.code, {"error": "http_error"}
    except Exception as exc:
        return 0, {"error": type(exc).__name__}


def main() -> int:
    failures = 0
    status, root = get_json("/")
    root_ok = status == 200 and isinstance(root, dict) and root.get("service") == "NovaComp Continuity Kernel"
    print(f"root: {'PASS' if root_ok else 'FAIL'} (HTTP {status})")
    failures += not root_ok

    status, health = get_json("/api/health")
    health_ok = status == 200 and isinstance(health, dict) and health.get("service") == "novacomp-continuity-kernel"
    print(f"health: {'PASS' if health_ok else 'FAIL'} (HTTP {status})")
    failures += not health_ok
    if health_ok:
        print(f"database_configured: {bool(health.get('database_configured'))}")
        print(f"database_reachable: {bool(health.get('database_reachable'))}")
        print(f"memory_auth_configured: {bool(health.get('memory_auth_configured'))}")

    status, schema = get_json("/openapi.json")
    openapi_ok = status == 200 and isinstance(schema, dict) and isinstance(schema.get("paths"), dict)
    print(f"openapi: {'PASS' if openapi_ok else 'FAIL'} (HTTP {status})")
    failures += not openapi_ok
    if openapi_ok:
        print(f"documented_paths: {len(schema['paths'])}")

    print("mode: read-only; no writes or queue claims attempted")
    print("result:", "PASS" if failures == 0 else "FAIL")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
