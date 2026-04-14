# DeepResearchWeb Frontend Design Document

## 1. Project Overview

**Project Name**: DeepResearchWeb Frontend
**Type**: Single-page application (SPA) with React 18
**Purpose**: Web-based deep research agent UI with chatbot interaction, citation panel, session management, and system configuration

## 2. Tech Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | React | 18.2.0 |
| Language | TypeScript | 5.3.3 |
| Build Tool | Vite | 5.1.0 |
| Routing | React Router DOM | 6.22.0 |
| State Management | Zustand | 4.5.0 |
| Data Fetching | TanStack Query + Axios | 5.20.0 / 1.6.0 |
| Styling | Tailwind CSS + tailwindcss-animate | 3.4.1 / 1.0.7 |
| Icons | Lucide React | 0.330.0 |
| Markdown | react-markdown + remark-gfm | 9.0.0 / 4.0.0 |
| Utilities | clsx, tailwind-merge | 2.1.0 / 2.2.0 |

### CSS Architecture

- **Tailwind CSS** with CSS variable-based theming (`index.css`)
- **Dark mode** via `.dark` class on `<html>` element
- **CSS variables** for design tokens: `--primary`, `--background`, `--foreground`, `--card`, `--border`, `--ring`, etc.
- **Custom border radius**: `lg: var(--radius)`, `md`, `sm`

## 3. Project Structure

```
frontend/src/
├── api/                    # API client layer
│   ├── auth.ts             # Authentication API
│   ├── chat.ts             # Chat streaming API (SSE)
│   ├── client.ts            # Axios instance with interceptors
│   ├── health.ts           # Health check API
│   ├── memory.ts           # Memory API
│   ├── mcp.ts              # MCP configuration API
│   ├── session.ts          # Session CRUD API
│   ├── skills.ts           # Skills configuration API
│   ├── tools.ts            # Tools configuration API
│   ├── userEnvConfig.ts    # Environment variable config API
│   └── userSettings.ts     # User settings API (notifications, password)
├── components/
│   ├── chat/               # Chat-related components
│   │   ├── ChatContainer.tsx   # Main chat container
│   │   ├── ChatWindow.tsx      # Chat window with messages + input
│   │   ├── CitationLink.tsx    # Inline citation marker
│   │   ├── InputBar.tsx        # Message input bar
│   │   ├── MessageBubble.tsx   # Single message bubble
│   │   └── ResearchProgress.tsx # 5-stage research progress bar
│   ├── common/             # Shared components
│   │   └── ReferenceCard.tsx   # Citation card in reference panel
│   └── layout/             # Layout components
│       ├── AppLayout.tsx       # Main app layout wrapper
│       ├── ReferencePanel.tsx   # Right-side citation panel
│       └── Sidebar.tsx         # Left navigation sidebar
├── hooks/
│   ├── useAuth.ts          # Authentication hook
│   ├── useChat.ts          # Main chat logic (stream, send, stop)
│   ├── useSSE.ts           # Generic SSE connection hook
│   └── useAuth.ts          # Auth state and update methods
├── pages/
│   ├── Chat.tsx            # Chat page (session management + ChatContainer)
│   ├── Login.tsx           # Login page
│   ├── Register.tsx        # Registration page
│   ├── Settings.tsx        # Settings page (4 tabs)
│   └── config/
│       ├── MCPConfig.tsx   # MCP server configuration
│       ├── SkillsConfig.tsx # Skills configuration
│       └── ToolsConfig.tsx  # Tools configuration
├── stores/                 # Zustand state stores
│   ├── authStore.ts        # Auth: token, user, isAuthenticated, isLoading
│   ├── chatStore.ts        # Chat: currentSession, messages, isLoading, error
│   ├── referenceStore.ts   # Citations: activeCitations, highlightedId, isPanelOpen
│   ├── sessionStore.ts     # Sessions: list, pagination, CRUD
│   └── settingsStore.ts    # (referenced in CLAUDE.md, not yet found)
├── types/
│   ├── auth.ts             # Auth types: User, LoginResponse
│   ├── citation.ts         # Citation types: Citation, ToolConfig, SkillConfig, MCPConfig
│   ├── index.ts            # Re-exports all types
│   ├── memory.ts           # Memory types
│   └── session.ts          # Session & Message types
├── App.tsx                 # Root component with routing
├── main.tsx                # Entry point
└── index.css               # Global styles + CSS variables
```

## 4. Design System

### Color Palette (CSS Variables)

| Token | Light Mode | Dark Mode |
|-------|-----------|-----------|
| `--background` | `0 0% 100%` | `222.2 84% 4.9%` |
| `--foreground` | `222.2 84% 4.9%` | `210 40% 98%` |
| `--primary` | `221.2 83.2% 53.3%` | `217.2 91.2% 59.8%` |
| `--primary-foreground` | `210 40% 98%` | `222.2 47.4% 11.2%` |
| `--secondary` | `210 40% 96.1%` | `217.2 32.6% 17.5%` |
| `--muted` | `210 40% 96.1%` | `217.2 32.6% 17.5%` |
| `--accent` | `210 40% 96.1%` | `217.2 32.6% 17.5%` |
| `--destructive` | `0 84.2% 60.2%` | `0 62.8% 30.6%` |
| `--border` | `214.3 31.8% 91.4%` | `217.2 32.6% 17.5%` |
| `--card` | `0 0% 100%` | `222.2 84% 4.9%` |
| `--sidebar-*` | Separate sidebar tokens for consistent side panel theming |

### Typography

- **Font**: System font stack via Tailwind defaults
- **Prose**: `prose prose-sm max-w-none` for message content rendering
- **Code/Mono**: Font-mono for env var names and technical labels

### Component Patterns

- **Borders**: `rounded-lg` (0.5rem), `rounded-2xl` for message bubbles
- **Shadows**: `shadow-md` on cards, `shadow-sm` on inputs
- **Focus**: `focus:outline-none focus:ring-2 focus:ring-primary`
- **Transitions**: `transition-colors`, `transition-all duration-300`
- **Dark mode**: `dark:` prefix for all dark-specific styles

## 5. Routing & Navigation

### Routes

| Path | Component | Auth Required |
|------|-----------|--------------|
| `/login` | `Login` | No |
| `/register` | `Register` | No |
| `/` | `HomePage` | Yes |
| `/chat` | `Chat` | Yes |
| `/chat/:sessionId` | `Chat` | Yes |
| `/config/tools` | `ToolsConfig` | Yes |
| `/config/skills` | `SkillsConfig` | Yes |
| `/config/mcp` | `MCPConfig` | Yes |
| `/settings` | `Settings` | Yes |

### PrivateRoute Component

All protected routes are wrapped in `PrivateRoute` which:
1. Shows loading spinner during auth initialization (`isLoading: true`)
2. Redirects to `/login` if `isAuthenticated: false`
3. Renders children once authenticated

### App Entry Flow

1. `App.tsx` mounts → reads `auth-storage` from localStorage
2. If token exists → sets auth state, calls `/auth/me` to validate and get user
3. If token invalid → clears auth state
4. Sets `isLoading: false` → renders routes

## 6. State Management (Zustand)

### Store Summary

| Store | Persistence | Key State |
|-------|------------|-----------|
| `authStore` | `localStorage` (token only) | `token`, `user`, `isAuthenticated`, `isLoading` |
| `chatStore` | None | `currentSession`, `messages`, `isLoading`, `error` |
| `sessionStore` | None | `sessions[]`, `total`, `page`, `pageSize`, `isLoading` |
| `referenceStore` | None | `activeCitations`, `highlightedId`, `isPanelOpen` |

### Auth Store

```typescript
{
  token: string | null,
  user: User | null,
  isAuthenticated: boolean,
  isLoading: boolean,  // true until auth init completes

  setAuth: (response: LoginResponse) => void,
  setUser: (user: User) => void,
  logout: () => void,
  setLoading: (loading: boolean) => void
}
```

### Chat Store

```typescript
{
  currentSession: Session | null,
  messages: Message[],
  isLoading: boolean,
  error: string | null,

  setCurrentSession: (session) => void,
  updateCurrentSessionId: (sessionId) => void,  // for new session ID from server
  setMessages: (messages) => void,
  addMessage: (message) => void,
  updateLastMessage: (content) => void,           // streaming update
  updateLastMessageThinking: (thinking) => void,  // thinking update
  setLoading: (loading) => void,
  setError: (error) => void,
  clearChat: () => void
}
```

## 7. API Layer

### Axios Client (`api/client.ts`)

- **Base URL**: `VITE_API_URL || "/api/v1"` (must end with `/api/v1`)
- **Request interceptor**: Reads `auth-storage` from localStorage → adds `Authorization: Bearer <token>`
- **Response interceptor**:
  - `/auth/me` 401 → clears token only (no redirect)
  - Other 401 → clears token + redirects to `/login`

### Chat Streaming (`api/chat.ts`)

Uses **native Fetch API** (not Axios) for SSE streaming:

```
GET /api/v1/chat/stream?session_id=<id>&message=<msg>&stream=true
Headers: Authorization: Bearer <token>
```

**SSE Events**:

| Event | Payload | Handler |
|-------|---------|---------|
| `thinking` | `{ content: string }` | `onThinking` — chain-of-thought output |
| `chunk` | `{ content: string }` | `onChunk` — message content streaming |
| `citations` | `{ citations: Citation[] }` | `onCitations` — message citations |
| `done` | `{ message_id: number }` | `onDone` — stream finished |
| `error` | `{ error: string }` | `onError` — stream error |

**Response Headers**:
- `X-Session-Id`: New session ID (when creating a new session)

### API Modules

| Module | Key Endpoints |
|--------|--------------|
| `auth.ts` | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| `session.ts` | `GET /sessions`, `POST /sessions`, `GET /sessions/:id`, `PUT /sessions/:id`, `DELETE /sessions/:id` |
| `chat.ts` | `POST /chat/message` (non-stream), `GET /chat/stream` (SSE) |
| `userSettings.ts` | `POST /user-settings/change-password`, `GET/PUT /user-settings/notifications` |
| `userEnvConfig.ts` | `GET /user-env-config`, `POST /user-env-config`, `PUT /user-env-config` |
| `tools.ts` | CRUD for tool configurations |
| `skills.ts` | CRUD for skill configurations |
| `mcp.ts` | CRUD for MCP server configurations |

## 8. Key Features

### 8.1 Chat System

**Chat Window Flow**:
1. User types in `InputBar` (Shift+Enter for newline, Enter to send)
2. `useChat.sendMessage()` creates user message + empty assistant placeholder
3. SSE stream begins → `onThinking` updates thought bubble, `onChunk` updates content
4. Citations appear after `done` event
5. Clicking citation index opens `ReferencePanel` with that citation highlighted

**Message Bubble Features**:
- Markdown rendering via `react-markdown` + `remark-gfm`
- Chain-of-thought (thinking) display with "思考中" / "思考结束" indicator
- Citation indices as clickable superscript badges
- Timestamps on each message
- Different styles for user (right, primary bg) vs assistant (left, muted bg)

**Input Bar Features**:
- Auto-resizing textarea (max 150px height)
- Stop button (square icon) when loading, Send button otherwise
- Keyboard: Enter sends, Shift+Enter adds newline
- Disabled state during loading

### 8.2 Session Management

- Session list in sidebar with title + relative date ("今天", "昨天", "X 天前")
- Create new session via "新建对话" button
- Delete session via trash icon (hover reveal)
- Session modes: `chat` (MessageSquare icon) vs `research` (Zap icon, amber color)
- Selecting session loads its full message history via `GET /sessions/:id`

### 8.3 Reference Panel

**States**:
- Empty: "暂无引用" with BookOpen icon
- With citations: list of `ReferenceCard` components

**ReferenceCard**:
- Source type icon (Globe=web, Database=mcp, Brain=memory, FileText=document)
- Citation index badge
- Title, URL (truncated), snippet
- External link to open URL
- Highlight state (primary border + ring) when clicked from message

### 8.4 Research Progress

5-stage progress bar for deep research mode:
1. **分析问题** (Triage) — Sparkles icon
2. **制定计划** (Plan) — FileText icon
3. **检索信息** (Search) — Search icon
4. **综合分析** (Synthesis) — Loader2 icon (animated)
5. **生成报告** (Report) — CheckCircle icon

**Visual states**:
- Pending: gray background
- Running: amber background + `animate-pulse` + spinning Loader2
- Completed: green background + checkmark

### 8.5 Settings Page

4-tab settings interface:

**个人资料 (Profile)**:
- Username (disabled, read-only)
- Email (editable)

**安全设置 (Security)**:
- Old password + new password + confirm password
- Show/hide password toggles
- Min 8 chars validation

**通知设置 (Notifications)**:
- Channels: email, browser push
- Types: new message, research complete, mention
- All checkboxes with disabled state when no channel enabled

**环境变量设置 (Environment Variables)**:
- Grouped by category: 数据库配置, Neo4j, Redis, RabbitMQ, Milvus, Qdrant, JWT, LLM, 搜索, ARQ, MemOS, 应用配置
- Each env var displayed as `label + monospace input`
- Save / Reset buttons
- "is_new" indicator for first-time config

### 8.6 Authentication

**Login/Register Pages**:
- Clean form layout with logo
- Form validation with inline error messages
- Redirect to `/chat` on success

**Auth Initialization**:
- Checks localStorage on app start
- Validates token via `/auth/me`
- Handles 401 gracefully (clears invalid token)

## 9. Custom Hooks

### `useChat()`

Central hook for chat functionality:

```typescript
{
  currentSession, messages, isLoading, error,
  sendMessage: (content: string) => Promise<void>,
  loadSession: (sessionId: number) => Promise<void>,
  createNewSession: (title?: string) => Promise<Session | null>,
  deleteSession: (sessionId: number) => Promise<void>,
  stopStream: () => void,
  clearChat: () => void
}
```

Key implementation details:
- Uses `useRef` to store cleanup function for SSE connection
- On send: creates user message → creates empty assistant placeholder → starts SSE stream
- `updateLastMessage` and `updateLastMessageThinking` for streaming updates
- `updateCurrentSessionId` called when server returns new session ID in `X-Session-Id` header

### `useSSE()`

Generic SSE hook for any SSE connection:

```typescript
{
  isConnected: boolean,
  connect: (url: string, options: SSEOptions) => EventSource,
  disconnect: () => void
}
```

Handles standard events: `message`, `chunk`, `citations`, `error`, `done`

## 10. Component Details

### MessageBubble

- **Thinking section**: Shows when `message.thinking` exists and has content
- **Thinking indicator**: "思考中" (spinner) or "思考结束" (CheckCircle) depending on whether `message.content` has content
- **Content**: ReactMarkdown for assistant, plain text for user
- **Citations**: Row of CitationLink badges below content, above timestamp

### ChatWindow

- Scrollable message list with `max-w-4xl mx-auto`
- Empty state: centered welcome message
- Error banner (red) below messages
- `messagesEndRef` for auto-scroll to bottom on new messages

### InputBar

- Textarea with auto-resize (up to 150px)
- Send/Stop button toggles based on `isLoading`
- Enter to send, Shift+Enter for newline

### Sidebar

- Logo header
- "新建对话" CTA button
- Session list with relative dates and mode icons
- Config nav: Tools, Skills, MCP (with Zap, Server icons)
- User info + logout at bottom

### ReferencePanel

- Slide-in panel (right side, 384px wide)
- Close button (X icon)
- Empty state with icon
- Scrollable citation list

### ResearchProgress

- Amber/amber-dark background strip
- Horizontal step display with dividers
- Stage-specific icons with correct running/pending/completed states

## 11. Configuration Pages

### ToolsConfig, SkillsConfig, MCPConfig

Located in `pages/config/`:
- List/table of configured items
- Enable/disable toggles
- CRUD operations (create, edit, delete)
- Form modals for add/edit

## 12. Environment Configuration

**Vite Environment Variables**:
- `VITE_API_URL`: Backend API base URL (default: `/api/v1`)

**Critical**: API_BASE_URL must end with `/api/v1` (warning logged if not)

## 13. Dependencies Summary

### Production
- `react` + `react-dom`: UI framework
- `react-router-dom`: Client-side routing
- `zustand`: Lightweight state management
- `@tanstack/react-query`: Data fetching/caching (configured but usage not deeply reviewed)
- `axios`: HTTP client for non-streaming requests
- `react-markdown` + `remark-gfm`: Markdown rendering in messages
- `lucide-react`: Icon library
- `clsx` + `tailwind-merge`: Class name utility functions

### Development
- `typescript`: Type safety
- `vite`: Build tool
- `tailwindcss` + `tailwindcss-animate`: Styling
- `eslint` + `@typescript-eslint/*`: Linting
- `@playwright/test` + `puppeteer`: E2E testing

## 14. Key Design Decisions

1. **Zustand over Redux/Context**: Chosen for simplicity and minimal boilerplate
2. **Fetch over Axios for SSE**: Native Fetch API used for streaming to avoid Axios interceptor complexity with SSE
3. **localStorage for token persistence**: `auth-storage` Zustand persist key, with manual token extraction in Axios interceptor
4. **CSS variables for theming**: Enables dark mode via class toggle without reloading
5. **Monospace for technical content**: Env var names and code snippets use font-mono
6. **Two-way store updates for streaming**: Both `messages[]` array and `updateLastMessage` ref-based approach coexist
7. **Placeholder message pattern**: Empty assistant message created upfront, then updated via `updateLastMessage` during streaming
8. **Thinking bubble**: Separate from main content, shown in a distinct styled box with indicator icon
9. **Citation panel as overlay**: Right-side panel rather than inline citations for cleaner message readability
