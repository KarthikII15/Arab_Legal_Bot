import React from 'react';
import { RotateCcw, Copy, Download, FileText } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
/* jsPDF import removed, logic moved to App.js */

/**
 * ToolsPanel Component
 * Right sidebar with document info, related cases, and quick actions
 */
export function ToolsPanel({
  uploadedCase,
  relatedCases = [],
  onExport,
  onRegenerate,
  onCopyAll,
  onViewCase,
  benchMemo,
  fetchingMemo,
  onFetchBenchMemo
}) {
  const { language, t } = useLanguage();
  const [activeTab, setActiveTab] = React.useState('tools');

  // Auto-fetch memo when switching to judge tab
  React.useEffect(() => {
    if (activeTab === 'judge' && !benchMemo && !fetchingMemo && uploadedCase) {
      onFetchBenchMemo();
    }
  }, [activeTab, benchMemo, fetchingMemo, uploadedCase, onFetchBenchMemo]);

  return (
    <aside className="app-tools">
      {/* Tab Switcher */}
      <div className="tools-tabs">
        <button
          className={`tool-tab ${activeTab === 'tools' ? 'active' : ''}`}
          onClick={() => setActiveTab('tools')}
        >
          {t('tools.title')}
        </button>
        <button
          className={`tool-tab ${activeTab === 'judge' ? 'active' : ''}`}
          onClick={() => setActiveTab('judge')}
        >
          {t('tools.judge_memo')}
        </button>
      </div>

      <div className="tools-content">
        {activeTab === 'tools' ? (
          <>
            {/* Uploaded Document Section */}
            {uploadedCase ? (
              <div className="tool-section">
                <div className="tool-section-title">{t('tools.uploaded_doc')}</div>
                <div className="tool-card">
                  <div className="tool-card-header">
                    <FileText size={18} className="tool-icon" />
                    <h3>{uploadedCase.name || t('tools.untitled_doc')}</h3>
                  </div>
                  <div className="tool-card-body">
                    <div className="tool-info-grid">
                      <div> {t('tools.type')}: <span className="text-secondary">{uploadedCase.type || 'PDF'}</span></div>
                      <div> {t('tools.pages')}: <span className="text-secondary">{uploadedCase.pages || 'N/A'}</span></div>
                      <div>⏰ {t('tools.uploaded')}: <span className="text-secondary">{uploadedCase.timestamp ? new Date(uploadedCase.timestamp).toLocaleDateString(language === 'ar' ? 'ar-SA' : 'en-US') : 'N/A'}</span></div>
                    </div>

                    {/* Keywords/Tags */}
                    {uploadedCase.keywords && uploadedCase.keywords.length > 0 && (
                      <div className="tool-keywords">
                        <div className="tool-keywords-title">{t('tools.keywords')}:</div>
                        <div className="tool-badges">
                          {uploadedCase.keywords.map((keyword, idx) => (
                            <span key={idx} className="badge badge-primary">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="tool-section empty">
                <div className="tool-section-title">{t('tools.uploaded_doc')}</div>
                <div className="tool-empty-text">{t('tools.no_doc')}</div>
              </div>
            )}

            {/* Related Cases Section */}
            {relatedCases.length > 0 && (
              <div className="tool-section">
                <div className="tool-section-title">{t('tools.related_cases')}</div>
                <div className="related-cases-list">
                  {relatedCases
                    .filter(caseItem => caseItem && caseItem.case)
                    .map((caseItem, idx) => (
                      <div
                        key={idx}
                        className="related-case-item"
                        onClick={() => onViewCase?.(caseItem?.case?.case_id)}
                      >
                        <div className="related-case-header">
                          <span className="related-case-title">{caseItem?.case?.case_id || 'Unknown Case'}</span>
                          <span className="badge badge-success">
                            {Math.round(caseItem?.similarity_score || 0)}%
                          </span>
                        </div>
                        <div className="related-case-preview">
                          {language === 'en' && caseItem?.preview_en ? caseItem.preview_en : (caseItem?.preview || 'No preview available')}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Quick Actions Section */}
            <div className="tool-section">
              <div className="tool-section-title">{t('tools.quick_actions')}</div>
              <div className="quick-actions-grid">
                <button className="tool-button" onClick={onRegenerate}>
                  <RotateCcw size={16} />
                  <div className="btn-text-stack">
                    <span>{t('tools.regenerate')}</span>
                  </div>
                </button>
                <button className="tool-button" onClick={onCopyAll}>
                  <Copy size={16} />
                  <div className="btn-text-stack">
                    <span>{t('tools.copy_all')}</span>
                  </div>
                </button>
                <button className="tool-button" onClick={onExport}>
                  <Download size={16} />
                  <div className="btn-text-stack">
                    <span>{t('tools.download_pdf')}</span>
                  </div>
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="tool-section">
            <div className="tool-section-title">{t('tools.judge_memo')}</div>
            {fetchingMemo ? (
              <div className="memo-loading">
                <div className="spinner-border text-primary mb-3"></div>
                <p>{t('tools.fetching_memo')}</p>
              </div>
            ) : benchMemo ? (
              <div className="memo-container">
                <div className="memo-actions mb-3">
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => navigator.clipboard.writeText(language === 'ar' ? benchMemo.bench_memo_ar : benchMemo.bench_memo_en)}
                  >
                    <Copy size={14} className="me-1" /> {t('message.copy')}
                  </button>
                </div>

                <div className="memo-body" dir={language === 'ar' ? 'rtl' : 'ltr'}>
                  {/* Summary of Facts Card */}
                  <div className="memo-card">
                    <div className="memo-card-header">
                      <FileText size={18} className="memo-icon" />
                      <h4>{t('tools.memo_facts')}</h4>
                    </div>
                    <div className="memo-card-content">
                      <p>{language === 'ar' ? benchMemo.summary_of_facts_ar : benchMemo.summary_of_facts_en}</p>
                    </div>
                  </div>

                  {/* Procedural Aspect Card */}
                  <div className="memo-card">
                    <div className="memo-card-header">
                      <RotateCcw size={18} className="memo-icon" />
                      <h4>{t('tools.memo_procedural')}</h4>
                    </div>
                    <div className="memo-card-content">
                      <p style={{ whiteSpace: 'pre-line' }}>
                        {language === 'ar' ? benchMemo.procedural_summary_ar : benchMemo.procedural_summary_en}
                      </p>
                    </div>
                  </div>

                  {/* Legal Issues Card */}
                  <div className="memo-card">
                    <div className="memo-card-header">
                      <span className="memo-icon">⚖️</span>
                      <h4>{t('tools.memo_issues')}</h4>
                    </div>
                    <div className="memo-card-content">
                      <ul className="memo-list">
                        {(language === 'ar' ? benchMemo.legal_issues_ar : benchMemo.legal_issues_en).map((issue, i) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Statutory References Card */}
                  <div className="memo-card">
                    <div className="memo-card-header">
                      <span className="memo-icon">📜</span>
                      <h4>{t('tools.memo_refs')}</h4>
                    </div>
                    <div className="memo-card-content">
                      <ul className="memo-list">
                        {benchMemo.statutory_references.map((ref, i) => (
                          <li key={i}>
                            <strong>{language === 'ar' ? ref.article : ref.article_en}</strong>
                            {language === 'ar' && ref.context && <span>: {ref.context}</span>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Recommended Actions Card */}
                  <div className="memo-card">
                    <div className="memo-card-header">
                      <span className="memo-icon">🎯</span>
                      <h4>{t('tools.memo_actions')}</h4>
                    </div>
                    <div className="memo-card-content">
                      <ul className="memo-list">
                        {(language === 'ar' ? benchMemo.recommended_actions_ar : benchMemo.recommended_actions_en).map((action, i) => (
                          <li key={i}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="memo-empty">
                <p className="text-secondary mb-3">لم يتم توليد مذكرة القاضي لهذه القضية بعد.</p>
                <button
                  className="btn btn-primary"
                  onClick={onFetchBenchMemo}
                  disabled={!uploadedCase}
                >
                  {t('tools.generate_memo')}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Powered By Section */}
        <div className="tool-help-section" style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--color-gray-200)', textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '0.2rem' }}>
            {t('tools.powered_by')} <strong style={{ color: 'var(--color-primary)' }}>{t('tools.motivity_labs')}</strong>
          </div>
          <div style={{
            color: 'var(--color-text-tertiary)',
            padding: '4px',
            fontSize: '0.75rem',
            lineHeight: '1.4'
          }}>
            {t('tools.ai_notice').split('\n').map((line, i) => (
              <span key={i}>{line}<br /></span>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}

export default ToolsPanel;
