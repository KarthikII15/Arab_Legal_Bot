import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState('');
  const [similarCases, setSimilarCases] = useState([]);
  const [summary, setSummary] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('main'); // 'main' or 'dashboard'
  const [dashboardMode, setDashboardMode] = useState('dataset'); // 'document' or 'dataset'
  const [selectedFile, setSelectedFile] = useState(null);
  const [draft, setDraft] = useState(null);
  const [queryResponse, setQueryResponse] = useState(null); // NEW: Query State
  const [selectedQuestion, setSelectedQuestion] = useState('outcome'); // Default question

  const [healthStatus, setHealthStatus] = useState("Checking...");
  const API_BASE = "http://127.0.0.1:5000";

  React.useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleInputChange = (e) => setInputText(e.target.value);

  const checkHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE}/health`);
      setHealthStatus("Connected ✅");
    } catch (err) {
      setHealthStatus("Disconnected ❌");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setLoadingAction('upload');
    setError(null);
    setAnalysis(null);
    setSimilarCases([]);
    setSummary(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(`${API_BASE}/upload-analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnalysis(response.data);
      // If the analysis contains text, update input box too
      // But looking at the response model, it returns classification, etc.
      // We might want to see the text? The response doesn't strictly return the text unless we modify backend to return it.
      // Actually upload-analyze returns AnalyzeResponse.
      // If we want to populate the text box, we'd need the text.
      // But AnalyzeResponse structure: classification, legal_principles, trends, recommendation.
      // It DOES NOT contain the original text.
      // Maybe we should just let the user see the results.
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.response?.data?.detail || "File upload failed");
    } finally {
      setLoading(false);
      setLoadingAction('');
    }
  };

  const generateDraft = async (partyRole) => {
    if (!analysis) return;
    setLoading(true); setLoadingAction('draft_' + partyRole); setError(null); setDraft(null);
    try {
      // Construct payload matching DraftRequest
      const payload = {
        case_type: analysis.classification.name_en, // or name_ar
        classification_confidence: analysis.classification.confidence,
        legal_principles: analysis.legal_principles,
        recommendation: analysis.recommendation,
        party_role: partyRole,
        entities: analysis.entities
      };

      const response = await axios.post(`${API_BASE}/draft`, payload);
      setDraft(response.data);
      // Scroll to draft
      setTimeout(() => {
        document.getElementById('draft-section')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      console.error("Draft error:", err);
      setError("Failed to generate draft. " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false); setLoadingAction('');
    }
  };

  const handleQuery = async () => {
    if (!analysis) return;
    setLoading(true); setLoadingAction('query'); setError(null); setQueryResponse(null);
    try {
      const payload = {
        query_type: selectedQuestion,
        analysis_data: analysis
      };
      const response = await axios.post(`${API_BASE}/query`, payload);
      setQueryResponse(response.data);
    } catch (err) {
      console.error("Query error:", err);
      setError("Query failed. " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false); setLoadingAction('');
    }
  };

  const findSimilarCases = async () => {
    setLoading(true); setLoadingAction('similar'); setError(null); setSimilarCases([]);
    try {
      const response = await axios.post(`${API_BASE}/similar`, { text: inputText, top_k: 3 });
      setSimilarCases(response.data);
    } catch (err) {
      setError(err.response ? `Server Error: ${err.response.status}` : `Network Error: ${err.message}`);
    } finally { setLoading(false); setLoadingAction(''); }
  };

  const summarizeCase = async () => {
    setLoading(true); setLoadingAction('summarize'); setError(null); setSummary(null);
    try {
      const response = await axios.post(`${API_BASE}/summarize`, { text: inputText });
      setSummary(response.data);
    } catch (err) {
      setError(err.response ? `Server Error: ${err.response.status}` : `Network Error: ${err.message}`);
    } finally { setLoading(false); setLoadingAction(''); }
  };

  const analyzeCase = async () => {
    setLoading(true); setLoadingAction('analyze'); setError(null); setAnalysis(null);
    try {
      const response = await axios.post(`${API_BASE}/analyze`, { text: inputText, top_k: 5 });
      setAnalysis(response.data);
    } catch (err) {
      setError(err.response ? `Server Error: ${err.response.status} - ${JSON.stringify(err.response.data)}` : `Network Error: ${err.message}`);
    } finally { setLoading(false); setLoadingAction(''); }
  };

  const loadAnalytics = async () => {
    setActiveTab('dashboard');
    // Determine dashboard mode: if we have analysis data, show document mode
    if (analysis) {
      setDashboardMode('document');
    } else {
      setDashboardMode('dataset');
    }
    if (analytics) return; // Already loaded
    setLoading(true); setLoadingAction('analytics'); setError(null);
    try {
      const response = await axios.get(`${API_BASE}/analytics`);
      setAnalytics(response.data);
    } catch (err) {
      setError(err.response ? `Server Error: ${err.response.status}` : `Network Error: ${err.message}`);
    } finally { setLoading(false); setLoadingAction(''); }
  };

  // ── Direction badge helper ──
  const directionBadge = (direction) => {
    const map = {
      'plaintiff_likely': { cls: 'bg-success', text: 'يُرجح نجاح المدعي' },
      'defendant_likely': { cls: 'bg-danger', text: 'يُرجح رفض الدعوى' },
      'uncertain': { cls: 'bg-warning text-dark', text: 'النتيجة غير مؤكدة' },
      'insufficient_data': { cls: 'bg-secondary', text: 'بيانات غير كافية' }
    };
    const d = map[direction] || { cls: 'bg-secondary', text: direction };
    return <span className={`badge ${d.cls}`}>{d.text}</span>;
  };

  // ── Reliability badge ──
  const reliabilityBadge = (rel) => {
    const map = {
      'high': { cls: 'bg-success', text: 'موثوقية عالية' },
      'medium': { cls: 'bg-warning text-dark', text: 'موثوقية متوسطة' },
      'low': { cls: 'bg-danger', text: 'موثوقية منخفضة' },
      'insufficient': { cls: 'bg-secondary', text: 'بيانات غير كافية' }
    };
    const r = map[rel] || { cls: 'bg-secondary', text: rel };
    return <span className={`badge ${r.cls} ms-2`}>{r.text}</span>;
  };

  return (
    <div className="container mt-4" dir="rtl">
      <h1 className="text-center mb-3">🏛 المساعد الذكي لتحليل القضايا القانونية (AI Legal Assistant)</h1>
      <p className="text-center text-muted small mb-3">AI Judicial Intelligence & Decision Support Platform v2.0</p>

      {/* Status + Tabs */}
      <div className="text-center mb-3 d-flex justify-content-center gap-3 align-items-center">
        <span className={`badge ${healthStatus.includes("Connected") ? "bg-success" : "bg-danger"}`}
          style={{ cursor: 'pointer' }} onClick={checkHealth}>
          {healthStatus}
        </span>
        <button className={`btn btn-sm ${activeTab === 'main' ? 'btn-dark' : 'btn-outline-dark'}`}
          onClick={() => setActiveTab('main')}>🏠 الرئيسية (Home)</button>
        <button className={`btn btn-sm ${activeTab === 'dashboard' ? 'btn-dark' : 'btn-outline-dark'}`}
          onClick={loadAnalytics}>📊 لوحة التحليلات (Analytics)</button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {/* ══════════════════ MAIN TAB ══════════════════ */}
      {activeTab === 'main' && (
        <>
          {/* Input Card */}
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h5 className="card-title">نص الحكم / القضية (Case Text)</h5>
              <textarea className="form-control" rows="5" value={inputText}
                onChange={handleInputChange} placeholder="أدخل نص القضية هنا... (Enter case text here...)" />
              <div className="mt-3 d-flex gap-2 flex-wrap">
                <button className="btn btn-primary" onClick={findSimilarCases}
                  disabled={loading || !inputText}>
                  {loadingAction === 'similar' ? '⏳ جاري البحث...' : '🔍 قضايا مشابهة (Find Similar)'}
                </button>
                <button className="btn btn-success" onClick={summarizeCase}
                  disabled={loading || !inputText}>
                  {loadingAction === 'summarize' ? '⏳ جاري التلخيص...' : '📝 تلخيص (Summarize)'}
                </button>
                <button className="btn btn-warning text-dark" onClick={analyzeCase}
                  disabled={loading || !inputText}>
                  {loadingAction === 'analyze' ? '⏳ جاري التحليل...' : '⚖️ تحليل شامل (Analyze)'}
                </button>
              </div>

              <hr />

              <div className="mt-3">
                <h6 className="card-subtitle mb-2 text-muted">أو قم برفع ملف (Or Upload File: PDF, DOCX)</h6>
                <div className="d-flex gap-2">
                  <input type="file" className="form-control" onChange={handleFileChange} accept=".pdf,.docx,.txt" />
                  <button className="btn btn-secondary" onClick={handleFileUpload}
                    disabled={loading || !selectedFile}>
                    {loadingAction === 'upload' ? '⏳ جاري الرفع...' : '📤 رفع وتحليل (Upload & Analyze)'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* ── FULL ANALYSIS RESULTS ── */}
          {analysis && (
            <div className="mb-4">
              {/* Classification */}
              <div className="card shadow-sm border-primary mb-3">
                <div className="card-header bg-primary text-white d-flex justify-content-between">
                  <h5 className="mb-0">🏷️ تصنيف القضية (Case Classification)</h5>
                  <span className="badge bg-light text-primary">
                    {(analysis.classification.confidence * 100).toFixed(0)}% Confidence
                  </span>
                </div>
                <div className="card-body">
                  <div className="d-flex align-items-center gap-3 mb-2">
                    <h4 className="mb-0 text-primary">{analysis.classification.name_ar}</h4>
                    <span className="text-muted">({analysis.classification.name_en})</span>
                  </div>
                  {analysis.classification.matched_keywords.length > 0 && (
                    <div className="mt-2">
                      <small className="text-muted">الكلمات المطابقة (Keywords): </small>
                      {analysis.classification.matched_keywords.slice(0, 8).map((kw, i) => (
                        <span key={i} className="badge bg-light text-dark border me-1 mb-1">{kw}</span>
                      ))}
                    </div>
                  )}
                  {analysis.classification.sub_types.length > 0 && (
                    <div className="mt-2">
                      <small className="text-muted">تصنيفات ثانوية (Sub-types): </small>
                      {analysis.classification.sub_types.map((st, i) => (
                        <span key={i} className="badge bg-info text-dark me-1">
                          {st.name_ar} ({(st.relevance * 100).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Legal Principles */}
              {analysis.legal_principles.length > 0 && (
                <div className="card shadow-sm border-warning mb-3">
                  <div className="card-header text-dark" style={{ backgroundColor: '#fff3cd' }}>
                    <h5 className="mb-0">⚖️ المبادئ القانونية (Legal Principles) ({analysis.legal_principles.length})</h5>
                  </div>
                  <div className="card-body">
                    {analysis.legal_principles.map((p, i) => (
                      <div key={i} className="mb-3 p-2" style={{
                        borderRight: '3px solid #ffc107', backgroundColor: '#fffef5', borderRadius: '6px'
                      }}>
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <strong>{p.name_ar}</strong>
                            <span className="text-muted ms-2 small">({p.name_en})</span>
                          </div>
                          <div>
                            <span className="badge bg-warning text-dark">{(p.relevance * 100).toFixed(0)}%</span>
                            <span className="badge bg-light text-dark border ms-1">{p.source_section}</span>
                          </div>
                        </div>
                        <p className="small text-muted mt-1 mb-0" style={{ whiteSpace: 'pre-line' }}>
                          {p.evidence.substring(0, 200)}{p.evidence.length > 200 ? '...' : ''}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Trend Stats */}
              {analysis.trends && (
                <div className="card shadow-sm border-info mb-3">
                  <div className="card-header bg-info text-white d-flex justify-content-between">
                    <h5 className="mb-0">📊 تحليل السوابق (Precedents Analysis) - ({analysis.trends.sample_size} cases)</h5>
                    {reliabilityBadge(analysis.trends.reliability)}
                  </div>
                  <div className="card-body">
                    <div className="row text-center">
                      <div className="col-md-3 mb-2">
                        <div className="p-3" style={{ backgroundColor: '#e8f5e9', borderRadius: '8px' }}>
                          <h3 className="text-success mb-0">{analysis.trends.plaintiff_win_rate}%</h3>
                          <small>نسبة نجاح المدعي (Plaintiff Win Rate)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="p-3" style={{ backgroundColor: '#e3f2fd', borderRadius: '8px' }}>
                          <h3 className="text-primary mb-0">{analysis.trends.average_compensation > 0 ?
                            analysis.trends.average_compensation.toLocaleString() : 'N/A'}</h3>
                          <small>متوسط التعويض (Avg Compensation)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="p-3" style={{ backgroundColor: '#fff3e0', borderRadius: '8px' }}>
                          <h3 className="text-warning mb-0">{analysis.trends.sample_size}</h3>
                          <small>قضايا مشابهة (Similar Cases)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="p-3" style={{ backgroundColor: '#fce4ec', borderRadius: '8px' }}>
                          <h3 className="text-danger mb-0">{analysis.trends.decided_cases}</h3>
                          <small>قضايا محسومة</small>
                        </div>
                      </div>
                    </div>
                    {/* Outcome bars */}
                    <div className="mt-3">
                      <small className="text-muted">توزيع النتائج (Outcome Distribution):</small>
                      <div className="d-flex gap-2 mt-1 flex-wrap">
                        {Object.entries(analysis.trends.outcomes).filter(([, v]) => v > 0).map(([key, val]) => {
                          const labels = {
                            plaintiff_win: '✅ فوز المدعي',
                            plaintiff_loss: '❌ رفض الدعوى',
                            dismissed: '📤 ترك الخصومة',
                            jurisdictional: '🔄 عدم اختصاص',
                            unknown: '❓ غير محدد'
                          };
                          return (
                            <span key={key} className="badge bg-light text-dark border">
                              {labels[key] || key}: {val}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Recommendation */}
              {analysis.recommendation && (
                <div className="card shadow-sm mb-3" style={{
                  borderColor: analysis.recommendation.direction === 'plaintiff_likely' ? '#198754' :
                    analysis.recommendation.direction === 'defendant_likely' ? '#dc3545' : '#ffc107'
                }}>
                  <div className="card-header text-white d-flex justify-content-between" style={{
                    backgroundColor: analysis.recommendation.direction === 'plaintiff_likely' ? '#198754' :
                      analysis.recommendation.direction === 'defendant_likely' ? '#dc3545' :
                        analysis.recommendation.direction === 'uncertain' ? '#ffc107' : '#6c757d',
                    color: analysis.recommendation.direction === 'uncertain' ? '#000' : '#fff'
                  }}>
                    <h5 className="mb-0" style={{
                      color: analysis.recommendation.direction === 'uncertain' ? '#000' : '#fff'
                    }}>💡 التوصية (Recommendation)</h5>
                    <div>
                      {directionBadge(analysis.recommendation.direction)}
                      <span className="badge bg-light text-dark ms-2">
                        {(analysis.recommendation.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="card-body">
                    <p className="mb-2" style={{ fontSize: '1.1em', whiteSpace: 'pre-line' }}>
                      {analysis.recommendation.recommendation_ar}
                    </p>
                    <p className="text-muted small mb-2">{analysis.recommendation.recommendation_en}</p>

                    {analysis.recommendation.supporting_principles.length > 0 && (
                      <div className="mt-2">
                        <small className="text-muted">المبادئ الداعمة (Supporting Principles):</small>
                        {analysis.recommendation.supporting_principles.map((sp, i) => (
                          <span key={i} className="badge bg-light text-dark border ms-1">
                            {sp.name_ar}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="alert alert-secondary mt-3 mb-0 small">
                      {analysis.recommendation.disclaimer_ar}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── SUMMARY RESULTS ── */}
          {summary && (
            <div className="card shadow-sm border-success mb-4">
              <div className="card-header bg-success text-white d-flex justify-content-between align-items-center">
                <h5 className="mb-0">⚖️ الملخص القانوني (Structured Summary)</h5>
                {summary.confidence > 0 && (
                  <span className="badge bg-light text-success">
                    {(summary.confidence * 100).toFixed(0)}% Confidence | Extractive
                  </span>
                )}
              </div>
              <div className="card-body">
                {summary.facts_summary && (
                  <div className="mb-3 p-3" style={{ backgroundColor: '#f8f9fa', borderRadius: '8px', borderRight: '4px solid #0d6efd' }}>
                    <h6 className="text-primary mb-2">📌 ملخص الوقائع (Facts Summary)</h6>
                    <p className="mb-0" style={{ whiteSpace: 'pre-line' }}>{summary.facts_summary}</p>
                  </div>
                )}
                {summary.reasoning_summary && (
                  <div className="mb-3 p-3" style={{ backgroundColor: '#f8f9fa', borderRadius: '8px', borderRight: '4px solid #ffc107' }}>
                    <h6 style={{ color: '#b8860b' }} className="mb-2">⚖️ ملخص الأسباب (Reasoning Summary)</h6>
                    <p className="mb-0" style={{ whiteSpace: 'pre-line' }}>{summary.reasoning_summary}</p>
                  </div>
                )}
                {summary.verdict_summary && (
                  <div className="mb-3 p-3" style={{ backgroundColor: '#f0fff4', borderRadius: '8px', borderRight: '4px solid #198754' }}>
                    <h6 className="text-success mb-2">🏛 منطوق الحكم (Verdict)</h6>
                    <p className="mb-0" style={{ whiteSpace: 'pre-line' }}>{summary.verdict_summary}</p>
                  </div>
                )}
                {!summary.facts_summary && !summary.reasoning_summary && !summary.verdict_summary && (
                  <p className="lead" style={{ whiteSpace: 'pre-line' }}>{summary.summary}</p>
                )}
              </div>
            </div>
          )}
          {/* ── DRAFT GENERATION ACTIONS ── */}

          {analysis && analysis.recommendation && (
            <div className="card shadow-sm border-dark mb-4">
              <div className="card-header bg-dark text-white">
                <h5 className="mb-0">📝 إنشاء مسودة قانونية (AI Legal Drafter)</h5>
              </div>
              <div className="card-body text-center">
                <p className="text-muted">بناءً على التحليل، يمكنك توليد مسودة قانونية فورية (Generate Draft):</p>
                <div className="d-flex justify-content-center gap-3">
                  <button className="btn btn-outline-success btn-lg"
                    onClick={() => generateDraft('plaintiff')} disabled={loading}>
                    {loadingAction === 'draft_plaintiff' ? '⏳ جاري التوليد...' : '📄 لائحة دعوى (Claim)'}
                  </button>
                  <button className="btn btn-outline-danger btn-lg"
                    onClick={() => generateDraft('defendant')} disabled={loading}>
                    {loadingAction === 'draft_defendant' ? '⏳ جاري التوليد...' : '🛡️ مذكرة دفاع (Defense)'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── GENERATED DRAFT DISPLAY ── */}
          {draft && (
            <div id="draft-section" className="card shadow-lg border-dark mb-5">
              <div className="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                <h5 className="mb-0">{draft.title}</h5>
                <span className="badge bg-light text-dark">{draft.type === 'claim' ? 'لائحة دعوى' : 'مذكرة دفاع'}</span>
              </div>
              <div className="card-body bg-light">
                <textarea
                  className="form-control"
                  rows="15"
                  readOnly
                  value={draft.content}
                  style={{ fontFamily: 'Times New Roman, serif', fontSize: '1.2em', lineHeight: '1.8' }}
                />
                <div className="mt-3 text-center">
                  <button className="btn btn-primary" onClick={() => navigator.clipboard.writeText(draft.content)}>
                    📋 نسخ النص (Copy Text)
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── INTERACTIVE LEGAL QUERY PANEL ── */}
          {analysis && (
            <div className="card shadow-sm border-info mb-5">
              <div className="card-header bg-info text-dark d-flex justify-content-between align-items-center">
                <h5 className="mb-0">🕵️ المساعد القضائي التفاعلي (Interactive Query)</h5>
              </div>
              <div className="card-body">
                <p className="text-muted mb-3">يمكنك طرح استفسارات محددة حول القضية للحصول على إجابات دقيقة بناءً على التحليل:</p>

                <div className="input-group mb-3">
                  <select className="form-select" value={selectedQuestion}
                    onChange={(e) => { setSelectedQuestion(e.target.value); setQueryResponse(null); }}>
                    <option value="outcome">⚖️ ما هي النتيجة المتوقعة؟ (Likely Outcome)</option>
                    <option value="principles">📜 ما هي المبادئ القانونية المستند عليها؟ (Legal Principles)</option>
                    <option value="similar_cases">🔍 هل توجد سوابق قضائية مشابهة؟ (Similar Cases)</option>
                    <option value="compensation">💰 ما هو متوسط التعويضات؟ (Compensation Trends)</option>
                    <option value="confidence">🛡️ ما مدى موثوقية هذا التحليل؟ (Reliability Check)</option>
                  </select>
                  <button className="btn btn-primary" onClick={handleQuery} disabled={loading}>
                    {loadingAction === 'query' ? '⏳ جاري البحث...' : '❓ اسأل المساعد (Ask AI)'}
                  </button>
                </div>

                {queryResponse && (
                  <div className="alert alert-secondary border-0 mt-3">
                    <h6 className="text-primary mb-2">💡 الإجابة (Answer):</h6>
                    <p className="lead mb-0" style={{ whiteSpace: 'pre-line' }}>{queryResponse.answer}</p>
                    <small className="text-muted mt-2 d-block">المصدر (Source): {queryResponse.source}</small>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── SIMILAR CASES RESULTS ── */}
          {similarCases.length > 0 && (
            <div className="mb-4">
              <h3 className="mb-3">🔍 قضايا مشابهة (Similar Cases)</h3>
              <div className="row">
                {similarCases.map((item) => (
                  <div className="col-md-4 mb-3" key={item.case_id}>
                    <div className="card h-100 shadow-sm">
                      <div className="card-body">
                        <h5 className="card-title text-primary">{item.case_id}</h5>
                        <h6 className="card-subtitle mb-2 text-muted">
                          نسبة التشابه: {item.similarity_score.toFixed(1)}%
                        </h6>
                        <p className="card-text small">{item.preview}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* ══════════════════ DASHBOARD TAB ══════════════════ */}
      {activeTab === 'dashboard' && (
        <div>
          {loadingAction === 'analytics' && (
            <div className="text-center py-5"><h4>⏳ جاري تحميل التحليلات...</h4></div>
          )}

          {/* ── Mode Toggle Buttons ── */}
          <div className="text-center mb-3">
            <div className="btn-group" role="group">
              <button
                className={`btn btn-sm ${dashboardMode === 'document' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => setDashboardMode('document')}
                disabled={!analysis}
              >
                📄 لوحة الوثيقة (Document)
              </button>
              <button
                className={`btn btn-sm ${dashboardMode === 'dataset' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => setDashboardMode('dataset')}
              >
                📊 تحليلات شاملة (Dataset)
              </button>
            </div>
            {dashboardMode === 'document' && !analysis && (
              <div className="alert alert-warning small mt-2">
                ⚠️ لا توجد وثيقة محللة. قم برفع ملف أو أدخل نص قضية أولاً.
                (No document analyzed. Upload a file or paste case text first.)
              </div>
            )}
          </div>

          {/* ═══════════════════════════════════════════════════ */}
          {/* ── DOCUMENT DASHBOARD MODE ──                      */}
          {/* ═══════════════════════════════════════════════════ */}
          {dashboardMode === 'document' && analysis && (
            <>
              <div className="alert alert-light border-primary small">
                📄 عرض تحليل الوثيقة المرفوعة (Showing analysis of the uploaded document)
              </div>

              {/* Extracted Document Info */}
              <div className="card shadow-sm mb-4 border-primary">
                <div className="card-header bg-primary text-white">
                  <h5 className="mb-0">🔍 بيانات الوثيقة المستخرجة (Extracted Document Info)</h5>
                </div>
                <div className="card-body">
                  <div className="row">
                    {analysis.entities && (
                      <>
                        <div className="col-md-6 mb-3">
                          <table className="table table-sm table-bordered">
                            <tbody>
                              <tr>
                                <th className="bg-light" style={{ width: '40%' }}>🏛 المحكمة (Court)</th>
                                <td>{analysis.entities.court_name || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">📋 نوع القضية (Case Type)</th>
                                <td>{analysis.classification?.name_ar || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">⚖️ نوع النزاع (Dispute)</th>
                                <td>
                                  <span className={`badge ${analysis.entities.dispute_type === 'عمالي' ? 'bg-info' :
                                      analysis.entities.dispute_type === 'تجاري' ? 'bg-warning text-dark' :
                                        'bg-secondary'
                                    }`}>{analysis.entities.dispute_type || '—'}</span>
                                </td>
                              </tr>
                              <tr>
                                <th className="bg-light">📄 نوع الوثيقة (Doc Type)</th>
                                <td>
                                  <span className={`badge ${analysis.entities.doc_type === 'judgement' ? 'bg-dark' : 'bg-success'
                                    }`}>{analysis.entities.doc_type === 'judgement' ? 'حكم قضائي (Judgment)' : 'لائحة دعوى (Claim)'}</span>
                                </td>
                              </tr>
                              <tr>
                                <th className="bg-light">📅 التاريخ (Date)</th>
                                <td>{analysis.entities.date || '—'}</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                        <div className="col-md-6 mb-3">
                          <table className="table table-sm table-bordered">
                            <tbody>
                              <tr>
                                <th className="bg-light" style={{ width: '40%' }}>👤 المدعي (Plaintiff)</th>
                                <td>{analysis.entities.plaintiff || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">👤 المدعى عليه (Defendant)</th>
                                <td>{analysis.entities.defendant || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">💰 الراتب (Salary)</th>
                                <td>{analysis.entities.salary || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">💵 مبلغ التعويض (Compensation)</th>
                                <td className="fw-bold text-success">{analysis.entities.compensation_amount || '—'}</td>
                              </tr>
                              <tr>
                                <th className="bg-light">📜 المواد المرصودة (Articles)</th>
                                <td>
                                  {analysis.entities.articles && analysis.entities.articles.length > 0
                                    ? analysis.entities.articles.map(a => (
                                      <span key={a} className="badge bg-danger me-1">المادة {a}</span>
                                    ))
                                    : '—'}
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Judgment Result (if judgement doc) */}
                  {analysis.entities?.judgment_result && (
                    <div className="alert alert-dark mt-2 mb-0">
                      <strong>⚖️ نتيجة الحكم (Verdict):</strong> {analysis.entities.judgment_result}
                    </div>
                  )}
                </div>
              </div>

              {/* Case-Specific Analytics from Trends */}
              {analysis.trends && (
                <div className="card shadow-sm mb-4 border-info">
                  <div className="card-header bg-info text-dark">
                    <h5 className="mb-0">📊 تحليل السوابق المشابهة (Similar Case Analytics)</h5>
                  </div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-3 mb-2">
                        <div className="card text-center p-3 bg-light">
                          <h2 className="text-primary">{analysis.trends.sample_size}</h2>
                          <small>سوابق مشابهة (Similar Cases)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="card text-center p-3 bg-light">
                          <h2 className="text-success">{analysis.trends.plaintiff_win_rate}%</h2>
                          <small>نسبة فوز المدعي (Win Rate)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="card text-center p-3 bg-light">
                          <h2 className="text-warning">{analysis.trends.average_compensation > 0
                            ? Math.round(analysis.trends.average_compensation).toLocaleString('en-US') + ' SAR'
                            : 'N/A'}</h2>
                          <small>متوسط التعويض (Avg Comp)</small>
                        </div>
                      </div>
                      <div className="col-md-3 mb-2">
                        <div className="card text-center p-3 bg-light">
                          <h2>{reliabilityBadge(analysis.trends.reliability)}</h2>
                          <small>مستوى الموثوقية (Reliability)</small>
                        </div>
                      </div>
                    </div>

                    {/* Outcome breakdown for this case type */}
                    {analysis.trends.outcomes && Object.keys(analysis.trends.outcomes).length > 0 && (
                      <div className="mt-3">
                        <h6>توزيع نتائج السوابق (Precedent Outcomes):</h6>
                        {Object.entries(analysis.trends.outcomes).filter(([, v]) => v > 0).map(([key, val]) => {
                          const labels = {
                            plaintiff_win: '✅ فوز المدعي',
                            plaintiff_loss: '❌ رفض الدعوى',
                            dismissed: '📤 ترك الخصومة',
                            jurisdictional: '🔄 عدم اختصاص',
                            unknown: '❓ غير محدد'
                          };
                          return (
                            <div key={key} className="d-flex justify-content-between align-items-center mb-1">
                              <span>{labels[key] || key}</span>
                              <span className="badge bg-secondary">{val}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recommendation Quick View */}
              {analysis.recommendation && (
                <div className="card shadow-sm mb-4 border-warning">
                  <div className="card-header bg-warning text-dark">
                    <h5 className="mb-0">💡 التوصية القضائية (Recommendation)</h5>
                  </div>
                  <div className="card-body">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      {directionBadge(analysis.recommendation.direction)}
                      <span className="text-muted">الثقة: {(analysis.recommendation.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <p className="lead" style={{ whiteSpace: 'pre-line' }}>{analysis.recommendation.recommendation_ar}</p>
                  </div>
                </div>
              )}
            </>
          )}

          {/* ═══════════════════════════════════════════════════ */}
          {/* ── DATASET DASHBOARD MODE ──                       */}
          {/* ═══════════════════════════════════════════════════ */}
          {dashboardMode === 'dataset' && analytics && (
            <>
              <div className="alert alert-info small">
                ℹ️ {analytics.data_source}
              </div>

              {/* Summary Stats */}
              <div className="row mb-4">
                <div className="col-md-3 mb-2">
                  <div className="card shadow-sm text-center p-3">
                    <h2 className="text-primary">{analytics.total_cases}</h2>
                    <small>إجمالي القضايا (Total Cases)</small>
                  </div>
                </div>
                <div className="col-md-3 mb-2">
                  <div className="card shadow-sm text-center p-3">
                    <h2 className="text-success">{analytics.compensation_stats.count}</h2>
                    <small>قضايا بتعويض (Cases w/ Comp)</small>
                  </div>
                </div>
                <div className="col-md-3 mb-2">
                  <div className="card shadow-sm text-center p-3">
                    <h2 className="text-warning">{analytics.compensation_stats.average > 0 ?
                      Math.round(analytics.compensation_stats.average).toLocaleString('en-US') : 'N/A'}</h2>
                    <small>متوسط التعويض (Avg Comp)</small>
                  </div>
                </div>
                <div className="col-md-3 mb-2">
                  <div className="card shadow-sm text-center p-3">
                    <h2 className="text-danger">{analytics.compensation_stats.max > 0 ?
                      Math.round(analytics.compensation_stats.max).toLocaleString('en-US') : 'N/A'}</h2>
                    <small>أعلى تعويض (Max Comp)</small>
                  </div>
                </div>
              </div>

              {/* Case Type Distribution */}
              <div className="card shadow-sm mb-4">
                <div className="card-header bg-primary text-white">
                  <h5 className="mb-0">🏷️ توزيع أنواع القضايا (Case Type Distribution)</h5>
                </div>
                <div className="card-body">
                  {Object.entries(analytics.case_type_distribution).sort((a, b) => b[1] - a[1]).map(([type, count]) => (
                    <div key={type} className="mb-2">
                      <div className="d-flex justify-content-between mb-1">
                        <span>{type}</span>
                        <span className="badge bg-primary">{count}</span>
                      </div>
                      <div className="progress" style={{ height: '20px' }}>
                        <div className="progress-bar" role="progressbar"
                          style={{ width: `${(count / analytics.total_cases) * 100}%` }}>
                          {((count / analytics.total_cases) * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Outcome Distribution */}
              <div className="card shadow-sm mb-4">
                <div className="card-header bg-success text-white">
                  <h5 className="mb-0">📊 توزيع النتائج القضائية (Verdict Distribution)</h5>
                </div>
                <div className="card-body">
                  {Object.entries(analytics.outcome_distribution).filter(([, v]) => v > 0).map(([key, val]) => {
                    const labels = {
                      plaintiff_win: '✅ فوز المدعي',
                      plaintiff_loss: '❌ رفض الدعوى',
                      dismissed: '📤 ترك الخصومة',
                      jurisdictional: '🔄 عدم اختصاص',
                      unknown: '❓ غير محدد'
                    };
                    const colors = {
                      plaintiff_win: '#198754',
                      plaintiff_loss: '#dc3545',
                      dismissed: '#ffc107',
                      jurisdictional: '#0dcaf0',
                      unknown: '#6c757d'
                    };
                    return (
                      <div key={key} className="mb-2">
                        <div className="d-flex justify-content-between mb-1">
                          <span>{labels[key] || key}</span>
                          <span className="badge" style={{ backgroundColor: colors[key] }}>{val}</span>
                        </div>
                        <div className="progress" style={{ height: '20px' }}>
                          <div className="progress-bar" style={{
                            width: `${(val / analytics.total_cases) * 100}%`,
                            backgroundColor: colors[key]
                          }}>
                            {((val / analytics.total_cases) * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
