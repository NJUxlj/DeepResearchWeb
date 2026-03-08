const http = require('http');

const BASE_URL = 'http://localhost:3000';

function httpGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    }).on('error', reject);
  });
}

async function testPages() {
  console.log('=== DeepResearchWeb 前端页面测试 ===\n');

  const pages = [
    { path: '/', name: '首页' },
    { path: '/login', name: '登录页' },
    { path: '/register', name: '注册页' },
    { path: '/chat', name: '聊天页' },
    { path: '/chat/123', name: '聊天页(带sessionId)' },
    { path: '/config/tools', name: '配置工具页' },
    { path: '/config/skills', name: '配置技能页' },
    { path: '/config/mcp', name: '配置MCP页' },
  ];

  let passed = 0;
  let failed = 0;

  for (const page of pages) {
    try {
      const result = await httpGet(BASE_URL + page.path);
      if (result.status === 200) {
        const hasTitle = result.body.includes('DeepResearchWeb');
        if (hasTitle) {
          console.log(`✅ ${page.name} (${page.path}): 200 - 标题正确`);
          passed++;
        } else {
          console.log(`⚠️  ${page.name} (${page.path}): 200 - 标题可能不正确`);
          passed++;
        }
      } else {
        console.log(`❌ ${page.name} (${page.path}): ${result.status}`);
        failed++;
      }
    } catch (e) {
      console.log(`❌ ${page.name} (${page.path}): ${e.message}`);
      failed++;
    }
  }

  console.log(`\n=== 测试结果: ${passed} 通过, ${failed} 失败 ===`);

  // 测试 API
  console.log('\n=== 后端 API 测试 ===\n');

  const apis = [
    { path: '/', name: '健康检查' },
    { path: '/docs', name: 'API文档' },
  ];

  for (const api of apis) {
    try {
      const result = await httpGet('http://localhost:8000' + api.path);
      console.log(`✅ ${api.name}: ${result.status}`);
    } catch (e) {
      console.log(`❌ ${api.name}: ${e.message}`);
    }
  }
}

testPages();
