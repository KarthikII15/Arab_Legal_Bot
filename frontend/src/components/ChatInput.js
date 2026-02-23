import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

/**
 * ChatInput Component
 * Multi-line input with auto-expansion, file upload, and slash commands
 */
export function ChatInput({
  onSend,
  onFileUpload,
  disabled = false,
  maxChars = 2000,
  showSlashCommands = true
}) {
  const [text, setText] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const { t } = useLanguage();

  const commands = [
    { name: '/summarize', label: t('commands.summarize'), icon: '📝' },
    { name: '/analyze', label: t('commands.analyze'), icon: '🔍' },
    { name: '/compare', label: t('commands.compare'), icon: '⚖️' },
    { name: '/extract', label: t('commands.extract'), icon: '🏷️' },
    { name: '/evidence', label: t('commands.evidence'), icon: '🔎' },
    { name: '/draft', label: t('commands.draft'), icon: '✍️' },
    { name: '/precedent', label: t('commands.precedent'), icon: '📚' },
    { name: '/clear', label: t('commands.clear'), icon: '🗑️' }
  ];

  // Auto-expand textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(
        textareaRef.current.scrollHeight,
        150
      ) + 'px';
    }
  }, [text]);

  // Check for slash commands
  useEffect(() => {
    if (text.startsWith('/') && showSlashCommands) {
      setShowCommands(true);
    } else {
      setShowCommands(false);
    }
  }, [text, showSlashCommands]);

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text, selectedFile);
      setText('');
      setSelectedFile(null);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleCommandClick = (command) => {
    setText(command.name + ' ');
    setShowCommands(false);
    textareaRef.current?.focus();
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      onFileUpload?.(file);
    }
  };

  const handleKeyDown = (e) => {
    // Enter sends the message
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    // Shift+Enter adds a new line (default textarea behavior)
  };

  const charCount = text.length;
  const charPercentage = (charCount / maxChars) * 100;
  const charColor = charPercentage > 90 ? 'var(--color-error)' :
    charPercentage > 75 ? 'var(--color-warning)' :
      'var(--color-text-tertiary)';

  return (
    <div className="input-wrapper">
      {/* File Preview */}
      {selectedFile && (
        <div className="chat-file-preview">
          <div className="chat-file-info">
            {selectedFile.name}
          </div>
          <button
            className="chat-file-remove"
            onClick={() => setSelectedFile(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* Slash Commands Palette */}
      {showCommands && (
        <div style={{
          background: 'white',
          border: '1px solid var(--color-gray-300)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-lg)',
          marginBottom: 'var(--space-3)',
          maxHeight: '300px',
          overflowY: 'auto',
          zIndex: 'var(--z-dropdown)'
        }}>
          {commands.map(cmd => (
            <div
              key={cmd.name}
              onClick={() => handleCommandClick(cmd)}
              style={{
                padding: 'var(--space-3)',
                borderBottom: '1px solid var(--color-gray-200)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
                fontSize: 'var(--font-size-sm)',
                transition: 'background var(--duration-base)'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg-tertiary)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
            >
              <span>{cmd.icon}</span>
              <div>
                <div style={{ fontWeight: 'var(--font-weight-semibold)' }}>
                  {cmd.name}
                </div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-tertiary)' }}>
                  {cmd.label} | {cmd.name.substring(1)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Input Group */}
      <div className="input-group">
        {/* Attach Button */}
        <button
          className="chat-input-attach"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          title={t('chat_input.attach')}
        >
          <Paperclip size={20} />
        </button>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.txt,.doc"
          title={t('chat_input.attach_title')}
        />

        {/* Text Area */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={t('app.input_placeholder')}
          className="chat-message-input"
        />

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className={`chat-input-send ${disabled || !text.trim() ? 'disabled' : ''}`}
          title={t('chat_input.send')}
        >
          <Send size={20} />
        </button>
      </div>

      {/* Character Counter */}
      {maxChars && (
        <div className="chat-char-counter" style={{ color: charColor }}>
          {charCount}/{maxChars} {t('chat_input.chars')}
        </div>
      )}
    </div>
  );
}

export default ChatInput;
