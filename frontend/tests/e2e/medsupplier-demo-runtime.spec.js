import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const PYTHON_BIN = process.env.PYTHON_BIN || '/home/felipe/proyectos/isosmart/backend/.venv312/bin/python';
const REPO_ROOT = path.resolve(process.cwd(), '..');
const DEMO_EMAIL = 'medsupplier.e2e@smart3ai.local';
const DEMO_PASSWORD = 'MedSupplierDemo@123';
const DEMO_ORG_SLUG = 'medsupplier-demo-e2e';
const ROLE_USERS = {
  supplierFinance: DEMO_EMAIL,
  supplierQuality: 'medsupplier.supplier.quality@smart3ai.local',
  supplierLogistics: 'medsupplier.supplier.logistics@smart3ai.local',
  supplierViewer: 'medsupplier.supplier.viewer@smart3ai.local',
  customerBuyer: 'medsupplier.customer.buyer@smart3ai.local',
  customerQuality: 'medsupplier.customer.quality@smart3ai.local',
  customerAuditor: 'medsupplier.customer.auditor@smart3ai.local',
  customerViewer: 'medsupplier.customer.viewer@smart3ai.local',
};

const loginAs = async (page, email) => {
  await page.goto('/login');
  await page.evaluate(() => window.localStorage.clear());
  await page.locator('#email').fill(email);
  await page.locator('#password').fill(DEMO_PASSWORD);
  await page.locator('button[type="submit"]').click();
  await page.waitForFunction(() => Boolean(window.localStorage.getItem('access_token')));
  await expect(page).not.toHaveURL(/\/login$/);
  await expect(page.getByText('Error al iniciar sesión. Verifica tus credenciales.')).toBeHidden();
};

const activeOrganizationId = async (page) => {
  const accessToken = await page.evaluate(() => window.localStorage.getItem('access_token'));
  expect(accessToken).toBeTruthy();
  const payload = JSON.parse(Buffer.from(accessToken.split('.')[1], 'base64url').toString('utf8'));
  expect(payload.organization_id).toBeTruthy();
  return payload.organization_id;
};

const apiGet = async (page, path) => {
  const token = await page.evaluate(() => window.localStorage.getItem('access_token'));
  return page.request.get(`/api${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

const apiPost = async (page, path, payload) => {
  const token = await page.evaluate(() => window.localStorage.getItem('access_token'));
  return page.request.post(`/api${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    data: payload,
  });
};

test.beforeAll(() => {
  execFileSync(
    PYTHON_BIN,
    [
      'backend/manage.py',
      'seed_medsupplier_demo',
      '--organization-slug',
      DEMO_ORG_SLUG,
      '--user-email',
      DEMO_EMAIL,
      '--user-password',
      DEMO_PASSWORD,
    ],
    {
      cwd: REPO_ROOT,
      stdio: 'inherit',
      env: process.env,
    }
  );
});

test('MedSupplier demo workspace supports data entry and explains blocked actions', async ({ page }) => {
  await loginAs(page, DEMO_EMAIL);

  await page.goto('/medsupplier/accounts');
  await expect(page.getByText('CardioNova Medical Devices')).toBeVisible();
  const accountCode = `E2E-${Date.now()}`;
  await page.getByRole('button', { name: 'Nuevo' }).click();
  await page.getByLabel('Cuenta *').fill('E2E Regulated Supplier Account');
  await page.getByLabel('Código *').fill(accountCode);
  await page.getByRole('button', { name: 'Crear registro' }).click();
  await expect(page.getByText(accountCode)).toBeVisible();

  await page.goto('/medsupplier/documents');
  await expect(page.getByText('MS-DOC-COC-001')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Aprobar' }).first()).toBeDisabled();

  await page.goto('/medsupplier/quotes');
  await expect(page.getByText('Q-CN-2026-001')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Aprobar' }).first()).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Rechazar' }).first()).toBeDisabled();
});

test('Supplier Finance can access private cockpit and financial API fields', async ({ page }) => {
  await loginAs(page, ROLE_USERS.supplierFinance);
  const orgId = await activeOrganizationId(page);

  await page.goto('/medsupplier/cockpit');
  await expect(page.getByText('Cockpit privado Supplier')).toBeVisible();
  await expect(page.getByText('Margen promedio')).toBeVisible();

  const response = await apiGet(page, `/medsupplier/quotes/?organization_id=${orgId}`);
  expect(response.status()).toBe(200);
  const payload = await response.json();
  expect(payload.results[0]).toHaveProperty('supplier_cost');
  expect(payload.results[0]).toHaveProperty('margin');
});

test('Supplier Quality and Logistics cannot access private financial cockpit', async ({ page }) => {
  for (const email of [ROLE_USERS.supplierQuality, ROLE_USERS.supplierLogistics]) {
    await loginAs(page, email);
    const orgId = await activeOrganizationId(page);

    const cockpit = await apiGet(page, `/medsupplier/cockpit/private/?organization_id=${orgId}`);
    expect(cockpit.status()).toBe(403);

    const quotes = await apiGet(page, `/medsupplier/quotes/?organization_id=${orgId}`);
    expect(quotes.status()).toBe(200);
    const payload = await quotes.json();
    expect(payload.results[0]).not.toHaveProperty('supplier_cost');
    expect(payload.results[0]).not.toHaveProperty('margin');

    await page.evaluate(() => window.localStorage.clear());
  }
});

test('Supplier Viewer is read-only and backend rejects mutation', async ({ page }) => {
  await loginAs(page, ROLE_USERS.supplierViewer);
  const orgId = await activeOrganizationId(page);

  await page.goto('/medsupplier/accounts');
  await expect(page.getByRole('button', { name: 'Nuevo' })).toHaveCount(0);

  const response = await apiPost(page, `/medsupplier/accounts/?organization_id=${orgId}`, {
    name: 'Blocked Viewer Account',
    account_code: `VIEW-${Date.now()}`,
    status: 'prospect',
  });
  expect(response.status()).toBe(403);
});

test('Customer roles are scoped, read filtered data, and never see private cockpit or financial fields', async ({ page }) => {
  for (const email of [ROLE_USERS.customerBuyer, ROLE_USERS.customerQuality, ROLE_USERS.customerAuditor, ROLE_USERS.customerViewer]) {
    await loginAs(page, email);
    const orgId = await activeOrganizationId(page);

    const cockpit = await apiGet(page, `/medsupplier/cockpit/private/?organization_id=${orgId}`);
    expect(cockpit.status()).toBe(403);

    const accounts = await apiGet(page, `/medsupplier/accounts/?organization_id=${orgId}`);
    expect(accounts.status()).toBe(200);
    const accountPayload = await accounts.json();
    const accountCodes = accountPayload.results.map((item) => item.account_code);
    expect(accountCodes).toContain('MS-DEMO-001');
    expect(accountCodes).not.toContain('MS-DEMO-PRIVATE');

    const quotes = await apiGet(page, `/medsupplier/quotes/?organization_id=${orgId}`);
    expect(quotes.status()).toBe(200);
    const quotePayload = await quotes.json();
    for (const field of ['private_margin_notes', 'supplier_cost', 'margin', 'commission', 'advance', 'internal_notes', 'pricing_internal']) {
      expect(quotePayload.results[0]).not.toHaveProperty(field);
    }

    if (email === ROLE_USERS.customerAuditor) {
      const evidence = await apiGet(page, `/medsupplier/evidence-packages/?organization_id=${orgId}`);
      expect(evidence.status()).toBe(200);
      const evidencePayload = await evidence.json();
      expect(evidencePayload.results.map((item) => item.package_number)).toContain('EP-CN-0001');
    }

    const mutation = await apiPost(page, `/medsupplier/accounts/?organization_id=${orgId}`, {
      name: 'Blocked Customer Account',
      account_code: `CUST-${Date.now()}`,
      status: 'prospect',
    });
    expect(mutation.status()).toBe(403);

    await page.evaluate(() => window.localStorage.clear());
  }
});
