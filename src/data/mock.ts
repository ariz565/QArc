// ═══════════════════════════════════════════════════════════════
// QA NEXUS — Mock Data for Demo
// All agent outputs, test cases, and results are pre-written
// so the demo works instantly without API keys.
// ═══════════════════════════════════════════════════════════════

export interface JiraStory {
  id: string;
  title: string;
  description: string;
  priority: "Critical" | "High" | "Medium";
  labels: string[];
  acceptance: string[];
  storyPoints: number;
  sprint: string;
}

export interface AgentDef {
  id: string;
  name: string;
  role: string;
  color: string;
  icon: string;
  model: string;
  description: string;
}

export interface TestCase {
  id: string;
  name: string;
  type: "functional" | "edge" | "security" | "performance" | "accessibility";
  priority: "P0" | "P1" | "P2" | "P3";
  scenario: string;
  steps: string[];
  expected: string;
  status: "pending" | "pass" | "fail" | "running" | "skipped";
  duration?: string;
  automationCode?: string;
}

export interface AgentOutput {
  agentId: string;
  content: string;
  testCases?: TestCase[];
  automationCode?: string;
  executionResults?: {
    id: string;
    status: "pass" | "fail";
    duration: string;
    error?: string;
  }[];
}

export interface LogEntry {
  time: string;
  agentId: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
}

// ─── Agent Definitions ───────────────────────────────────────

export const AGENTS: AgentDef[] = [
  {
    id: "story",
    name: "Story Analyzer",
    role: "Requirement Intelligence",
    color: "#22d3ee",
    icon: "story",
    model: "Claude Sonnet 4",
    description:
      "Reads Jira stories and extracts requirements, edge cases, risks, and testable acceptance criteria",
  },
  {
    id: "strategy",
    name: "Test Strategist",
    role: "Strategy & Planning",
    color: "#fb923c",
    icon: "strategy",
    model: "GPT-4o",
    description:
      "Determines optimal test types, priority matrix, and risk-based test allocation",
  },
  {
    id: "writer",
    name: "Test Case Writer",
    role: "BDD Test Generation",
    color: "#a78bfa",
    icon: "writer",
    model: "Claude Sonnet 4",
    description:
      "Generates comprehensive BDD test cases with Given/When/Then scenarios",
  },
  {
    id: "automation",
    name: "Automation Engineer",
    role: "Code Generation",
    color: "#34d399",
    icon: "automation",
    model: "Claude Sonnet 4",
    description:
      "Converts test cases into executable Playwright/Cypress automation code",
  },
  {
    id: "executor",
    name: "Test Executor",
    role: "Execution Engine",
    color: "#60a5fa",
    icon: "executor",
    model: "Runtime Engine",
    description:
      "Executes automated tests with parallel browser contexts and collects results",
  },
  {
    id: "bug",
    name: "Bug Detective",
    role: "Failure Analysis",
    color: "#fb7185",
    icon: "bug",
    model: "GPT-4o",
    description:
      "Analyzes test failures, identifies root causes, and generates detailed bug reports",
  },
  {
    id: "coverage",
    name: "Coverage Analyst",
    role: "Quality Insights",
    color: "#fbbf24",
    icon: "coverage",
    model: "Claude Sonnet 4",
    description:
      "Evaluates test coverage, identifies gaps, and provides go/no-go recommendations",
  },
];

// ─── Jira Stories ────────────────────────────────────────────

export const STORIES: JiraStory[] = [
  {
    id: "PROJ-1042",
    title: "User Authentication with OAuth2",
    description:
      "As a user, I want to log in using my Google or GitHub account so that I don't need to remember separate credentials. The system should redirect to the OAuth provider, receive the callback token, validate the JWT, create or update the user profile, and establish a secure session with httpOnly cookies.",
    priority: "High",
    labels: ["auth", "security", "oauth"],
    storyPoints: 8,
    sprint: "Sprint 23",
    acceptance: [
      "Given valid OAuth credentials, user is redirected to dashboard within 2 seconds",
      "Given invalid or expired token, user sees clear error and retry option",
      "Given new user, profile is auto-created from OAuth provider data",
      "Session expires after 24 hours of inactivity",
      "Concurrent sessions from different devices are supported",
    ],
  },
  {
    id: "PROJ-1043",
    title: "Shopping Cart Checkout Flow",
    description:
      "As a shopper, I want to complete purchase of items in my cart, including applying discount codes, selecting shipping method, entering payment via Stripe, and receiving order confirmation email with tracking link.",
    priority: "Critical",
    labels: ["payments", "cart", "stripe"],
    storyPoints: 13,
    sprint: "Sprint 23",
    acceptance: [
      "Valid discount codes reduce total price correctly",
      "Invalid discount codes show clear error without clearing cart",
      "Stripe payment succeeds and order record is created",
      "Failed payment shows retry option and preserves cart state",
      "Order confirmation email with tracking sent within 60 seconds",
    ],
  },
  {
    id: "PROJ-1044",
    title: "Real-time Notifications System",
    description:
      "As a user, I want to receive instant notifications for mentions, task assignments, and system alerts via WebSocket connection, with the ability to mark as read, filter by type, and configure notification preferences per category.",
    priority: "Medium",
    labels: ["websocket", "notifications", "realtime"],
    storyPoints: 5,
    sprint: "Sprint 24",
    acceptance: [
      "Notifications appear within 500ms of triggering event",
      "Badge count updates in real-time across all open tabs",
      "Mark all as read clears badge count instantly",
      "Notification filter preferences persist across sessions",
    ],
  },
];

// ─── Story-specific Agent Outputs ────────────────────────────

export const STORY_OUTPUTS: Record<string, AgentOutput[]> = {
  "PROJ-1042": [
    {
      agentId: "story",
      content: `📋 REQUIREMENT ANALYSIS — PROJ-1042: OAuth2 Authentication

━━━ Core Requirements (5) ━━━
  ✓ R1: OAuth redirect flow (Google + GitHub providers)
  ✓ R2: JWT token validation with provider-specific verification
  ✓ R3: Auto-create user profile from OAuth claims (name, email, avatar)
  ✓ R4: Session management with httpOnly secure cookies
  ✓ R5: Multi-device concurrent session support

━━━ Edge Cases Identified (6) ━━━
  ⚡ E1: OAuth popup blocked by browser — fallback to redirect flow
  ⚡ E2: Provider returns partial profile (missing email from GitHub)
  ⚡ E3: Network timeout during token exchange
  ⚡ E4: User revokes OAuth access mid-session
  ⚡ E5: Duplicate email conflict (same email, different OAuth providers)
  ⚡ E6: CSRF token mismatch on callback

━━━ Security Risks (4) ━━━
  🔒 S1: Token replay attacks — need nonce + timestamp validation
  🔒 S2: Open redirect vulnerability in callback URL
  🔒 S3: Session fixation during OAuth flow
  🔒 S4: Missing PKCE for public client authorization code flow

━━━ Integration Points (3) ━━━
  🔗 Google OAuth 2.0 API (accounts.google.com)
  🔗 GitHub OAuth App (github.com/login/oauth)
  🔗 Internal User Service (POST /api/users/upsert)

━━━ Risk Assessment: HIGH ━━━
Authentication is a critical security boundary. Recommend comprehensive security testing.`,
    },
    {
      agentId: "strategy",
      content: `📐 TEST STRATEGY — PROJ-1042: OAuth2 Authentication

━━━ Test Distribution ━━━
  Functional Tests     ████████████░░░  8 tests (40%)
  Security Tests       ██████████░░░░░  5 tests (25%)
  Edge Case Tests      ████████░░░░░░░  4 tests (20%)
  Performance Tests    ████░░░░░░░░░░░  2 tests (10%)
  Accessibility Tests  ██░░░░░░░░░░░░░  1 test  (5%)

━━━ Priority Matrix ━━━
  P0 (Must Pass):  Happy path login, token validation, session creation
  P1 (Critical):   Error handling, security checks, profile creation
  P2 (Important):  Edge cases, concurrent sessions, timeout handling
  P3 (Nice-Have):  Performance benchmarks, accessibility

━━━ Recommended Approach ━━━
  • Framework: Playwright (cross-browser, network interception)
  • Mocking: OAuth provider APIs mocked with route.fulfill()
  • Data: Unique test users per scenario to avoid state conflicts
  • Environment: Staging with test OAuth app credentials
  • Parallelism: 4 workers — tests are independent

━━━ Estimated Execution Time: 45 seconds (parallel) ━━━`,
    },
    {
      agentId: "writer",
      content: `✍ TEST CASES GENERATED — PROJ-1042: OAuth2 Authentication

Generated 8 comprehensive BDD test cases covering:
  • 4 functional flows (happy path + variations)
  • 2 security scenarios (token replay, open redirect)
  • 1 edge case (partial profile data)
  • 1 performance validation (redirect timing)

All cases follow Given/When/Then format with clear preconditions.
See test case panel for full details →`,
      testCases: [
        {
          id: "TC-001",
          name: "Successful Google OAuth Login",
          type: "functional",
          priority: "P0",
          scenario:
            "Given a user with valid Google credentials\nWhen they click 'Sign in with Google' and authorize\nThen they are redirected to dashboard with active session",
          steps: [
            "Navigate to /login page",
            "Click 'Sign in with Google' button",
            "Complete Google OAuth consent screen",
            "Verify redirect to /dashboard",
            "Verify session cookie is set (httpOnly, secure)",
            "Verify user profile shows Google display name",
          ],
          expected:
            "User lands on dashboard with valid session within 2 seconds",
          status: "pending",
        },
        {
          id: "TC-002",
          name: "Successful GitHub OAuth Login",
          type: "functional",
          priority: "P0",
          scenario:
            "Given a user with valid GitHub credentials\nWhen they click 'Sign in with GitHub' and authorize\nThen they are redirected to dashboard with active session",
          steps: [
            "Navigate to /login page",
            "Click 'Sign in with GitHub' button",
            "Authorize on GitHub OAuth page",
            "Verify redirect to /dashboard",
            "Verify user profile created from GitHub data",
          ],
          expected: "User authenticated and profile synced from GitHub",
          status: "pending",
        },
        {
          id: "TC-003",
          name: "Invalid Token Handling",
          type: "functional",
          priority: "P1",
          scenario:
            "Given an expired or tampered OAuth token\nWhen the callback is processed\nThen user sees error message with retry option",
          steps: [
            "Intercept OAuth callback with invalid token",
            "Verify error page is displayed",
            "Verify error message is user-friendly",
            "Click retry button and verify redirect to login",
          ],
          expected: "Clear error message displayed, no session created",
          status: "pending",
        },
        {
          id: "TC-004",
          name: "New User Auto-Registration",
          type: "functional",
          priority: "P0",
          scenario:
            "Given a first-time user with no existing account\nWhen they complete OAuth login\nThen a new user profile is created from OAuth data",
          steps: [
            "Use new OAuth credentials not in system",
            "Complete OAuth flow",
            "Verify user record created in database",
            "Verify name, email, avatar populated from OAuth",
            "Verify welcome email sent",
          ],
          expected: "New user profile created with OAuth provider data",
          status: "pending",
        },
        {
          id: "TC-005",
          name: "Token Replay Attack Prevention",
          type: "security",
          priority: "P1",
          scenario:
            "Given a valid OAuth callback token\nWhen the same token is submitted twice\nThen the second request is rejected",
          steps: [
            "Capture valid OAuth callback URL",
            "Submit callback (first time — succeeds)",
            "Replay same callback URL",
            "Verify second attempt is rejected (403)",
            "Verify security event is logged",
          ],
          expected: "Replay detected and blocked, security event logged",
          status: "pending",
        },
        {
          id: "TC-006",
          name: "Open Redirect Prevention",
          type: "security",
          priority: "P1",
          scenario:
            "Given a manipulated redirect_uri parameter\nWhen the OAuth callback processes\nThen the redirect is blocked or sanitized",
          steps: [
            "Craft OAuth request with redirect_uri=https://evil.com",
            "Attempt to complete OAuth flow",
            "Verify redirect goes to allowed domain only",
            "Verify manipulated URL is rejected",
          ],
          expected: "Redirect only to whitelisted domains",
          status: "pending",
        },
        {
          id: "TC-007",
          name: "Partial Profile Data Handling",
          type: "edge",
          priority: "P2",
          scenario:
            "Given a GitHub user with private email\nWhen they complete OAuth login\nThen system handles missing email gracefully",
          steps: [
            "Use GitHub account with email set to private",
            "Complete OAuth flow",
            "Verify user is prompted to provide email",
            "Submit email and verify profile completion",
          ],
          expected: "User prompted for missing info, not error page",
          status: "pending",
        },
        {
          id: "TC-008",
          name: "OAuth Redirect Performance",
          type: "performance",
          priority: "P2",
          scenario:
            "Given standard network conditions\nWhen user completes OAuth flow\nThen entire flow completes within 2 seconds",
          steps: [
            "Measure time from login click to dashboard render",
            "Include OAuth redirect + callback + session creation",
            "Run 10 iterations and calculate p95",
          ],
          expected: "P95 latency < 2000ms for complete OAuth flow",
          status: "pending",
        },
      ],
    },
    {
      agentId: "automation",
      content: `⟨/⟩ AUTOMATION CODE GENERATED — Playwright (TypeScript)`,
      automationCode: `import { test, expect } from '@playwright/test';

// ═══ OAuth2 Authentication Test Suite ═══
// Generated by QA Nexus AI — Automation Engineer Agent
// Framework: Playwright | Language: TypeScript

test.describe('OAuth2 Authentication', () => {

  test('TC-001: Successful Google OAuth Login', async ({ page }) => {
    // Mock Google OAuth endpoint
    await page.route('**/accounts.google.com/**', async (route) => {
      await route.fulfill({
        status: 302,
        headers: {
          'Location': '/auth/callback?code=mock_google_code&state=valid_state'
        }
      });
    });

    await page.goto('/login');
    await page.click('[data-testid="google-oauth-btn"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 2000 });

    // Verify session cookie
    const cookies = await page.context().cookies();
    const session = cookies.find(c => c.name === 'session_token');
    expect(session).toBeDefined();
    expect(session!.httpOnly).toBe(true);
    expect(session!.secure).toBe(true);

    // Verify user profile displayed
    await expect(page.locator('[data-testid="user-name"]'))
      .toBeVisible();
  });

  test('TC-003: Invalid Token Handling', async ({ page }) => {
    // Simulate expired token callback
    await page.goto('/auth/callback?code=expired_token&state=valid');

    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Authentication failed');

    await expect(page.locator('[data-testid="retry-btn"]'))
      .toBeVisible();

    // Verify no session created
    const cookies = await page.context().cookies();
    const session = cookies.find(c => c.name === 'session_token');
    expect(session).toBeUndefined();
  });

  test('TC-005: Token Replay Attack Prevention', async ({ page }) => {
    const callbackUrl = '/auth/callback?code=valid_once&state=nonce_123';

    // First request — should succeed
    const first = await page.goto(callbackUrl);
    expect(first?.status()).toBe(200);

    // Replay — should be rejected
    const replay = await page.goto(callbackUrl);
    expect(replay?.status()).toBe(403);
  });

  test('TC-008: OAuth Performance', async ({ page }) => {
    const start = Date.now();

    await page.goto('/login');
    await page.click('[data-testid="google-oauth-btn"]');
    await expect(page).toHaveURL('/dashboard');

    const elapsed = Date.now() - start;
    expect(elapsed).toBeLessThan(2000); // P95 < 2s
  });
});`,
    },
    {
      agentId: "executor",
      content: ``,
      executionResults: [
        { id: "TC-001", status: "pass", duration: "1.23s" },
        { id: "TC-002", status: "pass", duration: "1.18s" },
        { id: "TC-003", status: "pass", duration: "0.89s" },
        { id: "TC-004", status: "pass", duration: "1.45s" },
        {
          id: "TC-005",
          status: "fail",
          duration: "0.67s",
          error:
            "Expected status 403 but received 200 — replay protection not implemented",
        },
        { id: "TC-006", status: "pass", duration: "0.54s" },
        {
          id: "TC-007",
          status: "fail",
          duration: "2.12s",
          error:
            "User redirected to error page instead of email prompt — missing fallback UI",
        },
        { id: "TC-008", status: "pass", duration: "0.92s" },
      ],
    },
    {
      agentId: "bug",
      content: `🐛 BUG REPORT — 2 Failures Detected

━━━ BUG-001: Token Replay Protection Not Implemented ━━━
  Severity:  🔴 CRITICAL (Security)
  Test:      TC-005 — Token Replay Attack Prevention
  Expected:  Second submission of same OAuth token returns 403
  Actual:    Server returns 200 and creates duplicate session
  Root Cause: OAuth callback handler does not track consumed nonces
  
  Recommendation:
    Store consumed authorization codes in Redis with 10-min TTL.
    Reject any code that has been seen before.
    
    // Fix in auth/callback.ts:
    const consumed = await redis.get(\`oauth:code:\${code}\`);
    if (consumed) return res.status(403).json({ error: 'Token already used' });
    await redis.setEx(\`oauth:code:\${code}\`, 600, '1');

━━━ BUG-002: Missing Email Prompt for Private GitHub Users ━━━
  Severity:  🟡 HIGH (Functional)
  Test:      TC-007 — Partial Profile Data Handling
  Expected:  User prompted to provide email when GitHub email is private
  Actual:    Application shows 500 error page (null email in DB insert)
  Root Cause: User service does NOT NULL check on email before insert
  
  Recommendation:
    Add email fallback flow in OAuth callback:
    1. Check if email is present in OAuth claims
    2. If missing, redirect to /complete-profile with partial data
    3. Require email input before creating account
    
━━━ Impact Assessment ━━━
  BUG-001 is a SECURITY VULNERABILITY — must fix before release
  BUG-002 affects ~8% of GitHub users (private email setting)
  Combined risk: DO NOT SHIP without fixes`,
    },
    {
      agentId: "coverage",
      content: `◎ COVERAGE ANALYSIS — PROJ-1042: OAuth2 Authentication

━━━ Test Results Summary ━━━
  Total Tests:    8
  Passed:         6  ████████████░░  75%
  Failed:         2  ████░░░░░░░░░░  25%
  Execution Time: 9.0s (parallel: 4.2s)

━━━ Coverage by Category ━━━
  Functional     4/4  ████████████████  100%  ✓
  Security       1/2  ████████░░░░░░░░   50%  ⚠
  Edge Cases     0/1  ░░░░░░░░░░░░░░░░    0%  ✗
  Performance    1/1  ████████████████  100%  ✓
  Accessibility  0/0  — not tested —

━━━ Requirement Coverage ━━━
  R1: OAuth redirect flow          ✓ Covered (TC-001, TC-002)
  R2: JWT token validation         ✓ Covered (TC-003)
  R3: Auto-create user profile     ✓ Covered (TC-004)
  R4: Session management           ✓ Covered (TC-001)
  R5: Multi-device sessions        ✗ NOT COVERED — needs test

━━━ Recommendations ━━━
  1. 🔴 FIX BUG-001 (token replay) before any release
  2. 🟡 FIX BUG-002 (missing email) — affects GitHub users
  3. 🔵 ADD test for concurrent multi-device sessions (R5)
  4. 🔵 ADD test for session expiry after 24h inactivity
  5. 🔵 ADD accessibility test for OAuth login buttons

━━━ VERDICT: 🟡 CONDITIONAL GO ━━━
  Fix 2 critical bugs, add 3 gap tests, then clear for release.
  Estimated effort: 4-6 hours of development.`,
    },
  ],

  "PROJ-1043": [
    {
      agentId: "story",
      content: `📋 REQUIREMENT ANALYSIS — PROJ-1043: Shopping Cart Checkout

━━━ Core Requirements (6) ━━━
  ✓ R1: Apply valid discount codes with real-time price recalculation
  ✓ R2: Invalid code handling with clear error messaging
  ✓ R3: Shipping method selection with cost + ETA display
  ✓ R4: Stripe payment processing (card, Apple Pay, Google Pay)
  ✓ R5: Order creation and confirmation page
  ✓ R6: Email confirmation with tracking link within 60 seconds

━━━ Edge Cases Identified (7) ━━━
  ⚡ E1: Cart item goes out of stock during checkout
  ⚡ E2: Discount code expired between apply and payment
  ⚡ E3: Price changes during checkout flow
  ⚡ E4: Multiple browser tabs completing same cart
  ⚡ E5: Network failure mid-payment (Stripe intent created but not confirmed)
  ⚡ E6: Cart exceeds Stripe maximum charge ($999,999.99)
  ⚡ E7: Currency conversion edge cases ($0.01 rounding)

━━━ Security Risks (3) ━━━
  🔒 S1: Price tampering via API manipulation (server-side validation required)
  🔒 S2: Discount code brute force enumeration
  🔒 S3: PCI compliance — no raw card numbers in logs

━━━ Risk Assessment: CRITICAL ━━━
Payment flow — financial impact. Requires comprehensive testing.`,
    },
    {
      agentId: "strategy",
      content: `📐 TEST STRATEGY — PROJ-1043: Shopping Cart Checkout

━━━ Test Distribution ━━━
  Functional Tests     ██████████████░  9 tests (45%)
  Edge Case Tests      ████████░░░░░░░  4 tests (20%)
  Security Tests       ██████░░░░░░░░░  3 tests (15%)
  Integration Tests    ████░░░░░░░░░░░  2 tests (10%)
  Performance Tests    ████░░░░░░░░░░░  2 tests (10%)

━━━ Priority Matrix ━━━
  P0: Successful checkout, payment processing, order creation
  P1: Discount codes, error handling, email confirmation
  P2: Edge cases, concurrent checkout, inventory sync
  P3: Performance, 3DS flow, multi-currency

━━━ Recommended Approach ━━━
  • Mock Stripe API with test mode keys
  • Use Stripe test tokens: pm_card_visa, pm_card_declined
  • Seed database with test products and inventory
  • Run in isolated test environment with clean state

━━━ Estimated Execution Time: 65 seconds (parallel) ━━━`,
    },
    {
      agentId: "writer",
      content: `✍ TEST CASES GENERATED — PROJ-1043: Shopping Cart Checkout

Generated 8 comprehensive BDD test cases covering all critical flows.`,
      testCases: [
        {
          id: "TC-001",
          name: "Successful Checkout with Visa",
          type: "functional",
          priority: "P0",
          scenario:
            "Given items in cart totaling $149.99\nWhen user completes checkout with valid Visa card\nThen order is created and confirmation page shown",
          steps: [
            "Add items to cart",
            "Proceed to checkout",
            "Enter shipping address",
            "Select standard shipping",
            "Enter Visa test card (4242...)",
            "Click 'Place Order'",
            "Verify order confirmation page",
          ],
          expected: "Order created, confirmation shown, email sent",
          status: "pending",
        },
        {
          id: "TC-002",
          name: "Apply Valid Discount Code",
          type: "functional",
          priority: "P1",
          scenario:
            "Given cart with $100 total\nWhen user applies 20% discount code 'SAVE20'\nThen total reduces to $80",
          steps: [
            "Add $100 in items",
            "Apply code 'SAVE20'",
            "Verify discount line item",
            "Verify new total $80",
          ],
          expected: "20% discount applied, total recalculated",
          status: "pending",
        },
        {
          id: "TC-003",
          name: "Invalid Discount Code Error",
          type: "functional",
          priority: "P1",
          scenario:
            "Given checkout page\nWhen user enters invalid code 'FAKECODE'\nThen error shown and cart preserved",
          steps: [
            "Enter invalid code",
            "Verify error message",
            "Verify cart items unchanged",
            "Verify total unchanged",
          ],
          expected: "Error message, cart state preserved",
          status: "pending",
        },
        {
          id: "TC-004",
          name: "Declined Card Handling",
          type: "functional",
          priority: "P0",
          scenario:
            "Given valid cart\nWhen payment is declined by Stripe\nThen user sees retry option with cart intact",
          steps: [
            "Use test card pm_card_declined",
            "Verify decline error shown",
            "Verify retry button visible",
            "Retry with valid card",
          ],
          expected: "Graceful decline handling, retry available",
          status: "pending",
        },
        {
          id: "TC-005",
          name: "Out of Stock During Checkout",
          type: "edge",
          priority: "P1",
          scenario:
            "Given item in cart with 1 unit remaining\nWhen another user purchases last unit during checkout\nThen current user is notified before payment",
          steps: [
            "Add last-stock item to cart",
            "Simulate concurrent purchase",
            "Attempt to complete checkout",
            "Verify stock warning shown",
          ],
          expected: "User notified before charging card",
          status: "pending",
        },
        {
          id: "TC-006",
          name: "Price Tampering Prevention",
          type: "security",
          priority: "P0",
          scenario:
            "Given manipulated client-side price\nWhen checkout API is called with tampered amount\nThen server rejects and recalculates",
          steps: [
            "Intercept checkout API call",
            "Modify price to $0.01",
            "Submit payment",
            "Verify server rejects tampering",
          ],
          expected: "Server-side validation catches price mismatch",
          status: "pending",
        },
        {
          id: "TC-007",
          name: "Email Confirmation Within 60s",
          type: "functional",
          priority: "P1",
          scenario:
            "Given successful order\nWhen order is confirmed\nThen confirmation email arrives within 60 seconds",
          steps: [
            "Complete checkout successfully",
            "Check email inbox (test mailbox)",
            "Verify email within 60s",
            "Verify tracking link in email",
          ],
          expected: "Email with order details + tracking link",
          status: "pending",
        },
        {
          id: "TC-008",
          name: "Network Failure Mid-Payment",
          type: "edge",
          priority: "P1",
          scenario:
            "Given payment intent created\nWhen network drops during confirmation\nThen payment is handled idempotently",
          steps: [
            "Start payment",
            "Simulate network failure after intent",
            "Refresh page",
            "Verify no double charge",
            "Verify recovery flow",
          ],
          expected: "No duplicate charges, recovery possible",
          status: "pending",
        },
      ],
    },
    {
      agentId: "automation",
      content: `⟨/⟩ AUTOMATION CODE GENERATED — Playwright (TypeScript)`,
      automationCode: `import { test, expect } from '@playwright/test';

test.describe('Shopping Cart Checkout', () => {

  test.beforeEach(async ({ page }) => {
    // Seed cart with test items
    await page.goto('/test/seed-cart?items=2&total=14999');
  });

  test('TC-001: Successful Checkout with Visa', async ({ page }) => {
    await page.goto('/checkout');
    
    // Fill shipping
    await page.fill('[name="address"]', '123 Test St');
    await page.fill('[name="city"]', 'San Francisco');
    await page.selectOption('[name="state"]', 'CA');
    
    // Stripe test card
    const stripe = page.frameLocator('[name="__privateStripeFrame"]');
    await stripe.locator('[name="cardnumber"]')
      .fill('4242424242424242');
    await stripe.locator('[name="exp-date"]').fill('12/28');
    await stripe.locator('[name="cvc"]').fill('123');
    
    await page.click('[data-testid="place-order"]');
    
    await expect(page.locator('[data-testid="order-confirmation"]'))
      .toBeVisible({ timeout: 5000 });
    await expect(page.locator('[data-testid="order-id"]'))
      .toHaveText(/^ORD-/);
  });

  test('TC-004: Declined Card', async ({ page }) => {
    await page.goto('/checkout');
    // Use Stripe declining test card
    // ...payment flow with pm_card_declined
    await expect(page.locator('[data-testid="payment-error"]'))
      .toContainText('declined');
    await expect(page.locator('[data-testid="retry-btn"]'))
      .toBeEnabled();
  });
});`,
    },
    {
      agentId: "executor",
      content: ``,
      executionResults: [
        { id: "TC-001", status: "pass", duration: "2.34s" },
        { id: "TC-002", status: "pass", duration: "1.12s" },
        { id: "TC-003", status: "pass", duration: "0.78s" },
        { id: "TC-004", status: "pass", duration: "1.89s" },
        {
          id: "TC-005",
          status: "fail",
          duration: "3.21s",
          error:
            "Checkout proceeded despite 0 inventory — race condition in stock check",
        },
        { id: "TC-006", status: "pass", duration: "0.67s" },
        { id: "TC-007", status: "pass", duration: "1.45s" },
        {
          id: "TC-008",
          status: "fail",
          duration: "4.56s",
          error: "Double charge detected — payment intent not idempotent",
        },
      ],
    },
    {
      agentId: "bug",
      content: `🐛 BUG REPORT — 2 Failures Detected

━━━ BUG-001: Race Condition in Inventory Check ━━━
  Severity:  🔴 CRITICAL (Financial)
  Test:      TC-005 — Out of Stock During Checkout
  Expected:  Checkout blocked when item goes out of stock
  Actual:    Order completes, overselling occurs
  Root Cause: Inventory check uses SELECT without row lock
  
  Fix: Use SELECT FOR UPDATE or optimistic locking:
    UPDATE products SET stock = stock - 1
    WHERE id = $1 AND stock > 0
    RETURNING stock;

━━━ BUG-002: Double Charge on Network Failure ━━━
  Severity:  🔴 CRITICAL (Financial)
  Test:      TC-008 — Network Failure Mid-Payment
  Expected:  Idempotent payment processing
  Actual:    Retry creates second PaymentIntent
  Root Cause: Missing Stripe idempotency key
  
  Fix: Add idempotency_key to payment creation:
    stripe.paymentIntents.create({
      amount: total,
      idempotency_key: cart.checkoutSessionId
    });

━━━ VERDICT: 🔴 BLOCK RELEASE ━━━
Both bugs involve financial risk. Fix immediately.`,
    },
    {
      agentId: "coverage",
      content: `◎ COVERAGE ANALYSIS — PROJ-1043: Shopping Cart Checkout

━━━ Test Results Summary ━━━
  Total Tests:    8
  Passed:         6  ████████████░░  75%
  Failed:         2  ████░░░░░░░░░░  25%
  Execution Time: 16.0s (parallel: 6.3s)

━━━ VERDICT: 🔴 NO-GO ━━━
Critical financial bugs must be fixed before release.
Estimated fix effort: 3-4 hours.`,
    },
  ],

  "PROJ-1044": [
    {
      agentId: "story",
      content: `📋 REQUIREMENT ANALYSIS — PROJ-1044: Notifications System

━━━ Core Requirements (4) ━━━
  ✓ R1: WebSocket real-time delivery < 500ms
  ✓ R2: Badge count sync across browser tabs
  ✓ R3: Mark all as read functionality
  ✓ R4: Per-category notification preferences

━━━ Edge Cases (4) ━━━
  ⚡ E1: WebSocket disconnect/reconnect handling
  ⚡ E2: 1000+ unread notifications performance
  ⚡ E3: Notification received while tab is inactive
  ⚡ E4: Preference change doesn't affect already-sent notifications

━━━ Risk Assessment: MEDIUM ━━━`,
    },
    {
      agentId: "strategy",
      content: `📐 TEST STRATEGY — PROJ-1044: Notifications

━━━ Test Distribution ━━━
  Functional:  5 tests (50%)
  Performance: 2 tests (20%)
  Edge:        2 tests (20%)
  Integration: 1 test  (10%)

━━━ Estimated Execution Time: 30 seconds ━━━`,
    },
    {
      agentId: "writer",
      content: `✍ TEST CASES GENERATED — PROJ-1044: Notifications

Generated 6 test cases.`,
      testCases: [
        {
          id: "TC-001",
          name: "Real-time Notification Delivery",
          type: "functional",
          priority: "P0",
          scenario:
            "Given connected WebSocket\nWhen event triggers notification\nThen notification appears within 500ms",
          steps: [
            "Open app with WebSocket connected",
            "Trigger notification event",
            "Measure delivery time",
            "Verify < 500ms",
          ],
          expected: "Notification visible within 500ms",
          status: "pending",
        },
        {
          id: "TC-002",
          name: "Badge Count Updates Across Tabs",
          type: "functional",
          priority: "P0",
          scenario:
            "Given app open in 2 tabs\nWhen notification arrives\nThen badge updates in both tabs",
          steps: [
            "Open app in tab 1 and tab 2",
            "Send notification",
            "Verify badge in both tabs",
          ],
          expected: "Both tabs show updated badge",
          status: "pending",
        },
        {
          id: "TC-003",
          name: "Mark All As Read",
          type: "functional",
          priority: "P1",
          scenario:
            "Given 5 unread notifications\nWhen user clicks mark all read\nThen badge count becomes 0",
          steps: [
            "Accumulate 5 notifications",
            "Click mark all as read",
            "Verify badge is 0",
            "Verify all items marked read",
          ],
          expected: "All notifications marked read, badge cleared",
          status: "pending",
        },
        {
          id: "TC-004",
          name: "Preference Filtering",
          type: "functional",
          priority: "P1",
          scenario:
            "Given mentions disabled in preferences\nWhen mention event occurs\nThen no notification is delivered",
          steps: [
            "Disable mention notifications",
            "Trigger mention event",
            "Verify no notification appears",
          ],
          expected: "Notification suppressed per preferences",
          status: "pending",
        },
        {
          id: "TC-005",
          name: "WebSocket Reconnection",
          type: "edge",
          priority: "P1",
          scenario:
            "Given active WebSocket connection\nWhen connection drops\nThen client reconnects and fetches missed notifications",
          steps: [
            "Establish WS connection",
            "Simulate disconnect",
            "Send notification during disconnect",
            "Verify auto-reconnect",
            "Verify missed notification delivered",
          ],
          expected: "Auto-reconnect + catch-up on missed messages",
          status: "pending",
        },
        {
          id: "TC-006",
          name: "1000 Notifications Performance",
          type: "performance",
          priority: "P2",
          scenario:
            "Given 1000 unread notifications\nWhen user opens notification panel\nThen panel renders within 200ms",
          steps: [
            "Seed 1000 notifications",
            "Open notification panel",
            "Measure render time",
          ],
          expected: "Panel renders < 200ms with virtual scroll",
          status: "pending",
        },
      ],
    },
    {
      agentId: "automation",
      content: `⟨/⟩ AUTOMATION CODE GENERATED — Playwright (TypeScript)`,
      automationCode: `import { test, expect } from '@playwright/test';

test.describe('Notifications System', () => {
  test('TC-001: Real-time Delivery < 500ms', async ({ page }) => {
    await page.goto('/app');
    const start = Date.now();
    
    // Trigger notification via API
    await page.evaluate(() =>
      fetch('/api/test/trigger-notification', { method: 'POST' })
    );
    
    await expect(page.locator('[data-testid="notification-toast"]'))
      .toBeVisible({ timeout: 500 });
    
    expect(Date.now() - start).toBeLessThan(500);
  });
});`,
    },
    {
      agentId: "executor",
      content: ``,
      executionResults: [
        { id: "TC-001", status: "pass", duration: "0.42s" },
        { id: "TC-002", status: "pass", duration: "1.23s" },
        { id: "TC-003", status: "pass", duration: "0.56s" },
        { id: "TC-004", status: "pass", duration: "0.89s" },
        { id: "TC-005", status: "pass", duration: "2.34s" },
        { id: "TC-006", status: "pass", duration: "0.18s" },
      ],
    },
    {
      agentId: "bug",
      content: `🐛 BUG REPORT — 0 Failures

━━━ All 6 tests passed ━━━

No bugs found in this test run. Notification system is working as expected.

Note: Consider adding tests for:
  • Multi-user notification isolation
  • Notification expiry/TTL
  • Rate limiting for notification flood prevention`,
    },
    {
      agentId: "coverage",
      content: `◎ COVERAGE ANALYSIS — PROJ-1044: Notifications

━━━ Test Results Summary ━━━
  Total Tests:    6
  Passed:         6  ████████████████  100%
  Failed:         0  ░░░░░░░░░░░░░░░░    0%
  Execution Time: 5.6s (parallel: 2.8s)

━━━ VERDICT: ✅ GO ━━━
All tests passing. Ship it! 🚀`,
    },
  ],
};

// ─── Pipeline Console Logs ───────────────────────────────────

export function generateLogs(storyId: string): LogEntry[][] {
  const now = new Date();
  const fmt = (offset: number) => {
    const d = new Date(now.getTime() + offset);
    return (
      d.toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }) +
      "." +
      String(d.getMilliseconds()).padStart(3, "0")
    );
  };

  return [
    // Story Analyzer logs
    [
      {
        time: fmt(0),
        agentId: "story",
        message: `Parsing JIRA story ${storyId}...`,
        type: "info",
      },
      {
        time: fmt(400),
        agentId: "story",
        message: "Extracting acceptance criteria...",
        type: "info",
      },
      {
        time: fmt(900),
        agentId: "story",
        message: "Running NLU requirement extraction...",
        type: "info",
      },
      {
        time: fmt(1400),
        agentId: "story",
        message: "Identifying edge cases and risk areas...",
        type: "info",
      },
      {
        time: fmt(1900),
        agentId: "story",
        message: "Security threat modeling complete",
        type: "info",
      },
      {
        time: fmt(2200),
        agentId: "story",
        message: "✓ Analysis complete — 5 requirements, 6 edge cases, 4 risks",
        type: "success",
      },
    ],
    // Test Strategist logs
    [
      {
        time: fmt(2400),
        agentId: "strategy",
        message: "Ingesting requirement analysis...",
        type: "info",
      },
      {
        time: fmt(2800),
        agentId: "strategy",
        message: "Calculating risk-based test distribution...",
        type: "info",
      },
      {
        time: fmt(3200),
        agentId: "strategy",
        message: "Building priority matrix...",
        type: "info",
      },
      {
        time: fmt(3700),
        agentId: "strategy",
        message: "✓ Strategy complete — 20 tests across 5 categories",
        type: "success",
      },
    ],
    // Test Case Writer logs
    [
      {
        time: fmt(3900),
        agentId: "writer",
        message: "Generating BDD scenarios...",
        type: "info",
      },
      {
        time: fmt(4300),
        agentId: "writer",
        message: "Writing Given/When/Then for functional tests...",
        type: "info",
      },
      {
        time: fmt(4800),
        agentId: "writer",
        message: "Generating security test scenarios...",
        type: "info",
      },
      {
        time: fmt(5400),
        agentId: "writer",
        message: "Adding edge case coverage...",
        type: "info",
      },
      {
        time: fmt(6000),
        agentId: "writer",
        message: "Validating test independence (no shared state)...",
        type: "info",
      },
      {
        time: fmt(6500),
        agentId: "writer",
        message: "✓ Generated 8 test cases with full BDD scenarios",
        type: "success",
      },
    ],
    // Automation Engineer logs
    [
      {
        time: fmt(6700),
        agentId: "automation",
        message: "Initializing Playwright code generator...",
        type: "info",
      },
      {
        time: fmt(7100),
        agentId: "automation",
        message: "Generating test fixtures and helpers...",
        type: "info",
      },
      {
        time: fmt(7600),
        agentId: "automation",
        message: "Writing test functions with assertions...",
        type: "info",
      },
      {
        time: fmt(8200),
        agentId: "automation",
        message: "Adding API mocking (route.fulfill)...",
        type: "info",
      },
      {
        time: fmt(8800),
        agentId: "automation",
        message: "✓ Playwright test file generated (4 test functions)",
        type: "success",
      },
    ],
    // Test Executor logs
    [
      {
        time: fmt(9000),
        agentId: "executor",
        message: "Launching Chromium browser context...",
        type: "info",
      },
      {
        time: fmt(9300),
        agentId: "executor",
        message: "Configuring 4 parallel workers...",
        type: "info",
      },
      {
        time: fmt(9600),
        agentId: "executor",
        message: "Executing test suite...",
        type: "info",
      },
      {
        time: fmt(10500),
        agentId: "executor",
        message: "TC-001: ✓ PASS (1.23s)",
        type: "success",
      },
      {
        time: fmt(11000),
        agentId: "executor",
        message: "TC-002: ✓ PASS (1.18s)",
        type: "success",
      },
      {
        time: fmt(11400),
        agentId: "executor",
        message: "TC-003: ✓ PASS (0.89s)",
        type: "success",
      },
      {
        time: fmt(11900),
        agentId: "executor",
        message: "TC-004: ✓ PASS (1.45s)",
        type: "success",
      },
      {
        time: fmt(12400),
        agentId: "executor",
        message: "TC-005: ✗ FAIL (0.67s) — Replay protection not implemented",
        type: "error",
      },
      {
        time: fmt(12800),
        agentId: "executor",
        message: "TC-006: ✓ PASS (0.54s)",
        type: "success",
      },
      {
        time: fmt(13200),
        agentId: "executor",
        message: "TC-007: ✗ FAIL (2.12s) — Missing email fallback UI",
        type: "error",
      },
      {
        time: fmt(13500),
        agentId: "executor",
        message: "TC-008: ✓ PASS (0.92s)",
        type: "success",
      },
      {
        time: fmt(13800),
        agentId: "executor",
        message: "✓ Suite complete — 6/8 passed",
        type: "success",
      },
    ],
    // Bug Detective logs
    [
      {
        time: fmt(14000),
        agentId: "bug",
        message: "Analyzing 2 test failures...",
        type: "info",
      },
      {
        time: fmt(14400),
        agentId: "bug",
        message: "Correlating failure with source code...",
        type: "info",
      },
      {
        time: fmt(14800),
        agentId: "bug",
        message: "Root cause identified: missing nonce tracking",
        type: "warning",
      },
      {
        time: fmt(15200),
        agentId: "bug",
        message: "Root cause identified: null email handling",
        type: "warning",
      },
      {
        time: fmt(15600),
        agentId: "bug",
        message: "✓ 2 bug reports generated with fix recommendations",
        type: "success",
      },
    ],
    // Coverage Analyst logs
    [
      {
        time: fmt(15800),
        agentId: "coverage",
        message: "Calculating coverage matrix...",
        type: "info",
      },
      {
        time: fmt(16200),
        agentId: "coverage",
        message: "Mapping test results to requirements...",
        type: "info",
      },
      {
        time: fmt(16600),
        agentId: "coverage",
        message: "Identifying coverage gaps...",
        type: "info",
      },
      {
        time: fmt(17000),
        agentId: "coverage",
        message: "✓ Coverage report complete — CONDITIONAL GO",
        type: "success",
      },
    ],
  ];
}

// ─── Dashboard Stats ─────────────────────────────────────────

export const DASHBOARD_STATS = {
  totalTestsGenerated: 1247,
  totalTestsExecuted: 1183,
  bugsFound: 34,
  avgPassRate: 89,
  storiesAnalyzed: 156,
  timeSavedHours: 312,
  topIssues: [
    { type: "Security", count: 12, trend: "up" },
    { type: "Edge Case", count: 9, trend: "down" },
    { type: "Performance", count: 7, trend: "stable" },
    { type: "Functional", count: 6, trend: "down" },
  ],
  recentRuns: [
    {
      storyId: "PROJ-1042",
      title: "OAuth2 Auth",
      pass: 6,
      fail: 2,
      time: "4.2s",
      date: "2 min ago",
    },
    {
      storyId: "PROJ-1040",
      title: "User Profile API",
      pass: 12,
      fail: 0,
      time: "8.1s",
      date: "1 hour ago",
    },
    {
      storyId: "PROJ-1038",
      title: "File Upload",
      pass: 8,
      fail: 1,
      time: "12.3s",
      date: "3 hours ago",
    },
    {
      storyId: "PROJ-1035",
      title: "Search Filters",
      pass: 15,
      fail: 3,
      time: "6.7s",
      date: "Yesterday",
    },
    {
      storyId: "PROJ-1033",
      title: "Dashboard Charts",
      pass: 5,
      fail: 0,
      time: "3.2s",
      date: "Yesterday",
    },
  ],
  weeklyTrend: [
    { day: "Mon", tests: 145, pass: 128, fail: 17 },
    { day: "Tue", tests: 198, pass: 182, fail: 16 },
    { day: "Wed", tests: 167, pass: 149, fail: 18 },
    { day: "Thu", tests: 234, pass: 218, fail: 16 },
    { day: "Fri", tests: 189, pass: 171, fail: 18 },
    { day: "Sat", tests: 45, pass: 43, fail: 2 },
    { day: "Sun", tests: 22, pass: 22, fail: 0 },
  ],
};
