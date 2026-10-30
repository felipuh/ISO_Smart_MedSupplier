import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const ADMIN_EMAIL = process.env.TEST_EMAIL || 'admin@isosmart.local';
const ORIGINAL_PASSWORD = process.env.TEST_PASSWORD || 'Admin@123456';
const NEW_PASSWORD = 'RecoveryFlow@123';
const BACKEND_URL = 'http://127.0.0.1:8002';
const PYTHON_BIN = process.env.PYTHON_BIN || '/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python';
const REPO_ROOT = path.resolve(process.cwd(), '..');

async function loginByApi(request, email, password) {
  const response = await request.post(`${BACKEND_URL}/api/auth/login/`, {
    data: {
      email,
      password,
    },
  });

  expect(response.status(), 'login API should succeed').toBe(200);
  return response.json();
}

async function createRecoveryUser(request) {
  const adminLogin = await loginByApi(request, ADMIN_EMAIL, ORIGINAL_PASSWORD);
  const recoveryEmail = `recovery.e2e.${Date.now()}@isosmart.local`;

  const createResponse = await request.post(`${BACKEND_URL}/api/auth/users/`, {
    data: {
      email: recoveryEmail,
      first_name: 'Recovery',
      last_name: 'E2E',
      phone: '0000000000',
      password: ORIGINAL_PASSWORD,
      confirm_password: ORIGINAL_PASSWORD,
      organization_id: adminLogin.profile.organization,
      role: 'user',
    },
    headers: {
      Authorization: `Bearer ${adminLogin.access}`,
    },
  });

  expect(createResponse.status(), 'recovery test user should be created').toBe(201);
  return recoveryEmail;
}

function issueResetPath(email) {
  const script = `
from authentication.models import PasswordResetToken, User
user = User.objects.get(email='${email}')
reset_token, raw_token = PasswordResetToken.issue_for_user(user)
print(f'/reset-password?selector={reset_token.selector}&token={raw_token}')
`;
  return execFileSync(
    PYTHON_BIN,
    ['backend/manage.py', 'shell', '-c', script],
    { cwd: REPO_ROOT, encoding: 'utf8', env: process.env }
  ).trim().split('\\n').pop();
}

test('password recovery flow works end-to-end', async ({ page, request }) => {
  const recoveryEmail = await createRecoveryUser(request);

  await page.route('**/api/auth/password-reset/request/', async (route) => {
    const postData = route.request().postDataJSON();
    const response = await request.post(`${BACKEND_URL}/api/auth/password-reset/request/`, {
      data: postData,
    });
    await route.fulfill({
      status: response.status(),
      contentType: 'application/json',
      body: await response.text(),
    });
  });

  await page.route('**/api/auth/password-reset/confirm/', async (route) => {
    const postData = route.request().postDataJSON();
    const response = await request.post(`${BACKEND_URL}/api/auth/password-reset/confirm/`, {
      data: postData,
    });
    await route.fulfill({
      status: response.status(),
      contentType: 'application/json',
      body: await response.text(),
    });
  });

  await page.goto('/forgot-password');
  await expect(page.locator('input#email')).toBeVisible();

  const requestPromise = page.waitForResponse(
    (response) => response.url().includes('/api/auth/password-reset/request/') && response.request().method() === 'POST',
    { timeout: 45000 }
  );

  await page.locator('input#email').fill(recoveryEmail);
  await page.locator('button[type="submit"]').click();
  const formResponse = await requestPromise;
  expect(formResponse.status(), 'password reset form request should succeed').toBe(200);

  const resetPath = issueResetPath(recoveryEmail);
  await page.goto(resetPath);

  await page.locator('input#new-password').fill(NEW_PASSWORD);
  await page.locator('input#confirm-password').fill(NEW_PASSWORD);
  const confirmPromise = page.waitForResponse(
    (response) => response.url().includes('/api/auth/password-reset/confirm/') && response.request().method() === 'POST',
    { timeout: 45000 }
  );
  await page.locator('button[type="submit"]').click();
  const confirmResponse = await confirmPromise;
  expect(confirmResponse.status(), 'password reset confirmation should succeed').toBe(200);
  await page.waitForURL('**/login', { timeout: 45000 });

  await loginByApi(request, recoveryEmail, NEW_PASSWORD);
});
