# Shipment Exception Desk -- Starter Kit

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then paste your GROQ_API_KEY inside
```

Get a free Groq key at [console.groq.com](https://console.groq.com).

## Running tests

From the project root, activate the virtual environment and run the unit tests:

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate
python -m unittest discover -v
```

To run only the Gradio app handler tests:

```bash
python -m unittest tests.test_app -v
```

The pipeline's four end-to-end triage scenarios can be checked separately:

```bash
python triage_check.py
```

## What to do

Read `Problem_Statement_and_Milestones.md` (in the project root, one level
up) for the full problem statement and the asks. In short:

1. `tools.py` -- implement the three compensation calculators (each returns
   a dict).
2. `pipeline.py` -- this is the core exercise. Implement `process_exception`:
   call the chains from `chains.py`, branch on the category, decide whether to
   escalate, and call the right drafting chain.
3. `session.py` -- track every processed exception and build a Daily Triage
   Summary that names the costliest category, not just a flat recap.
4. Check your pipeline actually works:

```bash
python triage_check.py
```

5. `app.py` -- wrap it all in the (mandatory) Gradio interface.

This is your first LangChain project, so it's kept intentionally simple:
the LLM client, the three prompt chains, the CLI harness, and the test
harness (`main.py`, `triage_check.py`) are all given. The compensation logic,
the pipeline's branching, the aggregation, and the UI's event handlers are
yours to build.

## Files

| File | Description |
|---|---|
| `llm.py` | Shared LangChain chat model (Groq by default). |
| `chains.py` | Ready-made classify, escalate, and draft-email chains. |
| `tools.py` | Compensation calculators. |
| `pipeline.py` | Classification, compensation, and routing logic. |
| `session.py` | Daily Triage Log and costliest-category aggregation. |
| `app.py` | Gradio interface and event handlers. |
| `main.py` | CLI runner for quick terminal testing. |
| `triage_check.py` | Scripted check for the four triage scenarios. |
| `requirements.txt` | Python package dependencies. |
| `.env.example` | Safe environment-variable template. |
| `.gitignore` | Ignores virtual environments, `.env`, and cache files. |
