""" Compensation calculators for each shipment exception category. """

from __future__ import annotations


def _make_result(category: str, amount: float, shipment_value: float, reason: str) -> dict:
    amount = float(amount)
    payload = {
        "category": category,
        "amount": round(amount, 2),
        "compensation": round(amount, 2),
        "currency": "USD",
        "shipment_value": float(shipment_value or 0),
        "reason": reason,
    }
    return payload


def calculate_delay_compensation(shipment_value: float, delay_days: int = 1, customer_tier: str = "standard") -> dict:
    value = float(shipment_value or 0)
    if value <= 0:
        return _make_result("delayed", 0.0, value, "No shipment value provided.")

    multiplier = 0.08 if str(customer_tier).lower() != "premium" else 0.05
    amount = value * multiplier
    amount += max(0, delay_days - 1) * 15
    amount = max(25.0, amount)
    amount = min(amount, 350.0)
    return _make_result("delayed", amount, value, "Delay compensation based on shipment value and delay length.")


def calculate_damage_compensation(shipment_value: float, damage_severity: str = "minor", customer_tier: str = "standard") -> dict:
    value = float(shipment_value or 0)
    if value <= 0:
        return _make_result("damaged", 0.0, value, "No shipment value provided.")

    severity = (damage_severity or "minor").lower()
    if severity in {"minor", "light"}:
        rate = 0.12 if str(customer_tier).lower() != "premium" else 0.08
    elif severity in {"moderate", "medium"}:
        rate = 0.18 if str(customer_tier).lower() != "premium" else 0.12
    else:
        rate = 0.25 if str(customer_tier).lower() != "premium" else 0.18

    amount = value * rate
    amount = min(amount, 900.0)
    return _make_result("damaged", amount, value, "Damage compensation based on severity and shipment value.")


def calculate_lost_compensation(shipment_value: float, customer_tier: str = "standard") -> dict:
    value = float(shipment_value or 0)
    if value <= 0:
        return _make_result("lost", 0.0, value, "No shipment value provided.")

    rate = 0.85 if str(customer_tier).lower() != "premium" else 0.75
    amount = value * rate
    return _make_result("lost", amount, value, "Lost shipment compensation based on full shipment value.")
