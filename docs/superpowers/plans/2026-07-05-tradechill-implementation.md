# TradeChill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Python CLI tool called TradeChill that helps individual investors manage trading emotions and enforce cooling-off periods.

**Architecture:** Single-package Python project with modular design. Each domain concern (portfolio, impulse, cooldown, trap detection, review, dashboard) is its own module. A shared `db.py` handles all SQLite operations. `cli.py` serves as the Typer-based CLI entry point. `utils.py` provides shared helpers. The dashboard uses Rich for a live-refreshing TUI.

**Tech Stack:** Python 3.10+, Typer (CLI), Rich (TUI), SQLite3 (stdlib), random (for simulated prices)

**User Spec Reference:** The user provided a complete spec including database schemas, CLI commands, module responsibilities, and project structure. All commands, table schemas, emotion mappings, and trap detection thresholds are specified in detail.

## Global Constraints

- Python 3.10+ required (project uses Python 3.13.14)
- SQLite via stdlib sqlite3 only (no ORM)
- Rich for all terminal output (colors, tables, panels, progress bars)
- Typer for CLI framework (modern Click alternative)
- All code must have complete type hints
- All key functions must have docstrings
- Comprehensive error handling
- Rich styles must be polished (colors, borders, icons)
- Support `python -m tradechill` execution
- Database at `~/.tradechill/tradechill.db` with auto-created directories
- Use context manager for DB connections

---
## File Structure

```
/work/tradechill/
├── tradechill/
│   ├── __init__.py          # Package marker, version
│   ├── __main__.py          # python -m tradechill support
│   ├── cli.py               # Typer CLI app, all command groups
│   ├── db.py                # Database init, CRUD operations
│   ├── portfolio.py         # Portfolio management logic
│   ├── impulse.py           # Trading impulse recording logic
│   ├── cooldown.py          # Cooldown period calculator logic
│   ├── trap_detector.py     # Behavioral finance trap detection
│   ├── review.py            # Post-cooldown review logic
│   ├── dashboard.py         # Rich TUI dashboard
│   └── utils.py             # Shared utility functions
├── requirements.txt         # rich, typer (Python 3.10+)
├── README.md                # Full project documentation
├── pyproject.toml           # Modern packaging config
└── .gitignore               # Python standard ignores
```

---

### Task 1: Project Scaffold & Configuration

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `tradechill/__init__.py`
- Create: `tradechill/utils.py`

**Interfaces:**
- Consumes: nothing
- Produces: `tradechill/__init__.py` with `__version__ = "0.1.0"`, `tradechill/utils.py` with `get_db_path()`, `emotion_cooldown_map`, `random_price()` helpers

- [ ] **Step 1: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
# Virtualenv
venv/
.venv/
# IDE
.vscode/
.idea/
*.swp
*.swo
*~
# OS
.DS_Store
Thumbs.db
# Project
*.db
```

- [ ] **Step 2: Create requirements.txt**

```
typer>=0.9.0
rich>=13.0.0
```

- [ ] **Step 3: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "tradechill"
version = "0.1.0"
description = "交易冷静期助手 - 帮助个人投资者管理交易情绪，强制冷静期"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["investment", "trading", "emotion-management", "cli"]
authors = [
    {name = "TradeChill Contributors"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Office/Business :: Financial :: Investment",
]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.urls]
Homepage = "https://github.com/Hatsume0202/tradechill"

[project.scripts]
tradechill = "tradechill.cli:app"

[tool.setuptools.packages.find]
include = ["tradechill*"]
```

- [ ] **Step 4: Create tradechill/__init__.py**

```python
"""TradeChill - 交易冷静期助手"""

__version__ = "0.1.0"
```

- [ ] **Step 5: Create tradechill/utils.py**

```python
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
```

- [ ] **Step 6: Commit scaffold**

```bash
git add .gitignore pyproject.toml requirements.txt tradechill/__init__.py tradechill/utils.py
git commit -m "chore: scaffold project structure and configuration"
```

---

### Task 2: Database Module

**Files:**
- Create: `tradechill/db.py`

**Interfaces:**
- Consumes: `tradechill/utils.py` → `get_db_path()`
- Produces:
  - `get_connection() -> sqlite3.Connection` (context manager)
  - `init_db() -> None`
  - `execute_query(sql, params) -> sqlite3.Cursor`
  - `fetch_all(sql, params) -> list[dict]`
  - `fetch_one(sql, params) -> dict | None`
  - CRUD per table: holdings, impulses, cooldowns, reviews, trap_reports

- [ ] **Step 1: Create tradechill/db.py**

```python
"""Database operations module for TradeChill.

Uses SQLite via stdlib sqlite3. Database is stored at ~/.tradechill/tradechill.db.
All tables are created on first import if they don't exist.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, Optional
from .utils import get_db_path


# Schema definitions
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    cost_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS impulses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL CHECK(direction IN ('buy','sell')),
    target_code TEXT NOT NULL,
    target_name TEXT NOT NULL,
    emotion TEXT NOT NULL CHECK(emotion IN ('FOMO','恐慌','贪婪','冷静','其他')),
    reason TEXT DEFAULT '',
    cooldown_hours INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','cooling','completed','cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cooldowns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    impulse_id INTEGER NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY(impulse_id) REFERENCES impulses(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    impulse_id INTEGER NOT NULL,
    final_decision TEXT CHECK(final_decision IN ('executed','abandoned','modified')),
    note TEXT DEFAULT '',
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(impulse_id) REFERENCES impulses(id)
);

CREATE TABLE IF NOT EXISTS trap_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections.

    Ensures the connection is properly closed after use.
    Enables row_factory for dict-like access.

    Yields:
        A sqlite3.Connection object with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database by creating all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    """Fetch all rows from a query as dictionaries.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        List of dictionaries representing rows.
    """
    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def fetch_one(sql: str, params: tuple = ()) -> Optional[dict]:
    """Fetch a single row from a query as a dictionary.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        A dictionary representing the row, or None if not found.
    """
    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple = ()) -> int:
    """Execute a write query and return the lastrowid.

    Args:
        sql: SQL query string.
        params: Query parameters tuple.

    Returns:
        The row ID of the last inserted row, or 0 for other queries.
    """
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid or 0
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/db.py
git commit -m "feat: add database module with schema and CRUD helpers"
```

---

### Task 3: Portfolio Management Module

**Files:**
- Create: `tradechill/portfolio.py`

**Interfaces:**
- Consumes: `tradechill/db.py` → `execute()`, `fetch_all()`, `fetch_one()`
- Consumes: `tradechill/utils.py` → `random_price()`, `format_currency()`, `format_percent()`
- Produces:
  - `add_holding(code, name, cost_price, quantity) -> int`
  - `list_holdings() -> list[dict]`
  - `remove_holding(id) -> bool`
  - `update_holding(id, cost_price, quantity) -> bool`

- [ ] **Step 1: Create tradechill/portfolio.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/portfolio.py
git commit -m "feat: add portfolio management module"
```

---

### Task 4: Impulse Recording Module

**Files:**
- Create: `tradechill/impulse.py`

**Interfaces:**
- Consumes: `tradechill/db.py` → `execute()`, `fetch_all()`, `fetch_one()`
- Consumes: `tradechill/utils.py` → `EMOTION_COOLDOWN_MAP`
- Produces:
  - `record_impulse(direction, code, name, emotion, reason) -> int`
  - `list_impulses() -> list[dict]`
  - `get_impulse(id) -> dict | None`
  - `update_impulse_status(id, status) -> bool`

- [ ] **Step 1: Create tradechill/impulse.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/impulse.py
git commit -m "feat: add impulse recording module"
```

---

### Task 5: Cooldown Calculator Module

**Files:**
- Create: `tradechill/cooldown.py`

**Interfaces:**
- Consumes: `tradechill/db.py` → `execute()`, `fetch_all()`, `fetch_one()`
- Consumes: `tradechill/impulse.py` → `get_impulse()`, `update_impulse_status()`
- Produces:
  - `start_cooldown(impulse_id) -> int`
  - `get_active_cooldowns() -> list[dict]`
  - `get_cooldown_status() -> dict | None`
  - `list_cooldowns() -> list[dict]`
  - `check_expired_cooldowns() -> list[dict]`

- [ ] **Step 1: Create tradechill/cooldown.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/cooldown.py
git commit -m "feat: add cooldown calculator module"
```

---

### Task 6: Behavioral Finance Trap Detector Module

**Files:**
- Create: `tradechill/trap_detector.py`

**Interfaces:**
- Consumes: `tradechill/db.py` → `fetch_all()`, `execute()`
- Consumes: `tradechill/utils.py` → `EMOTION_COOLDOWN_MAP`
- Produces:
  - `run_trap_detection() -> dict`
  - `get_trap_history() -> list[dict]`
  - `get_latest_report() -> dict | None`

- [ ] **Step 1: Create tradechill/trap_detector.py**

```python
"""Behavioral finance trap detection logic for TradeChill.

Analyzes historical impulse records to detect common behavioral
finance pitfalls such as frequent trading, FOMO/panic patterns,
and contradictory trade signals.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from . import db


def run_trap_detection() -> dict:
    """Run all trap detection checks against impulse history.

    Analyzes impulse records for:
    1. Frequent trading (>5 impulses in 7 days)
    2. Buy-high/sell-low pattern detection
    3. Emotional trading ratio (>70% FOMO/恐慌/贪婪)
    4. Same-stock direction reversal frequency

    Returns:
        Dict containing detection results with risk levels and warnings.
    """
    now = datetime.now(timezone.utc)
    seven_days_ago = (now - timedelta(days=7)).isoformat()
    thirty_days_ago = (now - timedelta(days=30)).isoformat()

    # Get impulses for analysis
    all_impulses = db.fetch_all(
        "SELECT * FROM impulses ORDER BY created_at DESC"
    )

    recent_impulses = [
        i for i in all_impulses
        if i["created_at"] >= seven_days_ago
    ]

    traps_found = []
    risk_level = "low"
    total_score = 0

    # --- Check 1: Frequent trading ---
    if len(recent_impulses) >= 5:
        severity = "high" if len(recent_impulses) >= 10 else "medium"
        traps_found.append({
            "type": "频繁交易",
            "severity": severity,
            "detail": f"过去7天内记录了 {len(recent_impulses)} 次交易冲动",
            "advice": "建议减少交易频率，给自己更多时间分析市场。频繁交易往往导致更高的交易成本和更差的回报。",
        })
        total_score += 30 if severity == "high" else 15

    # --- Check 2: Emotional trading ---
    emotion_impulses = [
        i for i in all_impulses
        if i["emotion"] in ("FOMO", "恐慌", "贪婪")
    ]
    if all_impulses:
        emotion_ratio = len(emotion_impulses) / len(all_impulses)
        if emotion_ratio > 0.7:
            traps_found.append({
                "type": "情绪化交易",
                "severity": "high",
                "detail": f"非理性情绪交易占比 {emotion_ratio * 100:.0f}%（FOMO/恐慌/贪婪）",
                "advice": "绝大多数交易冲动被情绪驱动。建议在交易前强制24小时冷静期，并用交易日志记录理性分析。",
            })
            total_score += 30

    # --- Check 3: Same stock direction reversal ---
    stock_directions: dict[str, list[str]] = {}
    for imp in all_impulses:
        code = imp["target_code"]
        if code not in stock_directions:
            stock_directions[code] = []
        stock_directions[code].append(imp["direction"])

    for code, dirs in stock_directions.items():
        if len(dirs) >= 3:
            reversals = sum(
                1 for i in range(1, len(dirs))
                if dirs[i] != dirs[i - 1]
            )
            if reversals >= 2:
                name = next(
                    (i["target_name"] for i in all_impulses if i["target_code"] == code),
                    code,
                )
                traps_found.append({
                    "type": "追涨杀跌",
                    "severity": "medium",
                    "detail": f"{name} ({code}) 在短时间内方向频繁反转（{reversals}次）",
                    "advice": "对同一标的反复改变方向是情绪化决策的典型表现。建议对该标的设置至少3天冷静期。",
                })
                total_score += 20

    # --- Check 4: FOMO spikes ---
    fomo_count = sum(1 for i in recent_impulses if i["emotion"] == "FOMO")
    if fomo_count >= 3:
        traps_found.append({
            "type": "FOMO 恐慌",
            "severity": "medium",
            "detail": f"过去7天内有 {fomo_count} 次FOMO驱动的交易冲动",
            "advice": "FOMO（错失恐惧症）是投资者最大的敌人之一。记住：市场永远有机会，不要因为害怕错过而冲动交易。",
        })
        total_score += 20

    # Determine overall risk level
    if total_score >= 50:
        risk_level = "high"
    elif total_score >= 20:
        risk_level = "medium"

    report = {
        "risk_level": risk_level,
        "total_score": total_score,
        "traps_found": traps_found,
        "analyzed_at": now.isoformat(),
        "total_impulses_analyzed": len(all_impulses),
        "recent_impulses_7d": len(recent_impulses),
    }

    # Save report to database
    db.execute(
        "INSERT INTO trap_reports (report_data) VALUES (?)",
        (json.dumps(report, ensure_ascii=False),),
    )

    return report


def get_trap_history() -> list[dict]:
    """Retrieve all historical trap detection reports.

    Returns:
        List of report dicts with parsed report_data.
    """
    rows = db.fetch_all(
        "SELECT * FROM trap_reports ORDER BY created_at DESC"
    )
    results = []
    for row in rows:
        data = json.loads(row["report_data"])
        results.append({
            "id": row["id"],
            "report_data": data,
            "created_at": row["created_at"],
        })
    return results


def get_latest_report() -> Optional[dict]:
    """Get the most recent trap detection report.

    Returns:
        Latest report dict with parsed data, or None.
    """
    row = db.fetch_one(
        "SELECT * FROM trap_reports ORDER BY created_at DESC LIMIT 1"
    )
    if not row:
        return None
    data = json.loads(row["report_data"])
    return {
        "id": row["id"],
        "report_data": data,
        "created_at": row["created_at"],
    }
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/trap_detector.py
git commit -m "feat: add behavioral finance trap detector module"
```

---

### Task 7: Post-Cooldown Review Module

**Files:**
- Create: `tradechill/review.py`

**Interfaces:**
- Consumes: `tradechill/db.py` → `execute()`, `fetch_all()`, `fetch_one()`
- Consumes: `tradechill/impulse.py` → `get_impulse()`, `list_impulses()`
- Consumes: `tradechill/utils.py` → `random_price()`
- Produces:
  - `get_pending_reviews() -> list[dict]`
  - `do_review(impulse_id, final_decision, note) -> int`
  - `compare_decisions() -> list[dict]`

- [ ] **Step 1: Create tradechill/review.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/review.py
git commit -m "feat: add post-cooldown review module"
```

---

### Task 8: Rich Dashboard Module

**Files:**
- Create: `tradechill/dashboard.py`

**Interfaces:**
- Consumes: All other modules
- Produces: `show_dashboard() -> None`

- [ ] **Step 1: Create tradechill/dashboard.py**

```python
"""Rich TUI dashboard for TradeChill.

Displays a comprehensive investment behavior dashboard with:
- Portfolio overview (PnL, holdings count, overall return)
- Emotional trend chart (7-day emotion distribution)
- Trap detection alerts
- Active cooldowns
- Auto-refresh every 5 seconds
"""

import time
from datetime import datetime, timezone
from typing import Optional

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.text import Text
from rich.bar import Bar
from rich import box

from . import portfolio, cooldown, trap_detector
from .utils import format_currency, format_percent


console = Console()


def build_portfolio_section() -> Panel:
    """Build the portfolio overview panel.

    Returns:
        A Rich Panel with portfolio summary.
    """
    holdings = portfolio.list_holdings()
    total_holdings = len(holdings)
    total_invested = sum(h["total_cost"] for h in holdings)
    total_value = sum(h["total_value"] for h in holdings)
    total_pnl = total_value - total_invested

    if total_invested > 0:
        overall_return = total_pnl / total_invested
    else:
        overall_return = 0.0

    pnl_color = "green" if total_pnl >= 0 else "red"
    pnl_text = Text(
        f"{format_currency(total_pnl)} ({format_percent(overall_return)})",
        style=pnl_color,
    )

    table = Table.grid(padding=(0, 2))
    table.add_row("持仓数量", f"{total_holdings} 只")
    table.add_row("总投入", format_currency(total_invested))
    table.add_row("当前市值", format_currency(total_value))
    table.add_row("总盈亏", pnl_text)

    return Panel(
        table,
        title="📦 持仓概览",
        border_style="blue",
        box=box.ROUNDED,
    )


def build_emotion_chart() -> Panel:
    """Build the emotional trend chart for the last 7 days.

    Uses a simple bar chart showing emotion distribution.

    Returns:
        A Rich Panel with emotion distribution.
    """
    from . import db as db_module

    seven_days_ago = (
        (datetime.now(timezone.utc) - __import__("datetime").timedelta(days=7))
        .isoformat()
    )
    # Simple approach: get recent impulses and count emotions
    recent = db_module.fetch_all(
        "SELECT emotion, COUNT(*) as cnt FROM impulses "
        "WHERE created_at >= ? GROUP BY emotion ORDER BY cnt DESC",
        (seven_days_ago,),
    )

    if not recent:
        return Panel(
            Text("暂无近期情绪数据", style="dim"),
            title="📈 近期情绪趋势（7天）",
            border_style="cyan",
            box=box.ROUNDED,
        )

    table = Table.grid(padding=(0, 2))
    max_count = max(r["cnt"] for r in recent) if recent else 1

    emotion_colors = {
        "FOMO": "red",
        "恐慌": "magenta",
        "贪婪": "yellow",
        "冷静": "green",
        "其他": "blue",
    }

    for row in recent:
        emotion = row["emotion"]
        count = row["cnt"]
        color = emotion_colors.get(emotion, "white")
        bar_width = int((count / max_count) * 30) if max_count > 0 else 0
        bar = "█" * bar_width + "░" * (30 - bar_width)
        table.add_row(
            Text(f"{emotion}", style=color),
            Text(f"{bar} {count}", style=color),
        )

    return Panel(
        table,
        title="📈 近期情绪趋势（7天）",
        border_style="cyan",
        box=box.ROUNDED,
    )


def build_trap_section() -> Panel:
    """Build the trap detection alerts panel.

    Returns:
        A Rich Panel with trap detection results.
    """
    report = trap_detector.get_latest_report()

    if not report:
        return Panel(
            Text("暂无检测数据，请先运行 tradechill traps check", style="dim"),
            title="⚠️ 行为陷阱检测",
            border_style="yellow",
            box=box.ROUNDED,
        )

    data = report["report_data"]
    risk_level = data.get("risk_level", "low")
    traps = data.get("traps_found", [])

    if risk_level == "high":
        icon = "🔴"
        border_color = "red"
        status = Text("高风险", style="bold red")
    elif risk_level == "medium":
        icon = "🟡"
        border_color = "yellow"
        status = Text("中等风险", style="bold yellow")
    else:
        icon = "🟢"
        border_color = "green"
        status = Text("低风险", style="bold green")

    content = Table.grid(padding=(0, 1))
    content.add_row("风险等级", status)
    content.add_row("陷阱数量", str(len(traps)))

    if traps:
        content.add_row("")
        for t in traps[:3]:  # Show top 3
            severity_icon = "🔴" if t["severity"] == "high" else "🟡"
            content.add_row(
                f"  {severity_icon} {t['type']}",
                t["detail"][:50] + ("..." if len(t["detail"]) > 50 else ""),
            )

    return Panel(
        content,
        title=f"{icon} 行为陷阱检测",
        border_style=border_color,
        box=box.ROUNDED,
    )


def build_cooldown_section() -> Panel:
    """Build the active cooldown status panel.

    Returns:
        A Rich Panel with active cooldown info.
    """
    active = cooldown.get_primary_active_cooldown()

    if not active:
        return Panel(
            Text("当前无进行中的冷静期", style="dim"),
            title="⏳ 活跃冷静期",
            border_style="green",
            box=box.ROUNDED,
        )

    total_seconds = active["remaining_total_seconds"]
    total_hours = active["cooldown_hours"]
    elapsed = total_hours * 3600 - total_seconds
    progress = elapsed / (total_hours * 3600) if total_hours > 0 else 0

    content = Table.grid(padding=(0, 1))
    content.add_row("标的", f"{active['target_name']} ({active['target_code']})")
    content.add_row("方向", "买入" if active["direction"] == "buy" else "卖出")
    content.add_row("情绪", active["emotion"])
    content.add_row(
        "剩余时间",
        f"{active['remaining_hours']}小时{active['remaining_minutes']}分钟",
    )

    bar = Bar(
        size=30,
        begin=0,
        end=1,
        value=min(progress, 1.0),
        width=30,
    )
    content.add_row("进度", bar)

    return Panel(
        content,
        title="⏳ 活跃冷静期",
        border_style="yellow",
        box=box.ROUNDED,
    )


def build_layout() -> Layout:
    """Build the complete dashboard layout.

    Returns:
        A Rich Layout with all dashboard sections arranged.
    """
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
    )
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    layout["body"]["left"].split_column(
        Layout(name="portfolio"),
        Layout(name="emotion"),
    )
    layout["body"]["right"].split_column(
        Layout(name="traps"),
        Layout(name="cooldown"),
    )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = Panel(
        Text(f"📊 TradeChill 投资行为看板", style="bold white"),
        subtitle=f"更新于 {now_str}  |  按 q 退出",
        border_style="bright_blue",
        box=box.DOUBLE,
    )
    layout["header"].update(header)
    layout["portfolio"].update(build_portfolio_section())
    layout["emotion"].update(build_emotion_chart())
    layout["traps"].update(build_trap_section())
    layout["cooldown"].update(build_cooldown_section())

    return layout


def show_dashboard() -> None:
    """Display the live-updating dashboard.

    Refreshes every 5 seconds. Press 'q' to quit.
    """
    import sys
    import termios
    import tty
    import select

    console.print(Text("📊 启动看板中...", style="bold blue"))

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        with Live(build_layout(), refresh_per_second=4, screen=True) as live:
            while True:
                live.update(build_layout())
                # Check for 'q' key (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == "q":
                        break
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        console.print(Text("👋 看板已退出", style="dim"))
```

- [ ] **Step 2: Commit**

```bash
git add tradechill/dashboard.py
git commit -m "feat: add Rich TUI dashboard with live refresh"
```

---

### Task 9: CLI Entry Point (All Commands)

**Files:**
- Create: `tradechill/cli.py`
- Create: `tradechill/__main__.py`

**Interfaces:**
- Consumes: All modules
- Produces: Typer app with all command groups

- [ ] **Step 1: Create tradechill/cli.py**

```python
"""CLI entry point for TradeChill.

Defines all Typer command groups and commands with Rich-formatted output.
"""

from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from datetime import datetime

from . import db, portfolio, impulse, cooldown, review, trap_detector, dashboard
from .utils import (
    EMOTIONS,
    DIRECTIONS,
    format_currency,
    format_percent,
    EMOTION_COOLDOWN_MAP,
)


app = typer.Typer(
    name="tradechill",
    help="📊 TradeChill - 交易冷静期助手: 帮助个人投资者管理交易情绪",
    no_args_is_help=True,
)
console = Console()


# ─── Error Handler ────────────────────────────────────────────────────


def handle_error(e: Exception) -> None:
    """Display a rich-formatted error message and exit.

    Args:
        e: The exception to display.
    """
    console.print(f"\n[bold red]✖ 错误:[/bold red] {e}\n")
    raise typer.Exit(1)


# ─── Portfolio Commands ──────────────────────────────────────────────


@app.group()
def portfolio_cmd():
    """管理投资组合"""


@portfolio_cmd.command("add")
def portfolio_add(
    code: str = typer.Argument(..., help="股票代码，如 600519"),
    name: str = typer.Argument(..., help="股票名称，如 贵州茅台"),
    cost_price: float = typer.Argument(..., help="成本价（每股）"),
    quantity: int = typer.Argument(..., help="持有数量"),
):
    """添加新的持仓记录"""
    try:
        db.init_db()
        holding_id = portfolio.add_holding(code, name, cost_price, quantity)
        console.print(
            f"\n[bold green]✓[/bold green] 持仓添加成功！ID: {holding_id}\n"
        )
    except Exception as e:
        handle_error(e)


@portfolio_cmd.command("list")
def portfolio_list():
    """显示所有持仓"""
    try:
        db.init_db()
        holdings = portfolio.list_holdings()
        if not holdings:
            console.print("\n[yellow]暂无持仓记录[/yellow]\n")
            return

        table = Table(
            title="📦 持仓列表",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("代码")
        table.add_column("名称")
        table.add_column("成本价", justify="right")
        table.add_column("数量", justify="right")
        table.add_column("当前价*", justify="right")
        table.add_column("市值", justify="right")
        table.add_column("盈亏", justify="right")
        table.add_column("收益率", justify="right")

        for h in holdings:
            profit_color = "green" if h["profit"] >= 0 else "red"
            table.add_row(
                str(h["id"]),
                h["code"],
                h["name"],
                format_currency(h["cost_price"]),
                str(h["quantity"]),
                format_currency(h["current_price"]),
                format_currency(h["total_value"]),
                f"[{profit_color}]{format_currency(h['profit'])}[/{profit_color}]",
                f"[{profit_color}]{format_percent(h['profit_rate'])}[/{profit_color}]",
            )

        console.print(table)
        console.print(
            "\n[dim]* 当前价为模拟数据（基于成本价±10%随机波动），仅供参考\n[/dim]"
        )
    except Exception as e:
        handle_error(e)


@portfolio_cmd.command("remove")
def portfolio_remove(
    id: int = typer.Argument(..., help="持仓ID"),
):
    """删除持仓记录"""
    try:
        db.init_db()
        if portfolio.remove_holding(id):
            console.print(f"\n[bold green]✓[/bold green] 持仓 #{id} 已删除\n")
        else:
            console.print(f"\n[red]✖ 持仓 #{id} 不存在[/red]\n")
    except Exception as e:
        handle_error(e)


@portfolio_cmd.command("update")
def portfolio_update(
    id: int = typer.Argument(..., help="持仓ID"),
    cost_price: Optional[float] = typer.Option(None, "--cost-price", "-c", help="新成本价"),
    quantity: Optional[int] = typer.Option(None, "--quantity", "-q", help="新数量"),
):
    """更新持仓信息"""
    try:
        db.init_db()
        if portfolio.update_holding(id, cost_price, quantity):
            console.print(f"\n[bold green]✓[/bold green] 持仓 #{id} 已更新\n")
        else:
            console.print(f"\n[red]✖ 持仓 #{id} 不存在[/red]\n")
    except Exception as e:
        handle_error(e)


# ─── Impulse Commands ────────────────────────────────────────────────


@app.group()
def impulse():
    """管理交易冲动记录"""


@impulse.command("record")
def impulse_record(
    direction: str = typer.Argument(..., help="交易方向: buy/sell"),
    code: str = typer.Argument(..., help="股票代码"),
    name: str = typer.Argument(..., help="股票名称"),
    emotion: str = typer.Option(
        "冷静",
        "--emotion", "-e",
        help=f"当前情绪: {', '.join(EMOTIONS)}",
    ),
    reason: str = typer.Option("", "--reason", "-r", help="交易理由"),
):
    """记录一次交易冲动"""
    try:
        db.init_db()
        imp_id = impulse.record_impulse(direction, code, name, emotion, reason)
        cooldown_hours = EMOTION_COOLDOWN_MAP.get(emotion, 24)
        console.print(
            f"\n[bold green]✓[/bold green] 冲动记录成功！ID: {imp_id}\n"
        )
        console.print(
            Panel(
                f"[bold]建议冷静期: {cooldown_hours}小时[/bold]\n"
                f"可以使用 [cyan]tradechill cooldown start {imp_id}[/cyan] 开始冷静期倒计时",
                title="💡 提示",
                border_style="yellow",
            )
        )
    except Exception as e:
        handle_error(e)


@impulse.command("list")
def impulse_list(
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="筛选状态: pending/cooling/completed/cancelled",
    ),
):
    """查看所有冲动记录"""
    try:
        db.init_db()
        records = impulse.list_impulses(status)
        if not records:
            console.print("\n[yellow]暂无冲动记录[/yellow]\n")
            return

        table = Table(
            title="💭 交易冲动记录",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("方向")
        table.add_column("标的")
        table.add_column("情绪")
        table.add_column("理由")
        table.add_column("冷静时长")
        table.add_column("状态")
        table.add_column("时间")

        status_styles = {
            "pending": "yellow",
            "cooling": "blue",
            "completed": "green",
            "cancelled": "dim",
        }
        direction_labels = {"buy": "🟢 买入", "sell": "🔴 卖出"}

        for r in records:
            table.add_row(
                str(r["id"]),
                direction_labels.get(r["direction"], r["direction"]),
                f"{r['target_name']} ({r['target_code']})",
                r["emotion"],
                r["reason"][:30] + "..." if len(r["reason"]) > 30 else r["reason"],
                f"{r['cooldown_hours']}h",
                f"[{status_styles.get(r['status'], 'white')}]{r['status']}[/{status_styles.get(r['status'], 'white')}]",
                r["created_at"][:19],
            )

        console.print(table)
    except Exception as e:
        handle_error(e)


# ─── Cooldown Commands ───────────────────────────────────────────────


@app.group()
def cooldown_cmd():
    """管理冷静期"""


@cooldown_cmd.command("start")
def cooldown_start(
    impulse_id: int = typer.Argument(..., help="冲动记录ID"),
):
    """开始冷静期倒计时"""
    try:
        db.init_db()
        cd_id = cooldown.start_cooldown(impulse_id)
        console.print(
            f"\n[bold green]✓[/bold green] 冷静期已开始！冷静期ID: {cd_id}\n"
        )
    except Exception as e:
        handle_error(e)


@cooldown_cmd.command("status")
def cooldown_status():
    """显示进行中的冷静期状态"""
    try:
        db.init_db()
        active = cooldown.get_primary_active_cooldown()
        if not active:
            console.print("\n[green]✓ 当前无进行中的冷静期[/green]\n")
            return

        total_seconds = active["remaining_total_seconds"]
        total_hours = active["cooldown_hours"]
        elapsed = total_hours * 3600 - total_seconds
        progress_pct = elapsed / (total_hours * 3600) if total_hours > 0 else 0

        panel_content = (
            f"[bold]标的:[/bold] {active['target_name']} ({active['target_code']})\n"
            f"[bold]方向:[/bold] {'买入' if active['direction'] == 'buy' else '卖出'}\n"
            f"[bold]情绪:[/bold] {active['emotion']}\n"
            f"[bold]理由:[/bold] {active['reason'] or '无'}\n"
            f"[bold]冷静时长:[/bold] {active['cooldown_hours']}小时\n"
            f"[bold]剩余时间:[/bold] {active['remaining_hours']}小时{active['remaining_minutes']}分钟\n"
        )

        console.print(
            Panel(
                panel_content,
                title="⏳ 进行中的冷静期",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )

        # Show progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]冷静期进度...",
                total=100,
            )
            progress.update(task, completed=min(progress_pct * 100, 100))
        console.print()
    except Exception as e:
        handle_error(e)


@cooldown_cmd.command("list")
def cooldown_list():
    """查看冷静期历史"""
    try:
        db.init_db()
        records = cooldown.list_cooldowns()
        if not records:
            console.print("\n[yellow]暂无冷静期记录[/yellow]\n")
            return

        table = Table(
            title="📋 冷静期历史",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("冲动ID")
        table.add_column("标的")
        table.add_column("开始时间")
        table.add_column("结束时间")
        table.add_column("状态")

        for r in records:
            status_text = (
                "[green]已完成[/green]" if r["completed"]
                else "[yellow]进行中[/yellow]"
            )
            table.add_row(
                str(r["id"]),
                str(r["impulse_id"]),
                f"{r['target_name']} ({r['target_code']})",
                r["start_time"][:19] if r["start_time"] else "-",
                r["end_time"][:19] if r["end_time"] else "-",
                status_text,
            )

        console.print(table)
    except Exception as e:
        handle_error(e)


# ─── Trap Detection Commands ─────────────────────────────────────────


@app.group()
def traps():
    """行为金融学陷阱检测"""


@traps.command("check")
def traps_check():
    """执行陷阱检测分析"""
    try:
        db.init_db()
        console.print("\n[cyan]🔍 正在分析您的交易行为...[/cyan]\n")

        report = trap_detector.run_trap_detection()

        risk_level = report["risk_level"]
        if risk_level == "high":
            icon = "🔴"
            style = "bold red"
        elif risk_level == "medium":
            icon = "🟡"
            style = "bold yellow"
        else:
            icon = "🟢"
            style = "bold green"

        summary = (
            f"[{style}]风险等级: {icon} {risk_level.upper()}[/{style}]\n"
            f"分析冲动总数: {report['total_impulses_analyzed']}\n"
            f"近7天冲动数: {report['recent_impulses_7d']}\n"
        )

        if report["traps_found"]:
            traps_text = "\n[bold]检测到的问题:[/bold]\n"
            for t in report["traps_found"]:
                sev_icon = "🔴" if t["severity"] == "high" else "🟡"
                traps_text += f"\n{sev_icon} [bold]{t['type']}[/bold]\n"
                traps_text += f"   {t['detail']}\n"
                traps_text += f"   [dim]建议: {t['advice']}[/dim]\n"
        else:
            traps_text = "\n[green]✅ 未检测到明显的交易行为陷阱！继续保持！[/green]\n"

        console.print(
            Panel(
                summary + traps_text,
                title=f"{icon} 行为陷阱检测报告",
                border_style=risk_level,
                box=box.ROUNDED,
            )
        )
    except Exception as e:
        handle_error(e)


@traps.command("history")
def traps_history():
    """查看历史检测报告"""
    try:
        db.init_db()
        reports = trap_detector.get_trap_history()
        if not reports:
            console.print("\n[yellow]暂无检测历史，请先运行 tradechill traps check[/yellow]\n")
            return

        table = Table(
            title="📋 检测历史",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("风险等级")
        table.add_column("陷阱数")
        table.add_column("分析时间")

        for r in reports:
            data = r["report_data"]
            level = data.get("risk_level", "unknown")
            level_style = {
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }.get(level, "white")

            table.add_row(
                str(r["id"]),
                f"[{level_style}]{level.upper()}[/{level_style}]",
                str(len(data.get("traps_found", []))),
                r["created_at"][:19],
            )

        console.print(table)
    except Exception as e:
        handle_error(e)


# ─── Review Commands ─────────────────────────────────────────────────


@app.group()
def review_cmd():
    """冷静期后复盘"""


@review_cmd.command("pending")
def review_pending():
    """列出待复盘的冲动记录"""
    try:
        db.init_db()
        pending = review.get_pending_reviews()
        if not pending:
            console.print("\n[green]✓ 没有待复盘的记录[/green]\n")
            return

        table = Table(
            title="📝 待复盘记录",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("ID", style="dim")
        table.add_column("方向")
        table.add_column("标的")
        table.add_column("情绪")
        table.add_column("理由")
        table.add_column("冲动时间")

        direction_labels = {"buy": "🟢 买入", "sell": "🔴 卖出"}
        for p in pending:
            table.add_row(
                str(p["id"]),
                direction_labels.get(p["direction"], p["direction"]),
                f"{p['target_name']} ({p['target_code']})",
                p["emotion"],
                p["reason"][:30] + "..." if len(p["reason"]) > 30 else p["reason"],
                p["created_at"][:19],
            )

        console.print(table)
        console.print(
            "\n[dim]使用 [cyan]tradechill review do <id>[/cyan] 进行复盘[/dim]\n"
        )
    except Exception as e:
        handle_error(e)


@review_cmd.command("do")
def review_do(
    impulse_id: int = typer.Argument(..., help="冲动记录ID"),
    final_decision: str = typer.Option(
        ..., "--decision", "-d",
        help="最终决定: executed/abandoned/modified",
    ),
    note: str = typer.Option("", "--note", "-n", help="复盘备注"),
):
    """执行复盘"""
    try:
        db.init_db()
        r_id = review.do_review(impulse_id, final_decision, note)
        console.print(f"\n[bold green]✓[/bold green] 复盘完成！复盘ID: {r_id}\n")

        decision_labels = {
            "executed": "执行交易",
            "abandoned": "放弃交易",
            "modified": "修改后执行",
        }
        console.print(
            Panel(
                f"[bold]决定:[/bold] {decision_labels.get(final_decision, final_decision)}\n"
                f"[bold]备注:[/bold] {note or '无'}",
                title="📋 复盘结果",
                border_style="green",
            )
        )
    except Exception as e:
        handle_error(e)


@review_cmd.command("compare")
def review_compare():
    """对比冲动时与冷静后的收益差异"""
    try:
        db.init_db()
        comparisons = review.compare_decisions()
        if not comparisons:
            console.print("\n[yellow]暂无复盘数据可供对比[/yellow]\n")
            return

        table = Table(
            title="📊 冲动时 vs 冷静后 收益对比（模拟）",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("复盘ID", style="dim")
        table.add_column("标的")
        table.add_column("决定")
        table.add_column("模拟冲动价")
        table.add_column("模拟现价")
        table.add_column("差异", justify="right")

        for c in comparisons:
            decision_labels = {
                "executed": "🟢 执行",
                "abandoned": "🔴 放弃",
                "modified": "🟡 修改",
            }
            diff_color = "green" if c["simulated_diff"] >= 0 else "red"
            table.add_row(
                str(c["id"]),
                f"{c['target_name']} ({c['target_code']})",
                decision_labels.get(c["final_decision"], c["final_decision"]),
                format_currency(c["simulated_price_at_impulse"]),
                format_currency(c["simulated_current_price"]),
                f"[{diff_color}]{format_currency(c['simulated_diff'])} ({format_percent(c['simulated_diff_rate'])})[/{diff_color}]",
            )

        console.print(table)
        console.print(
            "\n[dim]* 价格为模拟数据，仅用于教育目的，不代表真实市场表现\n[/dim]"
        )
    except Exception as e:
        handle_error(e)


# ─── Dashboard Command ───────────────────────────────────────────────


@app.command()
def dashboard():
    """显示投资行为看板（按q退出，自动刷新）"""
    try:
        db.init_db()
        dashboard.show_dashboard()
    except Exception as e:
        handle_error(e)


# ─── App Initialization ──────────────────────────────────────────────


@app.callback()
def main():
    """TradeChill - 交易冷静期助手"""
    db.init_db()
```

- [ ] **Step 2: Create tradechill/__main__.py**

```python
"""Support for `python -m tradechill` execution."""

from .cli import app

if __name__ == "__main__":
    app()
```

- [ ] **Step 3: Commit**

```bash
git add tradechill/cli.py tradechill/__main__.py
git commit -m "feat: add CLI entry point with all command groups"
```

---

### Task 10: README and Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# 📊 TradeChill · 交易冷静期助手

> **管理交易情绪，做出更理性的投资决策**
>
> *"在金融市场中，最大的敌人往往是你自己。"*

---

## ✨ 核心理念

TradeChill 基于行为金融学的研究成果，帮助个人投资者：

- 🧠 **识别情绪驱动** — 记录交易时的情绪状态（FOMO、恐慌、贪婪…）
- ⏳ **强制冷静期** — 根据情绪自动建议冷静时长，倒计时强制执行
- 🔍 **发现行为陷阱** — 检测频繁交易、追涨杀跌等不理性模式
- 📝 **冷静后复盘** — 对比冲动决策 vs 冷静后的理性判断
- 📊 **数据看板** — 可视化你的投资行为模式

---

## 🚀 功能一览

| 命令 | 功能 | Emoji |
|------|------|-------|
| `tradechill portfolio add` | 添加持仓 | 📦 |
| `tradechill portfolio list` | 查看持仓列表 | 📋 |
| `tradechill portfolio update` | 更新持仓 | ✏️ |
| `tradechill portfolio remove` | 删除持仓 | 🗑️ |
| `tradechill impulse record` | 记录交易冲动 | 💭 |
| `tradechill impulse list` | 查看冲动记录 | 📜 |
| `tradechill cooldown start` | 开始冷静期 | ⏳ |
| `tradechill cooldown status` | 查看冷静期状态 | 📊 |
| `tradechill cooldown list` | 冷静期历史 | 📋 |
| `tradechill traps check` | 检测行为陷阱 | 🔍 |
| `tradechill traps history` | 查看检测历史 | 📜 |
| `tradechill review pending` | 待复盘列表 | 📝 |
| `tradechill review do` | 执行复盘 | ✅ |
| `tradechill review compare` | 冷静前后对比 | 📊 |
| `tradechill dashboard` | 数据看板 | 📊 |

---

## 📦 安装

### 通过 pip 安装

```bash
pip install tradechill
```

### 从源码安装

```bash
git clone https://github.com/Hatsume0202/tradechill.git
cd tradechill
pip install -e .
```

---

## 🏃 快速上手

### 1. 添加你的持仓

```bash
tradechill portfolio add 600519 贵州茅台 185.60 100
tradechill portfolio add 000858 五粮液 168.50 200
```

### 2. 查看持仓

```bash
tradechill portfolio list
```

### 3. 记录交易冲动

```bash
tradechill impulse record buy 600519 贵州茅台 --emotion FOMO --reason "感觉要大涨"
```

### 4. 开始冷静期

```bash
tradechill cooldown start 1
tradechill cooldown status
```

### 5. 检测行为陷阱

```bash
tradechill traps check
```

### 6. 冷静后复盘

```bash
tradechill review pending
tradechill review do 1 --decision abandoned --note "冷静后觉得追高风险太大"
```

### 7. 打开看板

```bash
tradechill dashboard
```

---

## 📖 详细命令文档

### portfolio - 持仓管理

```bash
# 添加持仓
tradechill portfolio add <股票代码> <名称> <成本价> <数量>

# 查看持仓
tradechill portfolio list

# 更新持仓
tradechill portfolio update <ID> --cost-price <新成本价> --quantity <新数量>

# 删除持仓
tradechill portfolio remove <ID>
```

### impulse - 冲动记录

```bash
# 记录冲动
tradechill impulse record <buy|sell> <代码> <名称> --emotion <情绪> --reason <理由>

# 查看记录
tradechill impulse list
```

### cooldown - 冷静期

```bash
# 开始冷静期
tradechill cooldown start <冲动ID>

# 查看状态
tradechill cooldown status

# 查看历史
tradechill cooldown list
```

### traps - 陷阱检测

```bash
# 执行检测
tradechill traps check

# 查看历史
tradechill traps history
```

### review - 复盘

```bash
# 待复盘列表
tradechill review pending

# 执行复盘
tradechill review do <冲动ID> --decision <executed|abandoned|modified> --note <备注>

# 对比分析
tradechill review compare
```

---

## 🏗️ 项目结构

```
tradechill/
├── tradechill/
│   ├── __init__.py          # 包定义
│   ├── __main__.py          # python -m 支持
│   ├── cli.py               # CLI 命令定义
│   ├── db.py                # 数据库操作
│   ├── portfolio.py         # 持仓管理
│   ├── impulse.py           # 冲动记录
│   ├── cooldown.py          # 冷静期计算
│   ├── trap_detector.py     # 行为陷阱检测
│   ├── review.py            # 复盘分析
│   ├── dashboard.py         # Rich 数据看板
│   └── utils.py             # 工具函数
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🛠️ 技术栈

- **Python 3.10+** — 现代 Python
- **Typer** — CLI 框架
- **Rich** — 终端 UI（颜色、表格、面板、进度条）
- **SQLite** — 本地数据存储（标准库）
- **类型提示** — 全量类型注解
- **行为金融学** — 内置心理学模型

---

## 🔐 数据隐私

所有数据存储在本地 `~/.tradechill/tradechill.db`，不会上传到任何服务器。你的交易数据完全由你自己掌控。

---

## 📄 开源协议

MIT License

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发设置

```bash
git clone https://github.com/Hatsume0202/tradechill.git
cd tradechill
pip install -e ".[dev]"
```

---

## ⚠️ 免责声明

TradeChill 是一个**教育工具**，旨在帮助投资者认识和管理自己的交易情绪。它不提供投资建议，所有模拟价格仅供参考。投资有风险，决策需谨慎。

---

<p align="center">
  <strong>保持冷静，理性投资</strong> 🧘
</p>
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README"
```

---

### Task 11: Integration Testing and Verification

**Files:**
- Verify all modules work together

- [ ] **Step 1: Install the package in dev mode**

```bash
cd /work/tradechill && pip install -e .
```

- [ ] **Step 2: Test all commands end-to-end**

```bash
# Test portfolio
tradechill portfolio add 600519 贵州茅台 185.60 100
tradechill portfolio add 000858 五粮液 168.50 200
tradechill portfolio list

# Test impulse
tradechill impulse record buy 600519 贵州茅台 --emotion FOMO --reason "感觉要大涨"
tradechill impulse record sell 000858 五粮液 --emotion 恐慌 --reason "市场下跌"
tradechill impulse list

# Test cooldown
tradechill cooldown start 1
tradechill cooldown status

# Test traps
tradechill traps check

# Test review
tradechill review pending
tradechill review do 1 --decision abandoned --note "冷静后觉得追高风险太大"

# Test compare
tradechill review compare
```

- [ ] **Step 3: Fix any issues found during testing**
- [ ] **Step 4: Final commit with integration fixes**
