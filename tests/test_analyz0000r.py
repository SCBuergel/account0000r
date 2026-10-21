import pandas as pd

import analyz0000r


def test_list_all_non_dust_balances(accounts, chains):
    df = analyz0000r.listAllNonDustBalances(accounts, chains)
    assert df.values.tolist() == [
        [accounts[0]["address"], "Testnet", 2.0, "ETH"],
        [accounts[0]["address"], "Testnet", 100.0, "DAI"],
        [accounts[1]["address"], "Testnet", 0.5, "ETH"],
    ]
    # the at-block loaders were never run, so nothing is reported for them
    assert analyz0000r.listAllNonDustBalances(accounts, chains, atBlock=True).empty


def test_portfolio_value(tmp_path, accounts, chains, capsys):
    pricesCsv = tmp_path / "prices.csv"
    pricesCsv.write_text("Asset,Price\nETH,2000\nDAI,1\n")
    df = analyz0000r.portfolioValue(accounts, chains, assetPricesCsv=str(pricesCsv), outputDir=str(tmp_path))
    assert df["Value"].sum() == 2 * 2000 + 100 + 0.5 * 2000
    assert df["Address"].tolist()[0] == accounts[0]["address"]  # richest account first
    out = capsys.readouterr().out
    assert "Total portfolio value (priced assets only): $5,100.00" in out
    assert "XDAI" in out  # configured but unheld assets are listed with a zero
    assert pd.read_csv(tmp_path / "asset_values.csv")["Asset"].tolist()[:2] == ["ETH", "DAI"]


def test_portfolio_value_without_prices_or_balances(tmp_path, chains, capsys):
    analyz0000r.portfolioValue([], chains, assetPricesCsv=str(tmp_path / "none.csv"), storeCsv=False)
    assert "$0.00" in capsys.readouterr().out


def test_binary_table_and_nonce_table(accounts, capsys):
    accounts[0]["chains"]["Testnet"]["nonce"] = {"nonce": 3}
    analyz0000r.tabulateNonZeroNonce(accounts)
    out = capsys.readouterr().out
    assert "alice" in out and "X" in out
    analyz0000r.printBinaryTable([])
    assert "no accounts match" in capsys.readouterr().out
