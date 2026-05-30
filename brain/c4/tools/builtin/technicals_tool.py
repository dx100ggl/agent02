# brain/c4/tools/technicals_tool.py

import pandas as pd
import numpy as np

class TechnicalsTool:
    """
    Compute RSI, MACD, ATR, trend regime, volatility regime.
    """
    def run(self, **kwargs):
        ohlcv = kwargs.get("ohlcv")
        if not ohlcv:
            return {"error": "ohlcv missing"}

        df = pd.DataFrame(ohlcv)

        # --- RSI ---
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- MACD ---
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        # --- ATR ---
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift()).abs()
        low_close = (df["Low"] - df["Close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["ATR"] = tr.rolling(14).mean()

        # --- Trend regime ---
        df["trend_regime"] = np.where(df["Close"] > df["Close"].rolling(50).mean(), "up", "down")

        # --- Volatility regime ---
        df["vol_regime"] = np.where(df["ATR"] > df["ATR"].rolling(50).mean(), "high", "low")

        # Extract last row
        result = (
            df[["RSI", "MACD", "MACD_signal", "ATR", "trend_regime", "vol_regime"]]
            .tail(1)
            .to_dict(orient="records")[0]
        )

        # JSON-safe keys
        result = {str(k): v for k, v in result.items()}

        return {"technicals": result}
