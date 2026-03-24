# QA Nexus Backend

**AI-Powered Multi-Agent Testing Pipeline** — A production-grade FastAPI backend that orchestrates 7 specialized AI agents to automatically analyze user stories, generate test cases, produce automation code, execute tests, detect bugs, and analyze coverage.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Request → Response Flow](#request--response-flow)
- [Module Reference](#module-reference)
- [Agents Architecture Deep Dive](#agents-architecture-deep-dive)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Integrations](#integrations)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Tech Stack](#tech-stack)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (React/Vite)                        │
│     Dashboard  │  Stories  │  Pipeline  │  Reports  │  Settings     │
└────────────────┬───────────────────────────────────┬────────────────┘
                 │  HTTP REST / WebSocket             │
                 ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Application Layer                       │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Stories  │ │ Pipeline │ │ Webhooks │ │Scheduler │ │  Bugs    │ │
│  │  Routes  │ │  Routes  │ │  Routes  │ │  Routes  │ │  Routes  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │             │             │             │             │       │
│       ▼             ▼             ▼             ▼             ▼       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                    Dependency Injection Layer                  │   │
│  │         Settings  │  DB Session  │  Provider Registry         │   │
│  └───────────────────┬───────────────────────────────────────────┘   │
└──────────────────────┼───────────────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────────────┐
       ▼               ▼                       ▼
┌──────────┐  ┌─────────────────┐  ┌───────────────────┐
│ Services │  │  Orchestrator   │  │   Integrations    │
│ (CRUD)   │  │  (Pipeline)     │  │                   │
│          │  │                 │  │  Jira  │  GitHub  │
│ Story    │  │  PipelineState  │  │  Slack │  Email   │
│ Exec.    │  │  run_pipeline() │  │                   │
│ Dash.    │  │                 │  └───────────────────┘
└──────────┘  └───────┬─────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │           3-Phase Pipeline with Adversarial Debates             │
  │                                                                 │
  │  ═══ PHASE 1: ANALYSIS (quick_think) ═══                       │
  │  ① Story Analyzer ──▶ ② Test Strategist                        │
  │           │ context summarization │                              │
  │                                                                 │
  │  ═══ PHASE 2: GENERATION + REVIEW DEBATE ═══                   │
  │  ③ Test Case Writer ◀──debate──▶ ③b Test Critic (N rounds)     │
  │           │                                                     │
  │  ④ Automation Engineer ──▶ ⑤ Test Executor                     │
  │           │ context summarization │                              │
  │                                                                 │
  │  ═══ PHASE 3: VERDICT DEBATE ═══                                │
  │  ⑥ Bug Detective ◀──debate──▶ ⑥b Quality Advocate (N rounds)   │
  │           │                                                     │
  │  ⑦ Coverage Judge (deep_think) ──▶ GO / NO-GO                  │
  │                                                                 │
  └──────────────────────────┬────────────────────────────────────┘
                             │
            ┌────────────────┼────────────────────┐
            ▼                ▼                    ▼
     ┌──────────┐    ┌──────────┐    ┌────────────────┐
     │   LLM    │    │  Test    │    │  Resilience    │
     │ Providers│    │ Runners  │    │                │
     │          │    │          │    │ Retry+Backoff  │
     │ OpenAI   │    │Playwright│    │ Fallback Chain │
     │ Anthropic│    │ Selenium │    │ 2-tier LLM     │
     │ Ollama   │    │ (subproc)│    └────────────────┘
     │ Groq     │    └──────────┘           │
     │ Mock     │                    ┌────────────────┐
     └──────────┘                    │ Reflection     │
            │                        │ Memory (BM25)  │
            ▼                        │ SQLite-backed  │
     ┌──────────┐                    └────────────────┘
     │ SQLite   │
     │ Database │
     │ (async)  │
     └──────────┘
```

---

## Request → Response Flow

### Full Pipeline Execution (POST /api/v1/pipeline/run)

Here is the complete life of a request from the frontend to backend and back:

```
1. CLIENT: POST /api/v1/pipeline/run
   Body: { "story_id": "PROJ-123", "framework": "playwright" }
                     │
                     ▼
2. FASTAPI ROUTING (app/api/pipeline.py)
   ├── Validates request body via Pydantic model (PipelineRunRequest)
   ├── Creates PipelineState(execution_id, story_id, framework)
   ├── Stores state in execution_service (in-memory)
   └── Adds _run_pipeline() to BackgroundTasks → Returns 202 Accepted
                     │
                     ▼
3. RESPONSE TO CLIENT: 202 Accepted
   Body: { "execution_id": "exec-a1b2c3d4", "status": "queued" }
   (Client immediately gets response, pipeline runs in background)
                     │
                     ▼
4. BACKGROUND: run_pipeline(state, story) — app/orchestrator/pipeline.py
   │
   ├─▶ AGENT 1 — Story Analyzer (app/agents/story_analyzer.py)
   │   ├── Reads system prompt from agents/prompts/story.md
   │   ├── Resolves LLM provider: settings.provider_for_agent("story")
   │   ├── Gets provider from registry: ProviderRegistry.get("anthropic")
   │   ├── Calls provider.chat([system_prompt, user_story]) → LLM API
   │   ├── LLM returns: test scope analysis, risk areas, business logic
   │   └── state.agent_completed("story", output)
   │
   ├─▶ AGENT 2 — Test Strategist (app/agents/test_strategist.py)
   │   ├── Input: Story + Agent 1 analysis
   │   ├── LLM returns: test strategy, approach, prioritization
   │   └── state.agent_completed("strategy", output)
   │
   ├─▶ AGENT 3 — Test Case Writer (app/agents/test_case_writer.py)
   │   ├── Input: Story + Strategy
   │   ├── LLM returns: detailed test cases (steps, expected results)
   │   └── state.agent_completed("writer", output)  →  Saved to files/
   │
   ├─▶ AGENT 4 — Automation Engineer (app/agents/automation_engineer.py)
   │   ├── Input: Test cases + framework (playwright/selenium)
   │   ├── LLM returns: executable automation code (.spec.ts or .py)
   │   ├── FileManager.save_automation_code() → workspace/{story}/automation/
   │   └── state.agent_completed("automation", output)
   │
   ├─▶ AGENT 5 — Test Executor (app/agents/test_executor.py)
   │   ├── Gets runner from registry: get_runner("playwright")
   │   ├── Creates TestSandbox → temp directory with test files
   │   ├── PlaywrightRunner.setup() → npm install + npx playwright install
   │   ├── PlaywrightRunner.run() → subprocess: npx playwright test
   │   │     └── ProcessManager.run(cmd, timeout, on_stdout, on_stderr)
   │   │           └── asyncio.create_subprocess_exec → real OS process
   │   ├── Parsers:
   │   │     ├── JUnit XML parser → passed/failed/skipped counts
   │   │     ├── Console parser (regex) → fallback counts
   │   │     └── Coverage parser → line/branch/function coverage %
   │   ├── EvidenceCollector.collect_from_workspace() → screenshots, traces
   │   └── state: tests_passed, tests_failed, tests_skipped populated
   │
   ├─▶ AGENT 6 — Bug Detective (app/agents/bug_detective.py)
   │   ├── Input: Test results + failure logs
   │   ├── LLM returns: bug reports with severity, steps, expected vs actual
   │   ├── BugRepository.save_batch() → SQLite (single transaction)
   │   └── If Jira configured: JiraBugReporter.report_bug() → Jira REST API
   │
   └─▶ AGENT 7 — Coverage Analyst (app/agents/coverage_analyst.py)
       ├── Input: All previous outputs + test results + coverage data
       ├── LLM returns: coverage gaps, risk assessment, verdict
       ├── state.verdict = "PASS" | "FAIL" | "NEEDS_REVIEW"
       └── state.complete()

                     │
                     ▼
5. PERSISTENCE (after pipeline completes)
   ├── ExecutionRepository.save_from_state() → SQLite executions table
   ├── FileManager.save_report() → workspace/{story}/reports/
   ├── ArtifactStorage.store_batch() → workspace/artifacts/{execution}/
   └── NotificationDispatcher.notify() → Slack + Email (parallel via asyncio.gather)

                     │
                     ▼
6. CLIENT GETS RESULTS via:
   ├── WebSocket: ws://localhost:8000/api/v1/ws/{execution_id} (real-time)
   ├── Polling: GET /api/v1/executions/{execution_id}
   └── Dashboard: GET /api/v1/dashboard/metrics
```

### How the LLM Provider System Works

```
Request: "Use Anthropic for story analysis, Ollama for test writing"

1. Config resolution:
   settings.provider_for_agent("story")
   → checks AGENT_STORY_PROVIDER env var
   → falls back to LLM_DEFAULT_PROVIDER
   → returns "anthropic"

2. Provider lookup:
   ProviderRegistry.get("anthropic")
   → returns AnthropicProvider instance (initialized at startup)

3. LLM call:
   provider.chat(messages=[
       {"role": "system", "content": "<prompt from .md file>"},
       {"role": "user",   "content": "<story + context>"},
   ])
   → makes async HTTP call to Anthropic API
   → returns agent output text
```

### How Jira Integration Works

```
INBOUND: Import stories from Jira
──────────────────────────────────
GET /api/v1/jira/sprint-stories?project_key=PROJ&sprint_name=Sprint+42
     │
     ├── JiraClient (reusable httpx.AsyncClient with connection pooling)
     │   └── base_url=https://your-org.atlassian.net
     │   └── Auth: Basic (email:token) for Cloud, Bearer for Server
     │   └── GET /rest/api/3/search?jql=project="PROJ" AND sprint="Sprint 42"
     │
     ├── JiraMapper.jira_issue_to_story()
     │   └── Converts ADF (Atlassian Document Format) → plain text
     │   └── Normalizes priority (Highest → critical)
     │   └── Extracts acceptance criteria, sprint, story points
     │
     └── Returns list of JiraStory Pydantic models

OUTBOUND: File bugs back to Jira
─────────────────────────────────
POST /api/v1/bugs/{bug_id}/file-to-jira
     │
     ├── BugRepository.get(bug_id) → from SQLite
     │
     ├── JiraBugReporter.report_bug(bug)
     │   ├── JiraMapper.story_to_jira_bug() → creates ADF payload
     │   │   └── Maps severity (critical → Highest, minor → Low)
     │   ├── JiraClient.create_issue(project_key, issue_data)
     │   │   └── POST /rest/api/3/issue → returns PROJ-456
     │   └── Returns jira_key
     │
     └── BugRepository.update_jira_key(bug_id, "PROJ-456")

Connection Best Practices:
  ✓ Single httpx.AsyncClient per JiraClient instance (connection pooling)
  ✓ base_url set on client → all requests use relative paths
  ✓ Fine-grained timeouts: Timeout(30.0, connect=10.0)
  ✓ Retry with exponential backoff (3 attempts)
  ✓ Proper auth header built once in __init__, not per-request
  ✓ Client.aclose() for graceful shutdown
```

---

## Module Reference

### Core Application

| Module             | File                     | Purpose                                                             |
| ------------------ | ------------------------ | ------------------------------------------------------------------- |
| **App Factory**    | `app/main.py`            | FastAPI app with lifespan (DB init, scheduler start, provider init) |
| **Config**         | `app/config.py`          | Pydantic Settings v2 — all env-driven configuration                 |
| **Dependencies**   | `app/dependencies.py`    | FastAPI DI — `get_settings()`, `get_db()`                           |
| **Error Handlers** | `app/core/__init__.py`   | `QANexusError`, exception → JSON response mapping                   |
| **Middleware**     | `app/core/middleware.py` | CORS, request timing headers                                        |
| **Event Bus**      | `app/core/events.py`     | In-process pub/sub for agent lifecycle events                       |

### API Layer (14 Route Modules)

| Router                | Prefix        | Key Endpoints                                            |
| --------------------- | ------------- | -------------------------------------------------------- |
| `pipeline.py`         | `/pipeline`   | `POST /run`, `GET /status/{id}`                          |
| `stories.py`          | `/stories`    | CRUD for user stories                                    |
| `agents.py`           | `/agents`     | `GET /` list, `GET /{id}` detail                         |
| `dashboard.py`        | `/dashboard`  | `GET /metrics`, `GET /recent`                            |
| `executions.py`       | `/executions` | `GET /{id}`, `GET /` list with pagination                |
| `reports.py`          | `/reports`    | `GET /{execution_id}` full report                        |
| `settings_routes.py`  | `/settings`   | `GET /`, `PATCH /` app config                            |
| `artifacts.py`        | `/artifacts`  | `GET /{execution_id}`, `GET /download`                   |
| `bugs.py`             | `/bugs`       | `GET /open`, `GET /{execution_id}`, `POST /file-to-jira` |
| `files.py`            | `/files`      | `GET /{story_id}`, `GET /{story_id}/content`             |
| `jira_routes.py`      | `/jira`       | `GET /health`, `GET /sprint-stories`, `POST /search`     |
| `scheduler_routes.py` | `/scheduler`  | CRUD for cron jobs, `GET /status`                        |
| `webhooks.py`         | `/webhooks`   | `POST /github` (HMAC-SHA256 verified)                    |
| `ws.py`               | `/ws`         | WebSocket real-time execution updates                    |

### 7 AI Agents

| Agent               | ID           | Input                  | Output                                      |
| ------------------- | ------------ | ---------------------- | ------------------------------------------- |
| Story Analyzer      | `story`      | User story text        | Risk areas, scope analysis, test priorities |
| Test Strategist     | `strategy`   | Story + analysis       | Test strategy, approach, prioritization     |
| Test Case Writer    | `writer`     | Strategy               | Detailed manual test cases with steps       |
| Automation Engineer | `automation` | Test cases + framework | Executable Playwright/Selenium code         |
| Test Executor       | `executor`   | Automation code        | Real test run results (pass/fail/skip)      |
| Bug Detective       | `bug`        | Test failures          | Bug reports with severity, repro steps      |
| Coverage Analyst    | `coverage`   | All outputs            | Coverage gaps, final verdict                |

### LLM Providers

| Provider  | Module                            | Model Default             |
| --------- | --------------------------------- | ------------------------- |
| OpenAI    | `providers/openai_provider.py`    | gpt-4o                    |
| Anthropic | `providers/anthropic_provider.py` | claude-sonnet-4-20250514  |
| Ollama    | `providers/ollama.py`             | llama3.1:8b               |
| Groq      | `providers/groq_provider.py`      | llama-3.3-70b-versatile   |
| Mock      | `providers/mock.py`               | (deterministic test data) |

### Database Layer

| Component      | File                                | Purpose                                                                                                                 |
| -------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Engine         | `db/engine.py`                      | SQLAlchemy 2.0 async engine + `async_sessionmaker`                                                                      |
| Tables         | `db/tables.py`                      | 8 ORM tables (stories, executions, test_cases, test_results, bug_reports, artifacts, scheduled_jobs, notification_logs) |
| Story Repo     | `db/repositories/story_repo.py`     | CRUD with `func.count()` (O(1) counting)                                                                                |
| Execution Repo | `db/repositories/execution_repo.py` | `save_from_state()`, pagination                                                                                         |
| Bug Repo       | `db/repositories/bug_repo.py`       | Batch save (single transaction), Jira key tracking                                                                      |
| Test Case Repo | `db/repositories/test_case_repo.py` | Batch save, query by execution/story                                                                                    |
| Artifact Repo  | `db/repositories/artifact_repo.py`  | Binary artifact metadata persistence                                                                                    |
| Schedule Repo  | `db/repositories/schedule_repo.py`  | CRUD + `list_enabled()`, `toggle()`                                                                                     |

### Test Runners

| Runner          | Module                        | How It Works                                                        |
| --------------- | ----------------------------- | ------------------------------------------------------------------- |
| Playwright      | `runner/playwright_runner.py` | Creates sandbox → `npm install` → `npx playwright test` → JUnit XML |
| Selenium        | `runner/selenium_runner.py`   | Creates sandbox → `pip install` → `pytest --junitxml`               |
| Process Manager | `runner/process_manager.py`   | `asyncio.create_subprocess_exec` with timeout + streaming           |
| Sandbox         | `runner/sandbox.py`           | Temp directory isolation, cleanup, file writing                     |

### Parsers

| Parser    | Module                       | Input → Output                                                         |
| --------- | ---------------------------- | ---------------------------------------------------------------------- |
| JUnit XML | `parsers/junit_parser.py`    | `.xml` → `JUnitReport` (test_cases, passed/failed/error counts)        |
| Console   | `parsers/console_parser.py`  | stdout → `{passed, failed, skipped}` (Playwright/pytest/Cypress regex) |
| Coverage  | `parsers/coverage_parser.py` | Istanbul JSON / text → `CoverageData` (line%, branch%, function%)      |

### Integrations

| Integration            | Module                                         | Protocol                                                 |
| ---------------------- | ---------------------------------------------- | -------------------------------------------------------- |
| **Jira**               | `integrations/jira/client.py`                  | REST API v3, async httpx with connection pooling + retry |
| **Jira Mapper**        | `integrations/jira/mapper.py`                  | ADF ↔ plain text conversion, priority normalization      |
| **Jira Bug Reporter**  | `integrations/jira/bug_reporter.py`            | Auto-file bugs + add test result comments                |
| **GitHub Webhooks**    | `integrations/github/webhook.py`               | HMAC-SHA256 signature verification, push/PR parsing      |
| **GitHub PR Comments** | `integrations/github/pr_commenter.py`          | Markdown result tables on PRs, Check Runs                |
| **Slack**              | `integrations/notifications/slack.py`          | Incoming webhook with Block Kit formatting               |
| **Email**              | `integrations/notifications/email_notifier.py` | SMTP/SMTP_SSL with HTML tables, thread-pool send         |
| **Dispatcher**         | `integrations/notifications/dispatcher.py`     | `asyncio.gather` parallel fan-out to all channels        |

### Scheduler

| Component | Module                   | Purpose                                                             |
| --------- | ------------------------ | ------------------------------------------------------------------- |
| Scheduler | `scheduler/scheduler.py` | APScheduler `AsyncIOScheduler` with cron triggers                   |
| Jobs      | `scheduler/jobs.py`      | `execute_scheduled_pipeline()` — full pipeline + DB + notifications |

### Evidence & Files

| Component          | Module                  | Purpose                                                     |
| ------------------ | ----------------------- | ----------------------------------------------------------- |
| Evidence Collector | `evidence/collector.py` | Scan sandbox for screenshots, videos, traces                |
| Artifact Storage   | `evidence/storage.py`   | File-based artifact storage with cleanup                    |
| File Manager       | `files/manager.py`      | Workspace layout: test-cases/, automation/, reports/, bugs/ |

---

## Agents Architecture Deep Dive

This section documents the complete prompt templates, agent implementation patterns, orchestration flow, and provider system that power the 7-agent pipeline.

### System Prompts

Each agent has a dedicated markdown prompt file in `app/agents/prompts/`. The prompts define the agent's role, input/output contract, formatting rules, and quality constraints.

#### Agent 1 — Story Analyzer (`prompts/story.md`)

```
You are the **Story Analyzer** — the first agent in a 7-agent QA testing pipeline.

## Your Role
Read Jira stories and extract structured requirements, edge cases, security
risks, and testable acceptance criteria.

## Input
You receive a Jira story with: title, description, acceptance criteria,
priority, and labels.

## Output Format
📋 REQUIREMENT ANALYSIS — {STORY_ID}: {TITLE}

━━━ Core Requirements ({count}) ━━━
  ✓ R1: {requirement}
  ✓ R2: {requirement}

━━━ Edge Cases Identified ({count}) ━━━
  ⚡ E1: {edge case}
  ⚡ E2: {edge case}

━━━ Security Risks ({count}) ━━━
  🔒 S1: {risk}
  🔒 S2: {risk}

━━━ Integration Points ({count}) ━━━
  🔗 {external system or API}

━━━ Risk Assessment: {LOW|MEDIUM|HIGH} ━━━
{brief justification}

## Rules
1. Extract EVERY testable requirement from the description and acceptance criteria
2. Identify at least 3 edge cases that aren't explicitly stated
3. Flag security risks relevant to the feature domain
4. List all external systems the feature touches
5. Be specific — vague requirements lead to gaps in test coverage
6. Keep output concise but thorough
```

#### Agent 2 — Test Strategist (`prompts/strategy.md`)

```
You are the **Test Strategist** — the second agent in a 7-agent QA testing pipeline.

## Your Role
Determine the optimal test distribution, priority matrix, and risk-based
test allocation based on the Story Analyzer's output.

## Input
You receive the requirement analysis from the Story Analyzer.

## Output Format
📐 TEST STRATEGY — {STORY_ID}: {TITLE}

━━━ Test Distribution ━━━
  Functional Tests     {bar}  {count} tests ({percent}%)
  Security Tests       {bar}  {count} tests ({percent}%)
  Edge Case Tests      {bar}  {count} tests ({percent}%)
  Performance Tests    {bar}  {count} tests ({percent}%)
  Accessibility Tests  {bar}  {count} tests ({percent}%)

━━━ Priority Matrix ━━━
  P0 (Must Pass):  {list}
  P1 (Critical):   {list}
  P2 (Important):  {list}
  P3 (Nice-Have):  {list}

━━━ Recommended Approach ━━━
  • Framework: {recommendation}
  • Mocking: {strategy}
  • Data: {test data approach}
  • Environment: {env recommendation}
  • Parallelism: {worker count} workers — {justification}

━━━ Total: {n} tests | Estimated Duration: {time} ━━━

## Rules
1. Distribute tests based on risk — high-risk areas get more coverage
2. P0 tests should cover the happy path and critical security boundaries
3. Total test count should be 15-25 for medium stories, 8-15 for small ones
4. Use bar charts (█ and ░) for visual distribution
5. Consider the feature's domain when recommending frameworks
```

#### Agent 3 — Test Case Writer (`prompts/writer.md`)

```
You are the **Test Case Writer** — the third agent in a 7-agent QA testing pipeline.

## Your Role
Generate comprehensive BDD test cases with Given/When/Then scenarios
based on the Test Strategist's plan.

## Input
You receive the test strategy (distribution, priorities) and the original
requirement analysis.

## Output Format
🧪 GENERATED TEST CASES ({total} total)

TC-{NNN} | {P0/P1/P2/P3} | {type}
  Scenario: {descriptive scenario name}
  Given {precondition}
  When {action}
  Then {expected result}
  And {additional assertion}

## Rules
1. Generate EXACTLY the number of test cases specified in the strategy
2. Each test case must have: ID (TC-001 format), priority, type, BDD scenario
3. P0 tests come first, then P1, P2, P3
4. Types: functional, edge, security, performance, accessibility
5. Scenarios must be specific enough to implement — no vague assertions
6. Each Given/When/Then should map to a concrete automation step
7. Include at least one negative test per P0/P1 requirement
8. Edge cases should test boundary values and error conditions specifically
```

#### Agent 4 — Automation Engineer (`prompts/automation.md`)

```
You are the **Automation Engineer** — the fourth agent in a 7-agent QA testing pipeline.

## Your Role
Convert BDD test cases into executable automation code for the specified
test framework.

## Input
1. BDD test cases from the Test Case Writer
2. The target framework (Playwright, Cypress, Selenium, Appium, k6, or axe-core)

## Output Format
🔧 AUTOMATION CODE — {Framework} ({Language})
{complete, runnable test file with imports and setup}
Generated {n} test files covering {m} test cases.

## Framework-Specific Guidelines

### Playwright (TypeScript)
- Use test.describe() for grouping, test() for cases
- Use locator strategies: getByRole, getByText, getByTestId
- Use expect() assertions from @playwright/test
- Use page.waitForURL(), page.waitForResponse() for async flows

### Cypress (TypeScript)
- Use describe() / it() pattern
- Use cy.visit(), cy.get(), cy.contains()
- Use cy.intercept() for API mocking

### Selenium (Python)
- Use WebDriverWait with expected_conditions
- Use By.XPATH, By.CSS_SELECTOR, By.ID
- Use pytest as the test runner

## Rules
1. Generate COMPLETE, RUNNABLE code — not pseudocode
2. Include all imports and test setup
3. Map each BDD scenario to a test function
4. Use proper selectors and assertions
5. Add meaningful test names that reference the TC-ID
6. Include comments linking back to BDD scenarios
```

#### Agent 5 — Test Executor (`prompts/executor.md`)

```
You are the **Test Executor** — the fifth agent in a 7-agent QA testing pipeline.

## Your Role
Simulate execution of the automated tests and report results with timing data.

## Input
You receive the automation code and test case list from previous agents.

## Output Format
⚡ EXECUTION RESULTS

━━━ Environment ━━━
  Framework: {name}
  Browser: Chromium {version}
  Workers: {n} parallel
  Headless: {yes/no}

━━━ Summary ━━━
  Total: {n} tests | Passed: {n} ✅ | Failed: {n} ❌ | Skipped: {n} ⏭
  Duration: {time}s

━━━ Results ━━━
  ✓ TC-001: {name} — {duration}
  ✗ TC-005: {name} — FAILED: {brief error}

━━━ Failed Tests Detail ━━━
  ✗ TC-005: {name}
    Error: {specific error message}
    Screenshot: test-results/TC-005-failure.png
    Step Failed: {which step of the BDD scenario}

## Rules
1. Report realistic execution times (50ms-5s per test)
2. Have 70-90% pass rate — a few failures make the pipeline interesting
3. Failed tests should have specific, realistic error messages
4. Include total duration and per-test timing
5. Failures should be traceable to specific BDD steps
```

#### Agent 6 — Bug Detective (`prompts/bug.md`)

```
You are the **Bug Detective** — the sixth agent in a 7-agent QA testing pipeline.

## Your Role
Analyze test failures from the Test Executor, identify root causes,
and generate actionable bug reports.

## Input
You receive the execution results showing which tests failed and their
error messages.

## Output Format
🐛 BUG ANALYSIS

━━━ BUG-{NNN}: {title} ━━━
  Severity: {Critical|High|Medium|Low}
  Test: {TC-ID} ({test name})
  Root Cause: {technical root cause analysis}
  Impact: {user-facing impact}
  Suggestion: {specific fix recommendation}
  Related: {any related tests affected}

━━━ Summary ━━━
  Total Bugs: {n}
  Critical: {n} | High: {n} | Medium: {n} | Low: {n}
  Blocking Release: {yes/no}

## Rules
1. Analyze EACH failed test — every failure gets a bug report
2. Root causes should be technical and specific (not "something broke")
3. Suggestions should be actionable — describe the fix, not just the problem
4. Severity should match the impact on users and the priority of the test
5. Identify patterns — if multiple tests fail for the same reason, note it
6. Be concise but thorough — developers should be able to act on your analysis
```

#### Agent 7 — Coverage Analyst (`prompts/coverage.md`)

```
You are the **Coverage Analyst** — the seventh and final agent in a 7-agent QA
testing pipeline.

## Your Role
Evaluate overall test coverage, identify gaps, and provide a go/no-go
recommendation for the feature.

## Input
You receive ALL outputs from the previous 6 agents: requirement analysis,
test strategy, test cases, automation code, execution results, and bug analysis.

## Output Format
📊 COVERAGE ANALYSIS

━━━ Coverage by Type ━━━
  Functional:    {pct}% {bar}
  Security:      {pct}% {bar}
  Edge Cases:    {pct}% {bar}
  Performance:   {pct}% {bar}
  Accessibility: {pct}% {bar}

━━━ Overall Coverage: {pct}% ━━━

━━━ Coverage Gaps ━━━
  ⚠ {gap description — what's not covered}

━━━ Verdict: {GO|CONDITIONAL GO|NO-GO} ━━━
{justification paragraph}

━━━ Recommendations ━━━
  1. {actionable recommendation}
  2. {actionable recommendation}
  3. {actionable recommendation}

## Verdict Criteria
- **GO**: ≥90% coverage, 0 critical/high bugs, all P0 tests pass
- **CONDITIONAL GO**: 75-89% coverage, no critical bugs, minor issues noted
- **NO-GO**: <75% coverage, OR any critical/high bugs, OR P0 test failures

## Rules
1. Calculate coverage based on requirements covered vs. total identified
2. Each test type gets its own coverage percentage
3. Identify specific gaps — what requirements or edge cases aren't tested
4. Recommendations should be prioritized and actionable
5. Verdict must be justified with specific data points
6. Consider the risk assessment from the Story Analyzer
```

---

### Agent Implementation Pattern

All 7 agents inherit from `BaseAgent` (`app/agents/base.py`). Each concrete agent is **extremely thin** — just 6 lines setting `agent_id`, `agent_name`, and `role`. All logic lives in the base class.

```python
# Example: app/agents/story_analyzer.py — ALL agents follow this pattern
class StoryAnalyzerAgent(BaseAgent):
    agent_id = "story"
    agent_name = "Story Analyzer"
    role = "Requirement Intelligence"
```

**BaseAgent provides:**

| Method                                      | Purpose                                                                  |
| ------------------------------------------- | ------------------------------------------------------------------------ |
| `system_prompt` (property)                  | Lazy-loads the `.md` prompt file from `agents/prompts/{agent_id}.md`     |
| `build_messages(user_input, context)`       | Constructs the LLM message array: `[system_prompt, context, user_input]` |
| `run(user_input, context)`                  | Resolves provider → calls `provider.generate()` → returns full response  |
| `stream(user_input, context, execution_id)` | Token-by-token streaming + event bus publishing                          |

**Message construction for each LLM call:**

```
[system]  → The .md prompt file (lazy-loaded once, cached)
[user]    → "Context from previous agents:\n{accumulated_context}"  (agents 2-7)
[user]    → The original story input (story details + target framework)
```

**Event lifecycle per agent (published to WebSocket via EventBus):**

```
AGENT_STARTED → AGENT_CHUNK (per token) → AGENT_COMPLETED
```

---

### Orchestration: Sequential Pipeline with Context Accumulation

The orchestrator (`app/orchestrator/pipeline.py`) implements a **DeerFlow-inspired sequential pipeline** where each agent builds on the accumulated output of all previous agents.

#### Pipeline Singleton Instances

```python
# 7 singleton agents — created once at module load
AGENT_PIPELINE = [
    StoryAnalyzerAgent(),      # agent_id="story"
    TestStrategistAgent(),     # agent_id="strategy"
    TestCaseWriterAgent(),     # agent_id="writer"
    AutomationEngineerAgent(), # agent_id="automation"
    TestExecutorAgent(),       # agent_id="executor"
    BugDetectiveAgent(),       # agent_id="bug"
    CoverageAnalystAgent(),    # agent_id="coverage"
]
```

#### Context Accumulation (the key design pattern)

Each agent receives ALL prior agent outputs via `state.accumulated_context`:

```python
# PipelineState.accumulated_context property
@property
def accumulated_context(self) -> str:
    parts = []
    for agent_id, output in self.outputs.items():
        parts.append(f"=== {agent_id.upper()} OUTPUT ===\n{output}")
    return "\n\n".join(parts)
```

So the context grows with each agent:

| Agent                 | Sees Context From                                  |
| --------------------- | -------------------------------------------------- |
| ① Story Analyzer      | (none — first agent)                               |
| ② Test Strategist     | `=== STORY OUTPUT ===`                             |
| ③ Test Case Writer    | `=== STORY OUTPUT ===` + `=== STRATEGY OUTPUT ===` |
| ④ Automation Engineer | Story + Strategy + Writer outputs                  |
| ⑤ Test Executor       | Story + Strategy + Writer + Automation outputs     |
| ⑥ Bug Detective       | All 5 previous outputs                             |
| ⑦ Coverage Analyst    | All 6 previous outputs                             |

#### Execution Loop

```python
async def run_pipeline(state: PipelineState, story: JiraStory) -> PipelineState:
    state.start()  # phase → RUNNING
    user_input = _build_user_input(story, state.framework)

    try:
        for agent in AGENT_PIPELINE:
            state.agent_started(agent.agent_id)

            # Stream agent output and collect full content
            full_output = ""
            async for token in agent.stream(
                user_input=user_input,
                context=state.accumulated_context,
                execution_id=state.execution_id,
            ):
                full_output += token

            state.agent_completed(agent.agent_id, full_output)

        _extract_metrics(state)  # regex parse: test counts, coverage%, verdict
        state.complete()         # phase → COMPLETED

    except Exception as exc:
        state.fail(str(exc))     # phase → FAILED
```

#### State Machine Lifecycle

```
QUEUED ──state.start()──▶ RUNNING ──[7 agents]──▶ state.complete() ──▶ COMPLETED
                                   └──exception──▶ state.fail(err) ──▶ FAILED
```

`PipelineState` tracks:

- `execution_id`, `story_id`, `framework` — immutable config
- `phase` — QUEUED → RUNNING → COMPLETED/FAILED
- `current_agent` — which agent is running right now
- `agents_completed` — list of finished agent IDs
- `outputs` — dict of `{agent_id: full_output_text}` (append-only)
- `test_cases_generated`, `tests_passed/failed/skipped`, `coverage_percent`, `verdict` — parsed after pipeline

#### Metrics Extraction

After all 7 agents finish, `_extract_metrics()` parses agent text outputs with regex:

```python
# From executor output:
Passed: 18  → state.tests_passed = 18
Failed: 2   → state.tests_failed = 2

# From coverage output:
Overall Coverage: 87.5%  → state.coverage_percent = 87.5
Verdict: CONDITIONAL GO   → state.verdict = "CONDITIONAL GO"

# From writer output:
TC-001, TC-002, ...  → state.test_cases_generated = count("TC-")
```

---

### Per-Agent LLM Routing

Each agent can use a different LLM provider, configured via environment variables:

```bash
# .env — route different agents to different providers
LLM_DEFAULT_PROVIDER=ollama          # fallback for all agents
AGENT_STORY_PROVIDER=anthropic       # Story Analyzer → Claude
AGENT_STRATEGY_PROVIDER=anthropic    # Test Strategist → Claude
AGENT_AUTOMATION_PROVIDER=openai     # Automation Engineer → GPT-4o
AGENT_COVERAGE_PROVIDER=openai       # Coverage Analyst → GPT-4o
```

**Resolution chain:**

```
get_for_agent("story")
  → settings.provider_for_agent("story")
    → checks AGENT_STORY_PROVIDER env var → "anthropic"
    → (or falls back to LLM_DEFAULT_PROVIDER → "ollama")
  → registry.get("anthropic")
    → returns AnthropicProvider instance (initialized at startup)
```

**Provider registry initialization** (runs once at app startup via lifespan):

```python
def initialize_providers():
    register("mock", MockProvider())                    # always available
    if settings.ollama_base_url:
        register("ollama", OllamaProvider(...))         # local inference
    if settings.openai_api_key:
        register("openai", OpenAIProvider(...))         # OpenAI API
    if settings.anthropic_api_key:
        register("anthropic", AnthropicProvider(...))   # Anthropic API
    if settings.groq_api_key:
        register("groq", GroqProvider(...))             # Groq API
```

**Provider contract** (`LLMProvider` ABC):

| Method           | Signature                                                        | Purpose                     |
| ---------------- | ---------------------------------------------------------------- | --------------------------- |
| `generate()`     | `async (messages, temperature, max_tokens) → LLMResponse`        | Full response               |
| `stream()`       | `async (messages, temperature, max_tokens) → AsyncIterator[str]` | Token-by-token streaming    |
| `health_check()` | `async () → (bool, float)`                                       | Connectivity test + latency |

---

### Key Design Insight

The agents are **prompt-driven, not code-driven**. The Python classes are minimal wrappers (6 lines each). All the intelligence — the input/output contracts, formatting rules, quality constraints, and domain knowledge — lives in the markdown prompt files. This means:

- **Changing agent behavior** = editing a `.md` file (no code changes, no redeployment)
- **Adding a new agent** = create a new `.md` prompt + 6-line Python class
- **Testing prompts** = swap to `mock` provider to get deterministic outputs
- **Switching LLMs** = change one env var per agent (no code changes)

---

### Enhanced Architecture (TradingAgents-inspired)

The pipeline evolved from a simple 7-agent linear sequence to a **3-phase architecture with adversarial debates**, inspired by TradingAgents' Bull-vs-Bear pattern.

#### Architecture Comparison

| Feature            | Before (Linear)                    | After (Debate)                                           |
| ------------------ | ---------------------------------- | -------------------------------------------------------- |
| Flow               | 7 agents in sequence               | 3 phases with debates                                    |
| Quality check      | None (trust the output)            | Adversarial debate (N rounds)                            |
| Verdict            | Single agent's opinion             | Debate + independent judge (deep_think)                  |
| LLM tiers          | Single provider                    | Two-tier: deep_think for judges, quick_think for workers |
| Context management | Growing (all outputs concatenated) | Summarized between phases                                |
| Memory             | Stateless per-run                  | BM25 reflection memory (SQLite-backed)                   |
| Fault tolerance    | None                               | Retry with exponential backoff + provider fallback chain |

#### Phase Flow

```
PHASE 1: ANALYSIS (quick_think)
  ① Story Analyzer → ② Test Strategist
  → Context Summarizer compresses output

PHASE 2: GENERATION + REVIEW DEBATE
  ③ Test Case Writer ↔ ③b Test Critic  (N rounds, default 3)
  → ④ Automation Engineer → ⑤ Test Executor
  → Context Summarizer compresses output

PHASE 3: VERDICT DEBATE
  ⑥ Bug Detective ↔ ⑥b Quality Advocate  (N rounds, default 2)
  → ⑦ Coverage Judge (deep_think) renders GO/NO-GO verdict
```

#### Debate Engine (`orchestrator/debate.py`)

The `DebateEngine` runs N-round adversarial debates between two agents:

- **Round 1**: Agent A produces → Agent B critiques
- **Round N**: A defends → B re-critiques (with full debate history)
- **Judge** (optional): Synthesizes the debate transcript into a final verdict

Each turn publishes events to the WebSocket stream so the UI can show debates in real-time.

#### New Agents

| Agent              | ID           | Role                                                          | LLM Tier    |
| ------------------ | ------------ | ------------------------------------------------------------- | ----------- |
| Test Critic        | `critic`     | Challenges test quality (missing edge cases, weak assertions) | quick_think |
| Quality Advocate   | `advocate`   | Defends feature quality (mitigating factors, passing tests)   | quick_think |
| Context Summarizer | `summarizer` | Compresses phase output to prevent context overflow           | deep_think  |

#### Resilience Layer (`providers/resilience.py`)

Every LLM call is wrapped in `ResilientLLM` which provides:

- **Exponential backoff**: `base_delay * 2^attempt` with random jitter
- **Provider fallback chain**: On max retries, tries the next provider in the chain
- **Structured logging**: Every retry/fallback logged with structlog

```
Primary (anthropic) → 3 retries → Fallback 1 (openai) → 3 retries → Fallback 2 (ollama) → error
```

#### Reflection Memory (`memory/__init__.py`)

BM25-based memory that stores agent outputs and retrieves relevant past experiences:

- **Store**: After each pipeline run, key agent outputs are saved
- **Retrieve**: Before each agent runs, BM25 ranks past experiences by relevance
- **Inject**: Top-K reflections are added to the agent's context as "past experience"

```python
# Automatic per-run
memory.store("writer", execution_id, writer_output)
# Before next run
past = memory.retrieve_formatted("writer", user_input, top_k=3)
```

---

## Database Schema

```sql
-- 8 tables in SQLite (via SQLAlchemy 2.0 async + aiosqlite)

stories         (id PK, title, description, priority, labels, acceptance,
                 story_points, sprint, source, created_at)

executions      (id PK, story_id, story_title, framework, status, phase,
                 agents_completed, agent_outputs, tests_passed, tests_failed,
                 tests_skipped, coverage_percent, verdict, error,
                 started_at, completed_at)

test_cases      (id PK, execution_id, story_id, title, description, steps,
                 expected_result, priority, status, automated)

test_results    (id PK, execution_id, test_case_id, status, duration_ms,
                 error_message, stack_trace, screenshot_path, created_at)

bug_reports     (id PK, execution_id, test_case_id, title, severity,
                 description, steps_to_reproduce, expected_result,
                 actual_result, environment, jira_key, status, created_at)

artifacts       (id PK, execution_id, test_case_id, type, file_path,
                 file_name, mime_type, size_bytes, created_at)

scheduled_jobs  (id PK, name, story_id, framework, cron_expression,
                 enabled, last_run_at, next_run_at, created_at)

notification_logs (id PK, execution_id, channel, success,
                   error_message, sent_at)
```

---

## API Endpoints

All under **`/api/v1`** prefix. Interactive docs at `/docs` (Swagger UI) and `/redoc`.

### Pipeline

| Method | Path                              | Description                        |
| ------ | --------------------------------- | ---------------------------------- |
| `POST` | `/pipeline/run`                   | Start a pipeline run (returns 202) |
| `GET`  | `/pipeline/status/{execution_id}` | Get pipeline status                |

### Stories

| Method   | Path            | Description      |
| -------- | --------------- | ---------------- |
| `GET`    | `/stories`      | List all stories |
| `POST`   | `/stories`      | Create a story   |
| `GET`    | `/stories/{id}` | Get story detail |
| `PUT`    | `/stories/{id}` | Update a story   |
| `DELETE` | `/stories/{id}` | Delete a story   |

### Executions

| Method | Path               | Description                 |
| ------ | ------------------ | --------------------------- |
| `GET`  | `/executions`      | List executions (paginated) |
| `GET`  | `/executions/{id}` | Get execution details       |

### Bugs

| Method | Path                          | Description           |
| ------ | ----------------------------- | --------------------- |
| `GET`  | `/bugs/open`                  | List unfiled bugs     |
| `GET`  | `/bugs/detail/{bug_id}`       | Single bug detail     |
| `GET`  | `/bugs/{execution_id}`        | Bugs for an execution |
| `POST` | `/bugs/{bug_id}/file-to-jira` | File bug to Jira      |

### Scheduler

| Method   | Path                   | Description                 |
| -------- | ---------------------- | --------------------------- |
| `GET`    | `/scheduler/jobs`      | List all cron jobs          |
| `POST`   | `/scheduler/jobs`      | Create a cron job           |
| `PATCH`  | `/scheduler/jobs/{id}` | Enable/disable job          |
| `DELETE` | `/scheduler/jobs/{id}` | Delete a cron job           |
| `GET`    | `/scheduler/status`    | Scheduler health + job list |

### Jira

| Method | Path                        | Description            |
| ------ | --------------------------- | ---------------------- |
| `GET`  | `/jira/health`              | Test Jira connectivity |
| `GET`  | `/jira/stories/{issue_key}` | Import single story    |
| `GET`  | `/jira/sprint-stories`      | Import sprint stories  |
| `POST` | `/jira/search`              | JQL search             |

### Webhooks

| Method | Path               | Description                   |
| ------ | ------------------ | ----------------------------- |
| `POST` | `/webhooks/github` | Receive GitHub push/PR events |

### Artifacts & Files

| Method | Path                             | Description              |
| ------ | -------------------------------- | ------------------------ |
| `GET`  | `/artifacts/{execution_id}`      | List execution artifacts |
| `GET`  | `/artifacts/download/{filename}` | Download artifact        |
| `GET`  | `/files/{story_id}`              | List generated files     |
| `GET`  | `/files/{story_id}/content`      | Read file content        |

### WebSocket

| Path                                 | Description                 |
| ------------------------------------ | --------------------------- |
| `ws://host/api/v1/ws/{execution_id}` | Real-time pipeline progress |

---

## Configuration

All config is environment-driven via **Pydantic Settings v2**. Copy `.env.example` → `.env`:

```bash
cp .env.example .env
```

### Key Environment Variables

| Variable                 | Default                                | Description                          |
| ------------------------ | -------------------------------------- | ------------------------------------ |
| `APP_ENV`                | `development`                          | Environment (development/production) |
| `APP_PORT`               | `8000`                                 | Server port                          |
| `LLM_DEFAULT_PROVIDER`   | `mock`                                 | Default LLM provider                 |
| `LLM_DEEP_PROVIDER`      | (none)                                 | Provider for judges/critical agents  |
| `LLM_QUICK_PROVIDER`     | (none)                                 | Provider for workers/analysts        |
| `DEBATE_MAX_ROUNDS`      | `3`                                    | Writer↔Critic debate rounds          |
| `RISK_DEBATE_MAX_ROUNDS` | `2`                                    | Bug Detective↔Advocate debate rounds |
| `LLM_MAX_RETRIES`        | `3`                                    | Retry attempts per LLM call          |
| `LLM_RETRY_BASE_DELAY`   | `1.0`                                  | Base backoff delay (seconds)         |
| `LLM_FALLBACK_PROVIDERS` | `[]`                                   | Ordered fallback chain (JSON array)  |
| `DB_URL`                 | `sqlite+aiosqlite:///data/qa_nexus.db` | Database connection string           |
| `WORKSPACE_DIR`          | `./workspace`                          | Generated files root directory       |
| `JIRA_BASE_URL`          | (empty)                                | Jira instance URL                    |
| `GITHUB_TOKEN`           | (empty)                                | GitHub PAT for PR comments           |
| `GITHUB_WEBHOOK_SECRET`  | (empty)                                | HMAC secret for webhook verification |
| `SLACK_WEBHOOK_URL`      | (empty)                                | Slack incoming webhook URL           |
| `SMTP_HOST`              | (empty)                                | SMTP server for email notifications  |

See `.env.example` for the full list.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for Playwright runner)

### Install & Run

```bash
cd qa-ai/backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn app.main:app --reload --port 8000

# Open API docs
# http://localhost:8000/docs
```

### Verify

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"healthy","version":"1.0.0"}

# List agents
curl http://localhost:8000/api/v1/agents
```

---

## Tech Stack

| Layer           | Technology                       | Version |
| --------------- | -------------------------------- | ------- |
| **Framework**   | FastAPI                          | ≥0.115  |
| **Server**      | Uvicorn (ASGI)                   | ≥0.34   |
| **Validation**  | Pydantic v2                      | ≥2.10   |
| **Database**    | SQLAlchemy 2.0 async + aiosqlite | ≥2.0    |
| **HTTP Client** | httpx (async)                    | ≥0.28   |
| **Scheduler**   | APScheduler                      | ≥3.11   |
| **Logging**     | structlog                        | ≥24.4   |
| **LLM SDKs**    | openai, anthropic, ollama, groq  | Latest  |

### Async Best Practices Applied

- **httpx.AsyncClient reuse** — single client per integration class (Jira, GitHub, Slack) for connection pooling, NOT a new client per request
- **Fine-grained timeouts** — `httpx.Timeout(30.0, connect=10.0)` separates connect vs read timeouts
- **Retry with exponential backoff** — 3 attempts with increasing delays for transient failures
- **SQLAlchemy async sessions** — `async_sessionmaker` with `expire_on_commit=False`, proper `async with` context managers
- **Thread-pool for blocking I/O** — SMTP email sends offloaded via `asyncio.get_running_loop().run_in_executor()`
- **Parallel notifications** — `asyncio.gather()` fans out to Slack + Email simultaneously
- **Non-blocking test execution** — subprocess runners use `asyncio.create_subprocess_exec`
- **Background tasks** — pipeline runs via FastAPI `BackgroundTasks` (non-blocking 202 response)
- **Lifespan management** — DB init/close, scheduler start/stop, provider init all in `@asynccontextmanager` lifespan

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # App factory + lifespan
│   ├── config.py                # Pydantic Settings v2
│   ├── dependencies.py          # FastAPI DI (settings, db session)
│   │
│   ├── api/                     # 14 route modules
│   │   ├── router.py            # Main router aggregation
│   │   ├── pipeline.py          # Pipeline trigger + status
│   │   ├── stories.py           # Story CRUD
│   │   ├── agents.py            # Agent info
│   │   ├── dashboard.py         # Metrics
│   │   ├── executions.py        # Execution history
│   │   ├── reports.py           # Full test reports
│   │   ├── settings_routes.py   # App settings
│   │   ├── artifacts.py         # Artifact download
│   │   ├── bugs.py              # Bug management + Jira filing
│   │   ├── files.py             # Generated file browser
│   │   ├── jira_routes.py       # Jira import/search
│   │   ├── scheduler_routes.py  # Cron job CRUD
│   │   ├── webhooks.py          # GitHub webhook receiver
│   │   └── ws.py                # WebSocket endpoint
│   │
│   ├── agents/                  # 9 AI agents + prompts
│   │   ├── base.py              # BaseAgent (retry/fallback via ResilientLLM)
│   │   ├── story_analyzer.py
│   │   ├── test_strategist.py
│   │   ├── test_case_writer.py
│   │   ├── test_critic.py       # NEW — adversarial debate partner for Writer
│   │   ├── automation_engineer.py
│   │   ├── test_executor.py
│   │   ├── bug_detective.py
│   │   ├── quality_advocate.py  # NEW — optimistic debate partner for Bug Detective
│   │   ├── coverage_analyst.py  # Upgraded → Coverage Judge (deep_think)
│   │   └── prompts/             # System prompts (.md files, +3 new)
│   │
│   ├── orchestrator/            # 3-phase pipeline with debates
│   │   ├── pipeline.py          # run_pipeline() — 3-phase orchestration
│   │   ├── debate.py            # NEW — DebateEngine (N-round adversarial)
│   │   ├── summarizer.py        # NEW — Context compression between phases
│   │   └── state.py             # PipelineState dataclass
│   │
│   ├── providers/               # LLM provider adapters
│   │   ├── base.py              # BaseProvider ABC
│   │   ├── registry.py          # Provider registration + build_resilient()
│   │   ├── resilience.py        # NEW — ResilientLLM (retry + fallback chain)
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── ollama.py
│   │   ├── groq_provider.py
│   │   └── mock.py
│   │
│   ├── db/                      # Database layer
│   │   ├── engine.py            # Async engine + session factory
│   │   ├── tables.py            # 8 ORM tables
│   │   └── repositories/       # Data access layer
│   │
│   ├── runner/                  # Real test execution
│   │   ├── base.py              # BaseRunner ABC + RunResult
│   │   ├── process_manager.py   # Async subprocess management
│   │   ├── sandbox.py           # Isolated temp directories
│   │   ├── playwright_runner.py
│   │   ├── selenium_runner.py
│   │   └── registry.py
│   │
│   ├── parsers/                 # Test result parsing
│   │   ├── junit_parser.py
│   │   ├── console_parser.py
│   │   └── coverage_parser.py
│   │
│   ├── integrations/            # External services
│   │   ├── jira/                # Jira Cloud/Server REST API
│   │   ├── github/              # Webhooks + PR comments
│   │   └── notifications/       # Slack + Email + Dispatcher
│   │
│   ├── scheduler/               # Cron-based pipeline triggers
│   │   ├── scheduler.py         # APScheduler wrapper
│   │   └── jobs.py              # Scheduled pipeline execution
│   │
│   ├── evidence/                # Test artifact collection
│   │   ├── collector.py
│   │   └── storage.py
│   │
│   ├── files/                   # Generated file management
│   │   └── manager.py
│   │
│   ├── memory/                  # NEW — Reflection memory system
│   │   └── __init__.py          # BM25-based memory (SQLite-backed)
│   │
│   ├── models/                  # Pydantic schemas (13 files)
│   │
│   ├── services/                # Business logic
│   │   ├── story_service.py
│   │   ├── execution_service.py
│   │   └── dashboard_service.py
│   │
│   └── adapters/                # Framework definitions
│       └── frameworks.py
│
├── .env.example                 # Environment config template
├── pyproject.toml               # Project metadata + dependencies
├── requirements.txt             # pip-installable dependencies
└── data/                        # SQLite database (auto-created)
    └── qa_nexus.db
```

---

_QA Nexus Backend — 95 source files, 14 API routers, 7 AI agents, 5 LLM providers, 2 test runners, 3 parsers, 4 integrations._
