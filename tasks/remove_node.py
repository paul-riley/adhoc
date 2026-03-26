#!/usr/bin/env python3
import json
import sys
import requests
import time

def fail(message, exit_code=1):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(exit_code)

def success(message):
    print(json.dumps({"status": "success", "message": message}))
    sys.exit(0)

def api_delete(url, headers, retries=1):
    """
    Perform a DELETE request with one retry on failure.
    Returns (success_bool, response_object)
    """
    attempt = 0
    while attempt <= retries:
        try:
            response = requests.delete(url, headers=headers, verify=False)
        except Exception as e:
            if attempt == retries:
                return False, f"Exception: {e}"
            attempt += 1
            time.sleep(1)
            continue

        if response.status_code in (200, 204):
            return True, response

        # If failed and retries remain, try again
        if attempt < retries:
            attempt += 1
            time.sleep(1)
            continue

        # Final failure
        return False, response

    # Should never reach here
    return False, "Unknown error"

def main():
    # Read parameters from STDIN
    try:
        params = json.load(sys.stdin)
    except Exception as e:
        fail(f"Failed to parse input parameters: {e}")

    certname = params.get("certname")
    token = params.get("token")

    if not certname:
        fail("Missing required parameter: certname")
    if not token:
        fail("Missing required parameter: token")

    # Puppet Server API endpoints
    base_url = "https://pe.caffeine.lan:8140"  # Adjust for your environment
    deactivate_url = f"{base_url}/puppet/v3/node/{certname}"
    purge_url = f"{base_url}/puppet-ca/v1/certificate_status/{certname}"

    headers = {
        "X-Authentication": token,
        "Content-Type": "application/json"
    }
    # Step 1: Deactivate node (with retry)
    ok, resp = api_delete(deactivate_url, headers, retries=1)
    if not ok:
        if isinstance(resp, str):
            fail(f"Failed to deactivate node '{certname}': {resp}")
        else:
            fail(f"Failed to deactivate node '{certname}': HTTP {resp.status_code} - {resp.text}")
    # Step 2: Purge certificate (with retry)
    ok, resp = api_delete(purge_url, headers, retries=1)
    if not ok:
        if isinstance(resp, str):
            fail(f"Failed to purge certificate '{certname}': {resp}")
        else:
            fail(f"Failed to purge certificate '{certname}': HTTP {resp.status_code} - {resp.text}")

    success(f"Node '{certname}' successfully deactivated and purged.")

if __name__ == "__main__":
    main()

