#!/bin/bash
# DeepResearchWeb API Test Script
# Tests all API endpoints comprehensively

set -e

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
API_PREFIX="/api/v1"
OUTPUT_DIR="${OUTPUT_DIR:-/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/output}"
LOG_FILE="$OUTPUT_DIR/api_test_$(date +%Y%m%d_%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Auth token
AUTH_TOKEN=""

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1" | tee -a "$LOG_FILE"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

pass() {
    echo -e "${GREEN}  ✓ PASS${NC}" | tee -a "$LOG_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

fail() {
    echo -e "${RED}  ✗ FAIL${NC} - $1" | tee -a "$LOG_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

# HTTP helper with detailed output
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local description=$5

    log_test "$method $endpoint - $description"

    local response
    local status_code

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$API_PREFIX$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$API_PREFIX$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "$data" 2>/dev/null || echo "000")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$API_PREFIX$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "$data" 2>/dev/null || echo "000")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$API_PREFIX$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")
    fi

    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n1)
    # Get body (all but last line)
    body=$(echo "$response" | sed '$d')

    # Save response to file (sanitize filename)
    local safe_endpoint=$(echo "$endpoint" | tr '/' '_' | tr -d '?&=:')
    echo "$body" > "$OUTPUT_DIR/response_${method}_${safe_endpoint}.json"

    # Check status
    if [ "$status_code" = "$expected_status" ]; then
        pass
        return 0
    else
        fail "Expected $expected_status, got $status_code. Response: $body"
        return 1
    fi
}

# Auth test (no token required)
test_auth_apis() {
    log_info "=========================================="
    log_info "Testing Authentication APIs"
    log_info "=========================================="

    # Generate unique username for this test run
    local timestamp=$(date +%s)
    local test_username="testuser_${timestamp}"

    # Test register
    test_endpoint "POST" "/auth/register" \
        "{\"username\":\"$test_username\",\"email\":\"${test_username}@example.com\",\"password\":\"Test123456\"}" \
        "201" "User registration"

    # Test login (using registered user)
    test_endpoint "POST" "/auth/login" \
        "{\"username\":\"$test_username\",\"password\":\"Test123456\"}" \
        "200" "User login"

    # Extract token from login response (if successful)
    if [ -f "$OUTPUT_DIR/response_POST_auth_login.json" ]; then
        AUTH_TOKEN=$(grep -o '"access_token":"[^"]*"' "$OUTPUT_DIR/response_POST_auth_login.json" | cut -d'"' -f4)
        if [ -n "$AUTH_TOKEN" ]; then
            log_info "Got auth token: ${AUTH_TOKEN:0:20}..."

            # Test get current user
            test_endpoint "GET" "/auth/me" \
                "" "200" "Get current user info"
        fi
    fi

    # Test login with invalid credentials
    log_test "POST /auth/login - Invalid credentials"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username":"invalid_user","password":"wrongpassword"}' 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "401" ] || [ "$status_code" = "400" ]; then
        pass
    else
        fail "Expected 401 or 400, got $status_code"
    fi

    # Test register with existing username
    log_test "POST /auth/register - Duplicate username"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$test_username\",\"email\":\"dup@example.com\",\"password\":\"Test123456\"}" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "400" ] || [ "$status_code" = "409" ]; then
        pass
    else
        fail "Expected 400 or 409, got $status_code"
    fi
}

# Session APIs
test_session_apis() {
    log_info "=========================================="
    log_info "Testing Session APIs"
    log_info "=========================================="

    # Create session
    test_endpoint "POST" "/sessions" \
        '{"title":"Test Session","mode":"chat"}' \
        "201" "Create new session"

    # Get sessions
    test_endpoint "GET" "/sessions" \
        "" "200" "Get all sessions"

    # Get single session (if we have one)
    SESSION_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_sessions.json" 2>/dev/null | head -1 | cut -d'"' -f4)
    if [ -n "$SESSION_ID" ]; then
        test_endpoint "GET" "/sessions/$SESSION_ID" \
            "" "200" "Get single session"

        # Update session
        test_endpoint "PUT" "/sessions/$SESSION_ID" \
            '{"title":"Updated Session"}' \
            "200" "Update session"

        # Delete session
        test_endpoint "DELETE" "/sessions/$SESSION_ID" \
            "" "204" "Delete session"
    fi
}

# Chat APIs
test_chat_apis() {
    log_info "=========================================="
    log_info "Testing Chat APIs"
    log_info "=========================================="

    # Create session first
    test_endpoint "POST" "/sessions" \
        '{"title":"Chat Session","mode":"chat"}' \
        "201" "Create chat session"

    SESSION_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_sessions.json" 2>/dev/null | head -1 | cut -d'"' -f4)

    # Test non-streaming chat (POST /chat/message)
    if [ -n "$SESSION_ID" ]; then
        log_test "POST /chat/message - Non-streaming chat"
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/chat/message" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "{\"session_id\":\"$SESSION_ID\",\"message\":\"Hello, test message\"}" 2>/dev/null || echo "000")
        status_code=$(echo "$response" | tail -n1)
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [ "$status_code" = "200" ]; then
            pass
            # Extract message_id for later use
            MESSAGE_ID=$(echo "$response" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)
            if [ -z "$MESSAGE_ID" ]; then
                MESSAGE_ID=$(echo "$response" | grep -o '"message_id":[0-9]*' | cut -d':' -f2)
            fi
        else
            fail "Expected 200, got $status_code"
        fi

        # Test streaming chat (GET /chat/stream)
        log_test "GET /chat/stream - SSE chat streaming"
        response=$(timeout 10 curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/chat/stream?session_id=$SESSION_ID&message=Hello" \
            -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")

        status_code=$(echo "$response" | tail -n1)
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [ "$status_code" = "200" ] || [ "$status_code" = "202" ]; then
            pass
        else
            fail "Expected 200 or 202, got $status_code"
        fi
    fi

    # Test chat without auth
    log_test "POST /chat/message without auth - Should return 401"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/chat/message" \
        -H "Content-Type: application/json" \
        -d '{"session_id":1,"message":"test"}' 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "401" ]; then
        pass
    else
        fail "Expected 401, got $status_code"
    fi
}

# Research APIs
test_research_apis() {
    log_info "=========================================="
    log_info "Testing Research APIs"
    log_info "=========================================="

    # Create research session
    test_endpoint "POST" "/sessions" \
        '{"title":"Research Session","mode":"research"}' \
        "201" "Create research session"

    SESSION_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_sessions.json" 2>/dev/null | head -1 | cut -d'"' -f4)

    # Test create research task (POST /research/tasks)
    if [ -n "$SESSION_ID" ]; then
        log_test "POST /research/tasks - Create research task"
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/research/tasks" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "{\"session_id\":$SESSION_ID,\"query\":\"What is AI?\"}" 2>/dev/null || echo "000")
        status_code=$(echo "$response" | tail -n1)
        echo "$response" > "$OUTPUT_DIR/response_POST_research_tasks.json"
        TOTAL_TESTS=$((TOTAL_TESTS + 1))

        # Extract task_id
        TASK_ID=$(echo "$response" | grep -o '"task_id":[0-9]*' | cut -d':' -f2)
        if [ -z "$TASK_ID" ]; then
            TASK_ID=$(echo "$response" | grep -o '"task_id":"[^"]*"' | cut -d'"' -f4)
        fi

        if [ "$status_code" = "200" ] || [ "$status_code" = "201" ]; then
            pass
            if [ -n "$TASK_ID" ]; then
                log_info "Got task_id: $TASK_ID"

                # Query task status (GET /research/tasks/{id})
                test_endpoint "GET" "/research/tasks/$TASK_ID" \
                    "" "200" "Get research task status"

                # Test task stream (GET /research/tasks/{id}/stream)
                log_test "GET /research/tasks/$TASK_ID/stream - SSE task progress"
                response=$(timeout 10 curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/research/tasks/$TASK_ID/stream" \
                    -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")
                status_code=$(echo "$response" | tail -n1)
                TOTAL_TESTS=$((TOTAL_TESTS + 1))
                if [ "$status_code" = "200" ]; then
                    pass
                else
                    fail "Expected 200, got $status_code"
                fi
            fi
        else
            fail "Expected 200 or 201, got $status_code"
        fi

        # Test research stream (POST /research/stream) - legacy SSE endpoint
        log_test "POST /research/stream - Start research with SSE (legacy)"
        response=$(timeout 30 curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/research/stream" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d "{\"session_id\":$SESSION_ID,\"query\":\"What is machine learning?\"}" 2>/dev/null || echo "000")
        status_code=$(echo "$response" | tail -n1)
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [ "$status_code" = "200" ]; then
            pass
        else
            fail "Expected 200, got $status_code"
        fi
    fi

    # Test list research tasks (GET /research/tasks)
    test_endpoint "GET" "/research/tasks?limit=10&offset=0" \
        "" "200" "List research tasks"

    # Test research without auth
    log_test "POST /research/tasks without auth - Should return 401"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/research/tasks" \
        -H "Content-Type: application/json" \
        -d '{"query":"test"}' 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "401" ]; then
        pass
    else
        fail "Expected 401, got $status_code"
    fi
}

# Tools APIs
test_tools_apis() {
    log_info "=========================================="
    log_info "Testing Tools APIs"
    log_info "=========================================="

    # Get all tools
    test_endpoint "GET" "/tools" \
        "" "200" "Get all tools"

    # Create custom tool
    test_endpoint "POST" "/tools" \
        '{
            "name":"test_tool",
            "description":"A test tool",
            "type":"custom",
            "config":{
                "type":"function",
                "function":{
                    "name":"test",
                    "description":"Test function",
                    "parameters":{"type":"object","properties":{}}
                }
            },
            "enabled":true
        }' \
        "201" "Create custom tool"

    # Get tool details
    TOOL_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_tools.json" 2>/dev/null | head -1 | cut -d'"' -f4)
    if [ -n "$TOOL_ID" ]; then
        test_endpoint "GET" "/tools/$TOOL_ID" \
            "" "200" "Get tool details"

        # Update tool
        test_endpoint "PUT" "/tools/$TOOL_ID" \
            '{"enabled":false}' \
            "200" "Update tool"

        # Delete tool
        test_endpoint "DELETE" "/tools/$TOOL_ID" \
            "" "204" "Delete tool"
    fi

    # Test get non-existent tool
    log_test "GET /tools/99999 - Non-existent tool"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/tools/99999" \
        -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "404" ]; then
        pass
    else
        fail "Expected 404, got $status_code"
    fi
}

# Skills APIs
test_skills_apis() {
    log_info "=========================================="
    log_info "Testing Skills APIs"
    log_info "=========================================="

    # Get all skills
    test_endpoint "GET" "/skills" \
        "" "200" "Get all skills"

    # Create skill
    test_endpoint "POST" "/skills" \
        '{
            "name":"test_skill",
            "description":"A test skill",
            "prompt_template":"You are a {role} assistant",
            "trigger_keywords":["test","help"],
            "enabled":true
        }' \
        "201" "Create skill"

    # Get skill details
    SKILL_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_skills.json" 2>/dev/null | head -1 | cut -d'"' -f4)
    if [ -n "$SKILL_ID" ]; then
        test_endpoint "GET" "/skills/$SKILL_ID" \
            "" "200" "Get skill details"

        # Update skill
        test_endpoint "PUT" "/skills/$SKILL_ID" \
            '{"enabled":false}' \
            "200" "Update skill"

        # Delete skill
        test_endpoint "DELETE" "/skills/$SKILL_ID" \
            "" "204" "Delete skill"
    fi
}

# MCP APIs
test_mcp_apis() {
    log_info "=========================================="
    log_info "Testing MCP APIs"
    log_info "=========================================="

    # Get all MCP servers
    test_endpoint "GET" "/mcp/servers" \
        "" "200" "Get all MCP servers"

    # Create MCP server (will fail if no valid config, but tests endpoint)
    test_endpoint "POST" "/mcp/servers" \
        '{
            "name":"test_mcp",
            "transport":"stdio",
            "command":"echo",
            "args":["hello"],
            "enabled":false
        }' \
        "201" "Create MCP server"

    # Get MCP server details
    MCP_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_mcp_servers.json" 2>/dev/null | head -1 | cut -d'"' -f4)
    if [ -n "$MCP_ID" ]; then
        test_endpoint "GET" "/mcp/servers/$MCP_ID" \
            "" "200" "Get MCP server details"

        # Get MCP tools (may fail if server not running, but tests endpoint)
        test_endpoint "GET" "/mcp/servers/$MCP_ID/tools" \
            "" "200" "Get MCP server tools"

        # Update MCP server
        test_endpoint "PUT" "/mcp/servers/$MCP_ID" \
            '{"enabled":false}' \
            "200" "Update MCP server"

        # Delete MCP server
        test_endpoint "DELETE" "/mcp/servers/$MCP_ID" \
            "" "204" "Delete MCP server"
    fi
}

# Messages APIs
test_messages_apis() {
    log_info "=========================================="
    log_info "Testing Messages APIs"
    log_info "=========================================="

    # Create a session for testing messages
    test_endpoint "POST" "/sessions" \
        '{"title":"Message Test Session","mode":"chat"}' \
        "201" "Create session for message tests"

    MSG_SESSION_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_sessions.json" 2>/dev/null | head -1 | cut -d'"' -f4)

    if [ -n "$MSG_SESSION_ID" ]; then
        # Create message
        test_endpoint "POST" "/messages" \
            "{\"session_id\":$MSG_SESSION_ID,\"role\":\"user\",\"content\":\"Test message\"}" \
            "201" "Create message"

        # Get message ID
        MSG_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_messages.json" 2>/dev/null | head -1 | cut -d'"' -f4)
        if [ -z "$MSG_ID" ]; then
            MSG_ID=$(grep -o '"id":[0-9]*' "$OUTPUT_DIR/response_POST_messages.json" 2>/dev/null | head -1 | cut -d':' -f2)
        fi

        # Get messages by session
        test_endpoint "GET" "/messages/by-session/$MSG_SESSION_ID" \
            "" "200" "Get messages by session"

        # Get single message
        if [ -n "$MSG_ID" ]; then
            test_endpoint "GET" "/messages/$MSG_ID" \
                "" "200" "Get message details"

            # Update message
            test_endpoint "PUT" "/messages/$MSG_ID" \
                '{"content":"Updated message content"}' \
                "200" "Update message"

            # Delete message
            test_endpoint "DELETE" "/messages/$MSG_ID" \
                "" "204" "Delete message"
        fi
    fi
}

# Memory APIs
test_memory_apis() {
    log_info "=========================================="
    log_info "Testing Memory APIs"
    log_info "=========================================="

    # Search memory (GET /memory/search)
    test_endpoint "GET" "/memory/search?query=test&top_k=5&search_type=hybrid" \
        "" "200" "Search memory (hybrid)"

    test_endpoint "GET" "/memory/search?query=test&top_k=3&search_type=preference" \
        "" "200" "Search memory (preference)"

    test_endpoint "GET" "/memory/search?query=test&top_k=3&search_type=tree" \
        "" "200" "Search memory (tree)"

    # Add tree memory (POST /memory/tree)
    test_endpoint "POST" "/memory/tree" \
        '{"content":"Test tree memory content","metadata":{"source":"test"}}' \
        "200" "Add tree memory"

    # Add preference memory (POST /memory/preference)
    # First create a session
    test_endpoint "POST" "/sessions" \
        '{"title":"Memory Preference Test","mode":"chat"}' \
        "201" "Create session for preference test"

    PREF_SESSION_ID=$(grep -o '"id":"[^"]*"' "$OUTPUT_DIR/response_POST_sessions.json" 2>/dev/null | head -1 | cut -d'"' -f4)

    if [ -n "$PREF_SESSION_ID" ]; then
        test_endpoint "POST" "/memory/preference" \
            "{\"session_id\":$PREF_SESSION_ID,\"messages\":[{\"role\":\"user\",\"content\":\"I prefer short answers\"}],\"preference_type\":\"chat\"}" \
            "200" "Add preference memory"
    fi

    # Memory feedback (POST /memory/feedback) - needs session_id as path param
    if [ -n "$PREF_SESSION_ID" ]; then
        log_test "POST /memory/feedback - Submit memory feedback"
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/memory/feedback?session_id=$PREF_SESSION_ID&feedback=More%20detailed%20answer" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d '[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi"}]' 2>/dev/null || echo "000")
        status_code=$(echo "$response" | tail -n1)
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if [ "$status_code" = "200" ] || [ "$status_code" = "201" ]; then
            pass
        else
            fail "Expected 200 or 201, got $status_code"
        fi
    fi
}

# Health check APIs
test_health_apis() {
    log_info "=========================================="
    log_info "Testing Health Check APIs"
    log_info "=========================================="

    # Test health endpoint
    log_test "GET /health - Basic health check"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/health" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "200" ]; then
        pass
    else
        fail "Expected 200, got $status_code"
    fi

    # Test health detail endpoint
    log_test "GET /health/detail - Detailed health check"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/health/detail" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "200" ]; then
        pass
    else
        fail "Expected 200, got $status_code"
    fi
}

# Edge cases and error handling
test_error_cases() {
    log_info "=========================================="
    log_info "Testing Error Cases"
    log_info "=========================================="

    # Test 401 Unauthorized
    log_test "GET /sessions without auth - Should return 401"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/sessions" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "401" ]; then
        pass
    else
        fail "Expected 401, got $status_code"
    fi

    # Test 404 Not Found
    log_test "GET /nonexistent - Should return 404"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/nonexistent" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "404" ]; then
        pass
    else
        fail "Expected 404, got $status_code"
    fi

    # Test 422 Validation Error
    log_test "POST /auth/register with invalid data - Should return 422"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{}' 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "422" ]; then
        pass
    else
        fail "Expected 422, got $status_code"
    fi

    # Test 422 Validation Error for missing query
    log_test "POST /research/tasks without query - Should return 422"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/research/tasks" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d '{}' 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "422" ]; then
        pass
    else
        fail "Expected 422, got $status_code"
    fi

    # Test 403 Forbidden (insufficient permissions - for future admin features)
    log_test "GET /auth/users - Should return 403 or 404 (admin only)"
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/auth/users" \
        -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$status_code" = "403" ] || [ "$status_code" = "404" ]; then
        pass
    else
        fail "Expected 403 or 404, got $status_code"
    fi
}

# Main execution
main() {
    log_info "=========================================="
    log_info "DeepResearchWeb API Test Suite"
    log_info "=========================================="
    log_info "Base URL: $BASE_URL"
    log_info "Output Directory: $OUTPUT_DIR"
    log_info "Log File: $LOG_FILE"
    log_info "=========================================="

    # Check if server is running
    log_info "Checking if server is running..."
    if ! curl -s --connect-timeout 5 "$BASE_URL/api/v1/health" > /dev/null 2>&1; then
        log_error "Server is not reachable at $BASE_URL"
        log_error "Please start the server first with: docker-compose up -d"
        exit 1
    fi
    log_info "Server is running"

    # Run all tests
    test_health_apis
    test_auth_apis
    test_session_apis
    test_messages_apis
    test_chat_apis
    test_research_apis
    test_tools_apis
    test_skills_apis
    test_mcp_apis
    test_memory_apis
    test_error_cases

    # Summary
    log_info "=========================================="
    log_info "Test Summary"
    log_info "=========================================="
    log_info "Total Tests: $TOTAL_TESTS"
    log_info "Passed: ${GREEN}$PASSED_TESTS${NC}"
    log_info "Failed: ${RED}$FAILED_TESTS${NC}"
    log_info "Success Rate: $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%"
    log_info "=========================================="

    # Write summary to file
    cat > "$OUTPUT_DIR/test_summary.txt" << EOF
DeepResearchWeb API Test Summary
=================================
Date: $(date)
Base URL: $BASE_URL
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Success Rate: $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)%
Log File: $LOG_FILE
Output Directory: $OUTPUT_DIR
EOF

    if [ $FAILED_TESTS -eq 0 ]; then
        log_info "All tests passed!"
        exit 0
    else
        log_error "Some tests failed!"
        log_error "Check $OUTPUT_DIR for detailed response files"
        exit 1
    fi
}

# Run main
main "$@"
