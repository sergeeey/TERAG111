import { Languages } from 'lucide-react';
import { useLanguage } from '../../i18n/LanguageContext';

export function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'ru' : 'en');
  };

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-300 border border-[#00FFE0]/20 hover:border-[#00FFE0]/40"
      title={language === 'en' ? 'Switch to Russian' : 'Переключить на английский'}
    >
      <Languages className="w-4 h-4 text-[#00FFE0]" />
      <span className="text-sm font-semibold text-white">
        {language === 'en' ? 'EN' : 'RU'}
      </span>
    </button>
  );
}
