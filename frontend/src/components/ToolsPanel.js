import React from 'react';
import { RotateCcw, Copy, Download, FileText, ChevronRight, Info } from 'lucide-react';
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
  return (
    <aside className="app-tools">
      {/* Header */}
      <div className="tools-header">
        <span className="tools-header-icon">🛠️</span>
        الأدوات والسياق
      </div>

      {/* Content */}
      <div className="tools-content">
        {/* Uploaded Document Section */}
        {uploadedCase ? (
          <div className="tool-section">
            <div className="tool-section-title">المستند المرفوع</div>
            <div className="tool-card">
              <div className="tool-card-header">
                <FileText size={18} className="tool-icon" />
                <h3>{uploadedCase.name || 'قضية بدون عنوان'}</h3>
              </div>
              <div className="tool-card-body">
                <div className="tool-info-grid">
                  <div>📄 النوع: <span className="text-secondary">{uploadedCase.type || 'PDF'}</span></div>
                  <div>📖 الصفحات: <span className="text-secondary">{uploadedCase.pages || 'N/A'}</span></div>
                  <div>⏰ تم الرفع: <span className="text-secondary">{uploadedCase.timestamp ? new Date(uploadedCase.timestamp).toLocaleDateString('ar-SA') : 'N/A'}</span></div>
                </div>

                {/* Keywords/Tags */}
                {uploadedCase.keywords && uploadedCase.keywords.length > 0 && (
                  <div className="tool-keywords">
                    <div className="tool-keywords-title">الكلمات المفتاحية:</div>
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
            <div className="tool-section-title">المستند المرفوع</div>
            <div className="tool-empty-text">لم يتم رفع مستند</div>
          </div>
        )}

        {/* Related Cases Section */}
        {relatedCases.length > 0 && (
          <div className="tool-section">
            <div className="tool-section-title">القضايا ذات الصلة</div>
            <div className="related-cases-list">
              {relatedCases.map((caseItem, idx) => (
                <div
                  key={idx}
                  className="related-case-item"
                  onClick={() => onViewCase?.(caseItem.id)}
                >
                  <div className="related-case-header">
                    <span className="related-case-title">{caseItem.title}</span>
                    <span className="badge badge-success">
                      {Math.round((caseItem.similarity || 0) * 100)}%
                    </span>
                  </div>
                  <div className="related-case-preview">
                    {caseItem.preview}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions Section */}
        <div className="tool-section">
          <div className="tool-section-title">الإجراءات السريعة</div>
          <div className="quick-actions-grid">
            <button className="tool-button" onClick={onRegenerate}>
              <RotateCcw size={16} />
              <span>إعادة توليد</span>
            </button>
            <button className="tool-button" onClick={onCopyAll}>
              <Copy size={16} />
              <span>نسخ الكل</span>
            </button>
            <button className="tool-button" onClick={onExport}>
              <Download size={16} />
              <span>تحميل PDF</span>
            </button>
          </div>
        </div>

        {/* Help Section */}
        <div className="tool-help-section">
          <div className="tool-help-box">
            <strong>💡 نصيحة:</strong> استخدم أوامر التشطة (/) أثناء الكتابة للوصول إلى الأدوات بسرعة.
          </div>
        </div>
      </div>
    </aside>
  );
}

export default ToolsPanel;
