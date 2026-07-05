"""Utility functions and shared constants for TradeChill."""

import os
from pathlib import Path
from typing import Optional
import random


# Emotion to cooldown hours mapping (from behavioral finance research)
EMOTION_COOLDOWN_MAP: dict[str, int] = {
    "FOMO": 48,
    "恐慌": 24,
    "贪婪": 36,
    "冷静": 12,
    "其他": 24,
}

EMOTIONS: list[str] = list(EMOTION_COOLDOWN_MAP.keys())

DIRECTIONS: list[str] = ["buy", "sell"]


def get_db_path() -> str:
    """Get the database file path, creating the directory if needed.

    Returns:
        Absolute path to the SQLite database file.
    """
    db_dir = Path.home() / ".tradechill"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / "tradechill.db")


def random_price(cost_price: float, max_variation: float = 0.1) -> float:
    """Generate a simulated current price around the cost price.

    Uses a random walk from cost price within +/- max_variation range,
    weighted slightly toward a small drift.

    Args:
        cost_price: The base cost price of the holding.
        max_variation: Maximum fractional variation (default 0.1 = 10%).

    Returns:
        Simulated current price rounded to 2 decimal places.
    """
    variation = random.uniform(-max_variation, max_variation)
    return round(cost_price * (1 + variation), 2)


def format_currency(value: float) -> str:
    """Format a number as CNY currency string.

    Args:
        value: The numeric value to format.

    Returns:
        Formatted string like ¥1,234.56.
    """
    return f"¥{value:,.2f}"


def format_percent(value: float) -> str:
    """Format a decimal as percentage string with sign.

    Args:
        value: Decimal value (e.g., 0.1234 for 12.34%).

    Returns:
        Formatted string like +12.34% or -5.67%.
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value * 100:.2f}%"
