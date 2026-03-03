# LLM Eval Harness

Versioned LLM prompt evaluation harness with LLM-as-judge scoring, PostgreSQL-backed result storage, and CI-ready regression infrastructure.

---

## Overview

LLM Eval Harness is a production-style evaluation system for testing prompt quality across multiple LLM providers.

It enables:

- Versioned evaluation suites  
- Deterministic model execution  
- Pluggable provider adapters  
- Structured LLM-as-judge scoring  
- Persistent run tracking  
- Regression detection infrastructure  

The system is designed to reduce prompt regression detection from manual review to automated, measurable runs.

---

# Current Status (Through Step 5)

## ✅ Completed

- Dockerized Postgres database  
- Alembic-managed schema migrations  
- Versioned eval suite JSON format  
- Provider adapter layer:
  - OpenAI  
  - Anthropic  
  - Local Llama (Ollama)  
- Deterministic smoke testing for provider layer  

## ⏳ Not Yet Implemented

- Eval runner orchestration  
- LLM-as-judge scoring pipeline  
- CI integration  
- Dashboard  
- Baseline comparison logic  

---

# High-Level Architecture Plan

## System Overview

```
            ┌──────────────────────┐
            │   Versioned Suite    │
            │   (JSON)             │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │     Eval Runner      │
            │  (Step 6 onward)     │
            └─────────┬────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼

┌────────────────┐       ┌────────────────┐
│ Model Under    │       │ Judge Model    │
│ Test (Provider)│       │ (LLM-as-Judge) │
└────────────────┘       └────────────────┘
              │
              ▼
      ┌──────────────────────┐
      │   Postgres Storage   │
      │ (runs, outputs,      │
      │  scores, metadata)   │
      └─────────┬────────────┘
                ▼
      ┌──────────────────────┐
      │  Dashboard / CI Gate │
      │   (future steps)     │
      └──────────────────────┘
```

---

# Core Components

## 1. Eval Suite (Versioned JSON)

**Location:**  
`backend/app/eval/suites/`

Each suite defines:

- `id`
- `version`
- `cases`
- `dimensions`
- `severity`
- `tags`

**Design Rule:**  
Cases must be specific and objectively scorable.  
Avoid vague instructions like “be helpful”.

Suites are versioned so regressions can be compared against stable baselines.

---

## 2. Provider Adapter Layer

**Location:**  
`backend/app/eval/providers/`

All providers implement:

```python
generate(prompt, system, temperature, max_tokens) -> LLMResult
```

### Return Structure

- `text`
- `input_tokens`
- `output_tokens`
- `latency_ms`
- `cost_usd`

### Implemented Providers

- OpenAI  
- Anthropic  
- Ollama Llama (local)  

### Design Principles

- Provider-specific SDK logic is isolated  
- Default `temperature = 0.2` for stability  
- Retries with exponential backoff  
- Hard timeouts  
- No provider logic leaks into runner  

This ensures the eval runner remains fully provider-agnostic.

---

## 3. Database Schema

Managed via **Alembic**.

### `eval_suites`
- `name`
- `version`
- `hash`

### `eval_cases`
- `suite_id`
- `case_id`
- `input`
- `context`
- `tags`
- `severity`

### `eval_runs`
- `id`
- `suite_id`
- `model`
- `provider`
- `git_sha`
- `started_at`
- `finished_at`
- `status`

### `eval_outputs`
- `run_id`
- `case_id`
- `output_text`
- `latency_ms`
- `prompt_tokens`
- `completion_tokens`
- `cost_usd`

### `eval_scores`
- `run_id`
- `case_id`
- `dimension`
- `score`
- `judge_model`
- `judge_prompt_version`
- `judge_notes`

### Schema Capabilities

- Multi-provider comparison  
- Multi-model baselines  
- Judge versioning  
- Reproducible regression tracking  

---

# Data Flow (Planned)

1. Load suite JSON  
2. Insert suite + cases into DB (if new version)  
3. Create `eval_run`  
4. For each case:
   - Call model under test  
   - Persist output  
   - Call judge model with structured rubric  
   - Persist scores  
5. Mark run complete  
6. Compare against baseline  
7. Fail CI if regression threshold exceeded  

---

# LLM-as-Judge Strategy (Planned)

### Judge Model Requirements

- `temperature = 0`  
- Deterministic scoring rubric  
- Strict JSON output  
- Versioned judge prompt  

Each score entry includes:

- `dimension`
- Numeric score  
- Explanation  
- Judge model tag  
- Judge prompt version  

If the judge model or prompt changes, baselines must be regenerated.

---

# Infrastructure Plan

## Phase 1 (Current)
- Schema  
- Suites  
- Provider abstraction  

## Phase 2
- Eval runner engine  
- Output persistence  
- Judge scoring integration  

## Phase 3
- Baseline comparison  
- Regression thresholding  
- CI gating (GitHub Actions)  

## Phase 4
- React dashboard  
- Run diff visualization  
- Dimension trend tracking  
- Cost tracking and optimization  

---

# Configuration Strategy

Environment variables:

```
OPENAI_API_KEY
ANTHROPIC_API_KEY
JUDGE_PROVIDER
JUDGE_MODEL
JUDGE_TEMPERATURE
DATABASE_URL
```

All model and judge selection must be configuration-driven.

No hard-coded provider logic in the runner.

---

# Design Philosophy

This is not a script collection.

It is structured as internal evaluation infrastructure:

- Deterministic  
- Versioned  
- Measurable  
- Extensible  
- Provider-agnostic  

The goal is automated regression detection at scale.

---

# Next Step

Implement **Eval Runner (Step 6)**:

- Suite loader  
- Run lifecycle  
- Output persistence  
- Judge integration  
- Status tracking  

Once complete, the system becomes production-grade.