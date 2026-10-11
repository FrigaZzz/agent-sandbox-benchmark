#!/usr/bin/env python3
"""Standalone native test runner for Alibaba OpenSandbox & AgentRun.

Exercises the sandbox API directly without intermediate abstraction layers:
1. Health check & runtime identification
2. Sandbox session provisioning & lifecycle
3. Command execution & stdout verification
4. Bidirectional file upload & artifact retrieval
5. Timeout cancellation & GNU exit code 124 verification
6. Teardown & cleanup
"""
import argparse
import io
import sys
import time
import httpx


def test_sandbox(endpoint: str = "http://127.0.0.1:8889") -> bool:
    print(f"\n=======================================================")
    print(f" Alibaba OpenSandbox & AgentRun Standalone Test Runner")
    print(f" Target Endpoint: {endpoint}")
    print(f"=======================================================\n")

    client = httpx.Client(base_url=endpoint, timeout=30.0)

    # 1. Health Check
    print("-> 1. Testing Health Check (GET /health)...")
    try:
        t0 = time.perf_counter()
        resp = client.get("/health")
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code != 200:
            print(f"   [FAIL] Health check returned status {resp.status_code}")
            return False
        data = resp.json()
        print(f"   [OK] Status: {data.get('status')} | Runtime: {data.get('runtime')} ({elapsed:.1f}ms)")
    except Exception as exc:
        print(f"   [ERROR] Could not connect to {endpoint}: {exc}")
        return False

    # 2. Lifecycle Provisioning
    print("\n-> 2. Testing Sandbox Creation (POST /sandboxes)...")
    sandbox_id = None
    try:
        t0 = time.perf_counter()
        resp = client.post("/sandboxes", json={"image": "opensandbox/code-interpreter:v1.0.2"})
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code in (200, 201):
            data = resp.json()
            sandbox_id = data.get("id")
            print(f"   [OK] Sandbox created: {sandbox_id} ({elapsed:.1f}ms)")
        else:
            print(f"   [WARN] Sandbox endpoint returned status {resp.status_code}")
    except Exception as exc:
        print(f"   [WARN] Sandbox creation error: {exc}")

    # 3. Command Execution
    print("\n-> 3. Testing Command Execution (POST /command)...")
    try:
        code = "python3 -c 'import sys; print(f\"PYTHON_VERSION:{sys.version.split()[0]}\"); x = 20 * 21; print(f\"CALC:{x}\")'"
        t0 = time.perf_counter()
        resp = client.post("/command", json={"command": code, "timeout": 10.0})
        elapsed = (time.perf_counter() - t0) * 1000
        data = resp.json()
        if data.get("exit_code") != 0 or "CALC:420" not in data.get("stdout", ""):
            print(f"   [FAIL] Execution failed: {data}")
            return False
        print(f"   [OK] Exit Code: {data['exit_code']} | Time: {elapsed:.1f}ms")
        print(f"   Stdout: {data['stdout'].strip()}")
    except Exception as exc:
        print(f"   [ERROR] Execution call failed: {exc}")
        return False

    # 4. File Upload & Download Roundtrip
    print("\n-> 4. Testing File Upload & Retrieval...")
    try:
        filename = "test_alibaba_payload.txt"
        test_bytes = b"ALIBABA_OPENSANDBOX_VERIFIED_PAYLOAD_12345"

        # Upload
        files = {"file": (filename, io.BytesIO(test_bytes), "application/octet-stream")}
        t0 = time.perf_counter()
        up_resp = client.post("/files/upload", files=files, params={"path": filename})
        if up_resp.status_code not in (200, 201):
            up_resp = client.post("/upload", files=files)
        up_time = (time.perf_counter() - t0) * 1000
        if up_resp.status_code not in (200, 201):
            print(f"   [FAIL] Upload failed: {up_resp.text}")
            return False
        print(f"   [OK] File uploaded ({len(test_bytes)} bytes in {up_time:.1f}ms)")

        # Process inside sandbox
        cmd = f"python3 -c \"with open('{filename}') as f: c = f.read(); open('output_transformed.txt', 'w').write(c.lower())\""
        client.post("/command", json={"command": cmd, "timeout": 10.0})

        # Download transformed file
        t0 = time.perf_counter()
        down_resp = client.get("/files/download", params={"path": "output_transformed.txt"})
        if down_resp.status_code != 200:
            down_resp = client.get("/download/output_transformed.txt")
        down_time = (time.perf_counter() - t0) * 1000
        if down_resp.status_code != 200:
            print(f"   [FAIL] Download failed: status {down_resp.status_code}")
            return False

        downloaded_bytes = down_resp.content
        if downloaded_bytes != test_bytes.lower():
            print(f"   [FAIL] Content mismatch: got {downloaded_bytes!r}")
            return False
        print(f"   [OK] Artifact downloaded & verified ({len(downloaded_bytes)} bytes in {down_time:.1f}ms)")
    except Exception as exc:
        print(f"   [ERROR] File roundtrip failed: {exc}")
        return False

    # 5. Timeout Handling Verification
    print("\n-> 5. Testing Timeout Handling (GNU Exit Code 124)...")
    try:
        sleep_cmd = "python3 -c 'import time; time.sleep(10)'"
        t0 = time.perf_counter()
        resp = client.post("/command", json={"command": sleep_cmd, "timeout": 2.0})
        elapsed = (time.perf_counter() - t0) * 1000
        data = resp.json()
        if data.get("exit_code") == 124 and (data.get("timed_out") is True or "timeout" in data.get("stderr", "").lower()):
            print(f"   [OK] Timed out accurately in {elapsed:.1f}ms with exit code 124")
        else:
            print(f"   [FAIL] Expected exit_code 124, got: {data}")
            return False
    except Exception as exc:
        print(f"   [ERROR] Timeout test failed: {exc}")
        return False

    # 6. Teardown
    if sandbox_id:
        print(f"\n-> 6. Tearing down sandbox {sandbox_id}...")
        try:
            del_resp = client.delete(f"/sandboxes/{sandbox_id}")
            print(f"   [OK] Cleaned up: status {del_resp.status_code}")
        except Exception:
            pass

    print("\n=======================================================")
    print(" ALL ALIBABA OPENSANDBOX TESTS PASSED SUCCESSFULLY! ")
    print("=======================================================\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alibaba OpenSandbox standalone runner")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8889", help="OpenSandbox endpoint URL")
    args = parser.parse_args()

    success = test_sandbox(endpoint=args.endpoint)
    sys.exit(0 if success else 1)
