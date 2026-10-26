"""Process a shipment exception from classification through compensation and routing."""

from __future__ import annotations

from chains import classify_chain, draft_email_chain, escalate_chain
from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)


def _normalize_category(category):
    value = (category or "unknown").strip().lower()
    mapping = {
        "delay": "delayed",
        "delayed": "delayed",
        "late": "delayed",
        "damage": "damaged",
        "damaged": "damaged",
        "broken": "damaged",
        "lost": "lost",
        "missing": "lost",
        "missing shipment": "lost",
        "unknown": "unknown",
    }
    return mapping.get(value, "unknown")


def _normalize_customer_tier(customer_tier):
    return (customer_tier or "standard").strip().lower()


def _route_for_category(category, shipment_value, customer_tier):
    if category == "delayed":
        return calculate_delay_compensation(shipment_value, delay_days=2, customer_tier=customer_tier)
    if category == "damaged":
        return calculate_damage_compensation(shipment_value, damage_severity="minor", customer_tier=customer_tier)
    if category == "lost":
        return calculate_lost_compensation(shipment_value, customer_tier=customer_tier)
    return {"category": "unknown", "amount": 0.0, "compensation": 0.0, "currency": "USD", "shipment_value": float(shipment_value or 0), "reason": "Unknown category."}


def process_exception(report, shipment_value, customer_tier="standard", **extra):
    """Classify a report, calculate compensation, decide escalation, and draft the response."""
    shipment_value = float(shipment_value or 0)
    customer_tier = _normalize_customer_tier(customer_tier)
    raw_category = classify_chain.invoke({"report": report})
    category = _normalize_category(raw_category)

    compensation = _route_for_category(category, shipment_value, customer_tier)
    compensation_amount = float(compensation.get("amount", compensation.get("compensation", 0.0)))
    threshold = 250.0 if customer_tier == "premium" else 500.0
    escalated = category == "unknown" or compensation_amount > threshold

    if escalated:
        manager_note = escalate_chain.invoke({
            "category": category,
            "amount": compensation_amount,
            "report": report,
            "customer_tier": customer_tier,
        })
        customer_email = None
        decision = "escalate"
    else:
        customer_email = draft_email_chain.invoke({
            "category": category,
            "amount": compensation_amount,
            "report": report,
            "customer_tier": customer_tier,
        })
        manager_note = None
        decision = "resolve"

    return {
        "category": category,
        "classification": category,
        "shipment_value": shipment_value,
        "customer_tier": customer_tier,
        "compensation": compensation_amount,
        "amount": compensation_amount,
        "currency": compensation.get("currency", "USD"),
        "escalated": escalated,
        "decision": decision,
        "customer_email": customer_email,
        "email": customer_email,
        "manager_note": manager_note,
        "internal_note": manager_note,
        "route": decision,
        "reason": compensation.get("reason", "Processed via default rules."),
    }
