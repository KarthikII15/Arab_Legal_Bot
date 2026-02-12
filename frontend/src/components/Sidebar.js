import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Archive } from 'lucide-react';

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
  onArchive
}) {
  const [searchText, setSearchText] = useState('');
  const [showContextMenu, setShowContextMenu] = useState(null);

  const filteredConversations = conversations.filter(conv =>
    conv.title?.toLowerCase().includes(searchText.toLowerCase()) ||
    conv.preview?.toLowerCase().includes(searchText.toLowerCase())
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const hours = Math.floor(diff / 3600000);

    if (diff < 60000) return 'الآن';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} دقيقة`;
    if (hours <= 24) return `${hours} ساعات`;
    return date.toLocaleDateString('ar-SA');
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
          <span className="app-sidebar-text">محادثة جديدة</span>
        </button>
      </div>

      {/* Search */}
      <div className="sidebar-search-container">
        <input
          type="text"
          placeholder="بحث عن محادثة..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="sidebar-search-input"
        />
      </div>

      {/* Conversations List */}
      <div className="sidebar-content">
        {filteredConversations.length === 0 ? (
          <div className="sidebar-empty-state">
            لا توجد محادثات
          </div>
        ) : (
          filteredConversations.map(conv => (
            <div
              key={conv.id}
              className={`conversation-item ${currentId === conv.id ? 'active' : ''}`}
              onClick={() => onSelect(conv.id)}
              onContextMenu={(e) => {
                e.preventDefault();
                setShowContextMenu(conv.id);
              }}
            >
              <MessageSquare size={16} className="conversation-icon" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="conversation-title">
                  {conv.title || 'محادثة بدون عنوان'}
                </div>
                <div className="conversation-preview">
                  {conv.preview || '...'}
                </div>
                <div className="conversation-time">
                  {formatTime(conv.timestamp)}
                </div>
              </div>

              {/* Context Menu */}
              {showContextMenu === conv.id && (
                <div className="context-menu">
                  <button
                    className="context-menu-item"
                    onClick={(e) => {
                      e.stopPropagation();
                      onArchive(conv.id);
                      setShowContextMenu(null);
                    }}
                  >
                    <Archive size={14} style={{ marginLeft: '0.5rem' }} />
                    أرشفة
                  </button>
                  <button
                    className="context-menu-item destructive"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(conv.id);
                      setShowContextMenu(null);
                    }}
                  >
                    <Trash2 size={14} style={{ marginLeft: '0.5rem' }} />
                    حذف
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
