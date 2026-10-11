"""List aged, benchmark-owned E2B/Modal/Blaxel sandboxes. Dry-run by default."""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core.providers.lifecycle import OWNER


def eligible(labels, created_at, now, max_age):
    """Both ownership and an unambiguous old timestamp are mandatory."""
    if not isinstance(labels, dict) or labels.get("benchmark_owner") != OWNER:
        return False
    if not re.fullmatch(r"bench-[a-f0-9]{12}", labels.get("benchmark_run_id", "")):
        return False
    try:
        if isinstance(created_at, datetime):
            if created_at.tzinfo is None:
                return False
            timestamp = created_at.timestamp()
        else:
            timestamp = float(created_at)
    except (ValueError, TypeError):
        return False
    return math.isfinite(timestamp) and 0 < timestamp <= now - max_age


async def resources(provider):
    # SDKs are imported only for the requested account/provider. No broad fallback.
    if provider == "e2b":
        from e2b_code_interpreter import Sandbox
        from e2b.sandbox.sandbox_api import SandboxQuery
        pager = await asyncio.to_thread(Sandbox.list, query=SandboxQuery(metadata={"benchmark_owner": OWNER}))
        while pager.has_next:
            for info in await asyncio.to_thread(pager.next_items):
                yield info.sandbox_id, info.metadata, info.started_at
    elif provider == "modal":
        import modal
        async for sandbox in modal.Sandbox.list.aio(tags={"benchmark_owner": OWNER}):
            labels = await sandbox.get_tags.aio()
            # Modal list does not expose creation time: use benchmark creation tag.
            yield sandbox.object_id, labels, labels.get("benchmark_created_at")
    else:
        from blaxel.core import SandboxInstance
        async for sandbox in SandboxInstance.list():
            metadata = sandbox.metadata
            labels = metadata.labels
            labels = labels.to_dict() if hasattr(labels, "to_dict") else labels
            created = metadata.created_at
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except ValueError:
                    created = None
            yield metadata.name, labels, created


async def delete(provider, identifier):
    if provider == "e2b":
        from e2b_code_interpreter import Sandbox
        # SDK's instance/class dual kill method accepts a sandbox ID as first arg.
        if not await asyncio.to_thread(Sandbox.kill, identifier):
            raise RuntimeError("Provider did not confirm sandbox kill")
    elif provider == "modal":
        import modal
        sandbox = await modal.Sandbox.from_id.aio(identifier)
        await sandbox.terminate.aio()
    else:
        from blaxel.core import SandboxInstance
        sandbox = await SandboxInstance.get(identifier)
        await sandbox.delete()


async def reap(provider, max_age, execute=False):
    candidates = []
    now = time.time()
    async for identifier, labels, created in resources(provider):
        if eligible(labels, created, now, max_age):
            candidates.append(identifier)
    for identifier in candidates:
        if execute:
            # Re-list and recheck ownership/age immediately before destructive action.
            current = [item async for item in resources(provider) if item[0] == identifier]
            if len(current) != 1 or not eligible(current[0][1], current[0][2], time.time(), max_age):
                raise RuntimeError("Ownership/age changed; deletion refused")
            await delete(provider, identifier)
        print(json.dumps({"provider": provider, "resource": identifier,
                          "action": "termination_requested" if execute else "would_terminate"}))
    print(json.dumps({"candidates": len(candidates), "dry_run": not execute,
                      "remote_absence_attested": False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=["e2b", "modal", "blaxel"])
    parser.add_argument("--max-age-seconds", type=int, default=900)
    parser.add_argument("--execute", action="store_true", help="Terminate only aged resources with matching benchmark ownership")
    args = parser.parse_args()
    if args.max_age_seconds < 60:
        parser.error("Age threshold must be at least 60 seconds")
    asyncio.run(reap(args.provider, args.max_age_seconds, args.execute))


if __name__ == "__main__":
    main()
