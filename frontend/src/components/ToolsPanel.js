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
  onViewCase
}) {
  const { language, t } = useLanguage();

  return (
    <aside className="app-tools">
      {/* Header */}
      <div className="tools-header">
        <span className="tools-header-icon"></span>
        <div className="header-text-stack">
          <span>{t('tools.title')}</span>
        </div>
      </div>

      {/* Content */}
      <div className="tools-content">
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

        {/* Help Section replaced by Motivity Notice */}
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
