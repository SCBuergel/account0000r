"""Where does the time go? Counters that every RPC request, retry back-off and loader
task feeds, and a report that names the bottleneck.

rpc.FailoverHTTPProvider times every request per endpoint, utils.retry records the seconds
it sleeps, account0000r records how long each loader task took in total. report() turns
that into a few lines; the loaders print it every REPORT_EVERY seconds and at the end.

Reading the report:
    rpc      time spent waiting for endpoints: slow endpoints or too few workers
    backoff  time spent sleeping between retries: failing endpoints (see the error lines)
    other    everything else in a task (building Web3 objects, decoding); should be small
    idle     workers waiting for work: only at the very start and end of a run
Tasks still running are counted in rpc/backoff but not yet in tasks, so the shares of a
report printed mid-run are approximate; the final one is exact.
"""

import threading
import time
from collections import defaultdict

REPORT_EVERY = 30  # seconds between progress reports

_lock = threading.Lock()
_calls = defaultdict(lambda: [0, 0.0, 0])  # endpoint -> [requests, seconds, failures]
_errors = defaultdict(int)  # (endpoint, reason) -> count
_backoff = 0.0  # seconds slept in utils.retry
_tasks = [0, 0.0]  # [count, seconds] of loader tasks


def recordCall(endpoint, seconds, reason=None):
    """One request to `endpoint`; `reason` is set when it failed."""
    with _lock:
        stats = _calls[endpoint]
        stats[0] += 1
        stats[1] += seconds
        if reason:
            stats[2] += 1
            _errors[(endpoint, reason)] += 1


def recordBackoff(seconds):
    global _backoff
    with _lock:
        _backoff += seconds


def recordTask(seconds):
    with _lock:
        _tasks[0] += 1
        _tasks[1] += seconds


def reset():
    global _backoff
    with _lock:
        _calls.clear()
        _errors.clear()
        _backoff = 0.0
        _tasks[:] = [0, 0.0]


def report(elapsed, workers):
    """Multi-line text: per-endpoint latency and failures, top error reasons, and how the
    worker time of the last `elapsed` seconds was spent."""
    with _lock:
        calls = sorted(_calls.items(), key=lambda kv: -kv[1][1])
        errors = sorted(_errors.items(), key=lambda kv: -kv[1])[:5]
        backoff, (tasks, taskSeconds) = _backoff, _tasks
    lines = [f"  {'endpoint':52} {'calls':>6} {'avg ms':>7} {'fail':>5} {'total s':>8}"]
    for endpoint, (n, seconds, failures) in calls:
        lines.append(f"  {endpoint[:52]:52} {n:6} {seconds / n * 1000:7.0f} {failures:5} {seconds:8.0f}")
    for (endpoint, reason), n in errors:
        lines.append(f"  {n:4}x {endpoint[:40]}: {reason}")
    rpc = sum(s[1] for _, s in calls)
    other = max(0.0, taskSeconds - rpc - backoff)
    capacity = max(elapsed * workers, 1e-9)
    idle = max(0.0, capacity - taskSeconds)

    def share(seconds):
        return f"{seconds:.0f}s ({seconds / capacity * 100:.0f}%)"

    lines.append(f"  {workers} workers x {elapsed:.0f}s = {capacity:.0f} worker-seconds: "
                 f"rpc {share(rpc)}, backoff {share(backoff)}, other {share(other)}, idle {share(idle)}")
    if tasks:
        lines.append(f"  {tasks} tasks, {taskSeconds / tasks:.2f}s each on average")
    return "\n".join(lines)
