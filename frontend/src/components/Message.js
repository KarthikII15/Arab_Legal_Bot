import React, { useState } from 'react';
import { Copy, RotateCcw, ThumbsUp, ThumbsDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

/**
 * Message Component
 * Display single message with actions (copy, regenerate, feedback)
 * Supports rich content including markdown and citations
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
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Translation Block */}
        {message.translation && (
          <div className="message-translation">
            <div className="translation-divider"></div>
            <div className="translation-content">
              <ReactMarkdown>{message.translation}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <div className="citations-container">
            <div className="citations-header">
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

        {/* Action Buttons (Now Inside Bubble) */}
        {showActions && !isUser && (
          <div className="message-actions">
            {/* Copy Button */}
            <button
              className="action-button"
              onClick={handleCopy}
              title={copied ? '✓ تم النسخ' : 'نسخ'}
            >
              <Copy size={12} className="btn-icon-spacing" />
              {copied ? '✓ تم النسخ' : 'نسخ'}
            </button>

            {/* Regenerate Button */}
            <button
              className="action-button"
              onClick={handleRegenerate}
              title="إعادة توليد"
            >
              <RotateCcw size={12} className="btn-icon-spacing" />
              إعادة توليد
            </button>

            {/* Feedback Buttons */}
            <div className="feedback-group">
              <button
                className={`action-button feedback-btn ${feedbackGiven === 'positive' ? 'active' : ''}`}
                onClick={() => handleFeedback('positive')}
                title="إجابة مفيدة"
              >
                <ThumbsUp size={12} />
              </button>

              <button
                className={`action-button feedback-btn ${feedbackGiven === 'negative' ? 'active' : ''}`}
                onClick={() => handleFeedback('negative')}
                title="إجابة غير مفيدة"
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
