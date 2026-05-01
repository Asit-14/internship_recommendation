'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import languages from '../locales/languages.json';

type Translations = Record<string, string>;

interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
  availableLanguages: typeof languages;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('language');
      if (savedLang && languages.some(l => l.code === savedLang)) {
        return savedLang;
      }
    }
    return 'en';
  });
  const [translations, setTranslations] = useState<Translations>({});

  // Lazy load translations
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const res = await import(`../locales/${language}.json`);
        setTranslations(res.default || res);
      } catch (error) {
        console.error(`Failed to load translations for ${language}`, error);
        if (language !== 'en') {
          const fallback = await import('../locales/en.json');
          setTranslations(fallback.default || fallback);
        }
      }
    };
    loadTranslations();
  }, [language]);

  const setLanguage = useCallback((lang: string) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
  }, []);

  const t = useCallback(
    (key: string): string => {
      // Split key by dot to allow nested keys if ever needed, though we use flat keys
      return translations[key] || key;
    },
    [translations]
  );

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, availableLanguages: languages }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};
