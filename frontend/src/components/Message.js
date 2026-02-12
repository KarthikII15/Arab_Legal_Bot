import React, { useState } from 'react';
import { Copy, RotateCcw, ThumbsUp, ThumbsDown } from 'lucide-react';

/**
 * Message Component
 * Display single message with actions (copy, regenerate, feedback)
 * Supports rich content including citations
 */
export function Message({ 
  message, 
  onCopy, 
  onRegenerate, 
  onFeedback, 
  showActions = true 
}) {
  const [copied, setCopied] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState(null);

  const isUser = message.role === 'user';
  const messageClass = isUser ? 'user' : 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onCopy?.(message.id);
  };

  const handleRegenerate = () => {
    onRegenerate?.(message.id);
  };

  const handleFeedback = (type) => {
    setFeedbackGiven(type);
    onFeedback?.(message.id, type);
  };

  return (
    <div className={`message ${messageClass}`}>
      {/* Avatar */}
      <div className="message-avatar">
        {isUser ? '👤' : '⚖️'}
      </div>

      {/* Message Content */}
      <div className="message-bubble">
        <div className="message-text">
          {message.content}
        </div>

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid currentColor', opacity: 0.8 }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              المصادر | Sources:
            </div>
            {message.citations.map((citation, idx) => (
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
                      المادة {citation.article}
                    </span>
                  )}
                </div>
                <div className="citation-text">
                  {citation.text}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Message Time */}
        <div className="message-time">
          {new Date(message.timestamp).toLocaleTimeString('ar-SA')}
        </div>
      </div>

      {/* Action Buttons */}
      {showActions && !isUser && (
        <div className="message-actions">
          {/* Copy Button */}
          <button 
            className="action-button"
            onClick={handleCopy}
            title={copied ? '✓ تم النسخ' : 'نسخ'}
          >
            <Copy size={14} style={{ marginRight: '0.25rem' }} />
            {copied ? '✓ تم النسخ' : 'نسخ'}
          </button>

          {/* Regenerate Button */}
          <button 
            className="action-button"
            onClick={handleRegenerate}
            title="إعادة توليد"
          >
            <RotateCcw size={14} style={{ marginRight: '0.25rem' }} />
            إعادة توليد
          </button>

          {/* Feedback Buttons */}
          <button 
            className={`action-button ${feedbackGiven === 'positive' ? 'active' : ''}`}
            onClick={() => handleFeedback('positive')}
            title="إجابة مفيدة"
            style={{
              background: feedbackGiven === 'positive' ? 'var(--color-success-pale)' : 'transparent',
              color: feedbackGiven === 'positive' ? 'var(--color-success)' : 'var(--color-primary)'
            }}
          >
            <ThumbsUp size={14} />
          </button>

          <button 
            className={`action-button ${feedbackGiven === 'negative' ? 'active' : ''}`}
            onClick={() => handleFeedback('negative')}
            title="إجابة غير مفيدة"
            style={{
              background: feedbackGiven === 'negative' ? 'var(--color-error-pale)' : 'transparent',
              color: feedbackGiven === 'negative' ? 'var(--color-error)' : 'var(--color-primary)'
            }}
          >
            <ThumbsDown size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

export default Message;
