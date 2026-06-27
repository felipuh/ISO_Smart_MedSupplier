import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const PYTHON_BIN = process.env.PYTHON_BIN || '/home/felipe/proyectos/isosmart/backend/.venv312/bin/python';
const REPO_ROOT = path.resolve(process.cwd(), '..');
const DEMO_EMAIL = 'medsupplier.e2e@smart3ai.local';
const DEMO_PASSWORD = 'MedSupplierDemo@123';
const DEMO_ORG_SLUG = 'medsupplier-demo-e2e';

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
  await page.goto('/login');
  await page.locator('#email').fill(DEMO_EMAIL);
  await page.locator('#password').fill(DEMO_PASSWORD);
  await page.locator('button[type="submit"]').click();

  await expect(page.getByRole('heading', { name: 'ISO Smart MedSupplier' })).toBeVisible();
  await expect(page.getByText('CardioNova Medical Devices')).toBeVisible();

  await page.goto('/medsupplier/accounts');
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
