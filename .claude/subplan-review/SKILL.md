# Subplan Review Skill

## 概述

此 skill 用于审查 DeepResearchWeb 项目的 subplan 文件，确保：
1. **逻辑正确性**: 每个 subplan 的设计逻辑是否合理、完整
2. **代码准确性**: 包含的代码示例是否正确、可运行
3. **逻辑一致性**: 各个 subplan 之间的设计是否相互兼容、无冲突

## 使用方法

调用方式：
```bash
kimi --skill subplan-review
```

或直接运行审查：
```bash
cd /Users/xiniuyiliao/Desktop/code/DeepResearchWeb && kimi --skill subplan-review
```

## 审查流程

### 1. 收集所有 Subplan

读取 `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/subplans` 目录下的所有 `.md` 文件。

### 2. 解析 Subplan 结构

每个 subplan 应包含以下部分：
- **标题和编号**: 清晰的标识
- **目标**: 本 subplan 要实现的功能
- **依赖**: 依赖的其他 subplan
- **Schema 定义**: 数据库模型、API 接口、类型定义等
- **实现细节**: 详细的代码实现
- **接口契约**: 与其他模块的交互接口

### 3. 审查维度

#### 3.1 逻辑正确性
- [ ] 功能设计是否完整
- [ ] 流程设计是否合理
- [ ] 边界情况是否考虑
- [ ] 错误处理是否完善

#### 3.2 代码准确性
- [ ] Python 语法是否正确
- [ ] TypeScript 类型是否正确
- [ ] SQL 语句是否正确
- [ ] Pydantic 模型定义是否正确
- [ ] API 端点定义是否符合 RESTful 规范

#### 3.3 逻辑一致性
- [ ] 数据模型之间是否一致（Python SQLAlchemy ↔ TypeScript 类型）
- [ ] API 接口定义是否一致（后端 ↔ 前端）
- [ ] 依赖关系是否合理（无循环依赖）
- [ ] 命名规范是否统一
- [ ] 配置项是否一致

### 4. 审查检查清单

#### 数据库模型一致性
```python
# 后端 SQLAlchemy 模型
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
```

```typescript
// 前端类型定义
interface User {
  id: number;
  username: string;
}
```

#### API 接口一致性
```python
# 后端 API
@router.post("/api/v1/auth/register", response_model=UserResponse)
async def register(data: UserCreate) -> UserResponse:
    ...
```

```typescript
// 前端 API 调用
export const register = (data: UserCreate): Promise<UserResponse> =>
  apiClient.post("/api/v1/auth/register", data);
```

#### 配置一致性
- Docker Compose 中的服务名、端口、环境变量
- 后端配置类中的默认值
- 前端 API client 中的 baseURL

### 5. 输出格式

审查完成后，输出报告：

```markdown
# Subplan Review Report

## 审查概览
- 审查时间: {timestamp}
- 审查文件数: {count}
- 总体状态: ✅ 通过 / ⚠️ 需要修改 / ❌ 未通过

## 详细审查结果

### 1. 逻辑正确性
| Subplan | 状态 | 说明 |
|---------|------|------|
| xxx.md | ✅ | ... |

### 2. 代码准确性
| Subplan | 问题 | 建议 |
|---------|------|------|
| xxx.md | xxx | xxx |

### 3. 逻辑一致性
#### 3.1 数据模型一致性
- [x] User 模型: 前后端一致
- [ ] Session 模型: 字段不匹配 (后端有 xxx, 前端缺少)

#### 3.2 API 接口一致性
- [x] /api/v1/auth/*: 定义一致

#### 3.3 配置一致性
- [x] Redis 端口: 一致 (6379)

## 需要修复的问题

### 高优先级
1. **xxx.md**: xxx 问题
   - 修复建议: xxx

### 中优先级
...

### 低优先级
...
```

## 修复指南

当发现问题时，按照以下优先级修复：

1. **破坏性错误**: 语法错误、类型不匹配（会导致编译/运行失败）
2. **逻辑缺陷**: 设计不完整、边界情况未处理
3. **不一致问题**: 命名不统一、配置不匹配
4. **优化建议**: 代码风格、可读性改进

## 示例

### 示例 1: 修复类型不一致

**问题**: User 模型在前端缺少 `created_at` 字段

**修复**:
```typescript
// 修改 frontend/src/types/index.ts
interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;  // 添加
}
```

### 示例 2: 修复 API 路径不一致

**问题**: 后端定义 `/api/v1/chat/stream`，前端调用 `/api/chat/stream`

**修复**:
统一为 `/api/v1/chat/stream`，修改前端 API 路径。
