import { Settings } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

/**
 * Header Component
 * Fixed header with logo, status indicator, and controls
 * - Desktop: Full header with text and status
 * - Mobile: Icon-only header with compact status
 */
export function Header({
  healthStatus = 'idle',
  onSettings
}) {
  const { language, toggleLanguage, t } = useLanguage();

  const getStatusInfo = () => {
    switch (healthStatus) {
      case 'connected':
        return { text: t('header.connected'), class: 'connected', dot: '●' };
      case 'disconnected':
        return { text: t('header.disconnected'), class: 'disconnected', dot: '●' };
      case 'connecting':
        return { text: t('header.connecting'), class: 'connecting', dot: '●' };
      default:
        return { text: t('header.checking'), class: 'idle', dot: '●' };
    }
  };

  const status = getStatusInfo();

  return (
    <header className="app-header">
      {/* Logo Section */}
      <div className="header-logo">
        <div className="header-logo-text" style={{ alignItems: language === 'ar' ? 'flex-end' : 'flex-start' }}>
          <h1>{t('app.title')}</h1>
          <p>{t('app.subtitle')}</p>
          <p style={{ color: 'var(--color-text-tertiary)', fontSize: '0.85rem' }}>{t('app.subtitle2')}</p>
        </div>
      </div>

      {/* Controls */}
      <div className="header-controls">
        <div className="status-indicator" title={status.text}>
          <div className={`status-dot ${status.class}`} />
          <div className="status-text-stack">
            <span>{status.text}</span>
          </div>
        </div>

        {/* Language Toggle */}
        <button
          className="btn-icon btn-icon-white"
          onClick={toggleLanguage}
          title={language === 'ar' ? 'English' : 'عربي'}
        >
          {language === 'ar' ? 'EN' : 'AR'}
        </button>

        {/* Settings Button */}
        <button
          className="btn-icon btn-icon-white"
          onClick={onSettings}
          title={t('header.settings')}
        >
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
}

export default Header;
