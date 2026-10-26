from pipeline import process_exception


cases = [
    {
        "report": "The item arrived 2 days late but the customer only wants a small goodwill credit.",
        "shipment_value": 150,
        "customer_tier": "standard",
        "expected_category": "delayed",
        "expected_escalated": False,
    },
    {
        "report": "The entire shipment is missing and the customer is asking for reimbursement of the full value.",
        "shipment_value": 5000,
        "customer_tier": "standard",
        "expected_category": "lost",
        "expected_escalated": True,
    },
    {
        "report": "The box was crushed and the contents arrived broken.",
        "shipment_value": 420,
        "customer_tier": "standard",
        "expected_category": "damaged",
        "expected_escalated": False,
    },
    {
        "report": "gibberish on the form with no clear issue details and a claim for $300.",
        "shipment_value": 2000,
        "customer_tier": "premium",
        "expected_category": "unknown",
        "expected_escalated": True,
    },
]


if __name__ == "__main__":
    failures = []
    for index, case in enumerate(cases, start=1):
        result = process_exception(
            case["report"],
            shipment_value=case["shipment_value"],
            customer_tier=case["customer_tier"],
        )
        category_ok = result["category"] == case["expected_category"]
        escalated_ok = result["escalated"] == case["expected_escalated"]
        if not (category_ok and escalated_ok):
            failures.append((index, case, result))
            print(f"CASE {index} FAILED")
            print(case)
            print(result)
        else:
            print(f"CASE {index} PASSED: {result['category']} / escalated={result['escalated']}")

    if failures:
        raise SystemExit(1)

    print("All triage checks passed.")
