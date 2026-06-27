const { defineConfig } = require('@playwright/test');

const baseURL = process.env.BASE_URL || 'http://127.0.0.1:3001';

module.exports = defineConfig({
  testDir: './tests/e2e',
  testMatch: ['**/*.spec.js'],
  timeout: 120000,
  expect: {
    timeout: 15000,
  },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL,
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: 'cd ../backend && /home/felipe/proyectos/isosmart/backend/.venv312/bin/python manage.py runserver 127.0.0.1:18002',
      url: 'http://127.0.0.1:18002/health',
      reuseExistingServer: true,
      env: {
        ...process.env,
      },
      timeout: 120000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 3001 --strictPort',
      url: baseURL,
      reuseExistingServer: true,
      env: {
        ...process.env,
        VITE_LOCAL_AUTH_BYPASS: process.env.VITE_LOCAL_AUTH_BYPASS || '1',
        VITE_API_PROXY_TARGET: process.env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:18002',
      },
      timeout: 120000,
    },
  ],
});
