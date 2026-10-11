"""Validate common schemas, source relationships and generated local report links."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core.models import BenchmarkExecutionResult


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key == 'href' and value)


def main():
    root = Path(__file__).resolve().parents[1]
    provider_schema = json.loads((root / 'providers/spec.schema.json').read_text())
    inventory_schema = json.loads((root / 'providers/runtime-inventory.schema.json').read_text())
    features = set(provider_schema['properties']['features']['items']['properties']['id']['enum'])
    providers = list((root / 'providers').glob('*/spec.json'))
    issues = []
    observations = 0
    for path in providers:
        spec = json.loads(path.read_text())
        jsonschema.validate(spec, provider_schema)
        ids = [f['id'] for f in spec['features']]
        if set(ids) != features or len(ids) != len(features):
            issues.append(f'{path.relative_to(root)}: feature ids missing or duplicated')
        sources = {s['id'] for s in spec['sources']}
        for source in spec['sources']:
            parsed = urlsplit(source['url'])
            if not parsed.scheme and parsed.path:
                target = (path.parent / unquote(parsed.path)).resolve()
                if not target.exists():
                    issues.append(f'{path.relative_to(root)}: missing source target {source["url"]}')
        for item in spec['features'] + spec['pricing']['rates']:
            if set(item['source_ids']) - sources:
                issues.append(f'{path.relative_to(root)}: dangling source reference')
        generated = path.with_name('tested-configurations.json')
        content = json.loads(generated.read_text())
        for config in content['configurations']:
            for observation in config['observations']:
                jsonschema.validate(observation['metrics'], inventory_schema)
                observations += 1
            for report in config['reports']:
                if not (root / 'reports' / report).exists():
                    issues.append(f'{generated.relative_to(root)}: missing {report}')
    validated_attempts = 0
    seen = set()
    for path in sorted((root / 'reports/data/attempts').rglob('*.json')):
        content = json.loads(path.read_text())
        if not isinstance(content, list):
            issues.append(f'{path.relative_to(root)}: expected an attempt array')
            continue
        for run in content:
            if run.get('schema_version') != 2:
                continue  # Explicit historical records are not retroactively certified.
            BenchmarkExecutionResult.model_validate(run)
            identity = (run['provider'], run['run_id'])
            if identity in seen:
                issues.append(f'{path.relative_to(root)}: duplicate attempt identity')
            seen.add(identity)
            if not re.fullmatch('[a-f0-9]{64}', run.get('workload_sha256', '')):
                issues.append(f'{path.relative_to(root)}: malformed workload identity')
            if run.get('evaluation_contract_sha256'):
                for label, value in [('contract', run['evaluation_contract_sha256']),
                                     ('adapter', run.get('provenance', {}).get('adapter_sha256', ''))]:
                    if not re.fullmatch('[a-f0-9]{64}', value):
                        issues.append(f'{path.relative_to(root)}: malformed {label} identity')
                validated_attempts += 1
            if run.get('evaluation') == 'pass' and (not run.get('checks') or
                    any(v is not True for v in run['checks'].values()) or
                    run.get('cleanup') != 'success' or run.get('teardown') != 'success'):
                issues.append(f'{path.relative_to(root)}: inconsistent passing checks/cleanup')
    pages = [root / 'readme.md', root / 'CONTRIBUTING.md', root / 'BENCHMARK_LOCATIONS.md', root / 'index.html']
    pages += [root / 'reports' / p for p in ['index.html']]
    pages += list((root / 'providers').rglob('*.md'))
    pages += list((root / 'reports').rglob('*.md'))
    links = 0
    for page in sorted(set(pages)):
        content = page.read_text()
        if page.suffix == '.html':
            parser = LocalLinks()
            parser.feed(content)
            matches = parser.links
        else:
            matches = re.findall(r'\]\(([^\s)]+)\)', content)
        for link in matches:
            parsed = urlsplit(link)
            if parsed.scheme or not parsed.path:
                continue
            links += 1
            path = (page.parent / unquote(parsed.path)).resolve()
            if not path.exists():
                issues.append(f'{page.relative_to(root)}: missing link target {link}')
    result = dict(status='pass' if not issues else 'fail', provider_schemas=len(providers),
                  inventory_observations=observations, contract_hashed_attempts=validated_attempts,
                  checked_local_links=links, issues=issues)
    (root / 'reports/checks').mkdir(parents=True, exist_ok=True)
    (root / 'reports/checks/schema-links.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
