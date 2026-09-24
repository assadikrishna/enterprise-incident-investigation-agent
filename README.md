# Enterprise Incident Investigation Agent

An AI-powered incident investigation agent that uses bounded ReAct reasoning, short-term memory, semantic retrieval, and external tools to help engineers investigate application incidents.

The project includes a Python-based ReAct implementation, LangGraph workflow orchestration, and LangChain integration with OpenRouter. The agent retrieves evidence from synthetic incident records and application logs, with access to runbooks, knowledge-base articles, and historical incidents through semantic RAG when additional context is needed.

Deterministic guardrails enforce evidence requirements and investigation limits. The agent produces investigation summaries that distinguish observed evidence from unverified root-cause hypotheses, while human engineers retain responsibility for production-impacting decisions.


---

## Project Purpose

This repository contains my capstone project for the **Agentic AI Program: Building Autonomous Systems for Real-World Applications**.

The project was developed incrementally throughout the course, with each module informing the final architecture and implementation. The final system focuses on grounded incident investigation, bounded agent behavior, retrieval verification, and human oversight.

---

## Project Status

The Enterprise Incident Investigation Agent includes:

- A bounded ReAct investigation agent implemented in Python.
- LangGraph-based investigation workflow orchestration.
- LangChain ChatOpenAI integration with OpenRouter.
- LangChain prompt templates and LCEL-based prompt execution.
- Semantic RAG over synthetic runbooks, knowledge-base articles, and historical incidents.
- Deterministic guardrails, minimum-evidence checks, and human-in-the-loop escalation.
- Automated tests and end-to-end investigation demonstrations.

---

## Current Capabilities

- Bounded ReAct-style reasoning loop
- Python-based ReAct investigation orchestration
- LangGraph-based investigation workflow orchestration
- LangChain prompt templates and LCEL-based model execution
- OpenRouter integration through LangChain ChatOpenAI
- Separate runnable demos for the original ReAct, LangGraph, and LangChain + LangGraph implementations
- Short-term working memory for the active investigation
- Evidence-only investigation memory for accepted tool observations
- Incident record retrieval
- Direct log search
- Runbook retrieval
- Semantic RAG over runbooks, knowledge-base articles, and historical incidents
- FAISS-based vector similarity search
- Retrieval relevance thresholding
- Evidence-consistency classification for retrieved documents
- Filtering of rejected retrieval results
- Deterministic parser guardrail that rejects fabricated ReAct observations
- Minimum-evidence guardrail before allowing a final conclusion
- Maximum-step reasoning limit
- Human-in-the-loop escalation when the reasoning budget is exhausted
- OpenRouter LLM integration with retries and request timeouts
- Investigation summaries that distinguish observed failure mechanisms from unverified root-cause hypotheses
- Human approval required for production-impacting decisions

---

## Project Structure

```text
enterprise-incident-investigation-agent/
│
├── data/
│   └── synthetic/              # Synthetic incident and knowledge data
│
├── docs/
│   ├── architecture.md
│   ├── design-decisions.md
│   └── project-charter.md
│
├── evaluation/
│   ├── evaluation-plan.md
│   ├── results.md
│   └── traces/                 # Saved evaluation traces
│
├── examples/
│   ├── demo_openrouter.py      # Original ReAct + OpenRouter demo
│   ├── demo_langgraph_openrouter.py
│   ├── demo_langchain_langgraph.py
│   ├── demo_react.py
│   ├── demo_verification.py
│   └── demo_max_steps_hitl.py
│
├── src/
│   ├── agent.py                # Original bounded ReAct agent
│   ├── graph/
│   │   ├── state.py            # LangGraph investigation state
│   │   ├── nodes.py            # Reasoning and tool execution nodes
│   │   └── workflow.py         # LangGraph workflow orchestration
│   ├── langchain_llm.py        # LangChain + OpenRouter integration
│   ├── llm.py                  # Original OpenRouter integration
│   ├── protocol.py             # Shared ReAct prompt and parser
│   ├── retrieval.py            # Semantic retrieval and relevance filtering
│   ├── tools.py                # Investigation tools
│   └── verification.py         # Retrieved-evidence verification
│
├── tests/                      # Automated tests
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository and create a Python virtual environment.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```text
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

The model can be replaced with another supported OpenRouter model.

Do not commit the `.env` file or API keys to source control.

---

## Running the Demo

The repository provides three ways to run an LLM-powered incident investigation.

### 1. Original ReAct Agent

Runs the Python-orchestrated ReAct investigation agent using OpenRouter.

```bash
python -m examples.demo_openrouter
```

### 2. LangGraph Agent

Runs the investigation using LangGraph for state management and workflow orchestration, with the existing OpenRouter integration.

```bash
python -m examples.demo_langgraph_openrouter
```

### 3. LangChain + LangGraph Agent

Runs the LangGraph investigation workflow using LangChain prompt templates and `ChatOpenAI` to access OpenRouter.

```bash
python -m examples.demo_langchain_langgraph
```

### Investigation Workflow

Depending on the available evidence and the agent's selected actions, an investigation may include:

1. Retrieving incident details.
2. Searching application logs for direct evidence.
3. Consulting the relevant service runbook.
4. Using semantic RAG to retrieve supporting knowledge-base articles, runbooks, or historical incidents when additional context is needed.
5. Verifying retrieved evidence before accepting it.
6. Enforcing minimum-evidence requirements before allowing a final conclusion.
7. Escalating to human review if the reasoning-step limit is reached.
8. Producing an investigation summary that identifies supporting evidence and remaining uncertainties.

The original ReAct implementation also uses a deterministic parser to reject model-generated observations that were not returned by tools.

Because the LLM is accessed through OpenRouter, execution time and availability can vary by provider and model.

---

## Design Principles

The implementation follows several architectural principles:

- Ground conclusions in evidence returned by tools rather than model-generated observations.
- Separate observed evidence from hypotheses and inferred explanations.
- Give the agent reasoning autonomy within an investigation while limiting its operational authority.
- Use deterministic runtime guardrails for boundaries that should not depend on LLM compliance.
- Verify retrieved knowledge before allowing it to influence the investigation.
- Require a minimum factual basis before allowing a final conclusion.
- Bound investigations with a maximum reasoning-step limit.
- Escalate unresolved investigations to a human rather than forcing a conclusion.
- Require human approval for production-impacting decisions.

---

## Evaluation

The results below describe the original Python-orchestrated ReAct capstone implementation. The LangGraph and LangChain integrations have also been exercised through live demonstrations and automated workflow tests, but the original end-to-end evaluation metrics should not be interpreted as measurements of those integrations.

The original capstone implementation was evaluated using four scenarios covering end-to-end investigation, retrieval verification, minimum-evidence enforcement, and human-in-the-loop escalation.

In three formal end-to-end investigation runs:

- 2 of 3 runs completed successfully (66.7% task completion).
- The two completed runs averaged 187.35 seconds end-to-end.
- All three runs contained at least one attempt by the LLM to generate an observation without executing the corresponding tool.
- The deterministic ReAct parser rejected those responses, resulting in zero accepted fabricated observations across the three runs.
- The unsuccessful run terminated because of repeated OpenRouter rate-limit errors.

Targeted tests also passed for retrieval relevance filtering and verification, the minimum-evidence conclusion guardrail, and maximum-step human-in-the-loop escalation.

Detailed evaluation criteria, results, and execution traces are available in the `evaluation/` directory.

---

## Technologies

- Python
- LangGraph
- LangChain
- OpenRouter
- OpenAI Python SDK
- SentenceTransformers
- FAISS
- python-dotenv
- pytest

---

## License

This repository is intended for educational purposes as part of the Agentic AI Program capstone project.