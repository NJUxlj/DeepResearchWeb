# GitHub MCP 服务器配置指南

本文档介绍如何在 DeepResearchWeb 项目中配置 GitHub MCP 服务器，以便 Agent 能够调用 GitHub API 进行仓库搜索、代码读取、Issue 管理等操作。

---

## 配置概览

GitHub MCP 服务器已添加至项目配置文件：`.claude/mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## 前置要求

- Node.js 18+ （用于运行 MCP 服务器）
- GitHub 账号
- GitHub Personal Access Token

---

## 配置步骤

### 1. 获取 GitHub Personal Access Token

1. 登录 GitHub，访问 [Personal Access Tokens](https://github.com/settings/tokens) 页面
2. 点击右上角 **"Generate new token"** → 选择 **"Generate new token (classic)"**
3. 填写 Token 描述（如："DeepResearchWeb MCP"）
4. 选择过期时间（建议 90 天或根据需求设置）
5. 勾选以下权限范围：

| 权限 | 说明 |
|------|------|
| `repo` | 访问仓库（包括私有仓库） |
| `read:user` | 读取用户基本信息 |
| `read:org` | 读取组织信息（可选） |
| `gist` | 访问 Gist（可选） |

6. 点击页面底部 **"Generate token"** 按钮
7. **立即复制生成的 Token**（页面关闭后将无法再次查看）

> ⚠️ **安全提示**: Token 相当于密码，请妥善保管，不要提交到代码仓库。

---

### 2. 设置环境变量

将获取的 Token 设置为环境变量 `GITHUB_TOKEN`：

#### macOS / Linux

```bash
# 临时设置（仅当前终端会话有效）
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 永久设置（添加到 shell 配置文件）
echo 'export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

#### Windows (PowerShell)

```powershell
# 临时设置
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# 永久设置（用户级别）
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_xxxxxxxxxxxxxxxxxxxx", "User")
```

#### Windows (CMD)

```cmd
setx GITHUB_TOKEN "ghp_xxxxxxxxxxxxxxxxxxxx"
```

---

### 3. 安装 MCP 服务器（首次使用）

确保已安装 Node.js 18+，然后安装 GitHub MCP 服务器：

```bash
# 使用 npx 直接运行（推荐，无需全局安装）
npx -y @modelcontextprotocol/server-github

# 或全局安装
npm install -g @modelcontextprotocol/server-github
```

---

### 4. 验证配置

配置完成后，可以通过以下方式验证 MCP 服务器是否正常工作：

#### 在对话中使用

```
请帮我查看我的 GitHub 仓库列表
```

或

```
使用 github 工具搜索关于 "fastapi" 的仓库
```

#### 检查 MCP 服务器状态

启动 Kimi Code CLI 后，观察启动日志中是否显示 GitHub MCP 服务器已成功加载。

---

## 支持的 GitHub 操作

GitHub MCP 服务器提供以下工具供 Agent 调用：

### 仓库操作
| 工具 | 功能 |
|------|------|
| `search_repositories` | 搜索 GitHub 仓库 |
| `get_repository` | 获取仓库详细信息 |
| `list_repository_contents` | 列出仓库目录内容 |
| `get_file_contents` | 读取文件内容 |
| `create_repository` | 创建新仓库 |

### Issue & PR
| 工具 | 功能 |
|------|------|
| `search_issues` | 搜索 Issue 和 Pull Request |
| `create_issue` | 创建 Issue |
| `update_issue` | 更新 Issue |
| `create_pull_request` | 创建 Pull Request |
| `merge_pull_request` | 合并 Pull Request |

### 代码操作
| 工具 | 功能 |
|------|------|
| `search_code` | 搜索代码 |
| `create_branch` | 创建分支 |
| `create_commit` | 创建提交 |
| `push_files` | 推送多个文件 |

### 用户/组织
| 工具 | 功能 |
|------|------|
| `search_users` | 搜索用户 |
| `get_user` | 获取用户信息 |

---

## 使用示例

### 示例 1：搜索热门 Python 项目

```
请使用 github 工具搜索 stars 超过 10000 的 Python 项目
```

### 示例 2：读取文件内容

```
请读取 https://github.com/tiangolo/fastapi 仓库中的 README.md 文件
```

### 示例 3：查找 Issue

```
请搜索 fastapi 仓库中与 "async" 相关的 open issue
```

### 示例 4：分析代码库

```
请分析 langchain 仓库的目录结构，并总结其主要模块
```

---

## 故障排查

### MCP 服务器无法启动

**现象**: 提示 `GITHUB_PERSONAL_ACCESS_TOKEN` 未设置

**解决**: 
1. 检查环境变量是否正确设置：`echo $GITHUB_TOKEN`
2. 重启 Kimi Code CLI 以加载新环境变量

### API 速率限制

**现象**: 调用频繁时报错 `API rate limit exceeded`

**解决**:
- GitHub API 对未认证请求限制为 60 次/小时
- 使用 Personal Access Token 后限制提升至 5000 次/小时
- 如仍不够，可考虑使用 GitHub App 获取更高配额

### 权限不足

**现象**: 无法访问私有仓库或某些操作被拒绝

**解决**:
1. 检查 Token 权限是否包含 `repo` 范围
2. 确认 Token 未过期
3. 检查是否有仓库的访问权限（对于组织仓库）

---

## 相关文档

- [GitHub MCP Server 官方仓库](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [GitHub Personal Access Token 文档](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [GitHub REST API 文档](https://docs.github.com/en/rest)

---

## 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-05 | v1.0 | 初始配置文档 |
