import React, { useState } from 'react';
import { Copy, RotateCcw, ThumbsUp, ThumbsDown, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { FileAttachment } from './FileAttachment';
import { useLanguage } from '../contexts/LanguageContext';
import ScaleLogo from './ScaleLogo';

/**
 * Message Component
 * Renders individual chat messages (user or assistant) with markdown support,
 * file attachments, citations, and actions.
 */
export function Message({ message, onRegenerate, onFeedback, onActionClick }) {
  const isUser = message.role === 'user';
  const messageClass = isUser ? 'message-user' : 'message-assistant';
  const { language, t } = useLanguage();

  const [copied, setCopied] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(message.feedback || null); // 'positive' or 'negative'

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerate = () => {
    onRegenerate?.(message);
  };

  const handleFeedback = (type) => {
    if (feedbackGiven === type) {
      // Toggle off if clicking the same button
      setFeedbackGiven(null);
      onFeedback?.(message.id, null);
      return;
    }
    setFeedbackGiven(type);
    onFeedback?.(message.id, type);
  };

  // Determine what to show based on language context
  // System messages/greeting might pass translation or we use translation in payload
  let displayContent = language === 'en' && message.translation
    ? message.translation
    : message.content;

  if (typeof displayContent === 'string' && displayContent.includes('\n\n---\n\n')) {
    const parts = displayContent.split('\n\n---\n\n');
    displayContent = language === 'ar' ? parts[0] : (parts[1] || parts[0]);
  }

  return (
    <div className={`message ${messageClass}`}>
      {/* Avatar */}
      <div className="message-avatar" style={!isUser ? { background: 'transparent', padding: 0 } : {}}>
        {isUser ? <User size={20} /> : <ScaleLogo size={32} />}
      </div>

      {/* Message Content */}
      <div className="message-bubble">
        <div className="message-text">
          {message.fileData && (
            <div style={{ marginBottom: '10px' }}>
              <FileAttachment file={message.fileData} />
            </div>
          )}
          <ReactMarkdown
            components={{
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: '#2dd4bf', textDecoration: 'underline' }}>
                  {children}
                </a>
              )
            }}
          >{displayContent}</ReactMarkdown>

          {/* Rendering the Bench Memo details if present */}
          {message.content_type === 'bench_memo' && message.details && (
            <div className="case-details">
              <div className="detail-row">
                <span className="detail-label">{t('message.case_type')}</span>
                <span className="detail-value">{language === 'en' ? message.details.case_type_en : message.details.case_type}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t('message.confidence')}</span>
                <span className="badge badge-primary">
                  {Math.round(message.details.confidence * 100)}%
                </span>
              </div>

              {/* Citations/Sources */}
              {message.details.relevant_articles && message.details.relevant_articles.length > 0 && (
                <div className="citations-list mt-3">
                  <div className="detail-label mb-2">{t('message.sources')}</div>
                  {message.details.relevant_articles.map((article, idx) => (
                    <div key={idx} className="citation-item">
                      <div className="citation-header">
                        <strong>{t('message.article')} {article.article_number}</strong>
                        <span className={`badge ${article.match_score > 0.8 ? 'badge-success' : 'badge-primary'}`}>
                          {Math.round(article.match_score * 100)}% Match
                        </span>
                      </div>
                      <div className="citation-text">
                        {language === 'en' ? article.text_en : article.text}
                      </div>

                      {/* Display hyperlinked references if they exist */}
                      {article.boe_links && article.boe_links.length > 0 && (
                        <div className="citation-links mt-2">
                          {article.boe_links.map((link, lIdx) => (
                            <a
                              key={lIdx}
                              href={link.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="boe-link"
                            >
                              🔗 {link.text}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Recommended Direction */}
              {message.details.recommended_direction && (
                <div className="mt-3 p-3 bg-gray-50 rounded-md border-l-4 border-primary">
                  <div className="detail-label mb-1">{t('message.ruling')}</div>
                  <div className="text-sm">
                    {language === 'en' ? message.details.recommended_direction_en : message.details.recommended_direction}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && String(message.intent || '').startsWith('draft') && (
          <div className="citations-container">
            {message.citations
              .filter(citation =>
                citation.source &&
                citation.source !== 'N/A' &&
                citation.article &&
                citation.article !== 'N/A' &&
                citation.text &&
                citation.text !== 'N/A'
              )
              .length > 0 && (
                <>
                  <div className="citations-header">
                    {t('message.sources')}
                  </div>
                  {message.citations
                    .filter(citation =>
                      citation.source &&
                      citation.source !== 'N/A' &&
                      citation.article &&
                      citation.article !== 'N/A' &&
                      citation.text &&
                      citation.text !== 'N/A'
                    )
                    .map((citation, idx) => (
                      <div
                        key={idx}
                        className="citation-card"
                        style={{ marginBottom: '0.5rem' }}
                      >
                        <div className="citation-source">
                          <span className="citation-badge">
                            {citation.source ? citation.source.substring(0, 20) : 'Source'}
                          </span>
                          {citation.article && (
                            <span className="citation-article">
                              {t('message.article')} {citation.article}
                            </span>
                          )}
                        </div>
                        <div className="citation-text">
                          {language === 'en' && citation.metadata?.text_en ? citation.metadata.text_en : citation.text}
                        </div>
                        {citation.metadata?.judgment && (
                          <div className="citation-judgment" style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--color-primary-dark)', borderLeft: '2px solid var(--color-primary)', paddingLeft: '0.5rem' }}>
                            <strong>{t('message.ruling')}</strong> {language === 'en' && citation.metadata?.judgment_en ? citation.metadata.judgment_en : citation.metadata.judgment}
                          </div>
                        )}
                      </div>
                    ))}
                </>
              )}
          </div>
        )}

        {/* Suggested Actions */}
        {message.suggested_actions && message.suggested_actions.length > 0 && !isUser && (
          <div className="suggested-actions-container">
            {message.suggested_actions.map((action, idx) => {
              // Extract logic: The backend might return "Label Arabic | Label English"
              const rawLabel = action.label || '';
              const parts = rawLabel.split('|').map(p => p.trim());
              const displayLabel = language === 'en'
                ? (parts.find(p => !/[\u0600-\u06FF]/.test(p)) || parts[0])
                : (parts.find(p => /[\u0600-\u06FF]/.test(p)) || parts[0]);

              return (
                <button
                  key={idx}
                  className="suggested-action-btn"
                  onClick={() => onActionClick?.(action.action, rawLabel)}
                >
                  <div className="btn-text-stack">
                    <span>{displayLabel}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Message Time */}
        <div className="message-time">
          {new Date(message.timestamp).toLocaleTimeString(language === 'ar' ? 'ar-SA' : 'en-US')}
        </div>

        {/* Action Buttons (Only for Assistant messages) */}
        {!isUser && (
          <div className="message-actions">
            {/* Copy Button */}
            <button
              className="action-button"
              onClick={handleCopy}
              title={copied ? t('message.copied') : t('message.copy')}
            >
              <Copy size={12} className="btn-icon-spacing" />
              <div className="btn-text-stack">
                <span>{copied ? t('message.copied') : t('message.copy')}</span>
              </div>
            </button>

            {/* Regenerate Button */}
            <button
              className="action-button"
              onClick={handleRegenerate}
              title={t('message.regenerate')}
            >
              <RotateCcw size={12} className="btn-icon-spacing" />
              <div className="btn-text-stack">
                <span>{t('message.regenerate')}</span>
              </div>
            </button>

            {/* Feedback Buttons */}
            <div className="feedback-group">
              <button
                className={`action-button feedback-btn ${feedbackGiven === 'positive' ? 'active' : ''}`}
                onClick={() => handleFeedback('positive')}
                title={t('message.helpful')}
              >
                <ThumbsUp size={12} />
              </button>

              <button
                className={`action-button feedback-btn ${feedbackGiven === 'negative' ? 'active' : ''}`}
                onClick={() => handleFeedback('negative')}
                title={t('message.not_helpful')}
              >
                <ThumbsDown size={12} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Message;
