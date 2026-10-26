import unittest
from unittest.mock import patch

from langchain_core.runnables import RunnableLambda

from chains import ChainAdapter, _build_llm_chains
from llm import get_llm


class ChainTests(unittest.TestCase):
    def test_adapter_uses_fallback_when_no_llm_chain_is_configured(self):
        chain = ChainAdapter(lambda report: f"fallback: {report}")

        self.assertEqual(chain.invoke({"report": "package is late"}), "fallback: package is late")

    def test_llm_helper_returns_none_when_no_api_key_is_configured(self):
        with patch.dict("os.environ", {"GROQ_API_KEY": "", "OPENAI_API_KEY": ""}):
            self.assertIsNone(get_llm())

    def test_llm_chains_invoke_model_and_parse_classification(self):
        llm = RunnableLambda(lambda _messages: "damaged")
        classify, escalate, draft_email = _build_llm_chains(llm)

        self.assertEqual(classify.invoke({"report": "The box arrived crushed."}), "damaged")
        self.assertEqual(
            escalate.invoke(
                {
                    "customer_tier": "standard",
                    "category": "lost",
                    "amount": 500,
                    "report": "Shipment not received.",
                }
            ),
            "damaged",
        )
        self.assertEqual(
            draft_email.invoke(
                {
                    "customer_tier": "premium",
                    "category": "delayed",
                    "amount": 50,
                    "report": "Delivery was late.",
                }
            ),
            "damaged",
        )

    def test_unrecognized_model_classification_falls_back_to_unknown(self):
        llm = RunnableLambda(lambda _messages: "I cannot determine the issue.")
        classify, _, _ = _build_llm_chains(llm)

        self.assertEqual(classify.invoke({"report": "Unclear report"}), "unknown")


if __name__ == "__main__":
    unittest.main()
