# Развертывание Streamlit Demo на Render.com

## Быстрый старт (5 минут)

### Шаг 1: Создать аккаунт на Render.com
1. Перейти на https://render.com
2. Зарегистрироваться через GitHub (рекомендуется)
3. Подтвердить email

### Шаг 2: Создать новый Web Service
1. В Dashboard нажать "New +" → "Web Service"
2. Подключить GitHub репозиторий TERAG
3. Выбрать branch: `main`

### Шаг 3: Настроить конфигурацию
1. **Name:** `terag-demo`
2. **Environment:** `Python 3`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `streamlit run demo/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

### Шаг 4: Добавить переменные окружения
В разделе "Environment Variables" добавить:

```
TERAG_API_URL=https://your-api-url.render.com
NEO4J_URI=bolt://your-neo4j-url:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
MONGODB_URI=mongodb://your-mongodb-url
TELEGRAM_BOT_TOKEN=your-token (опционально)
TELEGRAM_CHAT_ID=your-chat-id (опционально)
```

**Примечание:** Для demo можно оставить `TERAG_API_URL` пустым - будет работать Demo Mode.

### Шаг 5: Запустить деплой
1. Нажать "Create Web Service"
2. Дождаться завершения build (2-3 минуты)
3. Получить публичный URL: `https://terag-demo.onrender.com`

---

## Альтернатива: Streamlit Cloud (бесплатно, проще)

### Если Render.com не работает:

1. Перейти на https://streamlit.io/cloud
2. Войти через GitHub
3. Нажать "New app"
4. Выбрать репозиторий TERAG
5. Main file path: `demo/streamlit_app.py`
6. Нажать "Deploy"

**Преимущества:**
- Бесплатно навсегда
- Автоматический деплой при пуше
- Проще настройка

**Недостатки:**
- Меньше контроля над окружением
- Ограничения на ресурсы

---

## Проверка работоспособности

После деплоя проверить:

1. **Главная страница:** Должна загрузиться без ошибок
2. **Demo Mode:** Включить в настройках, проверить работу без API
3. **Auto Linker:** Загрузить `data/demo/mfo_clients_sample.json`, проверить связывание
4. **Fraud Detection:** Запустить детекцию, проверить результаты

---

## Troubleshooting

### Проблема: App не запускается
**Решение:** Проверить логи в Render Dashboard → Logs

### Проблема: Demo Mode не работает
**Решение:** Убедиться, что `demo_mode = True` в sidebar

### Проблема: API запросы не работают
**Решение:** Проверить `TERAG_API_URL` в переменных окружения

---

## Обновление demo

После изменений в коде:
1. Закоммитить изменения в `main` branch
2. Render автоматически пересоберет и задеплоит
3. Или нажать "Manual Deploy" в Dashboard

---

## Стоимость

**Render.com Starter Plan:**
- $7/мес (или бесплатно с ограничениями)
- 512 MB RAM
- Достаточно для demo

**Streamlit Cloud:**
- Бесплатно
- Ограничения на использование
