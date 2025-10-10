# TERAG Immersive Shell - Russian Language Support / Поддержка русского языка

## Overview / Обзор

TERAG Immersive Shell v1.1 now includes full Russian language support with automatic language detection and seamless switching between English and Russian.

TERAG Immersive Shell v1.1 теперь включает полную поддержку русского языка с автоматическим определением языка и плавным переключением между английским и русским.

## Features / Возможности

### English
- **Complete UI Translation**: All interface elements translated to Russian
- **TTS Support**: Text-to-Speech works with Russian voices
- **Language Toggle**: Easy switching between EN and RU
- **Persistent Settings**: Language choice saved to localStorage
- **Welcome Screen**: Localized welcome messages and instructions
- **Voice Mode**: Russian voice recognition and synthesis

### Русский
- **Полный перевод интерфейса**: Все элементы интерфейса переведены на русский
- **Поддержка TTS**: Синтез речи работает с русскими голосами
- **Переключение языка**: Простое переключение между EN и RU
- **Сохранение настроек**: Выбор языка сохраняется в localStorage
- **Экран приветствия**: Локализованные приветственные сообщения
- **Голосовой режим**: Распознавание и синтез русской речи

## Usage / Использование

### Switching Language / Переключение языка

**English:**
1. Look for the language selector in the top-right corner
2. Click the button showing "EN" or "RU"
3. Interface immediately switches to selected language
4. Choice is saved automatically

**Русский:**
1. Найдите переключатель языка в правом верхнем углу
2. Нажмите кнопку с надписью "EN" или "RU"
3. Интерфейс сразу переключится на выбранный язык
4. Выбор сохраняется автоматически

### Voice Mode in Russian / Голосовой режим на русском

**English:**
1. Switch to Russian language (RU button)
2. Click "Голосовой Режим" (Voice Mode)
3. Speak in Russian
4. TERAG responds in Russian with TTS

**Русский:**
1. Переключите язык на русский (кнопка RU)
2. Нажмите "Голосовой Режим"
3. Говорите по-русски
4. TERAG ответит на русском с озвучкой

## Translated Elements / Переведённые элементы

### Welcome Screen / Экран приветствия
- **EN**: "Welcome to TERAG" → **RU**: "Добро пожаловать в TERAG"
- **EN**: "A Cognitive Alignment System" → **RU**: "Система Когнитивного Выравнивания"
- **EN**: "Where Intelligence Breathes" → **RU**: "Где Интеллект Дышит"
- **EN**: "Begin Dialogue" → **RU**: "Начать Диалог"

### Cognitive Console / Когнитивная Консоль
- **EN**: "Ask TERAG anything..." → **RU**: "Спросите TERAG о чём угодно..."
- **EN**: "Voice Mode" → **RU**: "Голосовой Режим"
- **EN**: "Text Mode" → **RU**: "Текстовый Режим"
- **EN**: "TERAG Response" → **RU**: "Ответ TERAG"

### Status Messages / Статусные сообщения
- **EN**: "Listening to your voice..." → **RU**: "Слушаю ваш голос..."
- **EN**: "TERAG is reasoning..." → **RU**: "TERAG размышляет..."
- **EN**: "TERAG is speaking..." → **RU**: "TERAG говорит..."

### Metrics HUD / Панель метрик
- **EN**: "Cognitive Metrics" → **RU**: "Когнитивные Метрики"
- **EN**: "IEI Score" → **RU**: "IEI Оценка"
- **EN**: "Coherence" → **RU**: "Когерентность"
- **EN**: "Faithfulness" → **RU**: "Точность"
- **EN**: "System Status" → **RU**: "Статус Системы"
- **EN**: "ONLINE" → **RU**: "В СЕТИ"
- **EN**: "OFFLINE" → **RU**: "НЕ В СЕТИ"

### Agent Names / Имена агентов
- **EN**: "Planner" → **RU**: "Планировщик"
- **EN**: "Intuit" → **RU**: "Интуитор"
- **EN**: "Critic" → **RU**: "Критик"
- **EN**: "Verifier" → **RU**: "Верификатор"
- **EN**: "Curator" → **RU**: "Куратор"
- **EN**: "Reflector" → **RU**: "Рефлектор"
- **EN**: "Meta-Controller" → **RU**: "Мета-Контроллер"

## Technical Implementation / Техническая реализация

### Architecture / Архитектура

```typescript
// Language Context
src/i18n/
  ├── translations.ts       // EN & RU translations
  ├── LanguageContext.tsx   // React Context for i18n

// Components
src/components/
  ├── ui/LanguageSelector.tsx
  └── immersive/
      ├── WelcomeScreen.tsx (updated)
      └── VoiceOutput.tsx (updated for RU TTS)
```

### Translation Keys / Ключи переводов

```typescript
t('welcome.title1')           // "Welcome to TERAG" / "Добро пожаловать в TERAG"
t('console.placeholder')      // Input placeholder
t('states.listening')         // Voice state messages
t('hud.title')               // HUD components
t('agents.planner')          // Agent names
```

### Adding New Translations / Добавление новых переводов

**English:**
1. Open `src/i18n/translations.ts`
2. Add key to both `en` and `ru` objects
3. Use `t('your.key')` in components

**Русский:**
1. Откройте `src/i18n/translations.ts`
2. Добавьте ключ в объекты `en` и `ru`
3. Используйте `t('your.key')` в компонентах

Example / Пример:
```typescript
export const translations = {
  en: {
    mySection: {
      greeting: 'Hello',
    },
  },
  ru: {
    mySection: {
      greeting: 'Здравствуйте',
    },
  },
};

// In component:
const { t } = useLanguage();
<p>{t('mySection.greeting')}</p>
```

## TTS Voice Selection / Выбор голоса TTS

### Automatic Voice Detection / Автоматическое определение голоса

The system automatically selects appropriate TTS voices:

Система автоматически выбирает подходящие голоса TTS:

**English Voices:**
- Google US English
- Microsoft David
- Microsoft Zira

**Russian Voices / Русские голоса:**
- Google русский
- Microsoft Irina
- Microsoft Pavel
- Yandex (if available)

### Browser Support / Поддержка браузеров

| Browser / Браузер | Russian TTS | Quality / Качество |
|-------------------|-------------|--------------------|
| Chrome            | ✅           | Excellent / Отлично |
| Edge              | ✅           | Excellent / Отлично |
| Firefox           | ✅           | Good / Хорошо      |
| Safari            | ⚠️          | Limited / Ограничено |

## Testing / Тестирование

### Test Steps / Шаги тестирования

**English:**
1. Start app: `npm run dev`
2. Navigate to `/immersive`
3. Click RU button in top-right
4. Verify Welcome screen is in Russian
5. Click "Начать Диалог"
6. Type Russian query
7. Enable Voice Mode
8. Speak in Russian
9. Verify TTS responds in Russian

**Русский:**
1. Запустите приложение: `npm run dev`
2. Перейдите на `/immersive`
3. Нажмите кнопку RU в верхнем правом углу
4. Убедитесь, что экран приветствия на русском
5. Нажмите "Начать Диалог"
6. Введите запрос на русском
7. Включите Голосовой Режим
8. Говорите по-русски
9. Убедитесь, что TTS отвечает по-русски

## Known Issues / Известные проблемы

### Safari TTS
- **Issue / Проблема**: Limited Russian voice selection
- **Workaround / Решение**: Use Chrome or Edge for best experience

### Mobile Browsers
- **Issue / Проблема**: Some mobile browsers have limited TTS
- **Workaround / Решение**: Test on desktop first

## Future Enhancements / Будущие улучшения

### Planned Features / Планируемые функции

**English:**
- Ukrainian language support
- Belarusian language support
- Context-aware translations
- Regional dialect support
- Custom voice personas

**Русский:**
- Поддержка украинского языка
- Поддержка белорусского языка
- Контекстно-зависимые переводы
- Поддержка региональных диалектов
- Настраиваемые голосовые персоны

## Contributing Translations / Помощь с переводами

**English:**
To contribute or improve Russian translations:
1. Fork the repository
2. Edit `src/i18n/translations.ts`
3. Test your changes
4. Submit a pull request

**Русский:**
Чтобы помочь улучшить русские переводы:
1. Сделайте fork репозитория
2. Отредактируйте `src/i18n/translations.ts`
3. Протестируйте изменения
4. Отправьте pull request

## Examples / Примеры

### English Example
```typescript
import { useLanguage } from './i18n/LanguageContext';

function MyComponent() {
  const { t, language, setLanguage } = useLanguage();

  return (
    <div>
      <h1>{t('welcome.title1')}</h1>
      <button onClick={() => setLanguage('ru')}>
        Switch to Russian
      </button>
    </div>
  );
}
```

### Русский пример
```typescript
import { useLanguage } from './i18n/LanguageContext';

function MyComponent() {
  const { t, language, setLanguage } = useLanguage();

  return (
    <div>
      <h1>{t('welcome.title1')}</h1>
      <button onClick={() => setLanguage('en')}>
        Переключить на английский
      </button>
    </div>
  );
}
```

---

**Version / Версия**: 1.1.0
**Status / Статус**: Production Ready / Готово к продакшену
**Last Updated / Последнее обновление**: 2025-10-10
