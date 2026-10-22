import priceLoad0000rs as prices
from priceLoad0000rs import aliases, manual
from priceLoad0000rs.base import basePriceLoad0000r


class FixedPrices(basePriceLoad0000r):
    def __init__(self, table):
        self.table, self.asked = table, []

    def name(self):
        return "fixed"

    def version(self):
        return "test"

    def fetchPrice(self, symbol, timestamp):
        self.asked.append(symbol)
        if symbol == "BOOM":
            raise RuntimeError("api down")
        return self.table.get(symbol)


def test_eoy_timestamp():
    assert prices.eoyTimestamp(2024) == 1735689600


def test_collect_symbols(accounts, chains):
    assert prices.collectSymbols(accounts, chains) == ["DAI", "ETH", "XDAI"]


def test_loaders_are_tried_in_order_and_aliases_use_resolved_prices():
    first = FixedPrices({"ETH": 3000.0})
    second = FixedPrices({"HOPR": 0.1})
    result = prices.loadAssetPrices(["ETH", "HOPR", "WETH", "XHOPR", "UNKNOWN", "BOOM"], 0,
                                    [first, second, aliases.load0000r()])
    assert result == {"ETH": 3000.0, "HOPR": 0.1, "WETH": 3000.0, "XHOPR": 0.1}
    assert second.asked == ["HOPR", "WETH", "XHOPR", "UNKNOWN", "BOOM"]  # ETH was already priced


def test_manual_csv_roundtrip_and_bad_rows(tmp_path):
    path = tmp_path / "p.csv"
    prices.exportPrices({"SAI": 18.18, "RETH": 3737.11}, str(path))
    assert path.read_text().splitlines() == ["Asset,Price", "RETH,3737.11", "SAI,18.18"]
    path.write_text("Asset, Price\nsai, 1.5\nbroken,\nFOAM, abc\n")
    assert manual.readPriceCsv(str(path)) == {"SAI": 1.5}
    assert manual.load0000r(str(path)).fetchPrice("Sai", 0) == 1.5
    assert manual.readPriceCsv(str(tmp_path / "missing.csv")) == {}


def test_default_loaders_prepend_cache_only_if_it_exists(tmp_path):
    names = [l.name() for l in prices.defaultPriceLoaders("m.csv", [], cacheCsv=str(tmp_path / "none.csv"))]
    assert names == ["stablecoins", "chainlink", "uniswap", "aliases", "cryptocompare", "coingecko", "manual"]
    cache = tmp_path / "cache.csv"
    cache.write_text("Asset,Price\n")
    assert [l.name() for l in prices.defaultPriceLoaders("m.csv", [], cacheCsv=str(cache))][0] == "manual"


class FakeResponse:
    def __init__(self, data, status=200):
        self._data, self.status_code = data, status

    def json(self):
        return self._data


def test_cryptocompare_needs_a_key_and_reads_the_last_candle(monkeypatch):
    from priceLoad0000rs import cryptocompare
    monkeypatch.delenv("CRYPTOCOMPARE_API_KEY", raising=False)
    assert cryptocompare.load0000r().load(["ETH"], 0) == ({}, ["ETH"])

    calls = []
    monkeypatch.setattr(cryptocompare.requests, "get", lambda url, **kw: (calls.append(kw), FakeResponse(
        {"Response": "Success", "Data": {"Data": [{"close": 1.0}, {"close": 3333.5}]}}))[1])
    loader = cryptocompare.load0000r(api_key="k")
    assert loader.fetchPrice("eth", 1735689600) == 3333.5
    assert calls[0]["headers"] == {"authorization": "Apikey k"}
    assert calls[0]["params"]["fsym"] == "ETH"

    monkeypatch.setattr(cryptocompare.requests, "get", lambda url, **kw: FakeResponse(
        {"Data": {}, "Err": {"message": "API key required"}}))
    assert loader.fetchPrice("ETH", 0) is None


def test_coingecko_reports_api_errors_and_resolves_ids(monkeypatch, capsys):
    from priceLoad0000rs import coingecko

    def fake_get(url, params=None, headers=None, timeout=None):
        if url.endswith("/coins/list"):
            return FakeResponse([{"id": "hopr", "symbol": "hopr", "name": "HOPR"}])
        if "hopr" in url:
            return FakeResponse({"market_data": {"current_price": {"usd": 0.05}}})
        if "ethereum" in url:
            return FakeResponse({"error": {"status": {"error_message": "exceeds the allowed time range"}}}, 401)
        return FakeResponse({"error": "coin not found"}, 404)

    monkeypatch.setattr(coingecko.requests, "get", fake_get)
    loader = coingecko.load0000r()
    loader._ids["GONE"] = "gone"
    prices, missing = loader.load(["HOPR", "ETH", "GONE", "NOPE"], 1735689600)
    assert prices == {"HOPR": 0.05}
    assert missing == ["ETH", "GONE", "NOPE"]  # API errors are logged; NOPE has no id in the list
    out = capsys.readouterr().out
    assert "HTTP 401: exceeds the allowed time range" in out
    assert "HTTP 404: coin not found" in out
