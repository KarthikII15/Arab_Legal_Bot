import React, { createContext, useState, useEffect, useContext } from 'react';
import { getStorageItem, setStorageItem } from '../utils/storage';
import { translations } from '../translations';

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState(() => getStorageItem('language', 'ar'));

    useEffect(() => {
        document.documentElement.setAttribute('lang', language);
        document.documentElement.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
        setStorageItem('language', language);
    }, [language]);

    const toggleLanguage = () => {
        setLanguage(prev => (prev === 'ar' ? 'en' : 'ar'));
    };

    const t = (key) => {
        const keys = key.split('.');
        let result = translations[language];
        for (const k of keys) {
            if (result && result[k]) {
                result = result[k];
            } else {
                return key; // Fallback to key
            }
        }
        return result;
    };

    return (
        <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => useContext(LanguageContext);
