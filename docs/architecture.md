# System Architecture

## System Overview

The Enterprise Incident Investigation Agent is a bounded incident investigation agent built around the ReAct reasoning pattern.

The repository provides multiple implementations of the same investigation architecture: the original Python-orchestrated ReAct agent, a LangGraph-based workflow, and a LangChain-integrated LangGraph workflow using OpenRouter.

Across these implementations, the agent reasons about an incident, selects approved investigation actions, receives observations returned by tools, and continues until it has enough evidence to produce a conclusion or reaches a safety boundary that requires human intervention.

The architecture is designed around one central principle: the language model may reason and choose actions, but model-generated text does not automatically become authoritative evidence, and the agent does not autonomously execute production changes.

---

## High-Level Architecture

```text
Investigation Request with Incident ID
                |
                v
+-----------------------------+
| Bounded ReAct Agent         |
| - Reason about the incident |
| - Select one action         |
+-------------+---------------+
              |
              | Requested action
              v
+-----------------------------+
| Agent Control Layer         |
| - Execute requested tools   |
| - Enforce investigation     |
|   boundaries                |
| - e.g., allowed tools only  |
+-------------+---------------+
              |
        +-----+--------------------------------+
        |                                      |
        v                                      v
+--------------------------+        +--------------------------+
| Investigation Tools      |        | RAG Knowledge Retrieval  |
| - Retrieve incident      |        | - Search operational     |
|   details                |        |   knowledge              |
| - Search application     |        | - Runbooks               |
|   logs                   |        | - KB articles            |
| - Retrieve service       |        | - Past incidents         |
|   runbook                |        +------------+-------------+
+------------+-------------+                     |
             |                                   v
             |                        +--------------------------+
             |                        | Retrieval Reliability    |
             |                        | - Relevance filtering    |
             |                        | - Evidence-consistency   |
             |                        |   verification           |
             |                        | - Reject irrelevant      |
             |                        |   results                |
             |                        +------------+-------------+
             |                                     |
      Observation                         Verified Observation
             |                                     |
             +------------------+------------------+
                                |
                                v
                     +----------------------+
                     | Bounded ReAct Agent  |
                     | Next reasoning step  |
                     +----------+-----------+
                                |
                                | Agent proposes conclusion
                                v
                     +--------------------------+
                     | Conclusion Guardrails    |
                     | - Require incident       |
                     |   details                |
                     | - Require direct log     |
                     |   evidence               |
                     | - Allow conclusion only  |
                     |   when minimum evidence  |
                     |   is met                 |
                     +------------+-------------+
                                  |
                           +------+------+
                           |             |
                    Evidence met    Evidence not met
                           |             |
                           v             |
                +----------------------+ |
                | Investigation        | |
                | Conclusion           | |
                | - Grounded findings  | |
                | - Recommended next   | |
                |   steps              | |
                +----------------------+ |
                                         |
                                         +----> Continue reasoning
                                                with ReAct Agent


Independent reasoning limit:

+-----------------------------+
| Maximum Reasoning Steps     |
| Reached                     |
+-------------+---------------+
              |
              v
+-----------------------------+
| Human Review Required       |
| Preserve collected evidence |
| for engineer review         |
+-----------------------------+
```

---

## Implementation Layers

The repository provides three implementation paths that share the same investigation tools, evidence boundaries, and safety principles.

### Python-Orchestrated ReAct

The original implementation in `src/agent.py` explicitly manages the ReAct reasoning loop, action execution, observations, evidence tracking, and investigation limits in Python.

This implementation makes the underlying agent mechanics visible without relying on a workflow orchestration framework.

### LangGraph Orchestration

The LangGraph implementation separates investigation state, reasoning, tool execution, state updates, and routing into an explicit graph workflow.

The workflow is implemented under `src/graph/`:

- `state.py` defines the investigation state.
- `nodes.py` implements reasoning, tool execution, and state-update behavior.
- `workflow.py` defines graph transitions, conditional routing, termination, and maximum-step handling.

The LangGraph workflow reuses the existing investigation tools and evidence controls rather than replacing them.

### LangChain Integration

The LangChain integration in `src/langchain_llm.py` provides prompt and model integration for the LangGraph workflow.

It uses LangChain `ChatPromptTemplate`, LCEL composition, and `ChatOpenAI` configured to access the LLM through OpenRouter. LangGraph remains responsible for workflow orchestration, while LangChain provides the model and prompt integration layer.

---

## Core Components

### Bounded ReAct Agent

ReAct provides the core reasoning pattern used by the investigation agent.

In the original implementation, the reasoning loop is explicitly orchestrated in `src/agent.py`. The LangGraph implementation represents the same reasoning and action cycle through graph state, nodes, and conditional transitions.

At each reasoning step, the model is expected to produce exactly:

- one `Thought:`
- one `Action:`

The agent then waits for the real tool observation before continuing.

The investigation is bounded by a maximum number of reasoning steps. This gives the model reasoning autonomy during the investigation while limiting how long it can continue without reaching a conclusion or escalating to a human.

### Agent Control Layer and Parser Guardrail

The language model does not execute tools directly.

Python parses the model response, validates its structure, and executes only approved actions.

If the model attempts to generate its own `Observation:` or additional ReAct steps, the parser rejects the response before the fabricated observation can enter the accepted investigation evidence.

This creates a deterministic boundary between model-generated reasoning and authoritative tool output.

### Investigation Tools

The agent can access structured synthetic incident information through investigation tools.

These tools include:

- incident record retrieval
- application log search
- service runbook retrieval

These tools provide current operational evidence used during the investigation.

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

The architecture uses deterministic controls where model compliance alone is not sufficient.

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

The repository implements the incident investigation workflow through the original Python-orchestrated ReAct agent and a LangGraph-based workflow, with an additional LangChain integration for prompt and model access through OpenRouter.

The implementations operate on synthetic incident records, application logs, runbooks, knowledge-base articles, and historical incident data. Semantic RAG, retrieval verification, evidence controls, bounded reasoning, and human-in-the-loop escalation support the investigation process.

The agent is designed to assist with investigation and evidence gathering. Production-impacting decisions and actions remain under human control.