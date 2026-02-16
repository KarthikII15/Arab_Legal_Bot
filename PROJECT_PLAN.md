# Phase-Wise Project Resolution Plan

## Phase 1: Core Functionality & Stability (Week 1)
**Goal:** Ensure the application is stable, data is persistent, and critical bugs are resolved.

### Step 1: Fix Chat Persistence (Backend)
- [x] **Migrate from LocalStorage to JSON/SQLite Backend**:
    - Build a simple `JSON` or `SQLite` based persistence layer in `chat_engine.py`.
    - Create a new endpoint `POST /chat/save` and `GET /chat/load` to handle full conversation objects.
    - **Why**: Fixes the 5MB localStorage quota limit and prevents data loss.

### Step 2: Fix Frontend Race Conditions
- [x] **Refactor `App.js` State Management**:
    - Remove `localStorage` reliance for conversation list.
    - Implement `useEffect` to fetch conversation list from `GET /conversations` on mount.
    - Update `handleNewChat` and `sendChatMessage` to use proper state setter patterns (functional updates) to avoid race conditions.
    - Ensure `currentConversationId` state updates are atomic and propagate correctly to the save logic.
    - **Why**: Prevents "new chats not appearing" and "history not refreshing" bugs.

### Step 3: Implement Global Error Boundaries
- [x] **Add Global Error Handling**:
    - Wrap the main `App` component in an logic `ErrorBoundary` component.
    - Create a user-friendly "Something went wrong" fallback UI.
    - **Why**: Prevents white-screen-of-death when React errors occur.

---

## Phase 2: Intelligence & Accuracy (Week 2)
**Goal:** Improve the quality of legal analysis and fix hallucinated statistics.

### Step 4: Upgrade Classification Engine
- [x] **Implement Embedding-Based Classification**:
    - Replace the naive keyword counter in `classification_engine.py`.
    - Use `SimilarityEngine` to compare the input text against a set of "anchor cases" (Golden Set) for each category.
    - **Why**: Fixes the issue where every case is labeled "Labor Dispute" just because it contains the word "Contract".

### Step 5: Fix Hallucinated Statistics
- [x] **Enforce Statistical Significance**:
    - Update `trend_analyzer.py` to check `sample_size`.
    - If `sample_size < 5`, return "Insufficient Data" instead of a 100% win rate.
    - Filter out the input case itself from the similarity search results to avoid self-referencing bias.

### Step 6: Refine Entity & Document Type Detection
- [x] **Improve `doc_type` Logic**:
    - Prioritize "Judgment", "Ruling", "Operative Part" keywords over "Claim" keywords in `entity_extractor.py`.
    - If a Judgment is detected, suppress "Draft Claim" recommendations (force "Enforcement" or "Appeal" instead).

---

## Phase 3: UX & Localization Polish (Week 3)
**Goal:** Ensure a professional, bug-free user experience for Arabic users.

### Step 7: Fix "[object File]" Display Issue
- [x] **Create `FileAttachment` Component**:
    - A visual component (card/chip) to represent uploaded files in the chat.
- [x] **Update `Message.js`**:
    - Render `FileAttachment` if `message.fileData` is present.
- [x] **Fix `App.js`**:
    - Ensure `sendChatMessage` handles `File` objects correctly (extract name/size) instead of stringifying them to `[object File]`.

### Step 8: Fix Arabic PDF Extraction
- [x] **Enhance Text Extraction**:
    - Update `backend/utils.py` (or `text_extractor.py`) to use `pdfplumber` for better Arabic text extraction (or improve `pypdf` usage).
    - Detect pure image PDFs and flag them (or integrate Tesseract OCR if feasible).

### Step 9: UI Polish (RTL Support)
- [x] **Audit CSS for RTL**:
    - Ensure all chat bubbles, inputs, and sidebars have `dir="rtl"` or proper Flexbox direction.
    - Verify that mixed Arabic/English text renders correctly (e.g., phone numbers, dates).

---

## Phase 4: Production Readiness (Future)
- [ ] **Database Migration**: Move to PostgreSQL.
- [ ] **Authentication**: Re-enable JWT if required.
- [ ] **Advanced OCR**: Integrate Google Vision API or specialized Arabic OCR.
