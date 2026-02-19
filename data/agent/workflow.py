from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from agent.tools import get_logs
from agent.rag import search_docs
from agent.llm import ask_llm
from agent.guardrails import validate_output
from agent.log_parser import parse_logs

from collections import defaultdict
import re


# ---------------- STATE ---------------- #

class AgentState(TypedDict, total=False):
    query: str
    logs: List[Dict[str, Any]]
    context: List[str]
    raw_output: str
    final: Dict[str, Any]
    suspicious_activity: List[Dict[str, Any]]


# ---------------- RETRIEVE ---------------- #

def retrieve_logs(state: AgentState):
    raw_logs = get_logs()

    # ensure raw logs are separated correctly
    raw_logs = raw_logs.replace(" ssh2 ", " ssh2\n")
    raw_logs = raw_logs.replace(" HTTP ", " HTTP\n")

    logs = parse_logs(raw_logs) if raw_logs else []

    print(f"Logs loaded: {len(logs)}")

    state["logs"] = logs
    return state


def retrieve_context(state: AgentState):
    state["context"] = search_docs(state.get("query", ""))
    return state


# ---------------- DETECTION ENGINE ---------------- #

def detect_suspicious_activity(logs):
    """
    Robust SSH brute-force detection that works with:
    - concatenated logs
    - mixed syslog formats
    - missing timestamps
    - varied spacing
    """

    ip_regex = r'(?:\d{1,3}\.){3}\d{1,3}'
    time_regex = r'[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}'
    user_regex = r'(?:invalid user|for)\s+(\w+)'

    ip_data = defaultdict(lambda: {
        "attempts": 0,
        "users": set(),
        "timestamps": []
    })

    for entry in logs:
        msg = entry["message"]

        # detect failed ssh attempts
        if "Failed password" not in msg:
            continue

        ips = re.findall(ip_regex, msg)
        users = re.findall(user_regex, msg)
        times = re.findall(time_regex, msg)

        for ip in ips:
            ip_data[ip]["attempts"] += 1

            if users:
                ip_data[ip]["users"].update(users)

            if times:
                ip_data[ip]["timestamps"].extend(times)

    suspicious = []

    for ip, data in ip_data.items():
        if data["attempts"] >= 2:   # low threshold for demo reliability
            suspicious.append({
                "ip": ip,
                "attempts": data["attempts"],
                "first_seen": data["timestamps"][0] if data["timestamps"] else "unknown",
                "last_seen": data["timestamps"][-1] if data["timestamps"] else "unknown",
                "users_targeted": sorted(list(data["users"])),
                "activity": "SSH brute-force login attempts",
                "reason": "Repeated failed SSH login attempts detected"
            })

    return suspicious


# ---------------- ANALYZE ---------------- #

def analyze(state: AgentState):
    logs = state.get("logs", [])

    suspicious_activity = detect_suspicious_activity(logs)

    print(f"Suspicious IPs detected: {len(suspicious_activity)}")

    severity = "LOW"
    if suspicious_activity:
        severity = "HIGH"

    prompt = f"""
You are a senior cybersecurity analyst.

Create a clear operational security finding.

Include:
• suspicious IP addresses
• what activity was detected
• when it occurred
• why it is suspicious
• recommended mitigation

User Question:
{state.get("query")}

Suspicious Activity:
{suspicious_activity}

Severity Level: {severity}

Return ONLY valid JSON:

{{
  "summary": "...",
  "root_cause": "...",
  "impact": "...",
  "confidence": "HIGH | MEDIUM | LOW"
}}
"""

    try:
        response = ask_llm(prompt)
        state["raw_output"] = response.strip()
    except Exception:
        state["raw_output"] = ""

    state["suspicious_activity"] = suspicious_activity
    return state


# ---------------- GUARDRAILS ---------------- #

def guardrail_step(state: AgentState):
    validated = validate_output(state.get("raw_output", ""))

    # attach structured detection for Streamlit UI
    validated["suspicious_activity"] = state.get("suspicious_activity", [])

    state["final"] = validated
    return state


# ---------------- GRAPH ---------------- #

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


def run_agent(query: str):
    query = query.replace("“", "").replace("”", "")

    result = graph.invoke({"query": query})

    return result if result else {"final": {"error": "No result returned"}}
