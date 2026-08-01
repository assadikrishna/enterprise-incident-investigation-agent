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