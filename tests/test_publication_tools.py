import asyncio
import json
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from scripts.freeze_snapshot import freeze, verify
from scripts.reap_zombies import eligible, reap
from src.core.providers.lifecycle import bounded_ttl, ownership, ttl_seconds
from src.bench.portal import portal_html
from src.bench.provider_overview import update_spec_page, START, END


class PublicationTools(unittest.TestCase):
    def test_frozen_bytes_are_verified_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("readme.md", "pyproject.toml", "CONTRIBUTING.md", "index.html"):
                (root / name).write_text("Public fixture")
            with patch("scripts.freeze_snapshot.subprocess.check_output", side_effect=["abc\n", " M readme.md\n"]):
                identity = freeze(root, root / "frozen.zip")
            self.assertEqual(verify(root / "frozen.zip"), identity)
            with patch("scripts.freeze_snapshot.subprocess.check_output", side_effect=["abc\n", " M readme.md\n"]):
                with self.assertRaises(FileExistsError):
                    freeze(root, root / "frozen.zip")
            with zipfile.ZipFile(root / "frozen.zip") as original, zipfile.ZipFile(root / "tampered.zip", "w") as changed:
                for name in original.namelist():
                    changed.writestr(name, b"corrupt" if name == "readme.md" else original.read(name))
            with self.assertRaisesRegex(ValueError, "content mismatch"):
                verify(root / "tampered.zip")

    def test_ttl_bounds_and_ownership(self):
        self.assertEqual(ttl_seconds("15m"), 900)
        for value in ("1h", "0s", "unbounded"):
            with self.assertRaises(ValueError):
                ttl_seconds(value)
        for value in (True, 0, 901, 1.5):
            with self.assertRaises(ValueError):
                bounded_ttl(value)
        labels = ownership("bench-012345abcdef")
        now = time.time()
        self.assertTrue(eligible(labels, now - 1000, now, 900))
        for candidate, age in (({}, now - 1000), (labels, now), (labels, "nan"), (labels, None)):
            self.assertFalse(eligible(candidate, age, now, 900))

    def test_shared_nav_is_idempotent_and_marks_current_page(self):
        first = portal_html("<html><head></head><body><main>Page</main></body></html>", "../", "ui/index.html")
        second = portal_html(first, "../", "ui/index.html")
        self.assertEqual(first, second)
        self.assertEqual(first.count('aria-current="page"'), 1)
        self.assertIn('href="../executive/index.html"', first)

    def test_provider_regeneration_preserves_dossier_without_duplicate_overviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SPEC.md"
            dossier = "# Expert dossier\n\nA source-backed boundary.\n"
            path.write_text(dossier)
            overview = f"{START}\n# Common contract\n{END}\n\n## Detailed provider dossier\n\n"
            update_spec_page(path, overview)
            update_spec_page(path, overview)
            self.assertEqual(path.read_text().count(START), 1)
            self.assertTrue(path.read_text().endswith(dossier))


class ReaperSafety(unittest.IsolatedAsyncioTestCase):
    async def test_dry_run_never_deletes_and_skips_unowned_resources(self):
        async def listed(provider):
            yield "owned", ownership("bench-012345abcdef"), time.time() - 1000
            yield "other", {}, time.time() - 1000
        with patch("scripts.reap_zombies.resources", listed), patch("scripts.reap_zombies.delete", new_callable=AsyncMock) as delete:
            await reap("e2b", 900)
            delete.assert_not_awaited()
            await reap("e2b", 900, execute=True)
            delete.assert_awaited_once_with("e2b", "owned")

    async def test_changed_ownership_refuses_deletion(self):
        calls = 0
        async def listed(provider):
            nonlocal calls
            calls += 1
            yield "owned", ownership("bench-012345abcdef") if calls == 1 else {}, time.time() - 1000
        with patch("scripts.reap_zombies.resources", listed), patch("scripts.reap_zombies.delete", new_callable=AsyncMock) as delete:
            with self.assertRaisesRegex(RuntimeError, "changed"):
                await reap("modal", 900, execute=True)
            delete.assert_not_awaited()
