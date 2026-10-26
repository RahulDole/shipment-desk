from __future__ import annotations

import gradio as gr

from pipeline import process_exception
from session import DailyTriageSession

session = DailyTriageSession()


def _format_log(entries):
    if not entries:
        return "No exceptions processed yet."

    lines = []
    for index, entry in enumerate(entries, start=1):
        status = "ESCALATED" if bool(entry.get("escalated")) else "RESOLVED"
        lines.append(
            f"{index}. {entry.get('category', 'unknown').upper()} | "
            f"${float(entry.get('amount', 0) or 0):,.2f} | {status}"
        )
    return "\n".join(lines)


def _format_summary(summary):
    if not session.entries:
        return "Daily Summary: no exceptions processed yet."

    return (
        "Daily Summary\n"
        f"- Total compensation: ${summary['total_compensation']:,.2f}\n"
        f"- Escalation rate: {summary['escalation_rate']:.2f}%\n"
        f"- Costliest category: {summary['costliest_category']}\n"
        f"- Processed exceptions: {summary['entries']}"
    )


def process_report(report: str, shipment_value: float, customer_tier: str):
    result = process_exception(report, shipment_value=shipment_value, customer_tier=customer_tier)
    session.log_exception(result)

    decision = "Escalated to manager" if result.get("escalated") else "Auto-resolved with customer email"
    customer_message = result.get("customer_email") or "No customer email drafted because the case was escalated."
    manager_note = result.get("manager_note") or "No manager follow-up required."

    steps = [
        f"1. Classified as **{result.get('category', 'unknown')}**.",
        f"2. Calculated compensation of **${float(result.get('compensation', 0) or 0):,.2f}**.",
        f"3. Final decision: **{result.get('decision', 'resolve').upper()}**.",
        f"4. Outcome: **{decision}**.",
        f"5. Customer response: {customer_message}",
        f"6. Internal note: {manager_note}",
    ]

    summary = session.generate_daily_summary()
    log_text = _format_log(session.entries)
    summary_text = _format_summary(summary)

    outcome_md = (
        "## Shipment Exception Outcome\n"
        f"- Category: **{result.get('category', 'unknown')}**\n"
        f"- Shipment value: **${float(shipment_value or 0):,.2f}**\n"
        f"- Customer tier: **{customer_tier}**\n"
        f"- Compensation: **${float(result.get('compensation', 0) or 0):,.2f}**\n"
        f"- Escalated: **{'Yes' if result.get('escalated') else 'No'}**\n\n"
        "## Processing Steps\n"
        + "\n".join(f"- {step}" for step in steps)
    )
    return outcome_md, log_text, summary_text


def get_daily_summary():
    summary = session.generate_daily_summary()
    return _format_summary(summary)


with gr.Blocks(title="Shipment Exception Desk") as demo:
    gr.Markdown("# Shipment Exception Desk")

    with gr.Row():
        report_input = gr.Textbox(
            label="Exception report",
            lines=6,
            placeholder="Describe the shipment issue, such as a late delivery, damaged parcel, or missing shipment.",
            scale=2,
        )
        with gr.Column(scale=1):
            shipment_value = gr.Number(label="Shipment value", value=0, precision=2)
            customer_tier = gr.Dropdown(
                choices=["standard", "premium"],
                value="standard",
                label="Customer tier",
            )

    with gr.Row():
        submit_btn = gr.Button("Process Exception")
        summary_btn = gr.Button("Pull Daily Summary")

    with gr.Row():
        outcome_panel = gr.Markdown("## Outcome\nNo exception processed yet.")

    with gr.Row():
        log_box = gr.Textbox(
            label="Daily Triage Log",
            lines=12,
            value="No exceptions processed yet.",
        )

    summary_box = gr.Textbox(
        label="Daily Summary",
        lines=6,
        value="Daily Summary: no exceptions processed yet.",
    )

    submit_btn.click(
        process_report,
        inputs=[report_input, shipment_value, customer_tier],
        outputs=[outcome_panel, log_box, summary_box],
    )
    summary_btn.click(get_daily_summary, outputs=[summary_box])


if __name__ == "__main__":
    demo.launch()
