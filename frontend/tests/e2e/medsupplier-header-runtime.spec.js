import { expect, test } from '@playwright/test';
import { execFileSync } from 'node:child_process';
import path from 'node:path';

const PYTHON_BIN = process.env.PYTHON_BIN || '/home/felipe/proyectos/ISO_Smart_MedSupplier/backend/.venv312/bin/python';
const REPO_ROOT = path.resolve(process.cwd(), '..');
const DEMO_EMAIL = 'medsupplier.e2e@smart3ai.local';
const DEMO_PASSWORD = 'MedSupplierDemo@123';
const DEMO_ORG_SLUG = 'medsupplier-demo-e2e';

const loginAsDemo = async (page) => {
  await page.goto('/login');
  await page.evaluate(() => window.localStorage.clear());
  await page.locator('#email').fill(DEMO_EMAIL);
  await page.locator('#password').fill(DEMO_PASSWORD);
  await page.locator('button[type="submit"]').click();
  await page.waitForFunction(() => Boolean(window.localStorage.getItem('access_token')));
  await expect(page).toHaveURL(/\/medsupplier/);
};

const stubEmptyNotifications = async (page) => {
  await page.route('**/api/settings/notification_history/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: [] }),
    });
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

test('MedSupplier login ignores stale local auth tokens', async ({ page }) => {
  await page.goto('/login');
  await page.evaluate(() => {
    window.localStorage.setItem('access_token', 'stale.access.token');
    window.localStorage.setItem('refresh_token', 'stale.refresh.token');
  });
  await page.reload();

  await page.locator('#email').fill(DEMO_EMAIL);
  await page.locator('#password').fill(DEMO_PASSWORD);

  const loginResponsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/auth/login/') && response.request().method() === 'POST',
  );
  await page.locator('button[type="submit"]').click();
  const loginResponse = await loginResponsePromise;

  expect(loginResponse.status()).toBe(200);
  await page.waitForFunction(() => window.location.pathname === '/medsupplier');
  await expect(page.getByText('Producto MedSupplier independiente')).toBeVisible();
});

test('MedSupplier enterprise header persists theme, font size, language, notifications, and settings state', async ({ page }) => {
  await stubEmptyNotifications(page);

  await loginAsDemo(page);
  await expect(page.getByText('Producto MedSupplier independiente')).toBeVisible();

  await page.getByLabel('Cambiar a tema oscuro').click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart-theme'))).toBe('dark');
  await expect.poll(() => page.evaluate(() => document.documentElement.classList.contains('dark'))).toBe(true);

  await page.getByLabel('Aumentar tamaño de texto').click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart_font_size'))).toBe('large');
  await expect.poll(() => page.evaluate(() => document.documentElement.getAttribute('data-font-size'))).toBe('large');

  await page.getByLabel('Restablecer tamaño de texto').click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart_font_size'))).toBe('normal');

  await page.getByLabel('Idioma').selectOption('en');
  await expect(page.getByText('Independent MedSupplier product')).toBeVisible();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart_language'))).toBe('en');

  await page.reload();
  await expect(page.getByText('Independent MedSupplier product')).toBeVisible();
  await expect.poll(() => page.evaluate(() => document.documentElement.lang)).toBe('en');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart-theme'))).toBe('dark');

  await page.getByLabel('Open notifications').click();
  await expect(page.getByRole('menu', { name: 'Notifications panel' })).toBeVisible();
  await expect(page.getByText('There are no new notifications.')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('menu', { name: 'Notifications panel' })).toBeHidden();

  await page.getByLabel('Open settings').click();
  await expect(page.getByRole('menu', { name: 'Settings menu' })).toBeVisible();
  await page.getByRole('button', { name: 'Use system theme' }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart-theme'))).toBe('system');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('menu', { name: 'Settings menu' })).toBeHidden();

  const header = page.getByRole('banner');
  const userMenuButton = header.getByRole('button', { name: 'My Profile' });
  await expect(userMenuButton).toHaveAttribute('aria-haspopup', 'menu');
  await expect(userMenuButton).toHaveAttribute('aria-expanded', 'false');
  await userMenuButton.click();
  await expect(userMenuButton).toHaveAttribute('aria-expanded', 'true');
  await expect(page.locator('#user-menu-panel')).toBeVisible();
  await expect(page.locator('#user-menu-panel')).toContainText(DEMO_EMAIL);
  await expect(page.locator('#user-menu-panel').getByRole('link', { name: 'My Profile' })).toHaveAttribute('href', '/profile');
  await expect(page.locator('#user-menu-panel').getByRole('button', { name: 'Sign Out' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.locator('#user-menu-panel')).toBeHidden();
});

test('MedSupplier enterprise header keeps navigation and preference controls usable on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await stubEmptyNotifications(page);
  await loginAsDemo(page);

  await expect(page.getByText('Producto MedSupplier independiente')).toBeVisible();

  const header = page.getByRole('banner');
  await header.getByLabel('Abrir navegación').click();
  await expect(header.getByLabel('Cerrar navegación')).toHaveAttribute('aria-expanded', 'true');
  await page.getByRole('link', { name: /Proveedores/ }).click();
  await expect(page).toHaveURL(/\/medsupplier\/accounts/);
  await expect(header.getByLabel('Abrir navegación')).toHaveAttribute('aria-expanded', 'false');

  await page.getByLabel('Abrir configuración').click();
  await expect(page.getByRole('menu', { name: 'Menú de configuración' })).toBeVisible();
  await page.getByRole('button', { name: 'A+' }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart_font_size'))).toBe('large');
  await expect.poll(() => page.evaluate(() => document.documentElement.getAttribute('data-font-size'))).toBe('large');
  await page.getByRole('button', { name: 'Restablecer tamaño de texto' }).click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('isosmart_font_size'))).toBe('normal');
  await page.keyboard.press('Escape');
  await expect(page.getByRole('menu', { name: 'Menú de configuración' })).toBeHidden();

  await page.getByLabel('Abrir notificaciones').click();
  await expect(page.getByRole('menu', { name: 'Panel de notificaciones' })).toBeVisible();
  await page.mouse.click(20, 20);
  await expect(page.getByRole('menu', { name: 'Panel de notificaciones' })).toBeHidden();
});
