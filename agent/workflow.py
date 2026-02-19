from langgraph.graph import StateGraph, END
from agent.tools import get_logs
from agent.rag import search_docs
from agent.llm import ask_llm
from agent.guardrails import validate_output
from agent.log_parser import parse_logs


class AgentState(dict):
    pass


def retrieve_logs(state):
    print("STEP: retrieve_logs")

    raw_logs = get_logs()

    if not raw_logs:
        print("No logs returned!")
        state["logs"] = []
        return state

    state["logs"] = parse_logs(raw_logs)
    print(f"Parsed events: {len(state['logs'])}")
    return state


def retrieve_context(state):
    print("STEP: retrieve_context")

    query = state.get("query", "")
    state["context"] = search_docs(query)
    return state


def analyze(state):
    print("STEP: analyze")

    query = state.get("query", "")
    logs = state.get("logs", [])
    context = state.get("context", "")

    prompt = f"""
You are a cybersecurity and system reliability expert.

IMPORTANT:
Return ONLY valid JSON.
Do NOT include explanations or extra text.

User Query:
{query}

Parsed Log Events:
{logs[:50]}

Runbook Context:
{context}

Return JSON:

{{
  "summary": "...",
  "root_cause": "...",
  "impact": "...",
  "confidence": "HIGH | MEDIUM | LOW"
}}
"""


    try:
        response = ask_llm(prompt)
        print("LLM RESPONSE:", response)
        state["raw_output"] = response
    except Exception as e:
        print("LLM FAILED:", e)
        state["raw_output"] = ""

    return state


def guardrail_step(state):
    print("STEP: guardrails")

    validated = validate_output(state.get("raw_output", ""))

    print("VALIDATED OUTPUT:", validated)

    state["final"] = validated
    return state


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("logs", retrieve_logs)
    builder.add_node("context", retrieve_context)
    builder.add_node("analyze", analyze)
    builder.add_node("guardrails", guardrail_step)

    builder.set_entry_point("logs")

    builder.add_edge("logs", "context")
    builder.add_edge("context", "analyze")
    builder.add_edge("analyze", "guardrails")
    builder.add_edge("guardrails", END)

    return builder.compile()


graph = build_graph()


def run_agent(query):
    print("RUNNING AGENT with query:", query)

    result = graph.invoke({"query": query})

    print("GRAPH RESULT:", result)

    if result is None:
        return {"final": {"error": "Graph returned None"}}

    return result
