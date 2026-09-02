# Enterprise Incident Investigation Agent

An AI-powered incident investigation agent that uses a bounded ReAct reasoning loop, short-term memory, semantic retrieval, and external tools to help engineers investigate production incidents.

The agent gathers evidence from incident records, application logs, runbooks, knowledge-base articles, and historical incidents before producing evidence-based investigation summaries. Deterministic guardrails restrict how model-generated information can enter the accepted evidence, while human engineers remain responsible for production-impacting decisions.

---

## Project Purpose

This repository contains my capstone project for the **Agentic AI Program: Building Autonomous Systems for Real-World Applications**.

The project was developed incrementally throughout the course, with each module informing the final architecture and implementation. The final system focuses on grounded incident investigation, bounded agent behavior, retrieval verification, and human oversight.

---

## Project Status

Final capstone implementation and evaluation complete.

---

## Current Capabilities

- Bounded ReAct-style reasoning loop
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
- Evidence-based investigation summaries that distinguish observed evidence from remaining hypotheses
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
│   ├── evaluation-plan.md      # Evaluation scenarios and criteria
│   ├── results.md              # Evaluation results and metrics
│   └── traces/                 # Saved evaluation traces
│
├── examples/
│   ├── demo_openrouter.py      # End-to-end OpenRouter demo
│   ├── demo_react.py
│   ├── demo_verification.py
│   └── demo_max_steps_hitl.py
│
├── src/
│   ├── agent.py                # Bounded ReAct reasoning loop and guardrails
│   ├── llm.py                  # OpenRouter integration and retry handling
│   ├── retrieval.py            # Semantic retrieval and relevance filtering
│   ├── tools.py                # Investigation tools
│   └── verification.py         # Retrieved-evidence verification
│
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

Run the end-to-end OpenRouter-powered investigation demo:

```bash
python -m examples.demo_openrouter
```

The demo exercises the implemented investigation workflow, including:

1. Retrieving incident details.
2. Searching direct application logs.
3. Consulting the service runbook.
4. Performing semantic retrieval over the knowledge corpus.
5. Verifying retrieved evidence before use.
6. Rejecting malformed ReAct responses that contain fabricated observations.
7. Enforcing minimum-evidence requirements before allowing a final conclusion.
8. Escalating to human review if the reasoning-step limit is reached.
9. Producing a final investigation summary when sufficient evidence is available.

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

The final system was evaluated using four scenarios covering end-to-end investigation, retrieval verification, minimum-evidence enforcement, and human-in-the-loop escalation.

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
- OpenRouter
- OpenAI Python SDK
- SentenceTransformers
- FAISS
- python-dotenv

---

## Future Work

Potential extensions beyond the current capstone implementation include:

- LangGraph-based workflow orchestration
- Multi-agent investigation with specialized evidence, hypothesis, and verification roles
- Tree-of-Thought-style exploration of competing root-cause hypotheses
- Integration with real enterprise incident-management, logging, and knowledge systems
- More extensive retrieval-threshold calibration and evaluation datasets
- Improved handling of external LLM provider failures
- Repeated-action detection and investigation-loop prevention
- Longer-term memory for reusable incident knowledge

---

## License

This repository is intended for educational purposes as part of the Agentic AI Program capstone project.