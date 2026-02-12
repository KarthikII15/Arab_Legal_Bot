import React from 'react';

/**
 * Layout Component
 * 3-Column Responsive Grid Layout
 * - Desktop: Sidebar (280px) | Content | Tools (320px)
 * - Tablet: Icon Bar (64px) | Content
 * - Mobile: Full width with bottom navigation
 */
export function Layout({ children, showTools = true, showSidebar = true }) {
  return (
    <div className={`app-layout ${!showSidebar ? 'sidebar-hidden' : ''} ${!showTools ? 'tools-hidden' : ''}`}>
      {children}
    </div>
  );
}

export default Layout;
