# System Architecture

## System Overview

The Enterprise Incident Investigation Agent is implemented as a bounded single-agent ReAct system.

The agent reasons about an incident, selects one approved action at a time, receives the resulting observation, and continues until it has enough evidence to produce a conclusion or reaches a safety boundary that requires human intervention.

The architecture is designed around one central principle: the language model may reason and choose actions, but it does not directly create authoritative evidence or execute production changes.

---

## High-Level Architecture

```text
User Incident Request
        |
        v
+-----------------------+
| Bounded ReAct Agent   |
| - Reason              |
| - Select one action   |
| - Maximum step limit  |
+-----------+-----------+
            |
            v
+-----------------------+
| Deterministic Runtime |
| - Parse response      |
| - Validate format     |
| - Execute tools       |
| - Enforce boundaries  |
+-----------+-----------+
            |
       +----+------------------+
       |                       |
       v                       v
+---------------+       +------------------+
| Direct Tools  |       | Semantic RAG     |
|               |       |                  |
| Incident data |       | Runbooks         |
| Logs          |       | KB articles      |
| Runbooks      |       | Past incidents   |
+---------------+       +--------+---------+
                                 |
                                 v
                        +------------------+
                        | Retrieval        |
                        | Reliability      |
                        |                  |
                        | Relevance gate   |
                        | Verification     |
                        | REJECT filtering |
                        +--------+---------+
                                 |
                                 v
                    +----------------------------+
                    | Evidence-Only Memory       |
                    | Accepted tool observations |
                    +-------------+--------------+
                                  |
                                  v
                    +----------------------------+
                    | Conclusion Guardrails      |
                    | - Incident details present |
                    | - Direct log evidence      |
                    +-------------+--------------+
                                  |
                            +-----+-----+
                            |           |
                            v           v
                       finish[...]   Continue reasoning
                                        |
                                 Maximum steps reached
                                        |
                                        v
                               HUMAN_INPUT_REQUIRED
```

---

## Core Components

### Bounded ReAct Agent

The main investigation loop is implemented in `src/agent.py`.

At each reasoning step, the model is expected to produce exactly:

- one `Thought:`
- one `Action:`

The agent then waits for the real tool observation before continuing.

The reasoning loop is bounded by a maximum number of steps. This gives the model reasoning autonomy during the investigation while limiting how long it can continue without reaching a conclusion or escalating to a human.

### Deterministic Runtime and Parser Guardrail

The language model does not execute tools directly.

Python parses the model response, validates its structure, and executes only approved actions.

If the model attempts to generate its own `Observation:` or additional ReAct steps, the parser rejects the response before the fabricated observation can enter the accepted investigation evidence.

This creates a deterministic boundary between model-generated reasoning and authoritative tool output.

### Direct Investigation Tools

The agent can access structured synthetic incident information through direct tools.

These tools include:

- incident record retrieval
- application log search
- service runbook retrieval

Direct tools provide current operational evidence used during the investigation.

### Semantic Retrieval

Semantic retrieval is implemented in `src/retrieval.py`.

Runbooks, knowledge-base articles, and historical incident reports are chunked and embedded using SentenceTransformers. FAISS is used for vector similarity search.

The current retrieval index uses normalized embeddings and inner-product similarity.

### Retrieval Reliability Layer

Retrieved documents are not automatically treated as useful evidence.

The retrieval pipeline applies:

1. a minimum relevance threshold
2. evidence-consistency verification
3. filtering of documents classified as `REJECT`

Retrieved documents may be classified as:

- `SUPPORTING`
- `ALTERNATIVE`
- `CONTRADICTORY`
- `REJECT`

This helps prevent semantically similar but causally irrelevant documents from being treated as supporting evidence.

### Evidence-Only Investigation Memory

The system maintains two different forms of working state.

The full ReAct trace contains model thoughts, actions, observations, and debugging information.

A separate evidence-only trace contains the original user request and accepted tool observations. Model thoughts, parser failures, guardrail messages, and tool errors are not added to this evidence store.

This evidence-only state is used when retrieved knowledge is verified and when unresolved investigations are escalated for human review.

### Minimum-Evidence Conclusion Guardrail

The agent is not allowed to execute `finish[...]` immediately.

Before a final conclusion is accepted, the investigation must include:

- successfully retrieved incident details
- at least one real log observation

This rule establishes a minimum factual basis for a conclusion. It does not guarantee that the root cause has been proven.

### Human-in-the-Loop Escalation

If the investigation reaches the maximum reasoning-step limit without a sufficiently supported conclusion, the agent does not force a final answer.

Instead, it returns `HUMAN_INPUT_REQUIRED` together with the accepted evidence collected so far and a recommendation for additional human investigation.

Production-impacting actions also remain outside the autonomous authority of the agent and require human approval.

---

## Investigation Flow

A typical investigation follows this sequence:

1. The user provides an incident request.
2. The ReAct agent selects an approved investigation action.
3. Python validates the model response and executes the selected tool.
4. The resulting observation is added to the investigation state.
5. The agent may retrieve additional knowledge through semantic RAG.
6. Retrieved documents pass through relevance filtering and evidence-consistency verification.
7. Accepted observations are retained in evidence-only memory.
8. The agent continues reasoning until it has sufficient evidence to request `finish[...]`.
9. The minimum-evidence guardrail validates whether a conclusion is allowed.
10. If the reasoning budget is exhausted first, the system escalates to human review.

---

## Safety Boundaries

The final implementation uses deterministic controls where model compliance alone is not sufficient.

Key boundaries include:

- only approved tools may be executed
- Python, not the model, executes tools
- malformed multi-step ReAct responses are rejected
- fabricated model-generated observations are not accepted as evidence
- retrieved knowledge is filtered before use
- a minimum evidence requirement applies before final conclusions
- reasoning is limited by a maximum number of steps
- unresolved investigations escalate to a human
- production-impacting decisions require human approval

These controls are intended to improve grounding and bounded behavior rather than guarantee that every investigation will reach the correct root cause.

---

## Current Scope

The implemented capstone uses a bounded single-agent ReAct architecture.

Tree-of-Thought reasoning, LangGraph orchestration, and specialized multi-agent workflows were explored as design options during the course but are not part of the current implementation. They remain possible future extensions.