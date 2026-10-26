import unittest
from unittest.mock import patch

import app
from session import DailyTriageSession


class AppHandlerTests(unittest.TestCase):
    def setUp(self):
        self.original_session = app.session
        app.session = DailyTriageSession()

    def tearDown(self):
        app.session = self.original_session

    def test_empty_daily_summary(self):
        self.assertEqual(
            app.get_daily_summary(),
            "Daily Summary: no exceptions processed yet.",
        )

    def test_processing_reports_updates_outcome_log_and_aggregated_summary(self):
        reports = [
            {
                "category": "delayed",
                "compensation": 35.0,
                "escalated": False,
                "decision": "resolve",
                "customer_email": "Delay response",
                "manager_note": None,
            },
            {
                "category": "damaged",
                "compensation": 40.0,
                "escalated": False,
                "decision": "resolve",
                "customer_email": "Damage response",
                "manager_note": None,
            },
            {
                "category": "damaged",
                "compensation": 40.0,
                "escalated": False,
                "decision": "resolve",
                "customer_email": "Damage response",
                "manager_note": None,
            },
            {
                "category": "lost",
                "compensation": 70.0,
                "escalated": True,
                "decision": "escalate",
                "customer_email": None,
                "manager_note": "Manager review",
            },
        ]

        with patch.object(app, "process_exception", side_effect=reports) as process:
            outcome, log, summary = "", "", ""
            for _ in reports:
                outcome, log, summary = app.process_report(
                    "Report text", shipment_value=500, customer_tier="standard"
                )

        self.assertEqual(process.call_count, 4)
        self.assertIn("Category: **lost**", outcome)
        self.assertIn("Compensation: **$70.00**", outcome)
        self.assertIn("Escalated: **Yes**", outcome)
        self.assertIn("Manager review", outcome)
        self.assertEqual(log.splitlines()[-1], "4. LOST | $70.00 | ESCALATED")
        self.assertIn("Total compensation: $185.00", summary)
        self.assertIn("Escalation rate: 25.00%", summary)
        self.assertIn("Costliest category: damaged", summary)
        self.assertIn("Processed exceptions: 4", summary)
        self.assertEqual(app.get_daily_summary(), summary)

    def test_escalation_uses_manager_note_and_explains_no_customer_email(self):
        result = {
            "category": "unknown",
            "compensation": 0.0,
            "escalated": True,
            "decision": "escalate",
            "customer_email": None,
            "manager_note": "Investigate unclear report",
        }

        with patch.object(app, "process_exception", return_value=result):
            outcome, log, _ = app.process_report(
                "Unclear report", shipment_value=100, customer_tier="premium"
            )

        self.assertIn("No customer email drafted because the case was escalated.", outcome)
        self.assertIn("Investigate unclear report", outcome)
        self.assertEqual(log, "1. UNKNOWN | $0.00 | ESCALATED")


if __name__ == "__main__":
    unittest.main()
