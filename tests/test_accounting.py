import pytest

import accounting


def test_parse_steps():
    assert accounting.parseSteps("0-3,5") == [0, 1, 2, 3, 5]
    assert accounting.parseSteps(" 6 ") == [6]
    for bad in ["7", "3-1", "-1"]:
        with pytest.raises(ValueError):
            accounting.parseSteps(bad)


def test_context_paths_are_per_year():
    ctx = accounting.Context(2024, "personal")
    assert ctx.accountsFile == "data/accounts-2024.json"
    assert ctx.pricesFile == "data/assetPrices-2024.csv"
    assert ctx.workers == 10
    assert accounting.Context(2024, "personal", workers=3).workers == 3
