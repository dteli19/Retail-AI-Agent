# 🛒 Retail Analytics AI Agent

An agentic AI system that answers natural language questions about retail data — autonomously querying Databricks Delta Tables, reasoning over results, and delivering consulting-quality insights.

**Built with:** LangChain · Groq Llama 3 · Databricks · Streamlit

🔗 [Live Streamlit App](https://retail-ai-agent-9zx9rruldn4pb5umycmvpn.streamlit.app/)

---

## 🎯 Business Impact

Traditional retail analytics requires a data analyst to manually write SQL queries, pull reports, and interpret results — a process that takes hours or days. This AI agent compresses that cycle to seconds.

**Key business outcomes this agent enables:**

- **Faster decisions** — business users get instant answers without waiting for analyst availability
- **Democratized data access** — non-technical stakeholders can query complex data in plain English
- **Proactive retention** — agent identifies at-risk customer segments and recommends targeted campaigns
- **Revenue optimization** — instantly surfaces top-performing categories, stores, and promotions
- **Marketing ROI clarity** — ranks promotions by ROI so budget is allocated to what actually works

In a retail consulting engagement, this type of agent reduces ad-hoc reporting time by an estimated 60-70%, freeing analysts to focus on strategic work rather than routine data pulls.

---

## 🏗️ Architecture

```
User Question (plain English)
         │
         ▼
┌─────────────────────┐
│   Streamlit UI      │  ← Web interface for chat + charts
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   LangChain Agent   │  ← Orchestrates reasoning loop
│   (ReAct Pattern)   │     Thought → Action → Observation
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Groq LLM          │  ← Llama 3 powers reasoning
│   (Llama 3)         │     and insight generation
└─────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────────┐ ┌─────────────┐
│ inspect  │ │ query_data  │  ← Agent tools called
│ _data    │ │             │     autonomously
└──────────┘ └─────────────┘
         │
         ▼
┌─────────────────────┐
│ Databricks SQL      │  ← Cloud data warehouse
│ Warehouse           │     (Serverless)
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Delta Tables        │  ← customers, transactions,
│ (Unity Catalog)     │     promotions
└─────────────────────┘
```

---

## 🤖 What Makes It Agentic

This is not a simple chatbot or a hardcoded SQL report generator. It is an autonomous agent — meaning it decides what to do at each step without being explicitly programmed with a fixed sequence of actions.

**The ReAct reasoning loop in action:**

```
User: "Which promotions are giving the best ROI?"

Thought: I need to understand the promotions dataset first.
Action: inspect_data("promotions")
Observation: 50 rows, columns: promo_name, channel, revenue_generated, cost...

Thought: Now I will query ROI for each individual promotion.
Action: query_data("top promotions ranked by ROI")
Observation: Multi-channeled hub ROI: 3964%, Advanced middleware ROI: 3288%...

Thought: I have the data. Now I will generate a business insight.
Action: generate_insight("Top promotions by ROI are...")
Observation: Executive summary + recommendations generated.

Final Answer: Consulting-quality report delivered to user
```

Nobody programmed "inspect first, then query, then generate insight." The agent reasoned its way to that sequence. That autonomy is what makes it agentic.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Chat interface and Plotly charts |
| Orchestration | LangChain | Agent loop, tool management, ReAct prompting |
| LLM | Groq (Llama 3) | Reasoning and insight generation |
| Data Warehouse | Databricks SQL Warehouse | Serverless query execution |
| Data Storage | Delta Tables (Unity Catalog) | customers, transactions, promotions |
| Language | Python 3.14 | Core application |
| Visualization | Plotly Express | Interactive charts |

---

## 📁 Project Structure

```
retail-ai-agent/
├── agent.py                 ← Main agent — wires LangChain + Groq + tools
├── tools.py                 ← 3 agent tools: inspect, query, generate insight
├── databricks_connector.py  ← Databricks SQL connection and query runner
├── prompts.py               ← System prompt and ReAct reasoning template
├── mock_data.py             ← Generates realistic retail dataset
├── streamlit_app.py         ← Web UI with chat, metrics, and charts
├── data/                    ← CSV exports uploaded to Databricks
│   ├── customers.csv
│   ├── transactions.csv
│   └── promotions.csv
├── requirements.txt         ← Python dependencies
├── .env                     ← API keys (not committed to GitHub)
└── .gitignore               ← Excludes .env and venv
```

---

## 🧠 Code Walkthrough

### mock_data.py
Generates three realistic retail datasets using the Faker library. Creates 200 customers with RFM segments (Champions, Loyal, At Risk, Lost, New), 1000 purchase transactions across 5 categories and 5 stores, and 50 marketing promotions across 5 channels. Data is exported as CSV and uploaded to Databricks Delta Tables.

### databricks_connector.py
Establishes a secure connection to Databricks SQL Warehouse using the databricks-sql-connector library. Reads credentials from .env. Exposes a run_query() function that executes any SQL against Databricks and returns column names and rows — used by all three agent tools.

### prompts.py
Contains two prompts. The SYSTEM_PROMPT defines the agent's role, available datasets, tools, and rules — always inspect first, think step by step, end with a business insight. The REACT_PROMPT is the reasoning template that forces the agent to think before acting on every question.

### tools.py
Three LangChain tools decorated with @tool that the agent calls autonomously:
- **inspect_data** — queries Databricks for schema, row count, and sample data. Agent always calls this first to understand the data before querying.
- **query_data** — routes plain English queries to the correct SQL against Databricks. Handles 8 query types: segments, regions, categories, stores, promotions, discounts, monthly trends, and churn.
- **generate_insight** — structures data findings into an executive summary, top 3 key findings, and two business recommendations.

### agent.py
Wires everything together using LangChain's AgentExecutor with a ReAct prompt. Uses Groq's Llama 3 at temperature=0 for deterministic factual answers. verbose=True shows the full reasoning chain in the terminal. max_iterations=15 prevents infinite loops. Includes retry logic for rate limit handling.

### streamlit_app.py
Builds the web UI with live metrics pulled from Databricks on load, a chat interface with full session history, automatic Plotly chart generation based on question keywords, and a sidebar with example questions and tech stack.

---

## 🚀 Setup and Run

### Prerequisites
- Python 3.9+
- Groq account (free) at console.groq.com
- Databricks account (free Community Edition) at community.cloud.databricks.com

### Installation

```bash
git clone https://github.com/dteli19/Retail-AI-Agent.git
cd Retail-AI-Agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a .env file in the project root:

```
GROQ_API_KEY=your_groq_api_key
DATABRICKS_HOST=your_databricks_host
DATABRICKS_HTTP_PATH=your_http_path
DATABRICKS_TOKEN=your_databricks_token
```

### Generate and Upload Data

```bash
python mock_data.py
```

Then upload the three CSV files from the data/ folder to Databricks as Delta Tables in the retail_agent schema.

### Run the App

```bash
streamlit run streamlit_app.py
```

---

## 💬 Example Questions

| Category | Question |
|----------|---------|
| Customers | Which customer segments have the most customers? |
| Customers | Which region has the most at risk customers? |
| Customers | What gender purchases the most? |
| Sales | What are the top performing product categories by revenue? |
| Sales | Which store has the highest revenue? |
| Sales | Show me the monthly revenue trend |
| Promotions | Which promotions are giving the best ROI? |
| Promotions | How is each marketing channel performing? |
| Discounts | What is the impact of discounts on revenue? |
