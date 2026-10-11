#!/usr/bin/env python3
"""Standalone native test runner for Kubernetes-SIGs Agent-Sandbox.

Exercises the sandbox API directly without intermediate abstraction layers:
1. Health check & runtime identification
2. Command execution & stdout streaming
3. Bidirectional file upload & artifact retrieval
4. Timeout cancellation & GNU exit code 124 verification
"""
import argparse
import io
import sys
import time
import httpx


def test_sandbox(endpoint: str = "http://127.0.0.1:8888") -> bool:
    print(f"\n=======================================================")
    print(f" Kubernetes-SIGs Agent-Sandbox Standalone Test Runner")
    print(f" Target Endpoint: {endpoint}")
    print(f"=======================================================\n")

    client = httpx.Client(base_url=endpoint, timeout=30.0)

    # 1. Health Check
    print("-> 1. Testing Health Check (GET /)...")
    try:
        t0 = time.perf_counter()
        resp = client.get("/")
        elapsed = (time.perf_counter() - t0) * 1000
        if resp.status_code != 200:
            print(f"   [FAIL] Health check returned status {resp.status_code}")
            return False
        data = resp.json()
        print(f"   [OK] Status: {data.get('status')} | Runtime: {data.get('runtime')} ({elapsed:.1f}ms)")
    except Exception as exc:
        print(f"   [ERROR] Could not connect to {endpoint}: {exc}")
        return False

    # 2. Command Execution
    print("\n-> 2. Testing Command Execution (POST /execute)...")
    try:
        code = "python3 -c 'import sys; print(f\"PYTHON_VERSION:{sys.version.split()[0]}\"); x = 20 * 21; print(f\"CALC:{x}\")'"
        t0 = time.perf_counter()
        resp = client.post("/execute", json={"command": code, "timeout_seconds": 10.0})
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

    # 3. File Upload & Download Roundtrip
    print("\n-> 3. Testing File Upload & Retrieval...")
    try:
        filename = "test_input_payload.txt"
        test_bytes = b"K8S_AGENT_SANDBOX_VERIFIED_PAYLOAD_12345"
        
        # Upload
        files = {"file": (filename, io.BytesIO(test_bytes), "application/octet-stream")}
        t0 = time.perf_counter()
        up_resp = client.post("/upload", files=files)
        up_time = (time.perf_counter() - t0) * 1000
        if up_resp.status_code != 200:
            print(f"   [FAIL] Upload failed: {up_resp.text}")
            return False
        print(f"   [OK] File uploaded ({len(test_bytes)} bytes in {up_time:.1f}ms)")

        # Process inside sandbox
        cmd = f"python3 -c \"with open('{filename}') as f: c = f.read(); open('output_transformed.txt', 'w').write(c.lower())\""
        client.post("/execute", json={"command": cmd, "timeout_seconds": 10.0})

        # Download transformed file
        t0 = time.perf_counter()
        down_resp = client.get("/download/output_transformed.txt")
        down_time = (time.perf_counter() - t0) * 1000
        if down_resp.status_code != 200:
            print(f"   [FAIL] Download failed: {down_resp.status_code}")
            return False
        downloaded = down_resp.content
        if downloaded != test_bytes.lower():
            print(f"   [FAIL] Content mismatch: expected {test_bytes.lower()}, got {downloaded}")
            return False
        print(f"   [OK] Transformed output retrieved ({len(downloaded)} bytes in {down_time:.1f}ms)")
        print(f"   Content: {downloaded.decode()}")
    except Exception as exc:
        print(f"   [ERROR] File operations failed: {exc}")
        return False

    # 4. Timeout Handling
    print("\n-> 4. Testing Timeout Handling & Exit Code 124...")
    try:
        t0 = time.perf_counter()
        timeout_resp = client.post("/execute", json={"command": "sleep 10", "timeout_seconds": 1.5})
        elapsed = (time.perf_counter() - t0) * 1000
        data = timeout_resp.json()
        if data.get("exit_code") != 124 or not data.get("timed_out"):
            print(f"   [FAIL] Expected timeout exit code 124, got: {data}")
            return False
        print(f"   [OK] Correctly cancelled with exit code 124 in {elapsed:.1f}ms")
        print(f"   Stderr message: {data.get('stderr')}")
    except Exception as exc:
        print(f"   [ERROR] Timeout test failed: {exc}")
        return False

    print("\n✓ All Kubernetes-SIGs Agent-Sandbox verification checks PASSED successfully.\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone runner for k8s_agent_sandbox")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8888", help="Sandbox daemon base URL")
    args = parser.parse_args()

    success = test_sandbox(endpoint=args.endpoint)
    sys.exit(0 if success else 1)
