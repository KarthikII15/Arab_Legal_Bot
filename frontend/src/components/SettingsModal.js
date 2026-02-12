import React from 'react';
import { X, Sun, Moon, Trash2, Type } from 'lucide-react';

/**
 * SettingsModal Component
 * Allows users to configure application preferences.
 */
export function SettingsModal({
    isOpen,
    onClose,
    theme,
    onToggleTheme,
    fontSize,
    onFontSizeChange,
    onClearData
}) {
    if (!isOpen) return null;

    const fontSizes = [
        { value: 'small', label: 'صغير', labelEn: 'Small' },
        { value: 'medium', label: 'متوسط', labelEn: 'Medium' },
        { value: 'large', label: 'كبير', labelEn: 'Large' },
        { value: 'xl', label: 'كبير جداً', labelEn: 'Extra Large' },
    ];

    return (
        <div className="settings-modal-overlay" onClick={onClose}>
            <div className="settings-modal" onClick={e => e.stopPropagation()}>
                <div className="settings-header">
                    <h2>الإعدادات | Settings</h2>
                    <button className="btn-icon" onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>

                <div className="settings-content">
                    {/* Appearance Section */}
                    <section className="settings-section">
                        <h3>المظهر | Appearance</h3>
                        <div className="settings-row">
                            <span>الوضع الليلي / النهاري</span>
                            <button
                                className="btn-secondary theme-toggle-btn"
                                onClick={onToggleTheme}
                            >
                                {theme === 'light' ? (
                                    <>
                                        <Moon size={18} />
                                        <span>الوضع الليلي (Dark)</span>
                                    </>
                                ) : (
                                    <>
                                        <Sun size={18} />
                                        <span>الوضع النهاري (Light)</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </section>

                    {/* Typography Section */}
                    <section className="settings-section">
                        <h3>حجم الخط | Font Size</h3>
                        <div className="font-size-options">
                            {fontSizes.map((size) => (
                                <button
                                    key={size.value}
                                    className={`btn-option ${fontSize === size.value ? 'active' : ''}`}
                                    onClick={() => onFontSizeChange(size.value)}
                                >
                                    <span style={{ fontSize: size.value === 'small' ? '0.875rem' : size.value === 'medium' ? '1rem' : size.value === 'large' ? '1.125rem' : '1.25rem' }}>
                                        A
                                    </span>
                                    <span>{size.label}</span>
                                </button>
                            ))}
                        </div>
                    </section>

                    {/* Data Section */}
                    <section className="settings-section destructive">
                        <h3>البيانات | Data</h3>
                        <div className="settings-row">
                            <span>مسح جميع البيانات والمحادثات</span>
                            <button
                                className="btn-danger"
                                onClick={() => {
                                    if (window.confirm('هل أنت متأكد من مسح جميع البيانات؟ لا يمكن التراجع عن هذا الإجراء.\nAre you sure you want to clear all data? This cannot be undone.')) {
                                        onClearData();
                                    }
                                }}
                            >
                                <Trash2 size={18} />
                                <span>مسح البيانات (Clear Data)</span>
                            </button>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}

export default SettingsModal;
