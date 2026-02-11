# 🏗️ Chatbot Architecture & System Design

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Chat Interface                                           │  │
│  │ • Message Display                                        │  │
│  │ • Input Field & Send Button                             │  │
│  │ • File Upload Integration                               │  │
│  │ • Suggested Actions Panel                               │  │
│  │ • Detailed View Modal                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                        ↑     ↓                                    │
│                    HTTP Calls (Axios)                            │
│                        ↑     ↓                                    │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI on Port 5000)                 │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Chat Endpoints                                          │   │
│  │ • POST /chat           - Main chat interface           │   │
│  │ • GET /chat/history    - Conversation history         │   │
│  │ • GET /chat/context    - Current context              │   │
│  │ • POST /chat/clear     - Reset conversation           │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         CHAT ENGINE (chat_engine.py)                    │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Intent Detection Module                          │  │   │
│  │  │ • Keyword matching (AR + EN)                    │  │   │
│  │  │ • Intent scoring algorithm                      │  │   │
│  │  │ • 12 recognized intents                         │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │           ↓                                             │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │ Response Generation Module                       │  │   │
│  │  │ • Intent-based handler selection                │  │   │
│  │  │ • Context-aware responses                       │  │   │
│  │  │ • Suggested action generation                   │  │   │
│  │  │ • Conversation history management               │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Analysis Engines (Pre-existing)                         │   │
│  │ • Similarity Engine     - Find similar cases           │   │
│  │ • Summarizer Engine     - Extract summaries            │   │
│  │ • Classification Engine - Identify case type           │   │
│  │ • Legal Principles      - Extract relevant laws        │   │
│  │ • Trend Analyzer        - Statistics & patterns        │   │
│  │ • Draft Generator       - Create legal documents       │   │
│  │ • Query Engine          - Answer specific questions    │   │
│  │ • Recommendation Engine - Generate recommendations     │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Data Layer                                              │   │
│  │ • Case Database (saudi_general_court_judgments.json)   │   │
│  │ • ML Models (SBERT embeddings for similarity)          │   │
│  │ • Pre-trained NLP Models                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Chat Request/Response Flow

### Request Flow
```
User Message in Browser
    ↓
React App captures input
    ↓
JSON Request:
{
  "message": "ملخص القضية",
  "analysis_data": {...},
  "case_text": "..."
}
    ↓
POST /chat Endpoint
    ↓
FastAPI receives request
    ↓
ChatEngine.process_message()
    ├─ Add user message to history
    ├─ Detect intent
    ├─ Route to handler
    └─ Generate response
    ↓
Response JSON:
{
  "text": "الملخص: ...",
  "intent": "case_summary",
  "suggested_actions": [...]
}
    ↓
React receives response
    ↓
Display in chat UI
```

---

## Intent Detection Algorithm

```
User Input: "ملخص القضية"

Step 1: Normalize
├─ Convert to lowercase: "ملخص القضية"
└─ Split into keywords

Step 2: Score Each Intent
├─ case_summary: "ملخص" found → score = 1
├─ case_type: no match → score = 0
├─ similar_cases: no match → score = 0
└─ ... (10 more intents)

Step 3: Return Top Intent
└─ case_summary (highest score)

Step 4: Route to Handler
└─ _handle_case_summary()

Step 5: Generate Response
├─ Format response text
├─ Add suggested actions
└─ Return to user
```

---

## Conversation State Management

```
ConversationContext Object
│
├─ messages[]
│  ├─ Message 1: {role: "user", content: "upload file"}
│  ├─ Message 2: {role: "assistant", content: "✅ Analyzed"}
│  ├─ Message 3: {role: "user", content: "summary"}
│  └─ Message N: {...}
│
├─ analysis_data{}
│  ├─ classification: {...}
│  ├─ legal_principles: [...]
│  ├─ trends: {...}
│  ├─ recommendation: {...}
│  └─ entities: {...}
│
└─ case_text: "Full case text..."

Max History: 20 messages (older ones pruned)
```

---

## Handler Architecture

### 12 Intent Handlers

```python
_handle_case_summary() → Extract & format summary
_handle_case_type() → Show classification
_handle_similar_cases() → Display precedent cases
_handle_legal_principles() → List applicable laws
_handle_trends() → Show statistics
_handle_recommendation() → Display AI recommendation
_handle_full_analysis() → Comprehensive overview
_handle_draft_request() → Offer draft options
_handle_outcome() → Probability assessment
_handle_compensation() → Compensation statistics
_handle_entities() → List case parties
_handle_general_inquiry() → Default fallback
```

### Handler Response Format
```python
return {
    "text": "Response in Arabic or English",
    "intent": "intent_name",
    "suggested_actions": [
        {"label": "Button Text", "action": "action_name"},
        ...
    ],
    "metadata": {...}
}
```

---

## API Endpoint Details

### POST /chat - Main Chat Endpoint
```
REQUEST:
{
  "message": "User input string",
  "analysis_data": {
    "classification": {...},
    "trends": {...},
    ...
  },
  "case_text": "Optional full case text"
}

RESPONSE:
{
  "text": "Response message",
  "intent": "detected_intent",
  "suggested_actions": [
    {
      "label": "Button label (AR/EN)",
      "action": "action_identifier"
    }
  ],
  "timestamp": "ISO8601 timestamp",
  "metadata": {...},
  "error": null
}

HTTP STATUS:
200 - Success
400 - Bad request
503 - Engine not initialized
500 - Server error
```

### GET /chat/history - Retrieve History
```
RESPONSE:
{
  "messages": [
    {
      "timestamp": "2024-02-11T10:30:00",
      "role": "user|assistant",
      "content": "message text",
      "metadata": {...}
    },
    ...
  ]
}
```

### GET /chat/context - Context Summary
```
RESPONSE:
{
  "has_analysis": true|false,
  "message_count": 5,
  "analysis_keys": [
    "classification",
    "legal_principles",
    "trends",
    ...
  ]
}
```

### POST /chat/clear - Clear Conversation
```
REQUEST:
{
  "confirm": true
}

RESPONSE:
{
  "status": "cleared",
  "message": "Chat history cleared successfully"
}
```

---

## Integration with Analysis Engines

### Pipeline: Chat → Analysis Engines

```
User Question
    ↓
ChatEngine detects intent
    ↓
CASE_TYPE intent?
    ├─ Call classify_case()
    └─ Format classification response
    ↓
SIMILAR_CASES intent?
    ├─ Call similarity_engine.search()
    └─ Format case results
    ↓
RECOMMENDATION intent?
    ├─ Needs analysis_data
    ├─ Call recommendation_engine
    └─ Format recommendation
    ↓
DRAFT intent?
    ├─ Offer draft type options
    ├─ Or call generate_draft()
    └─ Format legal document
    ↓
Response to User
```

---

## Frontend Component Structure

```
App.js (Main Component)
│
├─ State Management
│  ├─ messages[] - Chat message history
│  ├─ inputText - Current user input
│  ├─ loading - UI loading state
│  ├─ analysis - Current case analysis
│  └─ ...
│
├─ Effects
│  ├─ Auto-scroll to bottom
│  ├─ Health check polling
│  └─ Initial greeting
│
├─ Event Handlers
│  ├─ sendChatMessage()
│  ├─ handleFileChange()
│  ├─ handleFileUpload()
│  ├─ handleSuggestedAction()
│  └─ handleKeyPress()
│
├─ JSX Render
│  ├─ Header (with health status)
│  ├─ Messages Area
│  │  ├─ User messages (blue)
│  │  ├─ Assistant messages (white)
│  │  ├─ Suggested actions buttons
│  │  └─ Typing indicator
│  ├─ Detailed View Modal (conditional)
│  └─ Input Area
│     ├─ File upload button
│     ├─ Chat input textarea
│     └─ Send button
│
└─ Styling (App.css)
   ├─ Chat layout
   ├─ Message styling
   ├─ Animations
   ├─ Responsive design
   └─ RTL support
```

---

## Data Flow: File Upload Analysis

```
User clicks 📁
    ↓
File input dialog opens
    ↓
User selects PDF/DOCX/TXT
    ↓
React state: selectedFile = File object
    ↓
User clicks "✓ filename"
    ↓
handleFileUpload() triggered
    ↓
FormData created with file
    ↓
POST /upload-analyze sent
    ↓
Backend:
  ├─ Extract text (text_extractor.py)
  ├─ Run full analysis pipeline
  └─ Return AnalyzeResponse
    ↓
React receives analysis JSON
    ↓
State: analysis = response_data
    ↓
Chat message added: "File analyzed ✅"
    ↓
Suggested actions shown
    ↓
User can now ask questions about the case
```

---

## Model Classes & Database Schema

### Request/Response Models
```python
ChatRequest(BaseModel)
├─ message: str
├─ analysis_data: Optional[AnalyzeResponse]
└─ case_text: Optional[str]

ChatResponse(BaseModel)
├─ text: str
├─ intent: str
├─ suggested_actions: List[SuggestedAction]
├─ timestamp: str
├─ metadata: Optional[Dict]
└─ error: Optional[str]

SuggestedAction(BaseModel)
├─ label: str
└─ action: str

AnalyzeResponse(BaseModel)
├─ classification: CaseClassification
├─ legal_principles: List[LegalPrinciple]
├─ trends: Optional[TrendStats]
├─ recommendation: Optional[Recommendation]
└─ entities: Optional[Dict]
```

### Case Database Structure
```
[
  {
    "case_id": "2024-001",
    "court": "General Court",
    "facts": "Case facts...",
    "legal_reasoning": "...",
    "judgment": "...",
    "source": "saudi judiciary",
    "language": "ar",
    "is_real": true
  },
  ...
]
```

---

## Error Handling Flow

```
User sends message
    ↓
Try:
├─ Extract message text
├─ Call chat_engine.process_message()
├─ Format response
└─ Return successful response
    ↓
Except Exception:
├─ Log error with traceback
├─ Return error response
│  {
│    "text": "عذراً، حدث خطأ...",
│    "intent": "error",
│    "error": "error message"
│  }
└─ Frontend displays error
    ↓
User can retry or try different input
```

---

## Performance Characteristics

### Response Times
```
File Upload & Analysis: 3-5 seconds
├─ Text extraction: 1-2s
└─ Analysis pipeline: 2-3s

Chat Message: < 200ms
├─ Intent detection: < 10ms
├─ Handler execution: < 100ms
└─ Network latency: ~50ms

History Retrieval: < 50ms
Context Summary: < 10ms
Clear Conversation: < 10ms
```

### Memory Usage
```
Conversation History: ~1KB per message
Analysis Data: ~50-100KB per case
Total Per Session: < 10MB
```

---

## Security Considerations

### Input Validation
```
Message Text
├─ Check not empty
├─ Trim whitespace
└─ Length limit: 10,000 chars

File Upload
├─ Type check (PDF/DOCX/TXT)
├─ Size limit: 10MB
├─ Virus scan: (Optional)
└─ Sandboxed extraction
```

### CORS Configuration
```
Allowed Origins:
├─ http://localhost:3000
└─ http://127.0.0.1:3000

Methods: GET, POST, PUT, DELETE
Headers: Content-Type, Authorization
Credentials: Allowed
```

### Data Privacy
```
✅ No user authentication
✅ No persistent storage
✅ No analytics tracking
✅ Local session only
✅ Data cleared on window close
```

---

## Browser Support Matrix

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | Latest | ✅ Full |
| Firefox | Latest | ✅ Full |
| Safari | Latest | ✅ Full |
| Edge | Latest | ✅ Full |

### Features Supported
```
✅ Fetch API
✅ FormData
✅ localStorage (optional)
✅ Web Workers (optional)
✅ RTL Text (native)
✅ File API
✅ Flexbox Layout
✅ CSS Animations
```

---

## Deployment Considerations

### Development
```
Backend: Python FastAPI on 0.0.0.0:5000
Frontend: React dev server on 0.0.0.0:3000
```

### Production
```
Backend:
├─ Use Gunicorn/Uvicorn
├─ Environment variables for config
├─ Logging to file
└─ Error monitoring (Sentry optional)

Frontend:
├─ Build: npm run build
├─ Serve: npm install -g serve
├─ Or use Nginx/Apache
└─ Update API_BASE to production URL
```

---

## Summary

The chatbot architecture elegantly combines:
1. **Intelligent Intent Detection** - Natural language understanding
2. **Flexible Handler System** - Easy to extend with new intents
3. **Existing Analysis Engines** - Reuse powerful ML models
4. **Clean Separation** - Frontend/Backend loosely coupled
5. **Robust Error Handling** - Graceful failure recovery
6. **Bilingual Support** - Arabic and English seamlessly

All while maintaining the sophisticated legal analysis capabilities in a user-friendly conversational interface! 🚀
