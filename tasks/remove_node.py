#!/usr/bin/env python3

import sys
import json
import ssl
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def fail(message, exit_code=1):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(exit_code)


def success(message):
    print(json.dumps({"status": "success", "message": message}))
    sys.exit(0)


def api_put(url, headers, data, retries=1):
    ctx = ssl._create_unverified_context()
    payload = json.dumps(data).encode("utf-8")
    attempt = 0

    while attempt <= retries:
        req = Request(url, data=payload, method="PUT", headers=headers)

        try:
            with urlopen(req, context=ctx) as resp:
                code = resp.getcode()
                body = resp.read().decode("utf-8")

                if code in (200, 204):
                    return True, body

                if attempt < retries:
                    attempt += 1
                    time.sleep(1)
                    continue

                return False, f"HTTP {code}: {body}"

        except HTTPError as e:
            body = e.read().decode("utf-8")
            if attempt < retries:
                attempt += 1
                time.sleep(1)
                continue
            return False, f"HTTP {e.code}: {body}"

        except URLError as e:
            if attempt < retries:
                attempt += 1
                time.sleep(1)
                continue
            return False, f"URL Error: {e.reason}"

        except Exception as e:
            if attempt < retries:
                attempt += 1
                time.sleep(1)
                continue
            return False, f"Exception: {e}"


def main():
    try:
        params = json.load(sys.stdin)
    except Exception as e:
        fail(f"Failed to parse input: {e}")

    certname = params.get("certname")
    token = params.get("token")

    if not certname:
        fail("Missing required parameter: certname")
    if not token:
        fail("Missing required parameter: token")

    clean_url = "https://pe.caffeine.lan:8140/puppet-ca/v1/clean"

    headers = {
        "X-Authentication": token,
        "Content-Type": "application/json"
    }

    body = {
        "certnames": [certname]
    }

    ok, msg = api_put(clean_url, headers, body, retries=1)
    if not ok:
        fail(f"Failed to clean certificate for '{certname}': {msg}")

    success(f"Certificate for '{certname}' successfully cleaned.")


if __name__ == "__main__":
    main()
