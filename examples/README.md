# Example Demonstrations

This directory contains runnable demonstrations of the Enterprise Incident Investigation Agent and its major components.

## Main End-to-End Demo

Run the OpenRouter-backed investigation:

```bash
python -m examples.demo_openrouter
```

This demonstrates the bounded ReAct investigation loop using the configured OpenRouter model, direct investigation tools, semantic retrieval, retrieval verification, and runtime guardrails.

## Component Demonstrations

The additional scripts exercise specific parts of the system:

- `demo_react.py` — deterministic ReAct loop using a scripted model.
- `demo_retrieval.py` — semantic retrieval over the synthetic knowledge corpus.
- `demo_search_knowledge.py` — retrieval relevance filtering and REJECT handling.
- `demo_verification.py` — evidence-consistency classification for retrieved documents.
- `demo_minimum_evidence_gate.py` — minimum-evidence conclusion guardrail.
- `demo_max_steps_hitl.py` — maximum-step human-in-the-loop escalation.

These focused demonstrations support deterministic testing of individual behaviors without depending on live model availability.