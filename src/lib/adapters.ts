// ═══════════════════════════════════════════════════════════════
// Framework Adapter System — Plug-and-Play Test Frameworks
// Each adapter defines identity, capabilities, and sample output.
// Add a new framework by implementing the FrameworkAdapter interface.
// ═══════════════════════════════════════════════════════════════

export type FrameworkCapability =
  | "e2e"
  | "component"
  | "api"
  | "visual"
  | "accessibility"
  | "performance"
  | "mobile"
  | "cross-browser"
  | "parallel"
  | "headless";

export type BrowserType = "chromium" | "firefox" | "webkit" | "edge";

export interface FrameworkAdapter {
  id: string;
  name: string;
  shortName: string;
  color: string;
  language: string;
  description: string;
  capabilities: FrameworkCapability[];
  browserSupport: BrowserType[];
  status: "active" | "available" | "coming-soon";
  sampleCode: string;
  docs: string;
}

export interface EnvironmentPreset {
  id: string;
  label: string;
  browser: BrowserType;
  viewport: { width: number; height: number };
  platform: string;
  enabled: boolean;
}

// ─── Framework Registry ──────────────────────────────────────

export const FRAMEWORKS: FrameworkAdapter[] = [
  {
    id: "playwright",
    name: "Playwright",
    shortName: "PW",
    color: "#2EAD33",
    language: "TypeScript",
    description:
      "Modern end-to-end testing with auto-wait, multi-browser support, and native mobile emulation.",
    capabilities: [
      "e2e",
      "component",
      "api",
      "visual",
      "mobile",
      "cross-browser",
      "parallel",
      "headless",
    ],
    browserSupport: ["chromium", "firefox", "webkit"],
    status: "active",
    docs: "https://playwright.dev",
    sampleCode: `import { test, expect } from '@playwright/test';

test('user login with OAuth2', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();
  await page.waitForURL('/dashboard');
  await expect(page.getByText('Welcome')).toBeVisible();
  expect(await page.locator('.session-cookie').count()).toBeGreaterThan(0);
});`,
  },
  {
    id: "selenium",
    name: "Selenium WebDriver",
    shortName: "Se",
    color: "#43B02A",
    language: "Python",
    description:
      "Industry-standard browser automation with the largest ecosystem and enterprise support.",
    capabilities: ["e2e", "cross-browser", "parallel", "headless"],
    browserSupport: ["chromium", "firefox", "webkit", "edge"],
    status: "active",
    docs: "https://selenium.dev",
    sampleCode: `from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_user_login_oauth2(driver):
    driver.get("http://localhost:3000/login")
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign in with Google']"))
    )
    btn.click()
    WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
    assert "Welcome" in driver.page_source`,
  },
  {
    id: "cypress",
    name: "Cypress",
    shortName: "Cy",
    color: "#69D3A7",
    language: "TypeScript",
    description:
      "Developer-friendly testing with real-time reloads, time-travel debugging, and automatic waiting.",
    capabilities: ["e2e", "component", "api", "visual", "headless"],
    browserSupport: ["chromium", "firefox", "edge"],
    status: "active",
    docs: "https://cypress.io",
    sampleCode: `describe('OAuth2 Authentication', () => {
  it('should login with Google OAuth', () => {
    cy.visit('/login');
    cy.contains('Sign in with Google').click();
    cy.url().should('include', '/dashboard');
    cy.get('.welcome-message').should('be.visible');
    cy.getCookie('session').should('exist');
  });
});`,
  },
  {
    id: "appium",
    name: "Appium",
    shortName: "Ap",
    color: "#662D91",
    language: "Python",
    description:
      "Cross-platform mobile testing for native, hybrid, and mobile web apps on iOS and Android.",
    capabilities: ["e2e", "mobile", "cross-browser", "parallel"],
    browserSupport: ["chromium", "webkit"],
    status: "available",
    docs: "https://appium.io",
    sampleCode: `from appium.webdriver.common.mobileby import MobileBy

def test_mobile_oauth_login(driver):
    login_btn = driver.find_element(
        MobileBy.ACCESSIBILITY_ID, "Sign in with Google"
    )
    login_btn.click()
    welcome = driver.find_element(MobileBy.ACCESSIBILITY_ID, "welcome-text")
    assert welcome.text == "Welcome back"`,
  },
  {
    id: "k6",
    name: "k6 (Grafana)",
    shortName: "k6",
    color: "#7D64FF",
    language: "JavaScript",
    description:
      "Performance and load testing with developer-friendly scripting and real-time metrics.",
    capabilities: ["performance", "api", "headless"],
    browserSupport: [],
    status: "available",
    docs: "https://k6.io",
    sampleCode: `import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = { vus: 50, duration: '30s' };

export default function () {
  const res = http.post('http://localhost:3000/api/auth/login', {
    email: 'test@example.com', password: 'test123'
  });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}`,
  },
  {
    id: "axe",
    name: "axe-core",
    shortName: "A11y",
    color: "#FF4D6A",
    language: "TypeScript",
    description:
      "Automated accessibility testing based on WCAG guidelines with detailed violation reports.",
    capabilities: ["accessibility", "headless"],
    browserSupport: ["chromium", "firefox", "webkit"],
    status: "available",
    docs: "https://deque.com/axe",
    sampleCode: `import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('login page meets WCAG 2.1 AA', async ({ page }) => {
  await page.goto('/login');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});`,
  },
];

// ─── Environment Presets ─────────────────────────────────────

export const ENVIRONMENT_PRESETS: EnvironmentPreset[] = [
  {
    id: "desktop-chrome",
    label: "Desktop Chrome",
    browser: "chromium",
    viewport: { width: 1920, height: 1080 },
    platform: "Linux",
    enabled: true,
  },
  {
    id: "desktop-firefox",
    label: "Desktop Firefox",
    browser: "firefox",
    viewport: { width: 1920, height: 1080 },
    platform: "Linux",
    enabled: true,
  },
  {
    id: "desktop-safari",
    label: "Desktop Safari",
    browser: "webkit",
    viewport: { width: 1920, height: 1080 },
    platform: "macOS",
    enabled: false,
  },
  {
    id: "desktop-edge",
    label: "Desktop Edge",
    browser: "edge",
    viewport: { width: 1920, height: 1080 },
    platform: "Windows",
    enabled: false,
  },
  {
    id: "tablet-ipad",
    label: "iPad Pro",
    browser: "webkit",
    viewport: { width: 1024, height: 1366 },
    platform: "iOS",
    enabled: true,
  },
  {
    id: "mobile-iphone",
    label: "iPhone 15 Pro",
    browser: "webkit",
    viewport: { width: 393, height: 852 },
    platform: "iOS",
    enabled: false,
  },
  {
    id: "mobile-pixel",
    label: "Pixel 8",
    browser: "chromium",
    viewport: { width: 412, height: 915 },
    platform: "Android",
    enabled: false,
  },
];

// ─── Default Config ──────────────────────────────────────────

export const DEFAULT_ADAPTER_CONFIG = {
  parallelWorkers: 4,
  timeout: 30000,
  retries: 2,
  headless: true,
  screenshotsOnFailure: true,
  videoOnFailure: false,
  baseUrl: "http://localhost:3000",
};

// ─── Helpers ─────────────────────────────────────────────────

export function getAdapter(id: string): FrameworkAdapter | undefined {
  return FRAMEWORKS.find((f) => f.id === id);
}

export function getActiveAdapters(): FrameworkAdapter[] {
  return FRAMEWORKS.filter((f) => f.status === "active");
}

export function getCapabilityLabel(cap: FrameworkCapability): string {
  const labels: Record<FrameworkCapability, string> = {
    e2e: "End-to-End",
    component: "Component",
    api: "API Testing",
    visual: "Visual Regression",
    accessibility: "Accessibility",
    performance: "Performance",
    mobile: "Mobile",
    "cross-browser": "Cross-Browser",
    parallel: "Parallel Execution",
    headless: "Headless Mode",
  };
  return labels[cap];
}
