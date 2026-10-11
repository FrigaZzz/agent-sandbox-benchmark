"""Network observations; failures alone do not prove enforcement or isolation."""
from ...core.models import ExecuteCodeRequest


class NetworkIsolationBenchmark:
    name = "net_isolation"
    description = "Observe DNS/public HTTPS/metadata endpoint outcomes without asserting security."

    @staticmethod
    def get_request():
        return ExecuteCodeRequest(code='''
import json, socket, urllib.request, urllib.error
observations = {}
try:
    socket.gethostbyname('example.com')
    observations['dns'] = {'outcome': 'resolved'}
except Exception as e:
    observations['dns'] = {'outcome': 'error', 'type': type(e).__name__}
for key, url in [('public_https', 'https://example.com'), ('metadata', 'http://169.254.169.254/')]:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(urllib.request.Request(url), timeout=3) as response:
            observations[key] = {'outcome': 'response', 'status': response.status}
    except urllib.error.HTTPError as e:
        observations[key] = {'outcome': 'http_error', 'status': e.code}
    except Exception as e:
        observations[key] = {'outcome': 'error', 'type': type(e).__name__}
print('BENCH_RESULT:' + json.dumps(observations))
''', timeout_seconds=30)
