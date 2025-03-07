import i18n from 'i18next';
import detector from 'i18next-browser-languagedetector';
import Backend from 'i18next-xhr-backend';
import { initReactI18next } from 'react-i18next';

// Get stored language from localStorage or default to 'en'
const storedLanguage = localStorage.getItem('i18nextLng') || 'en';

i18n
  .use(Backend)
  .use(detector)
  .use(initReactI18next)
  .init({
    supportedLngs: ['en', 'th'],
    lng: storedLanguage,
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json' // Simplified loadPath
    },
    ns: [
      'common',
      'login',
      'home',
      'approval',
      'approval-center',
      'approval-setting',
      'organization',
      'register',
      'reports',
      'settings',
      'super-admin',
      'business-partner',
      'project'
    ],
    defaultNS: 'common',
    fallbackLng: ['en', 'th'],
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    },
    react: {
      useSuspense: false // This helps prevent issues during loading
    }
  });

export default i18n;
