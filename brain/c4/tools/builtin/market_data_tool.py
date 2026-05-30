# brain/c4/tools/builtin/market_data_tool.py

import yfinance as yf
from brain.c4.tools.base import Tool

class MarketDataTool(Tool):
    """
    Real market data backend using yfinance.
    """

    def __init__(self):
        super().__init__(
            name="market_data",
            description="Fetch OHLCV data via yfinance"
        )

    def run(self, ticker: str, period: str = "6mo", interval: str = "1d"):
        data = yf.download(ticker, period=period, interval=interval)

        if data.empty:
            return {
                "ok": False,
                "error": f"No data returned for ticker {ticker}"
            }

        ohlcv = data[["Open", "High", "Low", "Close", "Volume"]].reset_index()

        return {
            "ok": True,
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "ohlcv": ohlcv.to_dict(orient="records"),
        }
