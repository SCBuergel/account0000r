"""Where does the time go? Counters that every RPC request, retry back-off and loader
task feeds, and a report that names the bottleneck.

rpc.FailoverHTTPProvider times every request per endpoint, utils.retry records the seconds
it sleeps, account0000r records how long each loader task took in total. Each loader loop
and the price fetch is a phase (startPhase/endPhase); report() describes the current
phase and the loops print it every REPORT_EVERY seconds and at the end, summary() lists
every phase and the whole run's endpoint table and the CLIs print it last.

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
# counters of the current phase (one loader loop, or the price fetch)
_calls = defaultdict(lambda: [0, 0.0, 0])  # endpoint -> [requests, seconds, failures]
_errors = defaultdict(int)  # (endpoint, reason) -> count
_backoff = 0.0  # seconds slept in utils.retry
_tasks = [0, 0.0]  # [count, seconds] of loader tasks
# the whole run, for summary()
_runStart = time.time()
_runCalls = defaultdict(lambda: [0, 0.0, 0])
_runErrors = defaultdict(int)
# phases are started and ended from the main thread only, so _phase and _phases are read
# without the lock; the counters above are written from worker threads and need it
_phase = None  # {"name", "start", "workers"} while a phase runs
_phases = []  # finished phases, see endPhase()


def recordCall(endpoint, seconds, reason=None):
    """One request to `endpoint`; `reason` is set when it failed."""
    with _lock:
        for stats in (_calls[endpoint], _runCalls[endpoint]):
            stats[0] += 1
            stats[1] += seconds
            if reason:
                stats[2] += 1
        if reason:
            _errors[(endpoint, reason)] += 1
            _runErrors[(endpoint, reason)] += 1


def recordBackoff(seconds):
    global _backoff
    with _lock:
        _backoff += seconds


def recordTask(seconds):
    with _lock:
        _tasks[0] += 1
        _tasks[1] += seconds


def startPhase(name, workers=1):
    """Begin a named phase: the per-phase counters start from zero. A phase still open
    is ended first."""
    global _backoff, _phase
    if _phase is not None:
        endPhase()
    with _lock:
        _calls.clear()
        _errors.clear()
        _backoff = 0.0
        _tasks[:] = [0, 0.0]
        _phase = {"name": name, "start": time.time(), "workers": workers}


def endPhase(errors=0):
    """Close the current phase, remembering its totals for summary(); `errors` is how
    many tasks or symbols failed."""
    global _phase
    with _lock:
        if _phase is None:
            return
        _phases.append({**_phase, "seconds": time.time() - _phase["start"], "tasks": _tasks[0],
                        "calls": sum(c[0] for c in _calls.values()),
                        "failed": sum(c[2] for c in _calls.values()), "backoff": _backoff, "errors": errors})
        _phase = None


def resetRun():
    """Forget every phase and the run's endpoint totals (for tests)."""
    global _runStart
    endPhase()
    with _lock:
        _phases.clear()
        _runCalls.clear()
        _runErrors.clear()
        _runStart = time.time()


def _endpointTable(calls, errors):
    lines = [f"  {'endpoint':52} {'calls':>6} {'avg ms':>7} {'fail':>5} {'total s':>8}"]
    for endpoint, (n, seconds, failures) in sorted(calls.items(), key=lambda kv: -kv[1][1]):
        lines.append(f"  {endpoint[:52]:52} {n:6} {seconds / n * 1000:7.0f} {failures:5} {seconds:8.0f}")
    for (endpoint, reason), n in sorted(errors.items(), key=lambda kv: -kv[1])[:5]:
        lines.append(f"  {n:4}x {endpoint[:40]}: {reason}")
    return lines


def _duration(seconds):
    return f"{seconds / 60:.0f}m{seconds % 60:02.0f}s" if seconds >= 60 else f"{seconds:.0f}s"


def summary():
    """Multi-line text for the end of a run: every phase with its time, workers, tasks,
    RPC calls and errors, then the endpoint table over the whole run."""
    if _phase is not None:
        endPhase()
    with _lock:
        phases, calls, errors = list(_phases), dict(_runCalls), dict(_runErrors)
    lines = [f"[run summary] {_duration(time.time() - _runStart)} in total"]
    if not phases:
        return lines[0] + ", no loading phase ran"
    lines.append(f"  {'phase':16} {'time':>7} {'workers':>7} {'tasks':>6} {'rpc calls':>9} {'failed':>6} {'backoff':>8} {'errors':>6}")
    for ph in phases:
        lines.append(f"  {ph['name'][:16]:16} {_duration(ph['seconds']):>7} {ph['workers']:7} {ph['tasks']:6} "
                     f"{ph['calls']:9} {ph['failed']:6} {_duration(ph['backoff']):>8} {ph['errors']:6}")
    if calls:
        lines += _endpointTable(calls, errors)
    return "\n".join(lines)


def report(elapsed, workers):
    """Multi-line text: per-endpoint latency and failures, top error reasons, and how the
    worker time of the last `elapsed` seconds was spent."""
    with _lock:
        calls = {k: list(v) for k, v in _calls.items()}
        errors = dict(_errors)
        backoff, (tasks, taskSeconds) = _backoff, _tasks
    lines = _endpointTable(calls, errors)
    rpc = sum(s[1] for s in calls.values())
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
