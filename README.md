# 🚀 ScoutMind — AI-Powered Talent Scouting Agent

<div align="center">

![ScoutMind Banner](./assets/ui_screenshot.png)

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green?style=for-the-badge)](https://github.com/langchain-ai/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai)](https://openai.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![AWS ECS](https://img.shields.io/badge/AWS-ECS%20Fargate-FF9900?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com/ecs/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Turn any Job Description into a ranked, outreach-aware candidate shortlist — fully automated.**

[🌐 Live Demo](#-live-demo) · [📘 API Docs](#-api-reference) · [🏗️ Architecture](#-architecture) · [🚀 Quick Start](#-quick-start)

</div>

---

## 🧠 Problem Statement

Hiring the right candidate is **time-consuming, manual, and inefficient**:

| Pain Point | Impact |
|---|---|
| Manual resume screening | Hours wasted per role |
| Skill-to-JD mismatch | Wrong candidates shortlisted |
| No interest evaluation | Offers sent to passive/uninterested candidates |
| Inconsistent follow-ups | Candidates go cold |
| Zero automation | No scalable workflow |

---

## 🎯 What ScoutMind Does

ScoutMind is an AI agent that takes a raw Job Description and:

- ✅ **Parses** the JD into structured requirements (skills, experience, seniority, domain)
- ✅ **Expands** skills dynamically with LLM-generated synonyms (works for any domain — tech, finance, marketing, legal)
- ✅ **Discovers** matching candidates via LLM Generated Keyword filter 
- ✅ **Simulates** personalised outreach and gauges genuine candidate interest
- ✅ **Ranks** candidates by a combined Match + Interest score with full explainability
- ✅ **Exports** a recruiter-ready shortlist CSV

---

## 🖥️ UI Preview

![ScoutMind UI](./assets/ui_screenshot.png)

The recruiter UI shows:
- Live pipeline steps (Parse JD → Expand Skills → Retrieve Talent → Score Fit → Gauge Interest → Rank Shortlist)
- JD input with sample button
- Real-time session tracking
- Candidate result cards with scores and Download CSV

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph 0.2+ |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Backend API** | FastAPI + Uvicorn |
| **Container** | Docker |
| **Cloud** | AWS ECS Fargate + ALB |
| **Registry** | AWS ECR |
| **Storage** | AWS S3 |
| **Secrets** | AWS Secrets Manager |
| **Monitoring** | AWS CloudWatch |
| **CI/CD** | GitHub Actions |

---

## 🏗️ Architecture

### LangGraph Agent Architecture

![LangGraph Architecture](./assets/langgraph_arch.png)

The core of ScoutMind is a **stateful LangGraph agent** with 6 nodes connected as a directed graph. State is checkpointed after each node, enabling resume on failure.

```
START
  ↓
1. JD Parser          → Extract role, skills, experience, seniority
  ↓
2. Skill Expander     → LLM generates dynamic synonym map (1 API call, cached)
  ↓
3. Candidate Retriever → LLM generated keyword Filter
  ↓
4. Outreach Agent     → Simulate recruiter message + candidate reply + interest score
  ↓
5. Re-ranker          → Final Score = 0.6 × Match + 0.4 × Interest, generate summary
  ↓
END → Ranked shortlist CSV
```

**Why LangGraph over a plain pipeline?**

| Feature | Plain Pipeline | LangGraph |
|---|---|---|
| State management | Manual | Built-in TypedDict |
| Failure recovery | Restart from zero | Resume from checkpoint |
| Conditional branching | Hard to add | Native edge conditions |
| Observability | Print statements | Node-level tracing |
| Scalability | Coupled | Modular nodes |

---

### AWS Cloud Architecture

![AWS Architecture](./assets/aws_arch.png)

```
User / Web Client
     │
     ▼ HTTP :80
Application Load Balancer (scoutmind-alb)
     │
     ▼ Forward Traffic
ECS Fargate Service (Desired Count: 2, Multi-AZ)
     ├── ECS Task A (FastAPI :8000)
     └── ECS Task B (FastAPI :8000)
           │
           ├──► OpenAI API (LLM + Embeddings)
           ├──► AWS S3 (Logs, CSV exports, JD files)
           └──► AWS Secrets Manager (API keys)

Supporting Services:
  - ECR: Docker image registry
  - CloudWatch: Logs, metrics, alarms
  - IAM: Least-privilege execution + task roles
  - GitHub Actions: CI/CD (build → ECR → ECS deploy)
```

**Health Check:** `GET /health`
**API Docs:** `GET /docs` (Swagger UI)

---

## 📂 Project Structure

```
ScoutMind/
│
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI app, UI serving, API routes
│   ├── main.py             # Agent runner, CSV export, S3 upload handling
│   └── schemas.py          # Pydantic request/response models
│
├── graph/
│   ├── __init__.py
│   ├── graph_builder.py    # LangGraph DAG definition and routing
│   ├── memory.py           # In-memory checkpointer helper
│   └── state.py            # AgentState and output TypedDicts
│
├── nodes/
│   ├── __init__.py
│   ├── jd_parser.py        # Node 1: Parse JD → structured dict
│   ├── skill_expander.py   # Node 2: Expand required skills
│   ├── candidate_retriever.py # Node 3: Load/filter candidates
│   ├── scorer.py           # Node 4: LLM candidate scoring
│   ├── outreach_agent.py   # Node 5: Simulate outreach + interest score
│   └── reranker.py         # Node 6: Final rank + conversation summary
│
├── llm/
│   ├── __init__.py
│   ├── jd_parser_chain.py
│   ├── skill_expander_chain.py
│   ├── scoring_chain.py
│   ├── outreach_chain.py
│   └── summary_chain.py
│
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Session log files
│   └── s3_utils.py         # S3 upload/download helpers
│
├── frontend/
│   ├── index.html          # Browser UI
│   ├── script.js           # API calls and UI interactions
│   └── styles.css          # UI styling
│
├── assets/
│   ├── architecture_image.png
│   ├── laggraph_agent.png
│   └── ui_image.png
│
├── notebook/               # Experimentation notebooks/data
├── logs/                   # Auto-created: one .log file per session
├── exports/                # Auto-created: one .csv shortlist per run
├── temp/                   # Auto-created: downloaded candidate CSV
│
├── .github/workflows/
│   └── deploy.yaml         # GitHub Actions deployment workflow
│
├── main.py                 # CLI test entry point
├── Dockerfile
├── requirements.txt
├── task-definition.json
├── ecs-trust-policy.json
└── README.md
```

---

## 🔗 Node-by-Node Breakdown

### Node 1 — JD Parser
Uses GPT-4o-mini with structured output to extract:
- `role`, `location`, `seniority` (junior/mid/senior)
- `experience_years`, `domain`
- `required_skills` (list), `preferred_skills` (list)

### Node 2 — Skill Expander
One LLM call per JD (cached with `lru_cache`). Generates synonyms dynamically for any skill in any domain:
```
"machine learning" → ["ml", "ai/ml", "scikit-learn", "deep learning", "predictive modeling"]
"seo"              → ["search engine optimization", "on-page seo", "serp", "keyword research"]
```

### Node 3 — Candidate Filter & Scorer (3 stages)
| Stage | Method | Cost | Cuts |
|---|---|---|---|
| Keyword filter | Regex + synonyms | $0 | 1000 → ~40 |

### Node 4 — Outreach Agent
- Builds personalised recruiter opening message per candidate
- 20% ghost rate simulated (realistic)
- GPT-4o-mini plays candidate persona, generates natural reply
- Scores interest 0–100 from conversation

### Node 5 — Re-ranker
```
Final Score = 0.6 × Match Score + 0.4 × Interest Score
```
- Status labels: `High Priority (≥85)` / `Consider (≥65)` / `Low Priority (<65)`
- LLM generates 1–2 line conversation summary per candidate
- Exports `outputs/shortlist_<session_id>.csv`

---

## 🧩 State & Memory

Every run gets a unique `session_id` (UUID). `AgentState` carries all data between nodes:

```python
class AgentState(TypedDict):
    session_id: str
    jd_raw: str
    jd_parsed: dict
    skill_synonyms: dict
    candidates_raw: list
    scored_candidates: list
    final_output: list
    error: Optional[str]
    failed_node: Optional[str]
    node_status: dict
```

LangGraph checkpoints state after each node using `MemorySaver`. To resume a failed run:
```bash
python main.py --session <prior-session-uuid>
```
For persistent memory across restarts, swap `MemorySaver` for `SqliteSaver`.

---

## 🛡️ Error Handling & Logging

**Every node is wrapped with `@node_guard`:**
- Catches all exceptions, writes full traceback to log
- Sets `state["error"]` and `state["failed_node"]`
- Downstream nodes skip gracefully (no crash)
- Graph always reaches `END` cleanly

**Per-session log files** written to `logs/<session_id>.txt`:
```
[2024-04-25 10:30:01 UTC] [INFO]  [jd_parser] Starting
[2024-04-25 10:30:02 UTC] [INFO]  [jd_parser] Completed — role: Data Scientist
[2024-04-25 10:30:04 UTC] [ERROR] [candidate_filter] OpenAI timeout
    --- traceback ---
    ...
```

---

## 🚀 Quick Start

### Local

```bash
git clone https://github.com/yourusername/scoutmind
cd scoutmind
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Run CLI
python main.py --jd path/to/jd.txt

# Run API server
uvicorn app.api:app --reload --port 8000
```

### Docker

```bash
docker build -t scoutmind .
docker run -p 8000:8000 --env-file .env scoutmind
```

---

## 📘 API Reference

### `POST /scout`

```bash
curl -X POST http://localhost:8000/scout \
  -H "Content-Type: application/json" \
  -d '{
    "jd_text": "Looking for a senior Data Scientist with Python, ML, and SQL. 3+ years required.",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "session_id": "abc-123",
  "final_answer": "Top 5 candidates ranked by combined score...",
  "candidates": [
    {
      "name": "Rahul Mohalder",
      "match_score": 85,
      "interest_score": 70,
      "final_score": 79.0,
      "status": "Consider",
      "explanation": "Matched: Python, SQL, ML. Missing: Semiconductor experience.",
      "conversation_summary": "Expressed interest, requested more details about team."
    }
  ]
}
```

### `GET /health`

```json
{ "status": "ok" }
```

---

## 🌍 Live Demo

**Public URL:** `http://scoutmind-alb-1074356397.us-east-1.elb.amazonaws.com/`

**Swagger Docs:** `http://<ALB_URL>/docs`

---

## ⚠️ Edge Cases Handled

- ✅ No matching candidates found → threshold lowered automatically
- ✅ Candidate does not respond → 20% ghost rate, scored as 0 interest
- ✅ Missing skills in JD → defaults and fallbacks applied
- ✅ OpenAI API failure → node_guard catches, logs, graph continues
- ✅ Partial candidate data → graceful field defaults

---

## 🔐 Security

- API keys stored in **AWS Secrets Manager** (never hardcoded)
- **IAM roles** with least-privilege (execution role + task role)
- ECS security group allows **only ALB traffic** on port 8000
- No secrets in Docker image or GitHub repo

---

## 📈 Future Improvements

- [ ] Real email / LinkedIn outreach integration
- [ ] Vector DB (ChromaDB / Pinecone) for candidate store
- [ ] Resume PDF parsing
- [ ] Multi-agent system with specialised sub-agents
- [ ] Real-time UI with WebSocket pipeline streaming
- [ ] Feedback loop — recruiter ratings improve scoring weights

---

## 👨‍💻 Author

**Dushyant Kumar Verma**

Built for **Catalyst Hackathon** — Deccan AI

---

## ⭐ Support

If you found this useful, give it a ⭐ on GitHub!
