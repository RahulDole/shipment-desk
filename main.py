from pipeline import process_exception


if __name__ == "__main__":
    report = "The package arrived two days late and the customer requested a refund."
    result = process_exception(report, shipment_value=350, customer_tier="standard")
    print(result)
