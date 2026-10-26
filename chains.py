"""LangChain-style chain adapters used by the exception pipeline.

The project is intentionally simple: the app has to work even without a live LLM
key, so each chain falls back to deterministic rule-based behaviour.
"""

from __future__ import annotations

from typing import Any


class ChainAdapter:
    def __init__(self, func):
        self.func = func

    def invoke(self, value: Any):
        if isinstance(value, dict):
            return self.func(**value)
        return self.func(value)

    def __call__(self, value: Any):
        return self.invoke(value)


def _classify_report(report: str) -> str:
    text = (report or "").lower()
    if not text:
        return "unknown"

    if any(keyword in text for keyword in ["lost", "missing", "never arrived", "not received", "not found"]):
        return "lost"
    if any(keyword in text for keyword in ["damaged", "broken", "crushed", "scratched", "wet", "bent"]):
        return "damaged"
    if any(keyword in text for keyword in ["late", "delay", "delayed", "arrived late", "slow transit", "after expected"]):
        return "delayed"
    return "unknown"


def _draft_email(**kwargs) -> str:
    category = (kwargs.get("category") or "unknown").lower()
    amount = kwargs.get("amount", 0)
    customer_tier = (kwargs.get("customer_tier") or "standard").lower()
    report = kwargs.get("report") or "the reported shipment issue"

    customer_greeting = "Dear customer" if customer_tier != "premium" else "Dear premium customer"
    return (
        f"{customer_greeting},\n\n"
        f"Thank you for contacting Northwind Logistics about {report}. "
        f"We reviewed this {category} issue and approved compensation of ${amount:,.2f}. "
        "We have applied the settlement and the shipment has been resolved."
    )


def _draft_escalation_note(**kwargs) -> str:
    category = (kwargs.get("category") or "unknown").upper()
    amount = kwargs.get("amount", 0)
    report = kwargs.get("report") or "the shipment exception"
    customer_tier = (kwargs.get("customer_tier") or "standard").upper()
    return (
        f"Escalate {category} exception for {customer_tier} customer. "
        f"Compensation request totals ${amount:,.2f}. "
        f"Report summary: {report}"
    )


classify_chain = ChainAdapter(_classify_report)
escalate_chain = ChainAdapter(_draft_escalation_note)
draft_email_chain = ChainAdapter(_draft_email)
