import threading
import time
from collections import defaultdict
from typing import Dict, Tuple


_lock = threading.Lock()
_request_counts: Dict[Tuple[str, int], int] = defaultdict(int)  # (path, status) -> count
_request_durations: Dict[str, list] = defaultdict(list)  # path -> [ms,...]


def record_request(path: str, status: int, duration_ms: int) -> None:
    key = (path, status)
    with _lock:
        _request_counts[key] += 1
        _request_durations[path].append(duration_ms)


def export_prometheus() -> str:
    lines = []
    lines.append("# HELP http_requests_total Total HTTP requests")
    lines.append("# TYPE http_requests_total counter")
    with _lock:
        for (path, status), count in _request_counts.items():
            lines.append(f'http_requests_total{{path="{path}",status="{status}"}} {count}')
        lines.append("# HELP http_request_duration_ms Request duration in ms (sum)")
        lines.append("# TYPE http_request_duration_ms summary")
        for path, durations in _request_durations.items():
            total = sum(durations)
            lines.append(f'http_request_duration_ms_sum{{path="{path}"}} {total}')
            lines.append(f'http_request_duration_ms_count{{path="{path}"}} {len(durations)}')
    return "\n".join(lines) + "\n"


