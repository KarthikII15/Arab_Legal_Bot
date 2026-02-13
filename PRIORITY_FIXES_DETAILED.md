# Priority Fixes - Detailed Implementation Guide

##  IMMEDIATE FIXES (1-2 hours)

### 1. Fix async/await in `/draft` endpoint - main.py (lines 255-260)

**Problem:**
The `/draft` endpoint has missing `await` calls for async functions, causing the code to return Promise objects instead of actual results.

**Current Code (BROKEN):**
```python
@app.post("/draft", response_model=DraftResponse)
async def generate_legal_draft_endpoint(request: DraftRequest):
    try:
        from draft_engine import generate_draft
        draft = generate_draft(  #  NOT awaited if it's async
            case_type=request.case_type,
            classification_confidence=request.classification_confidence,
            legal_principles=[p.dict() for p in request.legal_principles], 
            recommendation=request.recommendation.dict(),
            party_role=request.party_role,
        )
        # Returns incomplete data
        return draft
    except Exception as e:
        logger.error(f"Draft FAILED: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

**Fixed Code:**
```python
@app.post("/draft", response_model=DraftResponse)
async def generate_legal_draft_endpoint(request: DraftRequest):
    """
    Generate a legal draft (Claim/Defense) based on analysis data.
    """
    logger.info(f"Draft request for {request.case_type} ({request.party_role})")
    try:
        # Check if generate_draft is async
        draft = await generate_draft(
            case_type=request.case_type,
            classification_confidence=request.classification_confidence,
            legal_principles=[p.dict() for p in request.legal_principles], 
            recommendation=request.recommendation.dict(),
            party_role=request.party_role,
            party_name=request.party_name,
        ) if asyncio.iscoroutinefunction(generate_draft) else generate_draft(...)
        
        logger.info(f"Draft generated successfully for {request.case_type}")
        return draft
    except asyncio.TimeoutError:
        logger.error("Draft generation timed out")
        raise HTTPException(status_code=504, detail="Draft generation timed out")
    except Exception as e:
        logger.error(f"Draft FAILED: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate draft. Please check your input.")
```

**Implementation Steps:**
1. Open `backend/draft_engine.py`
2. Check if `generate_draft()` is defined as `async def`
3. If yes, add `await` when calling it in main.py
4. Add `import asyncio` at the top of main.py
5. Add timeout handling to prevent hanging requests

**Verification:**
```bash
# Test the endpoint
curl -X POST http://localhost:5000/draft \
  -H "Content-Type: application/json" \
  -d '{"case_type": "labor_dispute", "party_role": "employer", ...}'
# Should return draft object, not coroutine
```

---

### 2. Add Error Boundary to React - App.js (line 1)

**Problem:**
No error boundary exists, so one component crash crashes the entire app. Users see blank screen instead of helpful error message.

**Current Code (MISSING):**
```javascript
// App.js starts directly with imports, no error boundary
import React, { useState, useEffect, useRef } from 'react';
```

**Fixed Code:**
Add this before App component:
```javascript
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

// ===== ERROR BOUNDARY COMPONENT =====
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log to console for debugging
    console.error('ErrorBoundary caught:', error, errorInfo);
    
    // Update state to show error UI
    this.setState({
      error,
      errorInfo
    });

    // Optional: Send to error tracking service (e.g., Sentry)
    // logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#ffe6e6',
          color: '#cc0000',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          fontFamily: 'Arial, sans-serif'
        }}>
          <h1>️ Something Went Wrong</h1>
          <p>The application encountered an error. Please refresh the page to continue.</p>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{
              textAlign: 'left',
              backgroundColor: '#f5f5f5',
              padding: '10px',
              borderRadius: '5px',
              marginTop: '20px',
              maxWidth: '600px'
            }}>
              <summary>Error Details (Development Only)</summary>
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}

          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  // ... existing code ...
}

export default function AppWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
}
```

**Implementation Steps:**
1. Open `frontend/src/App.js`
2. Copy the `ErrorBoundary` class above (place before `function App()`)
3. Wrap the export at the bottom: `export default () => <ErrorBoundary><App /></ErrorBoundary>`
4. Test by throwing an error in a component to verify it's caught

**What it prevents:**
-  Entire app crash from single component error
-  Shows helpful error message instead of blank screen
-  Logs errors to console for debugging
-  Shows stack trace in development mode only
-  Allows user to refresh and recover

---

### 3. Fix setInterval Cleanup - App.js (lines 70-76)

**Problem:**
`setInterval` for health checks is never cleared, causing:
- Multiple intervals running after hot reload
- Memory leak from uncleaned intervals
- Multiple health checks firing simultaneously

**Current Code (BROKEN):**
```javascript
// Check health on mount
useEffect(() => {
  checkHealth();
  const interval = setInterval(checkHealth, 10000);
  //  NO CLEANUP - interval never cleared!
  //  Hot reload creates NEW intervals without clearing old ones
}, []);
```

**Fixed Code:**
```javascript
// Check health on mount and setup polling
useEffect(() => {
  checkHealth();
  
  const interval = setInterval(checkHealth, 10000);
  
  //  Cleanup function: Clear interval when component unmounts
  return () => {
    clearInterval(interval);
  };
}, []);

// Send greeting message only once
useEffect(() => {
  if (!greetingSent.current && messages.length === 0) {
    greetingSent.current = true;
    addAssistantMessage(
      "مرحباً، أنا مساعد تحليل القضايا القانونية الذكي. كيف يمكنني مساعدتك اليوم؟ " +
      "[Greeting message...]"
    );
  }
}, []);
```

**Alternative: Longer Interval + Better Practices:**
```javascript
// More efficient: Check health less frequently instead of every 10 seconds
useEffect(() => {
  checkHealth();
  
  // Check health every 30 seconds instead of 10
  const interval = setInterval(() => {
    if (document.visibilityState === 'visible') {
      // Only check if app is visible (save resources)
      checkHealth();
    }
  }, 30000);
  
  return () => clearInterval(interval);
}, []);

// Also handle visibility changes
useEffect(() => {
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      checkHealth(); // Check immediately when tab becomes visible
    }
  };

  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  };
}, []);
```

**Implementation Steps:**
1. Open `frontend/src/App.js` at lines 70-76
2. Add cleanup function `return () => { clearInterval(interval); }`
3. Test: Open DevTools, hot reload, and verify only ONE interval is active

**What it prevents:**
-  Memory leaks from uncleaned intervals
-  Multiple simultaneous health checks
-  CPU waste from redundant polling
-  Race conditions in health status

---

### 4. Change CORS to Environment Variable - main.py (lines 44-49)

**Problem:**
CORS origins are hardcoded, making it impossible to use in production without code changes. Credentials passed through code.

**Current Code (INSECURE):**
```python
# Allow CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  #  Hardcoded!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Fixed Code:**
First, create `.env` file in backend folder:
```bash
# backend/.env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
TIMEOUT=30
```

Then update main.py:
```python
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CORS configuration from environment
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Allow CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=not IS_PRODUCTION,  # Don't allow credentials in production
    allow_methods=["GET", "POST", "PUT", "DELETE"],  #  Restrict to needed methods
    allow_headers=["Content-Type", "Authorization"],  #  Restrict headers
)

logger.info(f"CORS enabled for: {CORS_ORIGINS}")
logger.info(f"Environment: {ENVIRONMENT}")
```

**Install python-dotenv:**
```bash
pip install python-dotenv
# Update requirements.txt
```

**For Production (example with railway, netlify, etc.):**
```bash
# Set environment variables in platform:
CORS_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
```

**Implementation Steps:**
1. Install: `pip install python-dotenv`
2. Create `backend/.env` file (from template above)
3. Add `import os` and `from dotenv import load_dotenv`
4. Update CORS middleware config
5. Add to `.gitignore`: `.env` (never commit secrets)
6. Create `.env.example` with template for team

**What it secures:**
-  No hardcoded origins in code
-  Different origins for dev/prod
-  Restricted HTTP methods (not `*`)
-  Restricted headers (not `*`)
-  Secure credential handling
-  Easy deployment to different environments

---

### 5. Add Request Timeout to Axios - App.js (line 210)

**Problem:**
Axios requests have no timeout, so if backend hangs, frontend freezes indefinitely. User sees infinite loading spinner.

**Current Code (BROKEN):**
```javascript
try {
  const response = await axios.post(`${API_BASE}/chat`, {
    message: userMessage,
    analysis_data: analysis,
    case_text: analysis ? "Case analyzed" : null
    //  NO TIMEOUT - waits forever if backend fails!
  });
```

**Fixed Code:**
First, add timeout config at top of App.js:
```javascript
// === AXIOS CONFIGURATION ===
axios.defaults.timeout = 30000; // 30 second global timeout

// Create axios instance with defaults
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - backend not responding');
      return Promise.reject(new Error('Request timeout. Server is not responding. Please try again.'));
    }
    return Promise.reject(error);
  }
);
```

Then update API calls:
```javascript
//  Update all axios.post calls
async function sendMessage(userMessage) {
  const msgId = `msg-${Date.now()}`;
  addUserMessage(userMessage, msgId);
  setLoading(true);

  try {
    const response = await apiClient.post('/chat', {
      message: userMessage,
      analysis_data: analysis,
      case_text: analysis ? "Case analyzed" : null
    });
    
    setHealthStatus("connected");
    const { text, citations, suggested_actions } = response.data;
    
    addAssistantMessage(text, citations, suggested_actions, msgId);
  } catch (error) {
    if (error.message.includes('timeout')) {
      addAssistantMessage(
        "️ Connection timeout. The server is not responding. Please check if backend is running and try again.",
        [], 
        []
      );
      setHealthStatus("timeout");
    } else {
      addAssistantMessage(
        ` Error: ${error.response?.data?.detail || error.message}`,
        [], 
        []
      );
      setHealthStatus("error");
    }
  } finally {
    setLoading(false);
  }
}
```

**Add Timeout Indicator:**
```javascript
// Add to UI to show timeout status
<div style={{
  marginTop: '10px',
  padding: '10px',
  backgroundColor: healthStatus === 'timeout' ? '#fff3cd' : 'transparent',
  color: '#856404',
  borderRadius: '4px'
}}>
  {healthStatus === 'timeout' && '️ Backend timeout - check if server is running'}
  {healthStatus === 'error' && ' Backend error'}
  {healthStatus === 'connected' && ' Backend connected'}
</div>
```

**Implementation Steps:**
1. Open `frontend/src/App.js`
2. Add axios config block at top (after imports)
3. Replace all `axios.post()` calls with `apiClient.post()`
4. Add timeout error handling in catch blocks
5. Update UI to show timeout status

**What it prevents:**
-  Infinite loading spinners
-  User frustration from hangs
-  Browser memory leaks
-  Clear error messages
-  Distinguishes timeout from other errors

---

##  URGENT FIXES (Hours 2-4)

### 1. Add `.env` File Support with `python-dotenv`

**Status:** Partially done above (CORS). Complete this for ALL secrets.

**What to add to `.env`:**
```bash
# backend/.env

# API Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30

# Database/Storage
DATABASE_URL=sqlite:///./case_analysis.db

# Model Configuration
MODEL_PATH=./models/similarity_model
BATCH_SIZE=32
MAX_SEQUENCE_LENGTH=512

# Feature Flags
ENABLE_CACHING=true
ENABLE_VECTOR_DB=false
USE_LOCAL_MODELS=true

# Backend Server
HOST=127.0.0.1
PORT=5000
RELOAD=true
```

**Update main.py to use all:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Server config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))
RELOAD = os.getenv("ENVIRONMENT") == "development"

# Model config
MODEL_PATH = os.getenv("MODEL_PATH", "./models/similarity_model")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

# Start server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
```

**Create `.env.example`:**
```bash
# Copy to .env and fill in your values
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**Add to `.gitignore`:**
```bash
# Don't commit environment secrets
.env
.env.local
.env.*.local
```

---

### 2. Remove Stack Trace Exposure in Error Responses

**Problem:**
When errors occur, full Python stack traces are sent to frontend, exposing internal code structure.

**Current Code (INSECURE):**
```python
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = chat_engine.process(request.message)
        return response
    except Exception as e:
        logger.error(f"Chat FAILED: {e}", exc_info=True)
        #  EXPOSES FULL TRACEBACK TO FRONTEND!
        raise HTTPException(status_code=500, detail=str(e))
```

**Fixed Code:**
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Create error handler middleware
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Catch all unhandled exceptions"""
    
    # Log full details server-side (for debugging)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Return safe error to client (no stack trace)
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Generic safe message for unexpected errors
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again or contact support.",
            "error_type": exc.__class__.__name__  # Only class name, not full stack
        }
    )

# Update all endpoints to use generic errors:
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = chat_engine.process(request.message)
        return response
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid input. Please check your message and try again."
        )
    except TimeoutError:
        logger.error("Chat processing timeout")
        raise HTTPException(
            status_code=504,
            detail="Request timeout. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        #  Returns safe message, logs full error server-side
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )
```

**Error Response Examples:**
```python
#  BEFORE (Exposes internals)
{
  "detail": "Traceback (most recent call last):\n  File 'main.py', line 205 in chat_endpoint\nKeyError: 'analysis_data'\n..."
}

#  AFTER (Safe for users)
{
  "detail": "Failed to process message. Please try again.",
  "error_type": "KeyError"  # Only the type, not the trace
}
```

**Implementation Steps:**
1. Add exception handler to main.py
2. Review all endpoints and remove `str(e)` from detail messages
3. Log full errors server-side
4. Test that frontend shows safe messages

---

### 3. Add localStorage Try-Catch Wrapper

**Problem:**
Direct `localStorage` calls can fail silently if storage is full or disabled (private mode, iOS Safari).

**Current Code (BROKEN):**
```javascript
//  No error handling
const [conversations, setConversations] = useState(() => {
  const saved = localStorage.getItem('conversations');
  return saved ? JSON.parse(saved) : [];
});

// Later in code...
localStorage.setItem('conversations', JSON.stringify(conversations));
```

**Fixed Code:**
Create utility file `frontend/src/utils/storage.js`:
```javascript
/**
 * Safe localStorage wrapper with error handling
 */

const STORAGE_KEY_PREFIX = 'arabicLegal_';

/**
 * Safely get item from localStorage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Value if key not found or error
 * @returns {any} Stored value or default
 */
export const getStorageItem = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(STORAGE_KEY_PREFIX + key);
    
    if (item === null) {
      return defaultValue;
    }
    
    return JSON.parse(item);
  } catch (error) {
    if (error instanceof SyntaxError) {
      console.warn(`Invalid JSON stored for key "${key}":`, error);
    } else if (error instanceof Error && error.name === 'QuotaExceededError') {
      console.error(`localStorage quota exceeded for key "${key}"`, error);
    } else {
      console.warn(`Could not access localStorage for key "${key}":`, error);
    }
    
    return defaultValue;
  }
};

/**
 * Safely set item in localStorage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 * @returns {boolean} True if successful, false otherwise
 */
export const setStorageItem = (key, value) => {
  try {
    localStorage.setItem(STORAGE_KEY_PREFIX + key, JSON.stringify(value));
    return true;
  } catch (error) {
    if (error instanceof Error && error.name === 'QuotaExceededError') {
      console.error(`localStorage quota exceeded. Cannot store "${key}". Try clearing old conversations.`);
      
      // Optional: Auto-cleanup oldest conversations
      try {
        cleanupOldConversations();
        localStorage.setItem(STORAGE_KEY_PREFIX + key, JSON.stringify(value));
        return true;
      } catch {
        return false;
      }
    } else {
      console.error(`Could not save to localStorage for key "${key}":`, error);
      return false;
    }
  }
};

/**
 * Safely remove item from localStorage
 * @param {string} key - Storage key
 * @returns {boolean} True if successful
 */
export const removeStorageItem = (key) => {
  try {
    localStorage.removeItem(STORAGE_KEY_PREFIX + key);
    return true;
  } catch (error) {
    console.error(`Could not remove from localStorage for key "${key}":`, error);
    return false;
  }
};

/**
 * Check if localStorage is available
 * @returns {boolean} True if localStorage is accessible
 */
export const isStorageAvailable = () => {
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
};

/**
 * Clean up old conversations to free space
 */
export const cleanupOldConversations = (keepCount = 10) => {
  try {
    const conversations = getStorageItem('conversations', []);
    
    if (conversations.length > keepCount) {
      // Sort by date and keep only newest
      const sorted = conversations
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, keepCount);
      
      setStorageItem('conversations', sorted);
      console.log(`Cleaned up old conversations. Kept ${keepCount} newest.`);
    }
  } catch (error) {
    console.error('Error cleaning up conversations:', error);
  }
};
```

**Update App.js to use wrapper:**
```javascript
import { getStorageItem, setStorageItem, isStorageAvailable } from './utils/storage';

function App() {
  // Check storage on mount
  useEffect(() => {
    if (!isStorageAvailable()) {
      console.warn('localStorage not available. Features depending on it may not work.');
      setShowStorageWarning(true);
    }
  }, []);

  // Use safe storage getters
  const [conversations, setConversations] = useState(() => {
    return getStorageItem('conversations', []);
  });

  const [fontSize, setFontSize] = useState(() => {
    return getStorageItem('fontSize', 'medium');
  });

  // Update saved conversations safely
  useEffect(() => {
    const success = setStorageItem('conversations', conversations);
    if (!success) {
      console.error('Failed to save conversations. They may not persist.');
    }
  }, [conversations]);

  // Save font size preference
  const handleFontSizeChange = (size) => {
    setFontSize(size);
    const success = setStorageItem('fontSize', size);
    if (!success) {
      console.warn('Could not save font size preference');
    }
  };

  return (
    // Show warning if storage unavailable
    {!isStorageAvailable() && (
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#fff3cd', 
        color: '#856404',
        marginBottom: '10px'
      }}>
        ️ Storage disabled (private mode or quota exceeded). Data may not persist.
      </div>
    )}
    // ... rest of component
  );
}
```

**Implementation Steps:**
1. Create `frontend/src/utils/storage.js` with code above
2. Update all `localStorage` calls in App.js to use wrapper
3. Add storage availability check on app load
4. Test in Private/Incognito mode

---

### 4. Implement Missing Backend Endpoints

**Missing Endpoints:**
1. `/chat/clear` - Clear current chat session
2. `/conversations/archive` - Archive a conversation

**Add to main.py:**
```python
from models import ClearChatRequest, ArchiveRequest, ConversationSummary

# ===== CLEAR CHAT ENDPOINT =====
@app.post("/chat/clear")
async def clear_chat_endpoint(request: ClearChatRequest):
    """
    Clear the current chat session.
    Optionally archive the conversation before clearing.
    """
    logger.info(f"Clear chat requested for conversation: {request.conversation_id}")
    
    try:
        # Optionally archive before clearing
        if request.archive_before_clear:
            if chat_engine.has_conversation(request.conversation_id):
                summary = chat_engine.get_conversation_summary(request.conversation_id)
                logger.info(f"Archived conversation {request.conversation_id}")
        
        # Clear the session
        chat_engine.clear_session(request.conversation_id)
        logger.info("Chat cleared successfully")
        
        return {
            "success": True,
            "message": "Chat cleared successfully",
            "archived": request.archive_before_clear
        }
    except Exception as e:
        logger.error(f"Clear chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to clear chat. Please try again."
        )


# ===== ARCHIVE CONVERSATION ENDPOINT =====
@app.post("/conversations/archive")
async def archive_conversation_endpoint(request: ArchiveRequest):
    """
    Archive a conversation for later reference.
    Stores metadata and summary without keeping full message history in memory.
    """
    logger.info(f"Archive request for conversation: {request.conversation_id}")
    
    try:
        # Get conversation summary
        conversation = chat_engine.get_conversation(request.conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Create archive entry
        archive_entry = {
            "id": request.conversation_id,
            "title": request.title or f"Conversation {request.conversation_id}",
            "archived_at": datetime.now().isoformat(),
            "message_count": len(conversation.get('messages', [])),
            "summary": chat_engine.generate_summary(conversation),
            "tags": request.tags or [],
            "case_type": conversation.get('case_type'),
        }
        
        # Save to archive storage
        with open("conversations_archive.json", "r") as f:
            archive = json.load(f)
        
        archive.append(archive_entry)
        
        with open("conversations_archive.json", "w") as f:
            json.dump(archive, f, indent=2)
        
        # Remove from active conversations
        chat_engine.delete_conversation(request.conversation_id)
        
        logger.info(f"Archived conversation {request.conversation_id}")
        
        return {
            "success": True,
            "message": "Conversation archived successfully",
            "archive_id": request.conversation_id
        }
    except FileNotFoundError:
        logger.error("Archive file not found, creating new archive")
        with open("conversations_archive.json", "w") as f:
            json.dump([{
                "id": request.conversation_id,
                "title": request.title,
                "archived_at": datetime.now().isoformat(),
                "message_count": 0,
                "summary": "",
                "tags": request.tags or [],
            }], f, indent=2)
        return {
            "success": True,
            "message": "Conversation archived successfully"
        }
    except Exception as e:
        logger.error(f"Archive failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to archive conversation. Please try again."
        )


# ===== GET ARCHIVED CONVERSATIONS =====
@app.get("/conversations/archived")
async def get_archived_conversations():
    """
    Retrieve list of archived conversations.
    """
    try:
        with open("conversations_archive.json", "r") as f:
            archive = json.load(f)
        
        return {
            "archived": archive,
            "count": len(archive)
        }
    except FileNotFoundError:
        return {"archived": [], "count": 0}
    except Exception as e:
        logger.error(f"Failed to retrieve archive: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve archived conversations"
        )
```

**Add models to backend/models.py:**
```python
from typing import Optional, List
from pydantic import BaseModel

class ClearChatRequest(BaseModel):
    conversation_id: str
    archive_before_clear: bool = False

class ArchiveRequest(BaseModel):
    conversation_id: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None

class ConversationSummary(BaseModel):
    id: str
    title: str
    message_count: int
    summary: str
    archived_at: str
    tags: List[str] = []
```

**Update frontend to use endpoints:**
```javascript
// In App.js
const clearChat = async () => {
  try {
    await apiClient.post('/chat/clear', {
      conversation_id: currentConversationId,
      archive_before_clear: false
    });
    
    setMessages([]);
    setAnalysis(null);
    greetingSent.current = false;
    setCurrentConversationId(null);
    
    addAssistantMessage("Chat cleared. How can I help you with a new case?");
  } catch (error) {
    console.error('Failed to clear chat:', error);
  }
};

const archiveConversation = async (conversationId) => {
  try {
    const response = await apiClient.post('/conversations/archive', {
      conversation_id: conversationId,
      title: `Case Analysis - ${new Date().toLocaleDateString()}`,
      tags: ['completed', 'archived']
    });
    
    setConversations(prev => 
      prev.filter(conv => conv.id !== conversationId)
    );
    
    console.log('Conversation archived:', response.data);
  } catch (error) {
    console.error('Failed to archive conversation:', error);
  }
};
```

---

### 5. Pin Dependency Versions in requirements.txt + package-lock.json

**Problem:**
Unpinned versions cause "works on my machine" bugs when dependencies update.

**Current requirements.txt (FLEXIBLE):**
```bash
fastapi
uvicorn
torch
transformers
```

**Fixed requirements.txt (PINNED):**
```bash
# Backend Requirements - Pinned Versions
# Generated: 2025-02-13

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# ML/NLP
torch==2.1.2
transformers==4.35.2
sentence-transformers==2.2.2
numpy==1.24.3
scikit-learn==1.3.2

# Text Processing
pdfplumber==0.10.3
python-docx==0.8.11

# Database/Storage
sqlalchemy==2.0.23

# Configuration
python-dotenv==1.0.0

# Async
aiofiles==23.2.1

# Logging
python-json-logger==2.0.7

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.12.1
flake8==6.1.0
```

**Generate pinned version:**
```bash
# Freeze current working environment
pip freeze > backend/requirements.txt

# Or use pip-tools for better management
pip install pip-tools
pip-compile backend/requirements.in  # Creates requirements.txt with hashes
```

**For frontend package-lock.json:**

The `package-lock.json` is automatically generated when you run `npm install`. To enforce pinned versions:

```bash
# Delete old node_modules and lock
rm -rf frontend/node_modules
rm frontend/package-lock.json

# Reinstall with exact versions
npm install

# Now package-lock.json has exact pinned versions
# Commit both package.json and package-lock.json
git add frontend/package-lock.json
git commit -m "Pin frontend dependencies"
```

**Using package-lock in CI/CD:**
```bash
# In GitHub Actions or Docker
npm ci  # Uses exact versions from package-lock.json
# NOT npm install (which might update packages)
```

**Implementation Steps:**
1. Run `pip freeze > backend/requirements.txt`
2. Review and remove development packages
3. Ensure compatibility (test thoroughly)
4. Commit both requirements.txt and package-lock.json
5. Use `npm ci` in CI/CD pipelines

---

##  IMPORTANT FIXES (Day 1)

### 1. Add Rate Limiting Middleware

**Problem:**
No rate limiting allows:
- DoS attacks (many requests)
- Brute force (API key guessing)
- Resource exhaustion

**Add to main.py:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Use Redis for distributed: redis://localhost:6379
)

# Add to FastAPI
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.post("/chat")
@limiter.limit("10/minute")  # 10 requests per minute per client
async def chat_endpoint(request: ChatRequest, request_obj = Request):
    # ... existing code ...
    pass

@app.post("/analyze")
@limiter.limit("5/minute")  # Stricter for heavy operations
async def analyze_endpoint(request: AnalyzeRequest, request_obj = Request):
    # ... existing code ...
    pass

@app.post("/upload")
@limiter.limit("2/minute")  # Very restricted for file uploads
async def upload_endpoint(file: UploadFile, request_obj = Request):
    # ... existing code ...
    pass

# Health check - no limit
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Install dependency:**
```bash
pip install slowapi
# For distributed: pip install redis
```

**Production with Redis:**
```python
# For scaling across multiple servers
from slowapi.stores import RedisStore

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"],
)
```

**What it prevents:**
-  API abuse
-  DoS attacks
-  Brute force attempts
-  Resource exhaustion
-  Fair resource allocation

---

### 2. Refactor Global State to Dependency Injection

**Problem:**
Global variables make testing hard and create tight coupling.

**Current Code (PROBLEMATIC):**
```python
# Main.py - global variables
similarity_engine = None
summarizer_engine = None
chat_engine = None
all_cases_global = []

@app.on_event("startup")
async def startup():
    global similarity_engine, chat_engine, all_cases_global
    similarity_engine = SimilarityEngine()
    chat_engine = ChatEngine()
    all_cases_global = load_cases()
```

**Fixed Code - Use Dependency Injection:**
```python
from fastapi import Depends

# Services module (backend/services.py)
class Services:
    def __init__(self):
        self.similarity_engine = None
        self.summarizer_engine = None
        self.chat_engine = None
        self.cases = None
    
    async def initialize(self):
        """Initialize all services"""
        self.similarity_engine = SimilarityEngine()
        self.summarizer_engine = SummarizerEngine()
        self.chat_engine = ChatEngine()
        self.cases = load_cases()
        logger.info("Services initialized")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        if self.chat_engine:
            await self.chat_engine.cleanup()
        logger.info("Services cleaned up")

# Global services instance
services = Services()

# Dependency function
async def get_services() -> Services:
    return services

# Update main.py
@app.on_event("startup")
async def startup():
    await services.initialize()

@app.on_event("shutdown")
async def shutdown():
    await services.shutdown()

# Use in endpoints
@app.post("/analyze")
async def analyze_endpoint(
    request: AnalyzeRequest,
    services_: Services = Depends(get_services)
):
    """
    Analyze a case using injected services
    """
    try:
        similar_cases = services_.similarity_engine.find_similar(
            case_text=request.case_text,
            top_k=5
        )
        
        classification = classify_case(request.case_text)
        
        summary = services_.summarizer_engine.summarize(request.case_text)
        
        return {
            "classification": classification,
            "similar_cases": similar_cases,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
```

**Benefits:**
-  Easier testing (inject mock services)
-  Loose coupling
-  Clear dependencies
-  Better resource management
-  Easier to debug

---

### 3. Add CSRF Protection

**Problem:**
Without CSRF protection, malicious sites can make requests on behalf of users.

**Add CSRF middleware:**
```python
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    autouse: bool = True

# Configure CSRF
@CsrfProtect.load_config
def load_config():
    return CsrfSettings()

# Create instance
csrf_protect = CsrfProtect()

# Add to app
csrf_protect.init_app(app)

# Get CSRF token endpoint
@app.get("/csrf-token")
def get_csrf_token(request: Request, csrf_protect: CsrfProtect = Depends()):
    """Endpoint to get CSRF token for frontend"""
    return {"csrf_token": csrf_protect.generate_csrf(request=request)}

# Protect endpoints
@app.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    csrf_protect: CsrfProtect = Depends()
):
    """Protected endpoint"""
    # csrf_protect validates automatically
    # ... code ...
    pass
```

**Update frontend:**
```javascript
// Get CSRF token on app load
useEffect(() => {
  const getCsrfToken = async () => {
    try {
      const response = await apiClient.get('/csrf-token');
      // Store token
      sessionStorage.setItem('csrf_token', response.data.csrf_token);
    } catch (error) {
      console.error('Failed to get CSRF token:', error);
    }
  };
  
  getCsrfToken();
}, []);

// Add token to all requests
const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('csrf_token');
  if (token) {
    config.headers['X-CSRF-Token'] = token;
  }
  return config;
});
```

---

### 4. Implement File Content Validation (Magic Bytes)

**Problem:**
Files aren't validated before processing. User uploads `.exe` as `.pdf` or malicious files.

**Add file validation:**
```python
import magic  # pip install python-magic-bin (Windows) or python-magic (Linux)
from pathlib import Path

# Allowed file types with magic bytes
ALLOWED_MIMETYPES = {
    'application/pdf': [b'%PDF'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [b'PK\x03\x04'],
    'text/plain': [],  # No magic bytes for plain text
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def validate_upload_file(file: UploadFile) -> bool:
    """Validate uploaded file by magic bytes"""
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    # Check magic bytes
    detected_mime = magic.from_buffer(file_content, mime=True)
    
    if detected_mime not in ALLOWED_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Got: {detected_mime}"
        )
    
    # For PDF, verify magic bytes more strictly
    if detected_mime == 'application/pdf':
        if not file_content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="Invalid PDF file")
    
    return True

# Use in upload endpoint
@app.post("/upload")
async def upload_endpoint(file: UploadFile):
    """Upload and validate case document"""
    try:
        # Validate file
        await validate_upload_file(file)
        
        # Process file safely
        text = extract_text(file)
        
        return {
            "filename": file.filename,
            "size": len(await file.read()),
            "extracted_text": text
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
```

**Install magic library:**
```bash
# Windows
pip install python-magic-bin

# Linux
pip install python-magic
```

---

### 5. Fix API Response Field Mismatches

**Problem:**
Frontend expects fields that backend doesn't return, or returns extra fields that frontend doesn't expect.

**Add response validation:**
```python
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

# Define strict response models
class ChatResponseMessage(BaseModel):
    """Validated chat response structure"""
    id: str
    text: str
    citations: list[str] = Field(default_factory=list)
    suggested_actions: list[dict] = Field(default_factory=list)
    user_translation: Optional[str] = None
    assistant_translation: Optional[str] = None
    intent: Optional[str] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "text": "Your message response",
                "citations": ["Case 1", "Case 2"],
                "suggested_actions": [
                    {"label": "View Case", "action": "view_case"}
                ],
                "intent": "ask_similar_cases",
                "timestamp": "2025-02-13T10:30:00Z"
            }
        }

class AnalysisResponse(BaseModel):
    """Validated analysis response"""
    classification: dict
    confidence: float
    legal_principles: list[dict]
    similar_cases: list[dict]
    recommendations: list[str]
    summary: str
    
    class Config:
        # Forbid extra fields to catch mismatches
        extra = "forbid"

# Update endpoints
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    """Analysis with validated response"""
    try:
        result = {
            "classification": {...},
            "confidence": 0.95,
            "legal_principles": [...],
            "similar_cases": [...],
            "recommendations": [...],
            "summary": "..."
        }
        # Pydantic validates all fields are present
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/chat", response_model=ChatResponseMessage)
async def chat_endpoint(request: ChatRequest):
    """Chat with strict response validation"""
    try:
        response_data = chat_engine.process(request.message)
        
        # This will fail if required fields are missing
        response = ChatResponseMessage(
            id=response_data.get("id", f"msg-{id(response_data)}"),
            text=response_data["text"],
            citations=response_data.get("citations", []),
            suggested_actions=response_data.get("suggested_actions", []),
            timestamp=datetime.now().isoformat()
        )
        
        return response
    except ValueError as e:
        logger.error(f"Response validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Invalid response format from backend"
        )
```

**Add validation in frontend:**
```javascript
// Validate response before using
const validateChatResponse = (data) => {
  const required = ['id', 'text'];
  const missing = required.filter(field => !(field in data));
  
  if (missing.length > 0) {
    console.error('Invalid response missing:', missing);
    throw new Error(`Invalid response: missing ${missing.join(', ')}`);
  }
  
  return {
    id: data.id,
    text: data.text,
    citations: data.citations || [],
    suggested_actions: data.suggested_actions || [],
    timestamp: data.timestamp || new Date().toISOString()
  };
};

// Use in API calls
try {
  const response = await apiClient.post('/chat', request);
  const validated = validateChatResponse(response.data);
  // Use validated response
} catch (error) {
  console.error('Response validation failed:', error);
}
```

---

##  SOON FIXES (Day 2-3)

### 1. Add Request Deduplication & Debouncing

**Problem:**
User rapidly clicks button → multiple identical requests sent → wasted resources → inconsistent state.

**Add debouncing to frontend:**
```javascript
// frontend/src/utils/debounce.js
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Use in App.js
const [lastSearchId, setLastSearchId] = useState(null);

const debouncedSearch = useCallback(
  debounce(async (searchQuery) => {
    const requestId = Date.now();
    setLastSearchId(requestId);
    
    try {
      const response = await apiClient.post('/search', {
        query: searchQuery,
        request_id: requestId
      });
      
      // Only process if this is still the latest request
      if (requestId === lastSearchId) {
        setSearchResults(response.data.results);
      }
    } catch (error) {
      console.error('Search failed:', error);
    }
  }, 500),  // Wait 500ms after typing stops
  [lastSearchId]
);
```

**Add request deduplication to backend:**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class RequestCache:
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, request_id: str):
        if request_id in self.cache:
            data, timestamp = self.cache[request_id]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return data
            else:
                del self.cache[request_id]
        return None
    
    def set(self, request_id: str, data):
        self.cache[request_id] = (data, datetime.now())
    
    def cleanup(self):
        """Remove expired entries"""
        now = datetime.now()
        expired = [k for k, (_, ts) in self.cache.items()
                   if now - ts > timedelta(seconds=self.ttl)]
        for k in expired:
            del self.cache[k]

# Global cache instance
request_cache = RequestCache(ttl_seconds=60)

@app.post("/search")
async def search_endpoint(query: str, request_id: Optional[str] = None):
    """Search with deduplication"""
    
    # Check if we already processed this request
    if request_id:
        cached = request_cache.get(request_id)
        if cached:
            logger.info(f"Returning cached result for request {request_id}")
            return cached
    
    try:
        # Process search
        results = search_index(query)
        
        # Cache result
        response = {"results": results, "request_id": request_id}
        if request_id:
            request_cache.set(request_id, response)
        
        return response
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
```

---

### 2. Add Markdown Sanitization (rehype-sanitize)

**Problem:**
User or API returns HTML/Markdown with scripts → XSS vulnerability.

**Install:**
```bash
npm install rehype-sanitize rehype-react remark-parse remark-rehype
```

**Create sanitization component:**
```javascript
// frontend/src/components/SafeMarkdown.js
import React from 'react';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import rehypeSanitize from 'rehype-sanitize';
import rehypeReact from 'rehype-react';

export const SafeMarkdown = ({ content }) => {
  const processMarkdown = React.useMemo(() => {
    const processor = unified()
      .use(remarkParse)
      .use(remarkRehype)
      .use(rehypeSanitize)  //  Removes dangerous HTML
      .use(rehypeReact, {
        components: {
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noopener noreferrer" />
          ),
          // Add more custom component mappings as needed
        }
      });
    
    return processor;
  }, []);

  try {
    const result = processMarkdown.processSync(content);
    return result.result;
  } catch (error) {
    console.error('Markdown processing error:', error);
    return <div>Unable to render content</div>;
  }
};

// Usage in App.js
<SafeMarkdown content={message.text} />
```

---

### 3. Implement List Virtualization for Conversations

**Problem:**
With hundreds of conversations, rendering all 300+ message items causes lag.

**Install:**
```bash
npm install react-window react-infinite-scroll
```

**Create virtualized list:**
```javascript
// frontend/src/components/VirtualizedConversations.js
import React from 'react';
import { FixedSizeList as List } from 'react-window';
import InfiniteScroll from 'react-infinite-scroll-component';

export const VirtualizedConversationList = ({ 
  conversations, 
  onSelectConversation,
  loadMoreConversations 
}) => {
  const ROW_HEIGHT = 80;  // px per conversation item
  
  const Row = ({ index, style }) => (
    <div style={style} onClick={() => onSelectConversation(conversations[index])}>
      <ConversationItem conv={conversations[index]} />
    </div>
  );

  return (
    <InfiniteScroll
      dataLength={conversations.length}
      next={loadMoreConversations}
      hasMore={true}
      height="600px"
      scrollableTarget="conversations-list"
    >
      <List
        height={600}
        itemCount={conversations.length}
        itemSize={ROW_HEIGHT}
        width="100%"
      >
        {Row}
      </List>
    </InfiniteScroll>
  );
};
```

**Benefits:**
-  Only renders visible items
-  Smooth scrolling
-  Handles 1000+ items easily
-  Lazy loads as user scrolls

---

### 4. Add ARIA Labels for Accessibility

**Problem:**
Screen reader users can't navigate app. Buttons have no labels.

**Add ARIA attributes:**
```javascript
// frontend/src/App.js - Update components

<button 
  aria-label="Clear current chat and start new conversation"
  onClick={clearChat}
  title="Clear chat"
>
  ️ Clear
</button>

<div 
  role="region"
  aria-live="polite"
  aria-label="Chat messages"
  id="messages-area"
>
  {messages.map(msg => (
    <Message key={msg.id} message={msg} />
  ))}
</div>

<input
  type="text"
  aria-label="Type your legal question in English or Arabic"
  placeholder="Ask about the case..."
  value={input}
  onChange={(e) => setInput(e.target.value)}
/>

<select
  aria-label="Case type classification"
  value={caseType}
  onChange={(e) => setCaseType(e.target.value)}
>
  <option value="">Select case type</option>
  <option value="labor">Labor Dispute</option>
  // ...
</select>
```

**Create accessibility guide:**
```txt
# Keyboard Navigation

- Tab: Navigate between form elements
- Shift+Tab: Navigate backwards
- Enter: Submit forms
- Escape: Close modals
- Arrow keys: Move through lists

# Screen Reader Support

- All buttons have aria-label
- Form inputs have associated labels
- Live regions announce new messages
- Status indicators announce connection state
```

---

### 5. Create Comprehensive `.env.example` Documentation

**Create `.env.example` file:**
```bash
# ============================================
# ARABIC AI LEGAL CASE ANALYSIS ASSISTANT
# Configuration Template
# ============================================

# Copy this file to .env and fill in your values
# NEVER commit .env to version control

# ===== SERVER CONFIGURATION =====

# Server host and port
HOST=127.0.0.1
PORT=5000

# Environment: development, staging, production
ENVIRONMENT=development

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Enable hot reload (development only)
RELOAD=true

# ===== CORS CONFIGURATION =====

# Allowed origins for frontend (comma-separated)
# For development: http://localhost:3000,http://127.0.0.1:3000
# For production: https://yourdomain.com
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Allow credentials in cross-origin requests
# Set to false in production
CORS_ALLOW_CREDENTIALS=true

# ===== API CONFIGURATION =====

# Request timeout in seconds
REQUEST_TIMEOUT=30

# Rate limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600  # seconds per window

# ===== DATABASE CONFIGURATION =====

# SQLite (local development)
DATABASE_URL=sqlite:///./case_analysis.db

# PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost/dbname

# ===== MODEL CONFIGURATION =====

# Path to similarity model
MODEL_PATH=./models/similarity_model

# Batch size for processing
BATCH_SIZE=32

# Maximum sequence length for models
MAX_SEQUENCE_LENGTH=512

# Device for model inference: cpu, cuda, mps
DEVICE=cpu

# ===== FEATURE FLAGS =====

# Enable/disable caching
ENABLE_CACHING=true

# Use local models vs. API services
USE_LOCAL_MODELS=true

# Enable vector database
ENABLE_VECTOR_DB=false

# ===== FILE UPLOAD CONFIGURATION =====

# Maximum file size in bytes (10 MB default)
MAX_FILE_SIZE=10485760

# Allowed file extensions
ALLOWED_FILE_TYPES=.pdf,.doc,.docx,.txt

# Upload directory
UPLOAD_DIR=./uploads

# ===== EXTERNAL SERVICES (if needed) =====

# OpenAI API (if using OpenAI instead of local LLM)
# OPENAI_API_KEY=sk-...

# Sentry error tracking (optional)
# SENTRY_DSN=https://...@sentry.io/...

# Redis for caching (optional)
# REDIS_URL=redis://localhost:6379/0

# ===== SECURITY =====

# Secret key for JWT tokens (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here-generate-new-one

# JWT token expiry in hours
JWT_EXPIRY=24

# CSRF secret key
CSRF_SECRET=your-csrf-secret-here

# ===== LOGGING =====

# Send logs to external service
# LOG_SERVICE_URL=https://logs.example.com
# LOG_SERVICE_KEY=key-here

# ===== DEVELOPMENT HELPERS =====

# Enable debug mode (shows full stack traces)
DEBUG=false

# Enable API documentation
ENABLE_DOCS=true

# Documentation URL
DOCS_URL=/api/docs
```

**Create setup guide README:**
```markdown
# Environment Configuration Guide

## Development Setup

1. **Copy template:**
   \`\`\`bash
   cp .env.example .env
   \`\`\`

2. **Edit `.env` with your values:**
   - Keep CORS_ORIGINS as default for local development
   - Set ENVIRONMENT=development
   - Leave MODEL_PATH as is (points to bundled models)

3. **Verify configuration:**
   \`\`\`bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('CORS_ORIGINS'))"
   \`\`\`

## Production Deployment

1. **Use strong SECRET_KEY:**
   \`\`\`bash
   openssl rand -hex 32
   \`\`\`

2. **Update for your domain:**
   \`\`\`
   CORS_ORIGINS=https://yourdomain.com
   ENVIRONMENT=production
   DEBUG=false
   \`\`\`

3. **Use PostgreSQL for database:**
   \`\`\`
   DATABASE_URL=postgresql://user:password@host/database
   \`\`\`

4. **Enable Redis caching:**
   \`\`\`
   REDIS_URL=redis://localhost:6379/0
   ENABLE_CACHING=true
   \`\`\`

## Common Issues

**"ModuleNotFoundError: No module named 'dotenv'"**
- Solution: \`pip install python-dotenv\`

**"CORS errors even with correct settings"**
- Clear browser cache (Ctrl+Shift+Delete)
- Check CORS_ORIGINS value matches frontend URL exactly

**"Model not found"**
- Ensure MODEL_PATH points to correct directory
- Run: \`python backend/download_models.py\`
```

---

## Prioritization Matrix

| Fix | Time | Impact | Difficulty | Start |
|-----|------|--------|-----------|-------|
| Async/await | 0.5h |  High |  Easy | Now |
| Error boundary | 0.5h |  High |  Easy | Now |
| setInterval cleanup | 0.5h |  Medium |  Easy | Now |
| CORS to env | 0.5h |  Medium |  Easy | Now |
| Axios timeout | 0.5h |  Medium |  Easy | Now |
| .env support | 1h |  High |  Medium | Hour 2 |
| Error responses | 1h |  Medium |  Medium | Hour 2 |
| Storage wrapper | 1.5h |  Medium |  Medium | Hour 2 |
| Missing endpoints | 2h |  Medium |  Hard | Hour 3 |
| Pin versions | 0.5h |  Medium |  Easy | Hour 4 |
| Rate limiting | 1h |  Medium |  Medium | Day 1 |
| Dependency injection | 2h |  Medium |  Hard | Day 1 |
| CSRF protection | 1.5h |  Medium |  Medium | Day 1 |
| File validation | 1h |  High |  Medium | Day 1 |
| Response validation | 1.5h |  Medium |  Medium | Day 1 |

---

## Testing Checklist

After each fix, verify:
- [ ] No console errors
- [ ] Backend logs show expected messages
- [ ] No memory leaks (Chrome DevTools → Performance)
- [ ] Response times acceptable
- [ ] Frontend handles timeout gracefully
- [ ] New code follows project style

---

## Next Steps

1. **Week 1**: Implement all IMMEDIATE fixes ( ~3 hours)
2. **Week 1-2**: Implement URGENT fixes ( ~6 hours)  
3. **Week 2**: Implement IMPORTANT fixes ( ~8 hours)
4. **Week 3**: Implement SOON fixes ( ~4 hours)
5. **Ongoing**: Add comprehensive testing and monitoring
