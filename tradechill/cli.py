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
