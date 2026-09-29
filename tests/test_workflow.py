import unittest
from types import SimpleNamespace
from unittest.mock import patch

from patterns.using_tools.graph import build_graph
from patterns.using_tools.nodes import QuestionAnalysis


class FakeLLM:
    def __init__(self, analysis, general_answer="Artificial intelligence is ..."):
        self.analysis = analysis
        self.general_answer = general_answer

    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        if "Classify the user's request" in prompt:
            return self.analysis
        return SimpleNamespace(content=self.general_answer)


class WorkflowTests(unittest.TestCase):
    def test_routes_calculation_to_math_agent(self):
        fake_llm = FakeLLM(
            QuestionAnalysis(intent="math", expression="((10 + 5) / 2) ** 2")
        )
        with patch("patterns.using_tools.nodes.get_llm", return_value=fake_llm):
            result = build_graph().invoke({"question": "Square the average of 10 and 5"})

        self.assertEqual(result["intent"], "math")
        self.assertEqual(result["result"], "56.25")

    def test_routes_general_question_to_fallback(self):
        fake_llm = FakeLLM(QuestionAnalysis(intent="general", expression=""))
        with patch("patterns.using_tools.nodes.get_llm", return_value=fake_llm):
            result = build_graph().invoke({"question": "Define AI."})

        self.assertEqual(result["intent"], "general")
        self.assertEqual(result["result"], "Artificial intelligence is ...")


if __name__ == "__main__":
    unittest.main()