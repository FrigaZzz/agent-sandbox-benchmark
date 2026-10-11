"""Bounded, deterministic real-work fixtures with independent host oracles."""
from __future__ import annotations

import csv
import io
import json
import textwrap
import zipfile

from ...core.models import ExecuteCodeRequest, InputFileRef


def request(code: str, **kwargs) -> ExecuteCodeRequest:
    return ExecuteCodeRequest(code=textwrap.dedent(code).strip(), **kwargs)


class DataPipelineBenchmark:
    name = "data_pipeline"
    description = "Stage 10k transactions; parse, deduplicate, reject invalid rows and aggregate cents."
    rows = 10000
    expected_metrics = {
        "valid_rows": 10000, "invalid_rows": 1, "duplicates": 1,
        "total_cents": sum((i * 37) % 100000 for i in range(rows)),
        "regions": {str(r): sum((i * 37) % 100000 for i in range(10000) if i % 5 == r) for r in range(5)},
    }
    expected_artifacts = {"summary.json": json.dumps(expected_metrics, sort_keys=True).encode()}

    @staticmethod
    def get_request():
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow(["id", "region", "cents"])
        writer.writerows((i, i % 5, (i * 37) % 100000) for i in range(10000))
        writer.writerow([0, 0, 0])
        writer.writerow(["bad", "0", "NaN"])
        return request('''
            import csv, json, os, pathlib, time
            t0 = time.perf_counter()
            source = pathlib.Path(os.environ.get('INPUT_DIR', '/tmp')) / 'transactions.csv'
            seen, regions = set(), {str(i): 0 for i in range(5)}
            valid = invalid = duplicates = total = 0
            for row in csv.DictReader(source.open()):
                try:
                    tx, cents = int(row['id']), int(row['cents'])
                    region = row['region']
                    assert region in regions and cents >= 0
                except (ValueError, AssertionError):
                    invalid += 1
                    continue
                if tx in seen:
                    duplicates += 1
                    continue
                seen.add(tx)
                valid += 1
                total += cents
                regions[region] += cents
            summary = dict(valid_rows=valid, invalid_rows=invalid, duplicates=duplicates,
                           total_cents=total, regions=regions)
            out = pathlib.Path(os.environ.get('ARTIFACT_DIR', '/tmp')) / 'summary.json'
            out.write_text(json.dumps(summary, sort_keys=True))
            print('BENCH_RESULT:' + json.dumps(dict(summary, workload_ms=(time.perf_counter()-t0)*1000)))
        ''', input_files=[InputFileRef(artifact_name="transactions.csv", text=buf.getvalue())],
            include_generated_artifacts=True, timeout_seconds=60)


class SQLiteAnalyticsBenchmark:
    name = "sqlite_analytics"
    description = "20k-row SQLite ingest, indexed query, aggregate and rollback correctness."
    expected_metrics = {"rows": 20000, "selected_sum": sum(i * 3 for i in range(20000) if i % 7 == 2),
                        "rollback_preserved": True}

    @staticmethod
    def get_request():
        return request('''
            import json, sqlite3, time
            t0 = time.perf_counter()
            db = sqlite3.connect('analytics.db')
            db.execute('DROP TABLE IF EXISTS tx')
            db.execute('CREATE TABLE tx(id INTEGER PRIMARY KEY, region INTEGER, cents INTEGER)')
            db.executemany('INSERT INTO tx VALUES(?, ?, ?)', ((i, i%7, i*3) for i in range(20000)))
            db.execute('CREATE INDEX by_region ON tx(region)')
            db.commit()
            value = db.execute('SELECT SUM(cents) FROM tx WHERE region=2').fetchone()[0]
            db.execute('DELETE FROM tx WHERE region=2')
            db.rollback()
            count = db.execute('SELECT COUNT(*) FROM tx').fetchone()[0]
            print('BENCH_RESULT:' + json.dumps(dict(rows=count, selected_sum=value,
                  rollback_preserved=count==20000, workload_ms=(time.perf_counter()-t0)*1000)))
            db.close()
        ''', timeout_seconds=60)


class RepositoryTaskBenchmark:
    name = "repository_task"
    description = "SWE-style edit/test loop: reproduce a CSV parsing bug, fix it and run tests in subprocesses."
    expected_metrics = {"red_test_failed": True, "green_test_passed": True, "cases": 4}

    @staticmethod
    def get_request():
        return request(r'''
            import json, pathlib, subprocess, sys, time
            t0 = time.perf_counter()
            pathlib.Path('solution.py').write_text('def parse(s):\n    return s.split(",")\n')
            pathlib.Path('test_solution.py').write_text(
                'from solution import parse\n'
                'assert parse(\'a,"b,c",d\') == ["a", "b,c", "d"]\n'
                'assert parse("a,b,c") == ["a", "b", "c"]\n'
                'assert parse(\'"a""b",c\') == [\'a"b\', "c"]\n'
                'assert parse("a,,c") == ["a", "", "c"]\n')
            red = subprocess.run([sys.executable, '-B', 'test_solution.py'], capture_output=True, timeout=10)
            pathlib.Path('solution.py').write_text('import csv\ndef parse(s):\n    return next(csv.reader([s]))\n')
            green = subprocess.run([sys.executable, '-B', 'test_solution.py'], capture_output=True, timeout=10)
            print('BENCH_RESULT:' + json.dumps(dict(red_test_failed=red.returncode!=0,
                  green_test_passed=green.returncode==0, cases=4, workload_ms=(time.perf_counter()-t0)*1000)))
        ''', timeout_seconds=60)


class OutputFidelityBenchmark:
    name = "output_fidelity"
    description = "Return 128 KiB stdout with Unicode, line order and exact host digest validation."
    payload = "".join(f"{i:05d}|café|λ|" + "x" * 48 + "\n" for i in range(2048))

    @staticmethod
    def get_request():
        return request(r'''
            import sys
            for i in range(2048):
                sys.stdout.write(f'{i:05d}|café|λ|' + 'x'*48 + '\n')
        ''', timeout_seconds=45)


class CrossCallStateBenchmark:
    name = "session_state"
    description = "Three separate API calls: create filesystem state, update, read back."
    requires_session = True
    expected_metrics = {"session_value": 42, "session_steps": 3}

    @staticmethod
    def get_requests():
        return [request(code, timeout_seconds=45) for code in [
            "import pathlib\npathlib.Path('session_state.json').write_text('40')",
            "import pathlib\np=pathlib.Path('session_state.json')\np.write_text(str(int(p.read_text())+2))",
            "import json, pathlib\nprint('BENCH_RESULT:'+json.dumps(dict(session_value=int(pathlib.Path('session_state.json').read_text()), session_steps=3)))",
        ]]

    @staticmethod
    def get_request():
        return CrossCallStateBenchmark.get_requests()[0]


class ErrorRecoveryBenchmark:
    name = "error_recovery"
    description = "An intentional Python exception followed by successful execution on the same runtime."
    requires_session = True
    step_statuses = ["failed", "success"]
    expected_metrics = {"recovered": True, "answer": 42}

    @staticmethod
    def get_requests():
        return [request("import pathlib\npathlib.Path('recovery_sentinel').write_text('41')\nraise ValueError('EXPECTED_BENCH_ERROR')", timeout_seconds=45),
                request("import json, pathlib\nanswer=int(pathlib.Path('recovery_sentinel').read_text())+1\nprint('BENCH_RESULT:'+json.dumps(dict(recovered=True, answer=answer)))", timeout_seconds=45)]

    @staticmethod
    def get_request():
        return ErrorRecoveryBenchmark.get_requests()[0]


def fixture_wheel() -> bytes:
    """Offline dependency: no network variance or modification of global site-packages."""
    buf = io.BytesIO()
    files = {
        "bench_fixture/__init__.py": "def transform(x):\n    return x * 7 + 1\n",
        "bench_fixture-1.0.dist-info/METADATA": "Metadata-Version: 2.1\nName: bench-fixture\nVersion: 1.0\n",
        "bench_fixture-1.0.dist-info/WHEEL": "Wheel-Version: 1.0\nGenerator: bench\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        "bench_fixture-1.0.dist-info/RECORD": "",
    }
    with zipfile.ZipFile(buf, "w") as wheel:
        for path, content in files.items():
            wheel.writestr(zipfile.ZipInfo(path, date_time=(2020, 1, 1, 0, 0, 0)), content)
    return buf.getvalue()


class DependencyInstallBenchmark:
    name = "dependency_install"
    description = "Install an uploaded offline wheel into a private target, import and execute it."
    expected_metrics = {"dependency_installed": True, "dependency_value": 43}

    @staticmethod
    def get_request():
        return request('''
            import json, os, pathlib, subprocess, sys, time
            t0 = time.perf_counter()
            wheel = pathlib.Path(os.environ.get('INPUT_DIR', '/tmp')) / 'bench_fixture-1.0-py3-none-any.whl'
            target = pathlib.Path('private_packages').resolve()
            installed = subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-index',
                '--no-deps', '--disable-pip-version-check', '--target', str(target), str(wheel)],
                capture_output=True, text=True, timeout=30)
            if installed.returncode:
                raise RuntimeError(installed.stderr)
            sys.path.insert(0, str(target))
            import bench_fixture
            print('BENCH_RESULT:' + json.dumps(dict(dependency_installed=True,
                  dependency_value=bench_fixture.transform(6), workload_ms=(time.perf_counter()-t0)*1000)))
        ''', input_files=[InputFileRef(artifact_name="bench_fixture-1.0-py3-none-any.whl", data=fixture_wheel())],
            timeout_seconds=60)
