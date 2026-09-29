from typing import TypedDict

class AgentState(TypedDict): #Agentic AI workflow memory
    question: str
    expression: str
    result: str