"""Bidirectional artifact transfer and checksum validation benchmark."""
from __future__ import annotations

import hashlib
from ...core.models import ExecuteCodeRequest, InputFileRef


class ArtifactRoundtripBenchmark:
    name = "artifact_roundtrip"
    description = "Stages an input payload, transforms it in sandbox, and collects output with SHA-256 validation."
    payload = (bytes(range(256)) + b"mixed Case\x00\xff\n") * 100
    expected_artifacts = {"transformed_output.txt": payload.upper()}
    expected_metrics = {"INPUT_BYTES_READ": len(payload)}

    @staticmethod
    def get_request() -> ExecuteCodeRequest:
        payload = ArtifactRoundtripBenchmark.payload

        code = (
            "import os, pathlib, hashlib\n"
            "# 1. Read input file\n"
            "in_path = os.environ.get('INPUT_DIR', '/tmp') + '/payload.bin'\n"
            "data = b''\n"
            "if os.path.exists(in_path):\n"
            "    data = pathlib.Path(in_path).read_bytes()\n"
            "elif 'INPUT_FILES' in globals() and 'payload.bin' in INPUT_FILES:\n"
            "    data = pathlib.Path(INPUT_FILES['payload.bin']).read_bytes()\n"
            "else:\n"
            "    raise FileNotFoundError('Required staged input payload.bin is missing')\n"
            "\n"
            "# 2. Transform and write to output\n"
            "out_dir = os.environ.get('ARTIFACT_DIR', '/tmp')\n"
            "out_path = f'{out_dir}/transformed_output.txt'\n"
            "transformed = data.upper()\n"
            "pathlib.Path(out_path).write_bytes(transformed)\n"
            "\n"
            "print(f'INPUT_BYTES_READ:{len(data)}')\n"
            "print(f'OUTPUT_BYTES_WRITTEN:{len(transformed)}')\n"
            "print(f'OUTPUT_SHA:{hashlib.sha256(transformed).hexdigest()}')\n"
        )

        return ExecuteCodeRequest(
            code=code,
            input_files=[
                InputFileRef(artifact_name="payload.bin", target_name="payload.bin", data=payload)
            ],
            include_generated_artifacts=True,
            timeout_seconds=45,
        )
