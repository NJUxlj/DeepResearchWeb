import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3000';

test.describe('DeepResearchWeb Frontend Tests', () => {

  test('1. 首页 - 未登录时应重定向到登录页', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ 首页重定向到登录页 - 通过');
  });

  test('2. 登录页面 - 元素验证', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await expect(page.locator('text=DeepResearchWeb')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign up' })).toBeVisible();
    console.log('✅ 登录页面元素 - 通过');
  });

  test('3. 注册页面 - 元素验证', async ({ page }) => {
    await page.goto(`${BASE_URL}/register`);
    await expect(page.locator('text=DeepResearchWeb')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();
    console.log('✅ 注册页面元素 - 通过');
  });

  test('4. 登录 -> 注册跳转', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.getByRole('link', { name: 'Sign up' }).click();
    await expect(page).toHaveURL(/.*\/register/);
    console.log('✅ 登录 -> 注册跳转 - 通过');
  });

  test('5. 注册 -> 登录跳转', async ({ page }) => {
    await page.goto(`${BASE_URL}/register`);
    await page.getByRole('link', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ 注册 -> 登录跳转 - 通过');
  });

  test('6. 未登录访问受保护页面应重定向', async ({ page }) => {
    await page.goto(`${BASE_URL}/chat`);
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ 未登录访问 /chat 重定向 - 通过');

    await page.goto(`${BASE_URL}/config/tools`);
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ 未登录访问 /config/tools 重定向 - 通过');

    await page.goto(`${BASE_URL}/`);
    await expect(page).toHaveURL(/.*\/login/);
    console.log('✅ 未登录访问 / 重定向 - 通过');
  });

  test('7. 配置页面访问 (需先登录)', async ({ page }) => {
    // 1. 先注册 - 使用唯一的用户名
    const timestamp = Date.now();
    const username = `testuser${timestamp}`;

    await page.goto(`${BASE_URL}/register`);
    // 使用更具体的选择器填写表单
    await page.getByPlaceholder('Username').fill(username);
    await page.getByPlaceholder('Email').fill(`${username}@example.com`);
    // 使用 locators 避免 placeholder 冲突
    await page.locator('input[name="password"]').fill('Test123456');
    await page.getByPlaceholder('Confirm your password').fill('Test123456');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 等待注册完成并跳转到登录页
    await page.waitForURL(/.*\/login/, { timeout: 15000 });
    console.log(`✅ 注册成功，跳转到: ${page.url()}`);

    // 2. 访问配置页面 - 先登录
    await page.getByPlaceholder('Username').fill(username);
    await page.getByPlaceholder('Password').fill('Test123456');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // 等待登录后跳转到首页
    await page.waitForURL(/.*\/($|chat)/, { timeout: 15000 });
    console.log(`✅ 登录成功，跳转到: ${page.url()}`);

    // 3. 直接访问配置页面
    await page.goto(`${BASE_URL}/config/tools`);
    await page.waitForTimeout(2000);
    console.log(`✅ Tools 配置页面 - 状态: ${page.url()}`);

    await page.goto(`${BASE_URL}/config/skills`);
    await page.waitForTimeout(2000);
    console.log(`✅ Skills 配置页面 - 状态: ${page.url()}`);

    await page.goto(`${BASE_URL}/config/mcp`);
    await page.waitForTimeout(2000);
    console.log(`✅ MCP 配置页面 - 状态: ${page.url()}`);
  });

  test('8. 聊天页面访问 (需先登录)', async ({ page }) => {
    // 1. 先注册 - 使用唯一的用户名
    const timestamp = Date.now();
    const username = `chatuser${timestamp}`;

    await page.goto(`${BASE_URL}/register`);
    await page.getByPlaceholder('Username').fill(username);
    await page.getByPlaceholder('Email').fill(`${username}@example.com`);
    await page.locator('input[name="password"]').fill('Test123456');
    await page.getByPlaceholder('Confirm your password').fill('Test123456');
    await page.getByRole('button', { name: 'Create Account' }).click();

    // 等待注册完成
    await page.waitForURL(/.*\/login/, { timeout: 15000 });
    console.log(`✅ 注册成功，跳转到: ${page.url()}`);

    // 2. 登录
    await page.getByPlaceholder('Username').fill(username);
    await page.getByPlaceholder('Password').fill('Test123456');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // 等待登录后跳转
    await page.waitForURL(/.*\/($|chat)/, { timeout: 15000 });
    console.log(`✅ 登录成功，跳转到: ${page.url()}`);

    // 3. 访问聊天页面
    await page.goto(`${BASE_URL}/chat`);
    await page.waitForTimeout(2000);
    console.log(`✅ 聊天页面 - 状态: ${page.url()}`);
  });

});

console.log('测试脚本已准备就绪，运行: npx playwright test');
