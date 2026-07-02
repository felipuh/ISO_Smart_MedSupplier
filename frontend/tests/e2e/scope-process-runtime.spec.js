import { expect, test } from '@playwright/test';

const EMAIL = process.env.TEST_EMAIL || 'admin@isosmart.local';
const PASSWORD = process.env.TEST_PASSWORD || 'Admin@123456';

async function login(page) {
  await page.goto('/login');
  await page.locator('input#email, input[type="email"]').first().fill(EMAIL);
  await page.locator('input#password, input[type="password"]').first().fill(PASSWORD);

  const loginResponsePromise = page.waitForResponse(
    (response) =>
      response.url().includes('/api/auth/login/') && response.request().method() === 'POST',
    { timeout: 45000 }
  );

  await page.locator('button[type="submit"]').first().click();

  const loginResponse = await loginResponsePromise;
  expect(loginResponse.status(), 'login should succeed').toBe(200);

  await page.waitForURL((url) => !url.pathname.endsWith('/login'), {
    timeout: 45000,
  });
}

test('legacy scope/process routes resolve safely and MedSupplier endpoints keep tenant protections', async ({ page }) => {
  await login(page);

  const token = await page.evaluate(() => localStorage.getItem('access_token'));
  expect(token, 'access token should be present after login').toBeTruthy();

  await page.goto('/scope');
  await expect(page).toHaveURL(/\/medsupplier/);
  await expect(page.getByRole('heading', { name: /ISO Smart MedSupplier/i }).first()).toBeVisible();

  await page.goto('/processes');
  await expect(page).toHaveURL(/\/medsupplier/);
  await expect(page.getByRole('heading', { name: /ISO Smart MedSupplier/i }).first()).toBeVisible();

  const forbiddenAccounts = await page.request.get('/api/medsupplier/accounts/?organization_id=999999', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  expect(forbiddenAccounts.status(), 'MedSupplier account endpoint should enforce tenant isolation').toBe(403);

  const forbiddenQuotes = await page.request.get('/api/medsupplier/quotes/?organization_id=999999', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  expect(forbiddenQuotes.status(), 'MedSupplier quotes endpoint should enforce tenant isolation').toBe(403);
});
