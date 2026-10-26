import unittest

from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)


class CompensationCalculatorTests(unittest.TestCase):
    def test_delay_compensation_returns_structured_result(self):
        result = calculate_delay_compensation(1000, delay_days=2, customer_tier="standard")

        self.assertEqual(result["category"], "delayed")
        self.assertEqual(result["amount"], 95.0)
        self.assertEqual(result["compensation"], 95.0)
        self.assertEqual(result["currency"], "USD")

    def test_damage_compensation_uses_severity_and_customer_tier(self):
        standard = calculate_damage_compensation(
            1000, damage_severity="moderate", customer_tier="standard"
        )
        premium = calculate_damage_compensation(
            1000, damage_severity="moderate", customer_tier="premium"
        )

        self.assertEqual(standard["amount"], 180.0)
        self.assertEqual(premium["amount"], 120.0)

    def test_lost_compensation_uses_customer_tier(self):
        standard = calculate_lost_compensation(1000, customer_tier="standard")
        premium = calculate_lost_compensation(1000, customer_tier="premium")

        self.assertEqual(standard["amount"], 850.0)
        self.assertEqual(premium["amount"], 750.0)

    def test_nonpositive_shipment_value_yields_zero_compensation(self):
        for calculate in (
            calculate_delay_compensation,
            calculate_damage_compensation,
            calculate_lost_compensation,
        ):
            with self.subTest(calculator=calculate.__name__):
                self.assertEqual(calculate(0)["amount"], 0.0)


if __name__ == "__main__":
    unittest.main()
