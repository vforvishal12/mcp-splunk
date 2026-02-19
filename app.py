import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()   # ← loads .env variables

from agent.workflow import run_agent

st.title("AI Log Analyzer")

query = st.text_input("Ask about system logs")

if st.button("Analyze") and query:
    result = run_agent(query)

    if result and "final" in result:
        st.json(result["final"])
    else:
        st.error("Agent failed to return a valid response.")
        st.write(result)
