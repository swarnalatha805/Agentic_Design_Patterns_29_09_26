from typing import Literal

from pydantic import BaseModel, Field

from config.llm import get_llm
from tools.calculator import calculator
from .state import AgentState


class QuestionAnalysis(BaseModel):
    intent: Literal["math", "general"] = Field(
        description="Use math only when the user asks for a numerical calculation."
    )
    expression: str = Field(
        description="A calculator expression for math requests; empty for general questions."
    )


def reasoning_agent(state: AgentState):
    prompt = f"""
Classify the user's request and prepare it for the correct workflow path.

Choose math only when the user asks for a numerical calculation, including
arithmetic word problems, percentages, averages, powers, or evaluating an
expression. For math, provide only a valid arithmetic expression using numbers
and +, -, *, /, //, %, and **. Do not include Python functions or other code.

Choose general for definitions, explanations, opinions, and all requests that
do not need a numerical calculation. For general requests, leave expression
empty. Examples: "What is 7 times 8?" is math; "Define AI." is general.

User request: {state['question']}
"""
    analysis = get_llm().with_structured_output(QuestionAnalysis).invoke(prompt)
    return {
        "intent": analysis.intent,
        "expression": analysis.expression if analysis.intent == "math" else "",
    }


def math_agent(state: AgentState):
    result = calculator(state["expression"])
    return {"result": result}


def fallback_agent(state: AgentState):
    prompt = f"""
Answer the user directly and clearly. Be concise but include enough context to
be useful. Do not try to turn the request into a calculator expression.

User request: {state['question']}
"""
    response = get_llm().invoke(prompt)
    return {"result": response.content}