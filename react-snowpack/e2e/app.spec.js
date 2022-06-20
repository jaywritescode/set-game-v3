const { test, expect } = require('@playwright/test');

test('basic test', async ({ page }) => {
  await page.goto('http://localhost:8080/');
  const title = page.locator('header .title');
  await expect(title).toHaveText('set game');
});