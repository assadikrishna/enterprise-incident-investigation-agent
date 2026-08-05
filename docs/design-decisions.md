# Design Decisions

## DD-001: Capstone Type

Decision:
Use the Personal Assistant capstone type.

Reason:
The Enterprise Incident Investigation Agent assists engineers by coordinating information gathering, structured reasoning, and recommendations while keeping the human engineer in control.

---

## DD-002: Initial Reasoning Architecture

Decision:
Implement a manual ReAct reasoning loop before adopting an orchestration framework.

Reason:
This provides a clear understanding of the underlying reasoning pattern before introducing higher-level frameworks such as LangGraph.

Status:
Implemented in v0.2

---

## DD-003: Initial Tool Design

Decision:
Implement synthetic Python tools for incident lookup, log search, and runbook retrieval.

Reason:
Supports Module 2 learning objectives while avoiding premature introduction of RAG or MCP.

Status:
Implemented in v0.2

---

## DD-004: Retrieval Strategy

Decision:
Delay RAG implementation until Module 3.

Reason:
The course introduces retrieval and vector databases in Module 3. Initial tool usage will use simple synthetic data sources.

Status:
Planned

---

## DD-005: Reasoning Framework

Decision:
Use the ReAct (Reasoning and Acting) framework as the primary reasoning loop.

Reason:
Incident investigation is an iterative process requiring reasoning, tool use, observation, and refinement. ReAct provides a natural structure that aligns with these requirements and the Module 2 learning outcomes.

Status:
Implemented in v0.2

---

## DD-006: LLM Integration

Problem

Real language models do not always return perfectly formatted or
deterministic responses.

Decision

The agent will treat the LLM as an unreliable component.

Mitigations

• Prompt engineering
• Output validation
• Retry logic
• Tool validation
• Human clarification
• Maximum reasoning steps

## DD-007: Prompt refinement for evidence-based reasoning.
Context

During integration with a real LLM through OpenRouter, the agent occasionally overstated conclusions, blurred the distinction between observed evidence and inferred hypotheses, and recommended production actions without sufficiently emphasizing human oversight. These behaviors reduced the reliability of the investigation.

Decision

The system prompt was refined to encourage evidence-based reasoning. The prompt now instructs the agent to:

-distinguish observed evidence from inferred hypotheses,
-avoid claiming causation unless supported by evidence,
-communicate uncertainty when evidence is incomplete,
-recommend human investigation steps for information the agent cannot access,
-require engineer approval before recommending production changes.

Rationale

A real language model is probabilistic and may produce different responses for the same input. Providing clearer instructions improves consistency, encourages grounded recommendations, and better aligns the agent's behavior with real-world incident investigation practices.

Trade-offs

Prompt refinement improves response quality but does not guarantee compliance. Important safety and validation rules will be implemented as application-level guardrails and protocol logic in later iterations of the project.