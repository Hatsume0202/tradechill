"""Post-cooldown review logic for TradeChill.

After a cooldown period expires, users can review their impulse
and decide whether to execute, abandon, or modify the trade.
Provides comparison between the impulse state and the cooled-down
decision.
"""

from datetime import datetime, timezone
from typing import Optional
from . import db
from .impulse import get_impulse, update_impulse_status
from .utils import random_price, format_currency, format_percent


def get_pending_reviews() -> list[dict]:
    """Get impulses that are ready for review but not yet reviewed.

    These are impulses with status 'completed' (cooldown expired)
    that don't have a review record yet.

    Returns:
        List of impulse dicts pending review.
    """
    return db.fetch_all(
        """SELECT i.*
           FROM impulses i
           LEFT JOIN reviews r ON i.id = r.impulse_id
           WHERE i.status = 'completed' AND r.id IS NULL
           ORDER BY i.created_at DESC"""
    )


def do_review(
    impulse_id: int,
    final_decision: str,
    note: str = "",
) -> int:
    """Execute a review for a completed cooldown.

    Records the final decision (executed, abandoned, or modified)
    and any notes from the user's cooled-down perspective.

    Args:
        impulse_id: The ID of the impulse to review.
        final_decision: 'executed', 'abandoned', or 'modified'.
        note: Optional notes about the decision.

    Returns:
        The ID of the new review record.

    Raises:
        ValueError: If impulse not found, not completed, or already reviewed.
    """
    impulse = get_impulse(impulse_id)
    if not impulse:
        raise ValueError(f"冲动记录 #{impulse_id} 不存在")
    if impulse["status"] != "completed":
        raise ValueError(
            f"冲动记录 #{impulse_id} 状态为 {impulse['status']}，"
            "只有已完成的冷静期可以复盘"
        )

    # Check for existing review
    existing = db.fetch_one(
        "SELECT id FROM reviews WHERE impulse_id = ?", (impulse_id,)
    )
    if existing:
        raise ValueError(f"冲动记录 #{impulse_id} 已经复盘过了")

    if final_decision not in ("executed", "abandoned", "modified"):
        raise ValueError("决策必须是 executed, abandoned 或 modified")

    sql = """INSERT INTO reviews (impulse_id, final_decision, note)
             VALUES (?, ?, ?)"""
    return db.execute(sql, (impulse_id, final_decision, note))


def compare_decisions() -> list[dict]:
    """Compare impulse-time decisions vs post-cooling review decisions.

    For review records with decision='abandoned' or 'modified',
    simulate what the outcome would have been if executed vs the
    cooled-down decision.

    Returns:
        List of comparison dicts with simulated outcome differences.
    """
    rows = db.fetch_all(
        """SELECT r.*, i.direction, i.target_code, i.target_name,
                  i.created_at as impulse_time, i.cooldown_hours
           FROM reviews r
           JOIN impulses i ON r.impulse_id = i.id
           ORDER BY r.reviewed_at DESC"""
    )

    now = datetime.now(timezone.utc)
    results = []
    for row in rows:
        # Simulate: if they had bought/sold at impulse time vs now
        simulated_price_at_impulse = random_price(100.0, 0.05)
        simulated_current_price = random_price(simulated_price_at_impulse, 0.08)

        if row["direction"] == "buy":
            diff = simulated_current_price - simulated_price_at_impulse
        else:  # sell
            diff = simulated_price_at_impulse - simulated_current_price

        diff_rate = diff / simulated_price_at_impulse

        results.append({
            **row,
            "simulated_price_at_impulse": simulated_price_at_impulse,
            "simulated_current_price": simulated_current_price,
            "simulated_diff": diff,
            "simulated_diff_rate": diff_rate,
            "impulse_time": row["impulse_time"],
        })

    return results
