import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { Plus, MessageSquare, Trash2, Archive, X } from 'lucide-react';
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

  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchText.toLowerCase()) ||
    conv.preview?.toLowerCase().includes(searchText.toLowerCase())
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / 3600000);

    if (diff < 60000) return 'الآن | Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} دقيقة | ${Math.floor(diff / 60000)}m ago`;
    if (hours <= 24) return `${hours} ساعات | ${hours}h ago`;
    return date.toLocaleDateString('ar-SA');
  };

  const handleDelete = (id, e) => {
    e.stopPropagation();
    if (window.confirm('هل أنت متأكد من حذف هذه المحادثة؟\nAre you sure you want to delete this conversation?')) {
      onDelete(id);
    }
  };

  const handleClearAll = () => {
    if (window.confirm('هل أنت متأكد من مسح جميع المحادثات نهائياً؟\nAre you sure you want to permanently delete all conversations?')) {
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
          title="محادثة جديدة"
        >
          <Plus size={18} />
          <div className="btn-text-stack">
            <span className="app-sidebar-text">محادثة جديدة</span>
            <span className="en-small">New Chat</span>
          </div>
        </button>
      </div>

      {/* Search */}
      <div className="sidebar-search-container" style={{ padding: '0 1rem 1rem 1rem' }}>
        <input
          type="text"
          placeholder="بحث عن محادثة... | Search chats..."
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
            <div>لا توجد محادثات</div>
            <div className="en-small">No conversations found</div>
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

              {/* Tooltip Removed form here - Handled outside loop via Portal-like div */}

              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="conversation-title">
                  {conv.title || (
                    <div className="title-stack">
                      <span>محادثة بدون عنوان</span>
                      <span className="en-tiny">Untitled Conversation</span>
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
                  title="حذف | Delete"
                >
                  <Trash2 size={14} />
                </button>
                <button
                  className="btn-action-sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onArchive(conv.id);
                  }}
                  title="أرشفة | Archive"
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
                      <span>أرشفة</span>
                      <span className="en-tiny">Archive</span>
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
                      <span>حذف</span>
                      <span className="en-tiny">Delete</span>
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
              <span>مسح السجل بالكامل</span>
              <span className="en-tiny">Clear Entire History</span>
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
                  <div className="tooltip-title">{conv.summary.topic || conv.title}</div>
                  <div className="tooltip-points">
                    <ul style={{ paddingRight: '1rem', margin: 0, fontSize: '0.75rem', lineHeight: '1.4' }}>
                      {conv.summary.points && conv.summary.points.length > 0 ? (
                        conv.summary.points.map((point, idx) => (
                          <li key={idx}>{point}</li>
                        ))
                      ) : (
                        <li>لا توجد نقاط رئيسية</li>
                      )}
                    </ul>
                  </div>
                </>
              ) : (
                <>
                  <div className="tooltip-title">{conv.title || 'محادثة بدون عنوان'}</div>
                  <div className="tooltip-preview">{conv.preview || 'لا يوجد ملخص متاح | No summary available'}</div>
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
