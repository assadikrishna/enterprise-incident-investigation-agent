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

## DD-008: ReAct Output Validation and Format Retry

During testing, the LLM sometimes generated more than the required Thought and Action. Instead of stopping after selecting an action and waiting for the application to execute the tool, the model generated its own Observation, continued reasoning, and sometimes generated additional actions or a final answer.

This created a reliability risk because the model-generated observations could contain information that was never returned by an actual tool. For example, the model invented specific connection-pool configuration values while attempting to call search_knowledge. The actual knowledge retrieval tool had not yet executed.

The agent was updated with two complementary safeguards:

Prompt-level protocol: The system prompt explicitly instructs the model to output exactly one Thought and one Action, not generate an Observation, and stop after the action. This did not help. 
Programmatic validation: parse_response() validates the model response and rejects responses containing additional Observation, Thought, or Action sections. This was timing out due to max steps.
Format retry: A malformed response is retried within the same reasoning step. Invalid formatting therefore does not consume an investigation step or allow fabricated observations to enter the agent's evidence.
Tool-controlled observations: Only the Python application executes actions and supplies observations back to the LLM.

During testing, the parser successfully rejected fabricated observations. On a subsequent retry, the model produced a valid search_knowledge action, Python executed the semantic retrieval tool, and real retrieved documents were returned as the observation.

This design separates LLM reasoning from trusted tool results and reduces the risk that hallucinated information will be treated as evidence during an incident investigation.


## DD-009: Retrieval Reliability and Verification
Problem 1 — Top-k always returns something

Current behavior:

top_k = 3
→ always returns the three best matches
→ even if all three are poor matches

Improvement:

top-k retrieval
→ minimum relevance threshold
→ 0–3 results can be returned

Problem 2 — Semantic similarity does not mean causal consistency

A document like INC-103 may legitimately have high semantic similarity because it contains payment-service, HTTP 503, timeouts, etc., while having a different root cause.

Improvement:

semantic retrieval
        ↓
minimum relevance threshold
        ↓
evidence-consistency verification
        ↓
supporting / alternative / contradictory / reject