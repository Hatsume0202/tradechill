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
