# brain/c4/tools/builtin/sentiment_tool.py

from datetime import datetime, timezone
from brain.c4.tools.base import Tool


class SentimentTool(Tool):
    """
    B3: Deterministic sentiment scores for:
    - news sentiment
    - social sentiment
    - earnings sentiment

    This is a schema-first implementation.
    Real data will be added in C3.
    """

    def __init__(self):
        super().__init__(
            name="sentiment",
            description="Provides deterministic sentiment scores for a ticker."
        )

    def run(self, **kwargs):
        ticker = kwargs.get("ticker")
        if not ticker:
            return {"error": "ticker missing"}

        # -----------------------------
        # Deterministic sentiment values
        # -----------------------------
        news_sentiment = 0.18
        social_sentiment = 0.12
        earnings_sentiment = 0.25

        # -----------------------------
        # Deterministic sample headlines
        # -----------------------------
        sample_news = [
            {
                "headline": f"{ticker} sees continued institutional interest",
                "sentiment": 0.22,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "headline": f"Analysts maintain stable outlook on {ticker}",
                "sentiment": 0.14,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]

        sample_social = [
            {
                "post": f"Retail traders discussing {ticker} momentum",
                "sentiment": 0.10,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "post": f"Mixed opinions on {ticker} valuation",
                "sentiment": 0.13,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ]

        sample_earnings = {
            "tone": "positive",
            "sentiment": earnings_sentiment,
            "summary": f"{ticker} earnings commentary shows constructive forward guidance.",
        }

        # -----------------------------
        # Final structured output
        # -----------------------------
        return {
            "ticker": ticker,
            "news_sentiment": news_sentiment,
            "social_sentiment": social_sentiment,
            "earnings_sentiment": earnings_sentiment,
            "news_samples": sample_news,
            "social_samples": sample_social,
            "earnings_summary": sample_earnings,
        }
