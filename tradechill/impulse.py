"""Trading impulse recording logic for TradeChill.

Allows users to log their trading impulses with associated
emotional states. Each impulse carries a suggested cooldown
period based on the emotion detected.
"""

from typing import Optional
from . import db
from .utils import EMOTION_COOLDOWN_MAP


def record_impulse(
    direction: str,
    target_code: str,
    target_name: str,
    emotion: str = "冷静",
    reason: str = "",
) -> int:
    """Record a new trading impulse.

    Automatically determines cooldown hours based on the emotion.

    Args:
        direction: 'buy' or 'sell'.
        target_code: Stock code.
        target_name: Stock name.
        emotion: Emotional state driving the impulse.
        reason: Text description of the reason for trading.

    Returns:
        The ID of the newly created impulse record.

    Raises:
        ValueError: If direction or emotion is invalid.
    """
    if direction not in ("buy", "sell"):
        raise ValueError("方向必须是 buy 或 sell")
    if emotion not in EMOTION_COOLDOWN_MAP:
        raise ValueError(f"情绪必须为: {', '.join(EMOTION_COOLDOWN_MAP.keys())}")

    cooldown_hours = EMOTION_COOLDOWN_MAP[emotion]
    sql = """INSERT INTO impulses (direction, target_code, target_name, emotion, reason, cooldown_hours)
             VALUES (?, ?, ?, ?, ?, ?)"""
    return db.execute(sql, (direction, target_code, target_name, emotion, reason, cooldown_hours))


def list_impulses(status: Optional[str] = None) -> list[dict]:
    """List impulse records, optionally filtered by status.

    Args:
        status: Optional filter ('pending', 'cooling', 'completed', 'cancelled').

    Returns:
        List of impulse record dicts.
    """
    if status:
        return db.fetch_all(
            "SELECT * FROM impulses WHERE status = ? ORDER BY created_at DESC",
            (status,),
        )
    return db.fetch_all(
        "SELECT * FROM impulses ORDER BY created_at DESC"
    )


def get_impulse(impulse_id: int) -> Optional[dict]:
    """Get a single impulse record by ID.

    Args:
        impulse_id: The impulse record ID.

    Returns:
        Impulse dict or None if not found.
    """
    return db.fetch_one(
        "SELECT * FROM impulses WHERE id = ?", (impulse_id,)
    )


def update_impulse_status(impulse_id: int, status: str) -> bool:
    """Update the status of an impulse record.

    Args:
        impulse_id: The impulse record ID.
        status: New status value.

    Returns:
        True if updated, False if impulse not found.
    """
    if status not in ("pending", "cooling", "completed", "cancelled"):
        raise ValueError("状态必须为: pending, cooling, completed, cancelled")
    cursor = db.execute(
        "UPDATE impulses SET status = ? WHERE id = ?",
        (status, impulse_id),
    )
    return cursor > 0
