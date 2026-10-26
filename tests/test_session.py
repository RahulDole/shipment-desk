import unittest

from session import DailyTriageSession, generate_daily_summary


class DailyTriageSessionTests(unittest.TestCase):
    def test_summary_aggregates_compensation_by_category_and_escalation_rate(self):
        session = DailyTriageSession()
        session.log_exception({"category": "damaged", "amount": 40, "escalated": False})
        session.log_exception({"category": "damaged", "amount": 40, "escalated": True})
        session.log_exception({"category": "lost", "amount": 70, "escalated": False})

        self.assertEqual(
            session.generate_daily_summary(),
            {
                "total_compensation": 150.0,
                "escalation_rate": 33.33,
                "costliest_category": "damaged",
                "entries": 3,
            },
        )

    def test_empty_summary_and_function_helper(self):
        self.assertEqual(
            DailyTriageSession().generate_daily_summary(),
            {
                "total_compensation": 0,
                "escalation_rate": 0.0,
                "costliest_category": "none",
                "entries": 0,
            },
        )
        self.assertEqual(
            generate_daily_summary(
                [{"category": "lost", "compensation": 100, "escalated": True}]
            )["total_compensation"],
            100.0,
        )


if __name__ == "__main__":
    unittest.main()
