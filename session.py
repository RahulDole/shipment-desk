"""Simple in-memory triage session tracker for the daily summary."""

from __future__ import annotations

from collections import defaultdict


class DailyTriageSession:
    def __init__(self):
        self.entries = []

    def log_exception(self, result):
        entry = {
            "category": result.get("category", "unknown"),
            "amount": float(result.get("amount", result.get("compensation", 0.0)) or 0),
            "escalated": bool(result.get("escalated", False)),
        }
        self.entries.append(entry)
        return entry

    def generate_daily_summary(self):
        total_compensation = sum(entry["amount"] for entry in self.entries)
        escalations = sum(1 for entry in self.entries if entry["escalated"])
        total_entries = len(self.entries) or 1
        escalation_rate = (escalations / total_entries) * 100

        totals_by_category = defaultdict(float)
        for entry in self.entries:
            totals_by_category[entry["category"]] += entry["amount"]

        costliest_category = "none"
        if totals_by_category:
            costliest_category = max(totals_by_category.items(), key=lambda item: item[1])[0]

        return {
            "total_compensation": round(total_compensation, 2),
            "escalation_rate": round(escalation_rate, 2),
            "costliest_category": costliest_category,
            "entries": len(self.entries),
        }


def generate_daily_summary(entries):
    session = DailyTriageSession()
    for entry in entries:
        session.log_exception(entry)
    return session.generate_daily_summary()
