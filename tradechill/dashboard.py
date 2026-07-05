"""Rich TUI dashboard for TradeChill.

Displays a comprehensive investment behavior dashboard with:
- Portfolio overview (PnL, holdings count, overall return)
- Emotional trend chart (7-day emotion distribution)
- Trap detection alerts
- Active cooldowns
- Auto-refresh every 5 seconds
"""

import time
from datetime import datetime, timedelta, timezone
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

    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

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
