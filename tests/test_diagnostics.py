import account0000r
import diagnostics
from test_account0000r import CountingLoader


def test_report_breaks_worker_time_down_by_endpoint_and_cause():
    diagnostics.startPhase("test", 2)
    diagnostics.recordCall("http://fast.invalid", 0.1)
    diagnostics.recordCall("http://slow.invalid", 0.9, reason="Unauthorized")
    diagnostics.recordCall("http://slow.invalid", 1.0)
    diagnostics.recordBackoff(2.0)
    diagnostics.recordTask(5.0)  # 2.0s rpc + 2.0s backoff + 1.0s other
    text = diagnostics.report(elapsed=5.0, workers=2)
    lines = text.splitlines()
    assert lines[1].split() == ["http://slow.invalid", "2", "950", "1", "2"]  # slowest endpoint first
    assert lines[2].split() == ["http://fast.invalid", "1", "100", "0", "0"]
    assert lines[3] == "     1x http://slow.invalid: Unauthorized"
    assert lines[4].endswith("rpc 2s (20%), backoff 2s (20%), other 1s (10%), idle 5s (50%)")
    assert lines[5] == "  1 tasks, 5.00s each on average"


def test_load_account_metadata_prints_a_diagnostics_report(accounts, chains, capsys):
    diagnostics.recordBackoff(99.0)  # left over from an earlier run; must not show up
    account0000r.loadAccountMetadata([CountingLoader()], accounts, chains, max_workers=2)
    out = capsys.readouterr().out
    assert "[diagnostics] after" in out
    assert "2 workers x" in out and "backoff 0s (0%)" in out
    assert "4 tasks," in out


def test_rpc_calls_and_backoff_are_recorded(monkeypatch):
    import rpc
    import utils
    from web3.providers import HTTPProvider

    diagnostics.startPhase("test", 2)
    monkeypatch.setattr(HTTPProvider, "make_request", lambda self, m, p: {"result": "0x1"})
    rpc.build_web3({"name": "Diag", "api": "http://only.invalid"}).provider.make_request("eth_blockNumber", [])
    monkeypatch.setattr(utils.time, "sleep", lambda s: None)
    attempts = []
    try:
        utils.retry(lambda: attempts.append(1) or 1 / 0, max_attempts=2)
    except ZeroDivisionError:
        pass
    text = diagnostics.report(elapsed=1.0, workers=1)
    assert "http://only.invalid" in text and "backoff 1s" in text


def test_summary_lists_every_phase_and_the_whole_run(accounts, chains):
    diagnostics.resetRun()
    assert diagnostics.summary().endswith("no loading phase ran")
    diagnostics.startPhase("first", 3)
    diagnostics.recordCall("http://x.invalid", 0.5, reason="HTTPError")
    diagnostics.recordTask(1.0)
    diagnostics.endPhase(errors=1)
    account0000r.loadAccountMetadata([CountingLoader()], accounts, chains, max_workers=2)
    diagnostics.recordCall("http://x.invalid", 0.1)  # outside any phase, still part of the run
    text = diagnostics.summary()
    lines = text.splitlines()
    assert lines[0].startswith("[run summary] ")
    assert lines[2].split() == ["first", "0s", "3", "1", "1", "1", "0s", "1"]
    assert lines[3].split()[0:1] + lines[3].split()[2:4] == ["balances", "2", "4"]
    assert any(l.split()[:2] == ["http://x.invalid", "2"] for l in lines)
    assert "1x http://x.invalid: HTTPError" in text
