import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { Plus, MessageSquare, Trash2, Archive, X } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import './TooltipStyles.css'; // Import tooltip styles

/**
 * Sidebar Component
 * Conversation history with search, new chat, and actions
 */
export function Sidebar({
  conversations = [],
  currentId,
  onNewChat,
  onSelect,
  onDelete,
  onArchive,
  onClearHistory
}) {
  const [searchText, setSearchText] = useState('');
  const [showContextMenu, setShowContextMenu] = useState(null);
  const [hoveredConvId, setHoveredConvId] = useState(null);
  const [hoverPos, setHoverPos] = useState({ top: 0, right: 0 });
  const { language, t } = useLanguage();

  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchText.toLowerCase()) ||
    conv.preview?.toLowerCase().includes(searchText.toLowerCase())
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const MathFloor = Math.floor;
    const hours = MathFloor(diff / 3600000);

    if (diff < 60000) return t('sidebar.just_now');
    if (diff < 3600000) return `${MathFloor(diff / 60000)} ${t('sidebar.mins_ago')}`;
    if (hours <= 24) return `${hours} ${t('sidebar.hours_ago')}`;
    return date.toLocaleDateString(language === 'ar' ? 'ar-SA' : 'en-US');
  };

  const handleDelete = (id, e) => {
    e.stopPropagation();
    if (window.confirm(t('sidebar.delete_confirm'))) {
      onDelete(id);
    }
  };

  const handleClearAll = () => {
    if (window.confirm(t('sidebar.clear_confirm'))) {
      onClearHistory();
    }
  };

  return (
    <aside className="app-sidebar">
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <button
          className="sidebar-new-chat btn-primary"
          onClick={onNewChat}
          title={t('app.new_chat')}
        >
          <Plus size={18} />
          <div className="btn-text-stack">
            <span className="app-sidebar-text">{t('app.new_chat')}</span>
          </div>
        </button>
      </div>

      {/* Search */}
      <div className="sidebar-search-container" style={{ padding: '0 1rem 1rem 1rem' }}>
        <input
          type="text"
          placeholder={t('sidebar.search')}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="sidebar-search"
          style={{ width: '100%', padding: '0.5rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-gray-200)' }}
        />
      </div>

      {/* Conversations List */}
      <div className="sidebar-content">
        {filteredConversations.length === 0 ? (
          <div className="sidebar-empty-state" style={{ padding: '2rem', textAlign: 'center', opacity: 0.5 }}>
            <div>{t('sidebar.no_conv')}</div>
          </div>
        ) : (
          filteredConversations.map(conv => (
            <div
              key={conv.id}
              className={`conversation-item ${currentId === conv.id ? 'active' : ''}`}
              onClick={() => onSelect(conv.id)}
              onMouseEnter={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                setHoverPos({
                  top: rect.top + (rect.height / 2),
                  right: window.innerWidth - rect.left + 10 // Position to the left of the item
                });
                setHoveredConvId(conv.id);
              }}
              onMouseLeave={() => setHoveredConvId(null)}
              onContextMenu={(e) => {
                e.preventDefault();
                setShowContextMenu(conv.id);
              }}
            >
              <MessageSquare size={16} className="conversation-icon" />

              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="conversation-title">
                  {conv.title || (
                    <div className="title-stack">
                      <span>{t('sidebar.untitled')}</span>
                    </div>
                  )}
                </div>
                <div className="conversation-preview">
                  {conv.preview || '...'}
                </div>
                <div className="conversation-time">
                  {formatTime(conv.timestamp)}
                </div>
              </div>

              {/* Action Buttons on Hover */}
              <div className="conversation-actions">
                <button
                  className="btn-action-sm destructive"
                  onClick={(e) => handleDelete(conv.id, e)}
                  title={t('sidebar.delete')}
                >
                  <Trash2 size={14} />
                </button>
                <button
                  className="btn-action-sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onArchive(conv.id);
                  }}
                  title={t('sidebar.archive')}
                >
                  <Archive size={14} />
                </button>
              </div>

              {/* Context Menu (Alternative) */}
              {showContextMenu === conv.id && (
                <div className="context-menu" onClick={e => e.stopPropagation()}>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '4px' }}>
                    <button className="btn-icon-xs" onClick={() => setShowContextMenu(null)}>
                      <X size={12} />
                    </button>
                  </div>
                  <button
                    className="context-menu-item"
                    onClick={(e) => {
                      e.stopPropagation();
                      onArchive(conv.id);
                      setShowContextMenu(null);
                    }}
                  >
                    <Archive size={14} style={{ marginLeft: '0.5rem' }} />
                    <div className="menu-text-stack">
                      <span>{t('sidebar.archive')}</span>
                    </div>
                  </button>
                  <button
                    className="context-menu-item destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(conv.id, e);
                      setShowContextMenu(null);
                    }}
                  >
                    <Trash2 size={14} style={{ marginLeft: '0.5rem' }} />
                    <div className="menu-text-stack">
                      <span>{t('sidebar.delete')}</span>
                    </div>
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Clear All Footer */}
      {conversations.length > 0 && (
        <div className="sidebar-footer" style={{ padding: '1rem', borderTop: '1px solid var(--color-gray-200)' }}>
          <button
            className="btn-secondary"
            onClick={handleClearAll}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              color: 'var(--color-error)',
              borderColor: 'var(--color-gray-200)',
              background: 'transparent',
              padding: '0.5rem',
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer'
            }}
          >
            <Trash2 size={16} />
            <div className="btn-text-stack">
              <span>{t('sidebar.clear_history')}</span>
            </div>
          </button>
        </div>
      )}
      {/* Global Tooltip Rendering (Portal) */}
      {hoveredConvId && (
        (() => {
          const conv = conversations.find(c => c.id === hoveredConvId);
          if (!conv) return null;
          return ReactDOM.createPortal(
            <div
              className="conversation-tooltip fixed-tooltip"
              style={{
                top: hoverPos.top,
                right: hoverPos.right
              }}
            >
              {conv.summary ? (
                <>
                  <div className="tooltip-title">{language === 'en' && conv.summary.topic_en ? conv.summary.topic_en : (conv.summary.topic || conv.title)}</div>
                  <div className="tooltip-points">
                    <ul style={{ paddingRight: '1rem', margin: 0, fontSize: '0.75rem', lineHeight: '1.4' }}>
                      {conv.summary.points && conv.summary.points.length > 0 ? (
                        (language === 'en' && conv.summary.points_en ? conv.summary.points_en : conv.summary.points).map((point, idx) => (
                          <li key={idx}>{point}</li>
                        ))
                      ) : (
                        <li>{t('sidebar.no_points')}</li>
                      )}
                    </ul>
                  </div>
                </>
              ) : (
                <>
                  <div className="tooltip-title">{conv.title || t('sidebar.untitled')}</div>
                  <div className="tooltip-preview">{conv.preview || t('sidebar.no_summary')}</div>
                </>
              )}
            </div>,
            document.body // Render at body root to break z-index/overflow issues from sidebar
          );
        })()
      )}
    </aside>
  );
}

export default Sidebar;
