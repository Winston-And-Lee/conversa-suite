import { Button, Space } from 'antd';
import { useTranslation } from 'react-i18next';

export const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'th' : 'en';
    localStorage.setItem('i18nextLng', newLang);
    i18n.changeLanguage(newLang);
  };

  return (
    <Space style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 1000 }}>
      <Button onClick={toggleLanguage}>{i18n.language === 'en' ? 'ไทย' : 'English'}</Button>
    </Space>
  );
};
