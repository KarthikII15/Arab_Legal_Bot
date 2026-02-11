# 🧪 Comprehensive Test Cases for Arabic AI Legal Chat

Test the chatbot to verify it returns **different responses** for different inputs and handles all workflows correctly.

---

## Part 1: Intent Detection Tests (Different Responses)

### Test 1.1: Greeting Intent
**Test Input**: `مرحبا` (or `Hello`, `Hi`)  
**Expected Response**: Welcome message with services list and emojis  
**Expected Intent**: `greeting`  
**Success Criteria**:
- ✅ Response contains "مرحباً بك" or "Welcome"
- ✅ Lists available services (6 items)
- ✅ Response is 200+ characters (not a short message)
- ✅ Suggested actions appear below

**Test Steps**:
```
1. Type "مرحبا" in chat input
2. Press Enter
3. Observe response and intent in browser logs (F12)
```

---

### Test 1.2: Services Inquiry Intent
**Test Input**: `ما الخدمات` (or `What services`, `Services`, `خدمات`)  
**Expected Response**: Detailed breakdown of available services (with/without upload)  
**Expected Intent**: `general_inquiry`  
**Success Criteria**:
- ✅ Response mentions both "without upload" and "with upload" sections
- ✅ DIFFERENT from greeting response
- ✅ Contains bullet points (•) with features

**Test Steps**:
```
1. Type "ما الخدمات" in chat input
2. Press Enter
3. Compare response to previous greeting - should be DIFFERENT
```

---

### Test 1.3: Saudi Legal System Intent
**Test Input**: `سعودي` (or `Saudi law`, `النظام`, `System`)  
**Expected Response**: Information about Saudi legal system  
**Expected Intent**: `general_inquiry`  
**Success Criteria**:
- ✅ Response contains "⚖️ النظام القانوني السعودي"
- ✅ Mentions sources (Sharia, regulations, legal system)
- ✅ DIFFERENT from services and greeting responses

**Test Steps**:
```
1. Type "سعودي" in chat input
2. Press Enter
3. Verify response is unique and about legal system
```

---

### Test 1.4: Case Summary Intent
**Test Input**: `ملخص` (or `Summary`, `ملخص القضية`)  
**Expected Response**: Request for case file (if not uploaded) or case summary (if uploaded)  
**Expected Intent**: `case_summary`  
**Success Criteria**:
- ✅ Without file: "يرجى رفع ملف" (Please upload)
- ✅ With file: Actual case summary
- ✅ Different from general inquiries

**Test Steps**:
```
1. Type "ملخص القضية"
2. Before upload → Should ask for file
3. Upload file (data/saudi_general_court_judgments.json)
4. Type "ملخص القضية" again
5. Should show case summary
```

---

### Test 1.5: Case Type/Classification Intent
**Test Input**: `النوع` (or `Type`, `Classification`, `تصنيف`)  
**Expected Response**: Explain case classification  
**Expected Intent**: `case_type`  
**Success Criteria**:
- ✅ If no file: Offers to upload
- ✅ If file uploaded: Shows classification with confidence %
- ✅ Suggests related actions (legal principles, similar cases)

---

### Test 1.6: Similar Cases Intent
**Test Input**: `قضايا مشابهة` (or `Similar cases`, `Precedent`)  
**Expected Response**: Find similar cases from database  
**Expected Intent**: `similar_cases`  
**Success Criteria**:
- ✅ If no file: "Please upload a case file"
- ✅ If file uploaded: Shows top 3 similar cases with similarity scores
- ✅ Lists cases with percentages (e.g., "80% match")

---

### Test 1.7: Legal Principles Intent
**Test Input**: `المبادئ` (or `Legal principles`, `قواعد قانونية`)  
**Expected Response**: Extract applicable legal principles  
**Expected Intent**: `legal_principles`  
**Success Criteria**:
- ✅ If no file: Asks for upload
- ✅ If file: Shows principles in Arabic and English

---

### Test 1.8: Recommendations Intent
**Test Input**: `توصية` (or `Advice`, `رأي`, `Recommendation`)  
**Expected Response**: Provide recommendations  
**Expected Intent**: `recommendation`  
**Success Criteria**:
- ✅ If no file: Explanation of features
- ✅ If file: AI-powered recommendations based on case

---

### Test 1.9: Full Analysis Intent
**Test Input**: `تحليل` (or `Analyze`, `Analysis`, `اشرح`)  
**Expected Response**: Comprehensive analysis trigger  
**Expected Intent**: `full_analysis`  
**Success Criteria**:
- ✅ Request shows different handling vs simple summary
- ✅ Indicates comprehensive approach

---

### Test 1.10: Compensation Intent
**Test Input**: `تعويض` (or `Compensation`, `Damages`, `مبلغ`)  
**Expected Response**: Compensation analysis  
**Expected Intent**: `compensation`  
**Success Criteria**:
- ✅ If no file: Explains compensation features
- ✅ If file: Shows compensation amounts/trends

---

### Test 1.11: Outcome/Probability Intent
**Test Input**: `احتمالية` (or `Outcome`, `Probability`, `النتيجة`)  
**Expected Response**: Win probability and outcome analysis  
**Expected Intent**: `outcome`  
**Success Criteria**:
- ✅ If no file: Describes features
- ✅ If file: Shows success probability %

---

### Test 1.12: Draft Request Intent
**Test Input**: `مسودة` (or `Draft`, `لائحة`, `Write a draft`)  
**Expected Response**: Legal document drafting  
**Expected Intent**: `draft`  
**Success Criteria**:
- ✅ If no file: Asks for case content
- ✅ If file: Offers to generate pleading/memo

---

### Test 1.13: Entities Intent
**Test Input**: `الأطراف` (or `Parties`, `Entities`, `من`)  
**Expected Response**: Extract parties/entities  
**Expected Intent**: `entities`  
**Success Criteria**:
- ✅ If no file: Explains entity extraction
- ✅ If file: Lists parties and key entities

---

### Test 1.14: Trend/Statistics Intent
**Test Input**: `الاتجاهات` (or `Trends`, `Statistics`, `معدلات`)  
**Expected Response**: Statistical analysis  
**Expected Intent**: `trends`  
**Success Criteria**:
- ✅ Shows trends in cases of this type
- ✅ Success rates, common outcomes

---

## Part 2: Suggested Action Button Tests

### Test 2.1: Upload Document Button
**Action**: Click "📁 رفع مستند" button  
**Expected Behavior**:
- ✅ File dialog opens
- ✅ Can select file from `data/` folder
- ✅ File uploads and shows success message
- ✅ Analysis is stored in context

**Test Steps**:
```
1. Click "📁 رفع مستند" button
2. Select file: data/saudi_general_court_judgments.json
3. Verify success message appears
4. Verify "Analysis loaded" message or similar
```

---

### Test 2.2: Paste Text Button
**Action**: Click "📋 لصق نص" button  
**Expected Behavior**:
- ✅ Message "أريد لصق نص القضية" appears in chat
- ✅ Bot responds with guidance on describing the case
- ✅ Suggested action buttons appear

**Test Steps**:
```
1. Click "📋 لصق نص" button
2. Verify message appears in user chat bubble
3. Verify bot responds with guidance
```

---

### Test 2.3: Learn More Button
**Action**: Click "ℹ️ اعرف المزيد" button  
**Expected Behavior**:
- ✅ Message "أخبرني المزيد عن الخدمات" appears
- ✅ Bot provides detailed services information
- ✅ Different from initial greeting

**Test Steps**:
```
1. Scroll up to find suggested action
2. Click "ℹ️ اعرف المزيد" button
3. Verify detailed services explanation appears
```

---

## Part 3: File Upload Workflow Tests

### Test 3.1: Upload and Analyze
**Test Input**: 
1. Click "📁 رفع مستند"
2. Select `data/saudi_general_court_judgments.json`
3. Wait for upload to complete

**Expected Behavior**:
- ✅ Success message appears
- ✅ Chat shows "File uploaded and analyzed"
- ✅ Health status remains "Connected ✅"
- ✅ Analysis data is stored

**Test Steps**:
```
1. Click upload button
2. Select JSON file
3. Wait for processing
4. Verify success notification
```

---

### Test 3.2: Post-Upload Case Summary
**After uploading file, test**: `ملخص القضية`

**Expected Response**: 
- ✅ Actual case summary (not generic message)
- ✅ Summary in both Arabic and English
- ✅ Suggests next steps (View details, Find similar)

---

### Test 3.3: Post-Upload Case Type
**After uploading file, test**: `ما نوع هذه القضية`

**Expected Response**:
- ✅ Shows classification type
- ✅ Shows confidence percentage
- ✅ Lists subtypes if available
- ✅ Suggests legal principles and similar cases

---

### Test 3.4: Post-Upload Similar Cases
**After uploading file, test**: `قضايا مشابهة`

**Expected Response**:
- ✅ Shows 3+ similar cases
- ✅ Each with similarity score (%)
- ✅ Different similarity percentages (not all same)

---

### Test 3.5: Clear Chat and Reset
**Action**: Look for "🗑️ Clear" or "Clear Chat" button/option

**Expected Behavior**:
- ✅ All messages disappear
- ✅ Chat resets to fresh state
- ✅ Greeting message appears again from backend
- ✅ Previous analysis is cleared

---

## Part 4: Multi-turn Conversation Tests

### Test 4.1: Greeting → Services → Legal Question Dialog
**Test Sequence**:
1. Start (should show greeting from backend)
2. Send: `ما الخدمات?`
3. Send: `كيف يمكنك مساعدتي في قضية تعويض؟`
4. Send: `هل تحلل قضايا العمل؟`

**Expected Behavior**:
- ✅ Each message gets a unique, context-aware response
- ✅ No repetition of same answer
- ✅ Conversation flows naturally
- ✅ Messages are added to chat history

---

### Test 4.2: Case Upload → Multiple Analysis Requests
**Test Sequence**:
1. Upload case file
2. Send: `ملخص القضية`
3. Send: `ما نوع القضية؟`
4. Send: `المبادئ القانونية المطبقة؟`
5. Send: `ما احتمالية النجاح؟`

**Expected Behavior**:
- ✅ Each request returns case-specific analysis (not generic)
- ✅ Different response content for each request
- ✅ Analysis data persists across requests
- ✅ Suggested actions vary by response type

---

### Test 4.3: English and Arabic Mix
**Test Sequence**:
1. Send: `Hello`
2. Send: `ما الخدمات`
3. Send: `Show me similar cases`
4. Send: `اخبرني عن النظام السعودي`

**Expected Behavior**:
- ✅ All languages recognized (Arabic & English)
- ✅ Intent detection works for both
- ✅ Responses appropriate regardless of language
- ✅ No encoding errors

---

## Part 5: Edge Case Tests

### Test 5.1: Empty/Whitespace Message
**Test Input**: Send only spaces or empty message

**Expected Behavior**:
- ✅ Message not sent (or ignored gracefully)
- ✅ No error message displayed
- ✅ Chat remains stable

---

### Test 5.2: Very Long Message
**Test Input**: Send 500+ character message about a complex legal scenario

**Expected Behavior**:
- ✅ Message is sent successfully
- ✅ Backend processes it
- ✅ Response is generated
- ✅ No timeout or error

---

### Test 5.3: Special Characters
**Test Input**: Messages with:
- Arabic diacritics (تشكيل)
- Numbers (123, ١٢٣)
- Punctuation (!@#$%^&*)

**Expected Behavior**:
- ✅ All processed correctly
- ✅ No encoding issues
- ✅ Intent still detected properly

---

### Test 5.4: Typos/Misspellings
**Test Input**: 
- `مرحبااا` (extra alef)
- `khidmat` (English transliteration of خدمات)

**Expected Behavior**:
- ✅ Intent matching still works (partial matches)
- ✅ Graceful fallback to general inquiry if no match
- ✅ Helpful response

---

### Test 5.5: Repeated Messages
**Test Sequence**:
1. Send: `مرحبا`
2. Send: `مرحبا` (same message again)
3. Send: `مرحبا` (third time)

**Expected Behavior**:
- ✅ Each returns same response (consistent)
- ✅ Added to message history 3 times
- ✅ No caching issues

---

## Part 6: Browser/UI Tests

### Test 6.1: Message Scrolling
**Test**: Send 10+ messages

**Expected Behavior**:
- ✅ Chat automatically scrolls to bottom
- ✅ Latest message is always visible
- ✅ Smooth scroll animation
- ✅ No messages cut off

---

### Test 6.2: Message Bubbles Alignment
**Expected Behavior**:
- ✅ User messages: Blue, right-aligned (LTR style)
- ✅ Assistant messages: White/gray, left-aligned
- ✅ Proper spacing between messages
- ✅ Timestamps visible

---

### Test 6.3: Loading Indicator
**Test**: Send a message and watch for loading state

**Expected Behavior**:
- ✅ Loading spinner appears while waiting
- ✅ Spinner disappears when response arrives
- ✅ Send button disabled during loading
- ✅ Input field disabled during loading

---

### Test 6.4: Responsive Design
**Test**: Resize browser window to different widths

**Expected Behavior**:
- ✅ Chat works on mobile width (320px)
- ✅ Chat works on tablet width (768px)
- ✅ Chat works on desktop width (1200px)
- ✅ All buttons still clickable at all sizes

---

### Test 6.5: RTL (Right-to-Left) Support
**Test**: View chat with Arabic messages

**Expected Behavior**:
- ✅ Text aligns right for Arabic ✓
- ✅ Input field is RTL
- ✅ Buttons and layout adapt
- ✅ No text overflow issues

---

## Part 7: Performance Tests

### Test 7.1: Backend Response Time
**Test**: Send message and measure response time

**Expected Behavior**:
- ✅ Response arrives within 2 seconds (most)
- ✅ File upload takes 5-10 seconds max
- ✅ No timeout errors
- ✅ Smooth user experience

---

### Test 7.2: Multiple Rapid Messages
**Test**: Send 5 messages quickly without waiting

**Expected Behavior**:
- ✅ All messages queued properly
- ✅ Responses come back in order
- ✅ No lost messages
- ✅ No duplicate responses

---

### Test 7.3: Browser Memory
**Test**: Run chat for 10+ minutes, send 20+ messages

**Expected Behavior**:
- ✅ No browser lag or slowdown
- ✅ Chat history stays responsive
- ✅ New messages load instantly
- ✅ No memory warnings

---

## Part 8: Backend Logging Tests

### Test 8.1: Intent Detection Logging
**How to Check**: Keep backend terminal visible, send messages

**Expected Logs**:
```
Chat request: "مرحبا"
Message length: 5, Has analysis: False
Detected intent: greeting
Response text (first 50 chars): مرحباً بك! 👋...
```

**Success Criteria**:
- ✅ See different intents logged for different messages
- ✅ NOT just "general_inquiry" for everything
- ✅ Response text changes per message

---

### Test 8.2: Error Logging
**How to Check**: Try invalid operations, watch backend logs

**Expected Behavior**:
- ✅ Errors logged with timestamps
- ✅ No unhandled exceptions
- ✅ Error messages are descriptive

---

## Quick Test Checklist

Print this and check off as you test:

```
Intent Tests:
☐ Test 1.1: Greeting (مرحبا) - Different response
☐ Test 1.2: Services (ما الخدمات) - Different response  
☐ Test 1.3: Saudi Law (سعودي) - Different response
☐ Test 1.4-1.14: Other intents - All different responses

Button Tests:
☐ Test 2.1: Upload button works
☐ Test 2.2: Paste text button sends message
☐ Test 2.3: Learn more button works

File Upload:
☐ Test 3.1: File uploads successfully
☐ Test 3.2-3.5: Case-specific queries work with file

Conversation:
☐ Test 4.1: Multi-turn dialog works
☐ Test 4.2: Analysis requests work after upload
☐ Test 4.3: English and Arabic mix works

UI/Performance:
☐ Test 6.1: Messages scroll properly
☐ Test 6.5: RTL display correct
☐ Test 7.1: Response time < 2 seconds

Logs:
☐ Test 8.1: Backend logs show different intents
☐ Test 8.2: No error spam in logs
```

---

## Test Results Template

Save this and fill in for your testing:

```
Test Date: ____________
Tester: ________________

PASSED: ___/___

Test Case | Status | Notes
---------|--------|-------
1.1 Greeting | ☐ PASS ☐ FAIL | _____________
1.2 Services | ☐ PASS ☐ FAIL | _____________
2.1 Upload | ☐ PASS ☐ FAIL | _____________
...

Overall: ☐ All Pass ☐ Some Failures ☐ Critical Issues

Issues Found:
1. __________________________________
2. __________________________________
3. __________________________________

Recommendations:
- ________________________
- ________________________
```

---

## Success Criteria Summary

The chatbot is working correctly when:

✅ **Different intents return different responses**
- Not the same greeting for all messages
- Contextual based on input keywords

✅ **File upload works end-to-end**
- Can select and upload JSON file
- Can ask case-specific questions after

✅ **All buttons function**
- Upload opens dialog
- Paste text sends message
- Learn more triggers response

✅ **Chat is responsive**
- Messages scroll smoothly
- Loads fast (< 2 sec)
- RTL display correct

✅ **Backend logs show variety**
- Different intents detected
- Logging shows intent changes per message

---

**Good luck testing! The chatbot should now provide varied, context-aware responses.** 🚀

