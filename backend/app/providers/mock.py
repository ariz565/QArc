"""Mock provider — deterministic output for development and testing.

Returns pre-written agent outputs so the pipeline can run without API keys.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from app.providers.base import LLMMessage, LLMProvider, LLMResponse


class MockProvider(LLMProvider):
    provider_name = "mock"

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Extract the system prompt to determine which agent is calling
        content = self._build_mock_response(messages)
        return LLMResponse(
            content=content,
            model="mock-model",
            provider=self.provider_name,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        content = self._build_mock_response(messages)
        # Simulate streaming by yielding word-by-word
        words = content.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.02)  # ~50 words/sec

    async def health_check(self) -> tuple[bool, float]:
        return True, 0.1

    def _build_mock_response(self, messages: list[LLMMessage]) -> str:
        """Build a mock response based on the system prompt content."""
        system = next((m.content for m in messages if m.role == "system"), "")
        lower = system.lower()

        if "story analyzer" in lower or "requirement" in lower:
            return self._mock_story_analysis()
        if "strategist" in lower or "strategy" in lower:
            return self._mock_test_strategy()
        if "test case writer" in lower or "bdd" in lower:
            return self._mock_test_cases()
        if "automation engineer" in lower or "code generation" in lower:
            return self._mock_automation_code()
        if "executor" in lower or "execution" in lower:
            return self._mock_execution_results()
        if "bug detective" in lower or "failure" in lower:
            return self._mock_bug_analysis()
        if "coverage analyst" in lower or "coverage" in lower:
            return self._mock_coverage_report()

        return "[Mock] Agent response generated successfully."

    @staticmethod
    def _mock_story_analysis() -> str:
        return """📋 REQUIREMENT ANALYSIS

━━━ Core Requirements (4) ━━━
  ✓ R1: Primary user flow validation
  ✓ R2: Error handling and edge cases
  ✓ R3: Security boundary checks
  ✓ R4: Performance under load

━━━ Edge Cases Identified (3) ━━━
  ⚡ E1: Concurrent access patterns
  ⚡ E2: Network timeout handling
  ⚡ E3: Invalid input boundaries

━━━ Risk Assessment: MEDIUM ━━━
Standard feature with moderate security implications."""

    @staticmethod
    def _mock_test_strategy() -> str:
        return """📐 TEST STRATEGY

━━━ Test Distribution ━━━
  Functional Tests     ████████████░░░  8 tests (40%)
  Security Tests       ██████████░░░░░  5 tests (25%)
  Edge Case Tests      ████████░░░░░░░  4 tests (20%)
  Performance Tests    ████░░░░░░░░░░░  2 tests (10%)
  Accessibility Tests  ██░░░░░░░░░░░░░  1 test  (5%)

━━━ Priority Matrix ━━━
  P0 (Must Pass):  Happy path, auth validation
  P1 (Critical):   Error handling, data integrity
  P2 (Important):  Edge cases, concurrent access
  P3 (Nice-Have):  Performance benchmarks"""

    @staticmethod
    def _mock_test_cases() -> str:
        return """🧪 GENERATED TEST CASES (8 total)

TC-001 | P0 | Functional
  Scenario: Verify primary user flow
  Given the user is on the main page
  When they complete the primary action
  Then the expected result is displayed
  And data is persisted correctly

TC-002 | P0 | Functional
  Scenario: Validate error handling
  Given the user provides invalid input
  When the form is submitted
  Then a clear error message appears
  And no data corruption occurs

TC-003 | P1 | Security
  Scenario: Authentication boundary check
  Given an unauthenticated user
  When they attempt a protected action
  Then they are redirected to login
  And the action is not executed"""

    @staticmethod
    def _mock_automation_code() -> str:
        return """🔧 AUTOMATION CODE — Playwright (TypeScript)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Validation', () => {
  test('TC-001: Primary user flow', async ({ page }) => {
    await page.goto('/feature');
    await page.getByRole('button', { name: 'Start' }).click();
    await page.waitForURL('/result');
    await expect(page.getByText('Success')).toBeVisible();
  });

  test('TC-002: Error handling', async ({ page }) => {
    await page.goto('/feature');
    await page.fill('#input', 'invalid-data');
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Error')).toBeVisible();
  });
});
```

Generated 2 test files covering 8 test cases."""

    @staticmethod
    def _mock_execution_results() -> str:
        return """⚡ EXECUTION RESULTS

━━━ Summary ━━━
  Total:    8 tests
  Passed:   6 ✅
  Failed:   2 ❌
  Skipped:  0
  Duration: 12.4s

━━━ Failed Tests ━━━
  ✗ TC-005: Concurrent access — Race condition on shared resource
  ✗ TC-007: Performance threshold — Response > 500ms under load"""

    @staticmethod
    def _mock_bug_analysis() -> str:
        return """🐛 BUG ANALYSIS

━━━ BUG-001: Race Condition ━━━
  Severity: High
  Test: TC-005 (Concurrent access)
  Root Cause: Missing mutex on shared state update
  Suggestion: Add optimistic locking or queue writes

━━━ BUG-002: Performance Degradation ━━━
  Severity: Medium
  Test: TC-007 (Performance threshold)
  Root Cause: N+1 query pattern in data fetch
  Suggestion: Batch queries or add database index"""

    @staticmethod
    def _mock_coverage_report() -> str:
        return """📊 COVERAGE ANALYSIS

━━━ Coverage by Type ━━━
  Functional:    92% ██████████░
  Security:      85% █████████░░
  Edge Cases:    78% ████████░░░
  Performance:   65% ███████░░░░
  Accessibility: 70% ███████░░░░

━━━ Overall Coverage: 82% ━━━

━━━ Verdict: CONDITIONAL GO ━━━
Feature can proceed to staging with noted caveats.
Two high-priority bugs must be resolved before production.

━━━ Recommendations ━━━
  1. Fix race condition in concurrent access flow
  2. Optimize database queries for performance
  3. Add retry logic for flaky network tests"""
