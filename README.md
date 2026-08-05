# Enterprise Incident Investigation Agent

An AI-powered incident investigation agent that uses a ReAct reasoning loop, short-term memory, and external tools to help engineers investigate production incidents. The agent gathers evidence from incident records, logs, and runbooks before generating evidence-based recommendations while keeping human engineers responsible for production decisions.

---

## Project Purpose

This repository contains my capstone project for the **Agentic AI Program: Building Autonomous Systems for Real-World Applications**. The project is developed incrementally throughout the course, with each module introducing new agent capabilities and architectural improvements.

---

## Project Status

**Current Phase:** Module 2 – ReAct Agent with OpenRouter Integration

### Milestones

- ✅ Capstone Checkpoint 1.1 – Project Scoping and Initial Agent Design
- ✅ Capstone Checkpoint 2.1 – Agent Architecture, Memory, and External Tools
- ⏳ Checkpoint 3.1 – Retrieval-Augmented Generation (RAG)
- ⏳ Checkpoint 4.1 – Tree-of-Thought Reasoning
- ⏳ Checkpoint 5.1 – Multi-Agent Workflow
- ⏳ Checkpoint 6.1 – Evaluation and Guardrails
- ⏳ Final Capstone Report and Presentation

---

## Current Capabilities

- ReAct-style reasoning loop
- Short-term investigation memory
- Incident record retrieval
- Log search
- Runbook retrieval
- OpenRouter LLM integration
- Evidence-based recommendations
- Human-in-the-loop decision making

---

## Project Structure

```
enterprise-incident-investigation-agent/
│
├── data/                  # Synthetic incident data
├── docs/                  # Checkpoints and design decisions
├── examples/              # Demo programs
│   ├── demo_react.py
│   └── demo_openrouter.py
├── src/
│   ├── agent.py           # ReAct reasoning loop
│   ├── llm.py             # OpenRouter integration
│   └── tools.py           # Investigation tools
├── tests/
│   └── test_tools.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository.

Create and activate a Python virtual environment.

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root.

```text
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
```

You can replace the model with any supported OpenRouter model.

---

## Running the Demo

Run the OpenRouter-powered investigation demo:

```bash
python -m examples.demo_openrouter
```

The demonstration performs a complete ReAct investigation by:

1. Retrieving the incident details.
2. Searching application logs.
3. Consulting the service runbook.
4. Producing an evidence-based investigation summary.

---

## Design Principles

The current implementation follows several important architectural principles:

- Evidence-based reasoning
- ReAct reasoning loop
- Short-term working memory
- External tool grounding
- Human approval for production actions
- Separation of observed evidence from inferred hypotheses
- Communication of remaining uncertainty

---

## Roadmap

### Completed

- ReAct reasoning loop
- OpenRouter integration
- External investigation tools
- Evidence-based incident summaries
- Prompt refinement for grounded reasoning
- Retry handling for transient LLM failures

### Planned

- Retrieval-Augmented Generation (RAG)
- Vector database integration
- Tree-of-Thought reasoning
- Multi-agent workflow
- Evaluation framework
- Application-level guardrails
- Long-term memory

---

## Technologies

- Python
- OpenRouter
- OpenAI Python SDK
- python-dotenv

---

## License

This repository is intended for educational purposes as part of the Agentic AI Program capstone project.