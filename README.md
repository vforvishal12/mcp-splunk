# MCP Splunk — Full Setup & Architecture Guide

This guide explains:

• utilities & frameworks used  
• how each component fits in the architecture  
• step‑by‑step Windows local setup  
• how MCP, RAG, LangGraph, Guardrails & LLM integrate  
• basic → advanced usage flow  

---

# 🧩 Architecture & Technology Flow

```
User → Streamlit UI → LangGraph Agent

            │
            ▼
   ┌────────────────────────────┐
   │     AGENT ORCHESTRATION    │
   │        LangGraph           │
   └────────────┬───────────────┘
                │
   ┌────────────┼─────────────┐
   ▼            ▼             ▼
Log Fetch    Runbook RAG   Detection Engine
(MCP API)    (Vector DB)   (Pattern Logic)

   │            │             │
   └────────────┴─────────────┘
                ▼
         LLM Reasoning Layer
        (OpenRouter / Llama3)

                ▼
          Guardrails Validation
             (Pydantic)

                ▼
          Structured Response
```

---

# 🧰 Utilities & Frameworks Used

## Core Runtime

### Python 3.10+
Primary runtime for orchestration and services.

---

## LLM Layer

### OpenRouter + Llama‑3
Used for reasoning over logs and generating security findings.

---

## LangChain Ecosystem

### LangChain
Provides embedding and vector search integration.

### LangGraph
Used for deterministic agent orchestration.

✔ stateful workflows  
✔ branching logic  
✔ production reliability  

### LangSmith (Optional)
Observability & debugging for agent flows.

---

## RAG Stack

### SentenceTransformers
Creates semantic embeddings.

Model:
```
all-MiniLM-L6-v2
```

### ChromaDB
Local vector database storing runbook embeddings.

---

## MCP Service Layer

### FastAPI
Provides log access endpoints.

Simulates enterprise log providers like Splunk or Elastic.

---

## Guardrails

### Pydantic
Validates LLM output structure.

Prevents malformed responses.

---

## Detection Engine

Custom Python detection for:

✔ SSH brute force attempts  
✔ suspicious IP activity  

---

# 🖥️ Windows Local Setup

## 1️⃣ Install Python

Verify:

```
python --version
```

---

## 2️⃣ Clone Repo

```
git clone https://github.com/vforvishal12/mcp-splunk.git
cd mcp-splunk
```

---

## 3️⃣ Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

---

## 4️⃣ Install Dependencies

```
pip install -r requirements.txt
```

If needed:

```
pip install streamlit fastapi uvicorn requests python-dotenv
pip install langchain langgraph chromadb sentence-transformers
pip install openai pydantic
```

---

## 5️⃣ Environment Variables

Create `.env`

```
OPENAI_API_KEY=your_key
```

---

## 6️⃣ Build Vector DB

Run once:

```
python
```

```python
from agent.rag import build_vector_db
build_vector_db()
exit()
```

---

## 7️⃣ Start MCP Server

```
uvicorn mcp_server:app --port 9000
```

Verify:

http://localhost:9000/service_health

---

## 8️⃣ Launch App

```
streamlit run app.py
```

Open:

http://localhost:8501

---

# 🔄 Execution Flow

1. User submits query  
2. Agent fetches logs via MCP  
3. Logs parsed & categorized  
4. Threat detection executed  
5. Runbook context retrieved (RAG)  
6. LLM generates security analysis  
7. Guardrails validate output  
8. Structured results displayed  

---

# 🧠 Basic vs Advanced Usage

## Basic
✔ run locally  
✔ detect suspicious activity  

## Advanced
✔ integrate Splunk/Elastic  
✔ stream logs via Kafka  
✔ enable LangSmith tracing  
✔ deploy via Docker & Kubernetes  

---

# 🚀 Production Upgrade Path

1. Replace file logs → streaming ingestion  
2. deploy vector DB remotely  
3. enable SIEM alerting  
4. multi-host correlation  

---
