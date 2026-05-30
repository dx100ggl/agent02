# brain/c4/tools/market_data_tool.py

import yfinance as yf
import pandas as pd

class MarketDataTool:
    """
    Fetch OHLCV data for a ticker.
    Returns a JSON‑safe dict with price series.
    """

    def run(self, **kwargs):
        ticker = kwargs.get("ticker")
        period = kwargs.get("period", "6mo")
        interval = kwargs.get("interval", "1d")

        if not ticker:
            return {"error": "ticker missing"}

        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df.empty:
            return {"error": f"no data for {ticker}"}

        # --- FIX 1: Flatten multi-index columns ---
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        # Reset index so Date becomes a column
        df = df.reset_index()

        # Convert Timestamp → ISO string
        if "Date" in df.columns:
            df["Date"] = df["Date"].astype(str)

        # Force all column names to strings
        df.columns = [str(c) for c in df.columns]

        # Convert numpy types → Python native types
        df = df.apply(lambda col: col.map(lambda x: x.item() if hasattr(x, "item") else x))

        # Convert to JSON-safe dict
        ohlcv = df.to_dict(orient="records")

        return {
            "ticker": ticker,
            "ohlcv": ohlcv
        }
