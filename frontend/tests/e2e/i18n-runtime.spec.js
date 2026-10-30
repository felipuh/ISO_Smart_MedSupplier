import { expect, test } from '@playwright/test';

const EMAIL = process.env.TEST_EMAIL || 'admin@isosmart.local';
const PASSWORD = process.env.TEST_PASSWORD || 'Admin@123456';

const LANGS = [
  {
    code: 'es-LATAM',
    loginSubtitle: 'Torre Supplier-Customer regulada',
    loginButton: 'Iniciar Sesión',
    productStatus: 'Producto MedSupplier independiente',
    languageOption: 'Español',
    navigationLabel: 'Proveedores',
  },
  {
    code: 'en',
    loginSubtitle: 'Regulated Supplier-Customer Control Tower',
    loginButton: 'Sign In',
    productStatus: 'Independent MedSupplier product',
    languageOption: 'English',
    navigationLabel: 'Suppliers',
  },
  {
    code: 'pt',
    loginSubtitle: 'Torre Supplier-Customer regulada',
    loginButton: 'Entrar',
    productStatus: 'Produto MedSupplier independente',
    languageOption: 'Português',
    navigationLabel: 'Fornecedores',
  },
];

async function login(page) {
  await page.context().setExtraHTTPHeaders({
    'X-ISO-LOCAL-AUTH-BYPASS': '1',
  });

  await page.locator('input#email, input[type="email"]').first().fill(EMAIL);
  await page.locator('input#password, input[type="password"]').first().fill(PASSWORD);

  const loginResponsePromise = page.waitForResponse(
    (response) =>
      response.url().includes('/api/auth/login/') && response.request().method() === 'POST',
    { timeout: 45000 }
  );

  await page.locator('button[type="submit"]').first().click();

  const loginResponse = await loginResponsePromise;

  if (loginResponse.status() >= 400) {
    let body = '';
    try {
      body = await loginResponse.text();
    } catch {
      body = '';
    }
    throw new Error(`Login failed with status ${loginResponse.status()} ${body}`.trim());
  }

  await page.waitForURL((url) => !url.pathname.endsWith('/login'), {
    timeout: 45000,
  });
}

async function getLanguageSelect(page) {
  const headerLanguageSelect = page.locator('header select').first();
  if (await headerLanguageSelect.count()) {
    return headerLanguageSelect;
  }

  const anyLanguageSelect = page.locator('select').filter({
    has: page.locator('option[value="es-LATAM"]'),
  }).first();
  if (await anyLanguageSelect.count()) {
    return anyLanguageSelect;
  }

  return null;
}

async function applyLanguage(page, languageCode) {
  const languageSelect = await getLanguageSelect(page);
  if (languageSelect) {
    await expect(languageSelect).toBeVisible({ timeout: 45000 });
    await languageSelect.selectOption(languageCode);
    await expect(languageSelect).toHaveValue(languageCode);
  }

  await expect.poll(async () => page.evaluate(() => document.documentElement.lang), {
    timeout: 45000,
  }).toBe(languageCode);
  await page.waitForTimeout(400);
}

for (const lang of LANGS) {
  test(`i18n runtime ${lang.code} login + dashboard`, async ({ page }) => {
    await page.addInitScript((selectedLang) => {
      localStorage.setItem('isosmart_language', selectedLang);
    }, lang.code);

    await page.goto('/login');

    await expect(page.getByText(lang.loginSubtitle)).toBeVisible();
    await expect(page.getByRole('button', { name: lang.loginButton })).toBeVisible();

    await login(page);
    await applyLanguage(page, lang.code);

    await expect(page).toHaveURL(/\/medsupplier/);
    await expect(page.getByText(lang.productStatus)).toBeVisible({ timeout: 45000 });
    await expect(page.getByRole('link', { name: new RegExp(lang.navigationLabel) }).first()).toBeVisible();
  });

  test(`i18n runtime ${lang.code} persisted MedSupplier preference`, async ({ browser }) => {
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'X-ISO-LOCAL-AUTH-BYPASS': '1',
      },
    });
    const page = await context.newPage();

    await page.addInitScript((selectedLang) => {
      localStorage.setItem('isosmart_language', selectedLang);
    }, lang.code);

    await page.goto('/login');
    await expect(page.getByText(lang.loginSubtitle)).toBeVisible();
    await login(page);
    await applyLanguage(page, lang.code);

    await expect(page.getByText(lang.productStatus)).toBeVisible({ timeout: 45000 });
    await expect(page.locator('header select').first()).toContainText(lang.languageOption);

    await page.reload();

    await expect.poll(async () => page.evaluate(() => document.documentElement.lang), {
      timeout: 45000,
    }).toBe(lang.code);
    await expect(page.getByText(lang.productStatus)).toBeVisible({ timeout: 45000 });

    await context.close();
  });
}
