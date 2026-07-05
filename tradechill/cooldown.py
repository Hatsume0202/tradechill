"""Cooldown period calculator logic for TradeChill.

Manages the cooling-off period lifecycle — starting a cooldown,
checking remaining time, and auto-completing expired cooldowns.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from . import db
from .impulse import get_impulse, update_impulse_status


def start_cooldown(impulse_id: int) -> int:
    """Start a cooldown period for a given impulse.

    Sets the impulse status to 'cooling' and creates a cooldown
    record with the calculated end time.

    Args:
        impulse_id: The ID of the impulse to cool down on.

    Returns:
        The ID of the new cooldown record.

    Raises:
        ValueError: If impulse not found, already cooling/completed/cancelled,
                    or already in a cooldown.
    """
    impulse = get_impulse(impulse_id)
    if not impulse:
        raise ValueError(f"冲动记录 #{impulse_id} 不存在")
    if impulse["status"] in ("cooling", "completed", "cancelled"):
        raise ValueError(
            f"冲动记录 #{impulse_id} 状态为 {impulse['status']}，无法开始冷静期"
        )

    # Check if a cooldown already exists for this impulse
    existing = db.fetch_one(
        "SELECT id FROM cooldowns WHERE impulse_id = ?", (impulse_id,)
    )
    if existing:
        raise ValueError(f"冲动记录 #{impulse_id} 已有冷静期记录")

    now = datetime.now(timezone.utc)
    end_time = now + timedelta(hours=impulse["cooldown_hours"])

    sql = """INSERT INTO cooldowns (impulse_id, start_time, end_time, completed)
             VALUES (?, ?, ?, 0)"""
    cooldown_id = db.execute(sql, (impulse_id, now.isoformat(), end_time.isoformat()))

    update_impulse_status(impulse_id, "cooling")
    return cooldown_id


def get_active_cooldowns() -> list[dict]:
    """Get all currently active (not completed) cooldowns.

    Checks for expired cooldowns and auto-completes them before returning.

    Returns:
        List of active cooldown dicts with remaining time info.
    """
    # Auto-complete expired cooldowns
    check_expired_cooldowns()

    rows = db.fetch_all(
        """SELECT c.*, i.direction, i.target_code, i.target_name, i.emotion,
                  i.cooldown_hours, i.reason
           FROM cooldowns c
           JOIN impulses i ON c.impulse_id = i.id
           WHERE c.completed = 0
           ORDER BY c.start_time DESC"""
    )

    now = datetime.now(timezone.utc)
    results = []
    for row in rows:
        end = datetime.fromisoformat(row["end_time"])
        remaining = end - now
        total_seconds = max(int(remaining.total_seconds()), 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        results.append({
            **row,
            "remaining_hours": hours,
            "remaining_minutes": minutes,
            "remaining_total_seconds": total_seconds,
            "is_expired": total_seconds == 0,
        })
    return results


def get_primary_active_cooldown() -> Optional[dict]:
    """Get the most recent active cooldown, if any.

    Returns:
        The most recent active cooldown dict, or None.
    """
    active = get_active_cooldowns()
    return active[0] if active else None


def list_cooldowns() -> list[dict]:
    """List all cooldown records with joined impulse data.

    Returns:
        List of cooldown dicts.
    """
    return db.fetch_all(
        """SELECT c.*, i.direction, i.target_code, i.target_name, i.emotion,
                  i.cooldown_hours, i.reason, i.status as impulse_status
           FROM cooldowns c
           JOIN impulses i ON c.impulse_id = i.id
           ORDER BY c.start_time DESC"""
    )


def check_expired_cooldowns() -> list[dict]:
    """Find and auto-complete cooldowns that have expired.

    Marks both the cooldown record as completed and the impulse
    as 'completed' (ready for review).

    Returns:
        List of cooldown records that were just completed.
    """
    now = datetime.now(timezone.utc)
    expired = db.fetch_all(
        """SELECT c.* FROM cooldowns c
           WHERE c.completed = 0 AND c.end_time <= ?""",
        (now.isoformat(),),
    )

    for row in expired:
        db.execute(
            "UPDATE cooldowns SET completed = 1 WHERE id = ?",
            (row["id"],),
        )
        update_impulse_status(row["impulse_id"], "completed")

    return expired
