"""Portfolio management logic for TradeChill.

Handles CRUD operations on stock holdings and provides
simulated current pricing for display purposes.
"""

from typing import Optional
from . import db
from .utils import random_price, format_currency, format_percent


def add_holding(
    code: str,
    name: str,
    cost_price: float,
    quantity: int,
) -> int:
    """Add a new holding to the portfolio.

    Args:
        code: Stock code (e.g., '600519').
        name: Stock name (e.g., '贵州茅台').
        cost_price: Cost price per share.
        quantity: Number of shares held.

    Returns:
        The ID of the newly created holding.

    Raises:
        ValueError: If cost_price <= 0 or quantity <= 0.
    """
    if cost_price <= 0:
        raise ValueError("成本价必须大于0")
    if quantity <= 0:
        raise ValueError("数量必须大于0")

    sql = """INSERT INTO holdings (code, name, cost_price, quantity)
             VALUES (?, ?, ?, ?)"""
    return db.execute(sql, (code, name, cost_price, quantity))


def list_holdings() -> list[dict]:
    """Retrieve all holdings with simulated current prices.

    Each holding dict includes a computed 'current_price' field
    and derived fields for display.

    Returns:
        List of holding dicts with computed fields.
    """
    rows = db.fetch_all(
        "SELECT * FROM holdings ORDER BY created_at DESC"
    )
    results = []
    for row in rows:
        current_price = random_price(row["cost_price"])
        total_cost = row["cost_price"] * row["quantity"]
        total_value = current_price * row["quantity"]
        profit = total_value - total_cost
        profit_rate = (current_price - row["cost_price"]) / row["cost_price"]
        results.append({
            **row,
            "current_price": current_price,
            "total_cost": total_cost,
            "total_value": total_value,
            "profit": profit,
            "profit_rate": profit_rate,
        })
    return results


def remove_holding(holding_id: int) -> bool:
    """Remove a holding by its ID.

    Args:
        holding_id: The ID of the holding to remove.

    Returns:
        True if a row was deleted, False otherwise.
    """
    cursor = db.execute(
        "DELETE FROM holdings WHERE id = ?", (holding_id,)
    )
    return cursor > 0


def update_holding(
    holding_id: int,
    cost_price: Optional[float] = None,
    quantity: Optional[int] = None,
) -> bool:
    """Update a holding's cost price and/or quantity.

    Args:
        holding_id: The ID of the holding to update.
        cost_price: New cost price per share (None to keep).
        quantity: New quantity (None to keep).

    Returns:
        True if a row was updated, False otherwise.

    Raises:
        ValueError: If cost_price <= 0 or quantity <= 0.
    """
    existing = db.fetch_one(
        "SELECT * FROM holdings WHERE id = ?", (holding_id,)
    )
    if not existing:
        return False

    new_cost = cost_price if cost_price is not None else existing["cost_price"]
    new_qty = quantity if quantity is not None else existing["quantity"]

    if new_cost <= 0:
        raise ValueError("成本价必须大于0")
    if new_qty <= 0:
        raise ValueError("数量必须大于0")

    cursor = db.execute(
        """UPDATE holdings
           SET cost_price = ?, quantity = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (new_cost, new_qty, holding_id),
    )
    return cursor > 0
