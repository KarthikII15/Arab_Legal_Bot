import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

// Import Components
import { Layout } from './components/Layout';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Message } from './components/Message';
import { ChatInput } from './components/ChatInput';
import { ToolsPanel } from './components/ToolsPanel';
import { ThinkingIndicator } from './components/StateIndicators';
import { SettingsModal } from './components/SettingsModal';
import { RelatedCaseModal } from './components/RelatedCaseModal';
import { jsPDF } from 'jspdf';
import { PanelLeft, PanelRight } from 'lucide-react';

function App() {
  // Chat State
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [healthStatus, setHealthStatus] = useState("checking");
  const [analysis, setAnalysis] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showTools, setShowTools] = useState(true);

  // Settings State
  const [showSettings, setShowSettings] = useState(false);
  const [fontSize, setFontSize] = useState(() => localStorage.getItem('fontSize') || 'medium');
  const [viewingCase, setViewingCase] = useState(null);

  // Conversation management
  const [conversations, setConversations] = useState(() => {
    const saved = localStorage.getItem('conversations');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentConversationId, setCurrentConversationId] = useState(null);

  const messagesEndRef = useRef(null);
  const greetingSent = useRef(false);
  const API_BASE = "http://127.0.0.1:5000";

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check health on mount
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);

    // Send greeting message
    if (!greetingSent.current && messages.length === 0) {
      greetingSent.current = true;
      addAssistantMessage(
        "مرحباً بك! 👋 أنا مساعدك القانوني الذكي.\n\nيمكنني مساعدتك في:\n- 📊 تحليل القضايا\n- ⚖️ تصنيف القضايا\n- 💡 التوصيات القانونية\n- 🔍 البحث في السوابق\n\n---\n\nWelcome! Your AI Legal Assistant.\n\nI can help with:\n- Case Analysis\n- Classification\n- Legal Recommendations\n- Precedent Search",
        "greeting",
        [],
        null,
        [
          { label: "Upload Case | رفع قضية", action: "upload" },
          { label: "Ask Question | اسأل سؤال", action: "ask_question" }
        ]
      );
    }

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Theme Management
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Font Size Management
  useEffect(() => {
    document.documentElement.setAttribute('data-font-size', fontSize);
    localStorage.setItem('fontSize', fontSize);
  }, [fontSize]);

  // Sync current messages/analysis to conversation list for persistence in session
  useEffect(() => {
    if (currentConversationId) {
      setConversations(prev => prev.map(conv =>
        conv.id === currentConversationId
          ? { ...conv, messages: [...messages], analysis: analysis }
          : conv
      ));
    }
  }, [messages, analysis, currentConversationId]);

  // Persistence Management
  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(conversations));
  }, [conversations]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const handleFontSizeChange = (size) => {
    setFontSize(size);
  };

  const checkHealth = async () => {
    try {
      await axios.get(`${API_BASE}/health`, { timeout: 3000 });
      setHealthStatus("connected");
    } catch (err) {
      setHealthStatus("disconnected");
    }
  };

  const handleClearData = () => {
    setMessages([]);
    setConversations([]);
    setAnalysis(null);
    setSelectedFile(null);
    setCurrentConversationId(null);
    greetingSent.current = false;
    localStorage.removeItem('conversations'); // Assuming persistence might use this key later

    // Send greeting again after clear
    setTimeout(() => {
      addAssistantMessage(
        "مرحباً بك! 👋 أنا مساعدك القانوني الذكي.\n\nيمكنني مساعدتك في:\n- 📊 تحليل القضايا\n- ⚖️ تصنيف القضايا\n- 💡 التوصيات القانونية\n- 🔍 البحث في السوابق\n\n---\n\nWelcome! Your AI Legal Assistant.\n\nI can help with:\n- Case Analysis\n- Classification\n- Legal Recommendations\n- Precedent Search",
        "greeting",
        [],
        null,
        [
          { label: "Upload Case | رفع قضية", action: "upload" },
          { label: "Case Summary | ملخص القضية", action: "case_summary" }
        ]
      );
    }, 500);

    setShowSettings(false);
  };

  const addUserMessage = (text, displayLabel = null) => {
    const newMessage = {
      id: Date.now(),
      role: 'user',
      content: displayLabel || text, // Use label for UI bubble if provided
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const addAssistantMessage = (text, intent = '', citations = [], translation = null, suggestedActions = []) => {
    const newMessage = {
      id: Date.now(),
      role: 'assistant',
      content: text,
      translation: translation,
      intent: intent,
      citations: citations,
      suggested_actions: suggestedActions,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const sendChatMessage = async (userMessage, displayLabel = null) => {
    if (!userMessage.trim()) return;

    const msgId = addUserMessage(userMessage, displayLabel);
    setLoading(true);

    // Initial placeholder for streaming response
    const assistantMsgId = Date.now() + 100;
    const initialAssistantMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '', // Start empty
      intent: 'general_inquiry',
      citations: [],
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, initialAssistantMessage]);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          analysis_data: analysis,
          case_text: analysis ? "Case analyzed" : null
        })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            if (data.type === 'start') {
              setMessages(prev => prev.map(m => {
                if (m.id === assistantMsgId) return { ...m, intent: data.intent };
                return m;
              }));
            } else if (data.type === 'metadata' && data.user_translation) {
              setMessages(prev => prev.map(m => {
                if (m.id === msgId) return { ...m, translation: data.user_translation };
                return m;
              }));
            } else if (data.type === 'content') {
              fullText += data.text;
              setMessages(prev => prev.map(m =>
                m.id === assistantMsgId ? {
                  ...m,
                  content: fullText,
                  citations: data.citations || m.citations
                } : m
              ));
            } else if (data.type === 'analysis' && data.analysis_data) {
              setAnalysis(data.analysis_data);
            } else if (data.type === 'end') {
              setMessages(prev => prev.map(m =>
                m.id === assistantMsgId ? {
                  ...m,
                  suggested_actions: data.suggested_actions || [],
                  citations: data.citations || m.citations
                } : m
              ));
            }
          } catch (e) {
            console.error("Error parsing stream chunk:", e);
          }
        }
      }

      setHealthStatus("connected");

      // Final post-processing (cleanup, translation check, etc.)
      const finalizedMessage = messages.find(m => m.id === assistantMsgId);
      if (finalizedMessage && finalizedMessage.content.includes("---")) {
        // It's already bilingual
      }

      // Add to conversations if new
      if (!currentConversationId) {
        const newConvId = Date.now();
        setCurrentConversationId(newConvId);
        setConversations(prev => [{
          id: newConvId,
          title: userMessage.substring(0, 30) + (userMessage.length > 30 ? '...' : ''),
          preview: 'محادثة نصية',
          timestamp: new Date().toISOString(),
          messages: [...messages, initialAssistantMessage, { ...initialAssistantMessage, content: fullText }],
          analysis: analysis
        }, ...prev]);
      }

    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => prev.filter(m => m.id !== assistantMsgId));
      addAssistantMessage(
        "عذراً، حدث خطأ في معالجة طلبك.\n\nSorry, an error occurred processing your request.",
        "error",
        [],
        null,
        [
          { label: "Try Again | حاول مرة أخرى", action: "retry" },
          { label: "Upload Case | رفع قضية", action: "upload" }
        ]
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setSelectedFile(file);
    addUserMessage(`رفع الملف: ${file.name}`, {
      name: file.name,
      size: file.size
    });
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE}/upload-analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setAnalysis(response.data);
      setHealthStatus("connected");
      setSelectedFile(null);

      addAssistantMessage(
        `تم تحليل الملف بنجاح!\n\nنوع القضية: ${response.data.classification.name_ar}\n\n---\n\nFile analyzed successfully!\n\nCase Type: ${response.data.classification.name_en}`,
        "file_analyzed"
      );

      // Add to conversations if new
      if (!currentConversationId) {
        const newConvId = Date.now();
        setCurrentConversationId(newConvId);
        setConversations(prev => [{
          id: newConvId,
          title: response.data.classification.name_ar,
          preview: file.name,
          timestamp: new Date().toISOString(),
          messages: [...messages, { id: Date.now() + 1, role: 'assistant', content: `تم تحليل الملف بنجاح!\n\nنوع القضية: ${response.data.classification.name_ar}\n\n---\n\nFile analyzed successfully!`, intent: "file_analyzed", timestamp: new Date().toISOString() }],
          analysis: response.data
        }, ...prev]);
      }

    } catch (error) {
      console.error("Upload error:", error);
      addAssistantMessage(
        `❌ خطأ في رفع الملف\n\n${error.response?.data?.detail || error.message}\n\nError uploading file`,
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    // Reset backend context
    axios.post(`${API_BASE}/chat/clear`, { confirm: true }).catch(err => console.error(err));

    const newConvId = Date.now();
    setCurrentConversationId(newConvId);
    setMessages([]);
    setAnalysis(null);
    setSelectedFile(null);
    greetingSent.current = false;
    // Trigger greeting again
    addAssistantMessage(
      "مرحباً بك! 👋 أنا مساعدك القانوني الذكي.\n\nيمكنني مساعدتك في:\n- 📊 تحليل القضايا\n- ⚖️ تصنيف القضايا\n- 💡 التوصيات القانونية\n- 🔍 البحث في السوابق\n\n---\n\nWelcome! Your AI Legal Assistant.\n\nI can help with:\n- Case Analysis\n- Classification\n- Legal Recommendations\n- Precedent Search",
      "greeting",
      [],
      null,
      [
        { label: "Upload Case | رفع قضية", action: "upload" },
        { label: "Ask Question | اسأل سؤال", action: "ask_question" }
      ]
    );
  };

  const handleSelectConversation = (convId) => {
    const selected = conversations.find(c => c.id === convId);
    if (selected) {
      setCurrentConversationId(convId);
      setMessages(selected.messages || []);
      setAnalysis(selected.analysis || null);
      // Mark greeting as sent if we have messages so it doesn't re-trigger
      if (selected.messages && selected.messages.length > 0) {
        greetingSent.current = true;
      }
    }
  };

  const handleDeleteConversation = (convId) => {
    setConversations(prev => prev.filter(c => c.id !== convId));
    if (currentConversationId === convId) {
      handleNewChat();
    }
  };

  const handleArchiveConversation = async (convId) => {
    // 1. Find conversation data before removing from UI
    const conversationToArchive = conversations.find(c => c.id === convId);

    // 2. Optimistic UI update
    setConversations(prev =>
      prev.map(c => c.id === convId ? { ...c, archived: true } : c)
        .filter(c => !c.archived)
    );

    if (!conversationToArchive) return;

    // 3. Prepare payload (include messages if it's the current active chat)
    const messagesToArchive = (convId === currentConversationId) ? messages : [];

    try {
      await axios.post(`${API_BASE}/conversations/archive`, {
        conversation_id: String(convId),
        title: conversationToArchive.title,
        preview: conversationToArchive.preview,
        timestamp: conversationToArchive.timestamp,
        messages: messagesToArchive
      });
      console.log("Conversation archived on backend");
    } catch (error) {
      console.error("Failed to archive conversation:", error);
    }
  };

  const handleSuggestedAction = (action, label) => {
    console.log("Suggested action clicked:", action, label);

    switch (action) {
      case 'upload':
        // Trigger file input or show prompt
        document.querySelector('input[type="file"]')?.click();
        break;
      case 'ask_question':
        // Focus the chat input
        document.querySelector('textarea')?.focus();
        break;
      case 'retry':
        // Find last user message
        const userMsgs = messages.filter(m => m.role === 'user');
        if (userMsgs.length > 0) {
          sendChatMessage(userMsgs[userMsgs.length - 1].content);
        }
        break;
      case 'paste_text':
      case 'learn_more':
      case 'full_analysis':
      case 'similar_cases':
      case 'recommendations':
      case 'draft_claim':
      case 'draft_defense':
      case 'draft_appeal':
      case 'draft_enforcement':
      case 'legal_principles':
      case 'trends':
      case 'case_summary':
      case 'outcome':
      case 'compensation':
      case 'entities':
        // Send the action string for backend, but show the professional label in UI
        sendChatMessage(action, label);
        break;
      default:
        sendChatMessage(label);
        break;
    }
  };

  const handleMessageAction = (msgId, action) => {
    const message = messages.find(m => m.id === msgId);
    if (!message) return;

    switch (action) {
      case 'copy':
        navigator.clipboard.writeText(message.content);
        break;
      case 'regenerate':
        sendChatMessage(message.content);
        break;
      default:
        break;
    }
  };

  return (
    <Layout showSidebar={showSidebar} showTools={showTools}>
      {/* Header */}
      <Header
        healthStatus={healthStatus}
        onSettings={() => setShowSettings(true)}
      />

      {/* Sidebar - Conversations */}
      <Sidebar
        conversations={conversations}
        currentId={currentConversationId}
        onNewChat={handleNewChat}
        onSelect={handleSelectConversation}
        onDelete={handleDeleteConversation}
        onArchive={handleArchiveConversation}
        onClearHistory={handleClearData}
      />

      {/* Main Content Area */}
      <main className="app-main">
        {/* Edge Toggle Buttons */}
        <button
          className={`edge-toggle sidebar-trigger ${!showSidebar ? 'collapsed' : ''}`}
          onClick={() => setShowSidebar(!showSidebar)}
          title={showSidebar ? "إخفاء السجل" : "عرض السجل"}
        >
          <PanelRight size={18} />
        </button>

        <button
          className={`edge-toggle tools-trigger ${!showTools ? 'collapsed' : ''}`}
          onClick={() => setShowTools(!showTools)}
          title={showTools ? "إخفاء الأدوات" : "عرض الأدوات"}
        >
          <PanelLeft size={18} />
        </button>

        <div className="chat-messages-container">
          {messages.length === 0 ? (
            <div className="chat-empty-state">
              <div className="chat-empty-icon">⚖️</div>
              <h2 className="chat-empty-title">
                أهلاً بك في المساعد القانوني
              </h2>
              <p className="chat-empty-subtitle-en en-large">Welcome to Legal AI Assistant</p>
              <p className="chat-empty-subtitle">ابدأ برفع ملف قانوني أو اطرح سؤالاً</p>
              <p className="chat-empty-subtitle-en">Upload a document or ask a question to begin</p>
            </div>
          ) : (
            messages.map((msg) => (
              <Message
                key={msg.id}
                message={msg}
                onCopy={() => handleMessageAction(msg.id, 'copy')}
                onRegenerate={() => handleMessageAction(msg.id, 'regenerate')}
                onFeedback={(id, type) => console.log('Feedback:', id, type)}
                onActionClick={handleSuggestedAction}
                showActions={msg.role === 'assistant'}
              />
            ))
          )}

          {/* Loading State */}
          {loading && (
            <div className="chat-loading-wrapper">
              <div className="chat-loading-icon">⚖️</div>
              <div className="thinking-text">
                <ThinkingIndicator message="جاري معالجة طلبك..." />
                <div className="en-tiny">Processing your request...</div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <ChatInput
          onSend={sendChatMessage}
          onFileUpload={handleFileUpload}
          disabled={loading}
          maxChars={2000}
          showSlashCommands={true}
        />
      </main>

      {/* Tools Panel */}
      <ToolsPanel
        uploadedCase={analysis ? {
          name: selectedFile?.name || 'القضية المرفوعة',
          type: analysis.classification.name_ar,
          pages: messages.filter(m => m.fileData).length > 0 ? 'متعدد' : '1',
          timestamp: new Date().toISOString(),
          keywords: [
            analysis.classification.name_ar,
            'قضية قانونية'
          ]
        } : null}
        relatedCases={analysis?.related_cases || []}
        onExport={() => {
          try {
            const doc = new jsPDF();

            // Document Setup
            doc.setFontSize(18);
            doc.text("Legal Case Analysis", 10, 10);

            doc.setFontSize(10);
            doc.text(`Generated: ${new Date().toLocaleString()}`, 10, 20);
            doc.line(10, 22, 200, 22); // Horizontal line

            let y = 30;
            const lineHeight = 7;
            const pageHeight = doc.internal.pageSize.height;
            const maxWidth = 190;

            // 1. Case Info
            if (analysis) {
              doc.setFontSize(14);
              doc.text("Case Details", 10, y);
              y += 8;

              doc.setFontSize(11);
              doc.text(`Title: ${analysis.classification.name_ar}`, 10, y);
              y += lineHeight;
              doc.text(`Type: ${analysis.classification.name_en}`, 10, y);
              y += lineHeight;
              doc.text(`File: ${selectedFile?.name || 'N/A'}`, 10, y);
              y += 15;
            }

            // 2. Chat History
            doc.setFontSize(14);
            doc.text("Conversation History", 10, y);
            y += 10;

            doc.setFontSize(10);

            messages.forEach((msg) => {
              if (y > pageHeight - 20) { doc.addPage(); y = 20; }
              doc.setFont(undefined, 'bold');
              const role = msg.role === 'user' ? 'User' : 'Assistant';
              doc.text(`${role}:`, 10, y);
              y += 5;

              doc.setFont(undefined, 'normal');
              const splitText = doc.splitTextToSize(msg.content, maxWidth);
              splitText.forEach(line => {
                if (y > pageHeight - 10) { doc.addPage(); y = 20; }
                doc.text(line, 10, y);
                y += 5;
              });
              y += 10;
            });

            doc.save(`case-analysis-${currentConversationId || Date.now()}.pdf`);
          } catch (err) {
            console.error("PDF Export failed:", err);
            alert("Failed to export PDF.");
          }
        }}
        onRegenerate={() => {
          const lastUserMessage = messages.filter(m => m.role === 'user').pop();
          if (lastUserMessage) {
            sendChatMessage(lastUserMessage.content);
          }
        }}
        onCopyAll={() => {
          const content = messages.map(m => `${m.role}: ${m.content}`).join('\n\n');
          navigator.clipboard.writeText(content);
        }}
        onViewCase={(caseId) => {
          const rawCase = analysis?.related_cases?.find(rc => (rc.case?.case_id === caseId || rc.id === caseId));

          if (rawCase && rawCase.case) {
            setViewingCase({
              id: rawCase.case.case_id,
              title: rawCase.case.case_id,
              type: rawCase.case.court,
              year: '2024',
              similarity: rawCase.similarity_score / 100,
              preview: rawCase.preview || rawCase.case.facts.substring(0, 300) + '...',
              principles: [rawCase.case.legal_reasoning.substring(0, 300) + "..."]
            });
          } else if (rawCase) {
            setViewingCase(rawCase);
          } else {
            setViewingCase({
              id: caseId,
              title: 'قضية تجارية رقم ٤٥٣ (Commercial Case #453)',
              type: 'تجاري (Commercial)',
              year: '2024',
              similarity: 0.85,
              abstract: 'تتعلق هذه القضية بنزاع حول عقود التوريد وتأخير التسليم، حيث حكمت المحكمة بالتعويض عن الضرر الفعلي.',
              principles: [
                'العقد شريعة المتعاقدين',
                'الضرر يجب أن يكون مباشراً ومحققاً',
                'القوة القاهرة تعفي من المسؤولية'
              ]
            });
          }
        }}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        theme={theme}
        onToggleTheme={toggleTheme}
        fontSize={fontSize}
        onFontSizeChange={handleFontSizeChange}
        onClearData={handleClearData}
      />

      {/* Related Case Modal */}
      <RelatedCaseModal
        isOpen={!!viewingCase}
        onClose={() => setViewingCase(null)}
        caseData={viewingCase}
      />
    </Layout>
  );
}

export default App;
