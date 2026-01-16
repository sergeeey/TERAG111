# 🧠 Learning Bridge — Когнитивная адаптация TERAG

## 🎯 Концепция

**Learning Bridge** — это мост между LM Studio (reasoning) и TERAG Graph (память), который создаёт цикл самообучения:

```
Запрос → Контекст из графа → LM Studio рассуждает → Сохранение в граф → Улучшенный контекст
```

### Компоненты:

- **LM Studio** = рабочая память и интеллект (рассуждает)
- **TERAG Graph** = долговременная память (хранит факты и связи)
- **Learning Bridge** = мост между ними (обмен знаниями)

---

## 🚀 Быстрый старт

### 1. Инициализация

```python
from src.integration.learning_bridge import LearningBridge
from src.integration.lmstudio_client import LMStudioClient
from installer.app.modules.graph_updater import GraphUpdater

# Инициализация компонентов
lm_client = LMStudioClient()
await lm_client.connect()

graph_updater = GraphUpdater(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="terag_neo4j_2025"
)

bridge = LearningBridge(lm_client=lm_client, graph_updater=graph_updater)
```

### 2. Reasoning с контекстом

```python
# Выполнить reasoning с контекстом из графа
result = await bridge.reason_with_context(
    question="What are best practices for error handling in Python?",
    domain="Programming",
    save_result=True  # Сохранить результат в граф
)

print(f"Answer: {result['text']}")
print(f"Context used: {result['context_used']}")
```

### 3. Получение best practices

```python
# Получить лучшие практики из графа
practices = bridge.get_best_practices("Programming", limit=5)

for practice in practices:
    print(f"- {practice['concept']} (confidence: {practice['confidence']:.2f})")
```

---

## 📚 API Reference

### `LearningBridge.__init__(lm_client, graph_updater, default_domain="General")`

Инициализация Learning Bridge.

**Параметры:**
- `lm_client`: Экземпляр `LMStudioClient`
- `graph_updater`: Экземпляр `GraphUpdater`
- `default_domain`: Домен по умолчанию для классификации

---

### `async get_context_from_graph(domain=None, concept=None, limit=5) -> str`

Получить контекст из графа знаний для reasoning.

**Параметры:**
- `domain` (str, optional): Домен для фильтрации (например, "Programming", "AI")
- `concept` (str, optional): Концепт для поиска связанных фактов
- `limit` (int): Максимальное количество фактов (по умолчанию 5)

**Возвращает:**
- `str`: Текстовый контекст для промпта

**Пример:**
```python
# Контекст по домену
context = await bridge.get_context_from_graph(domain="Programming", limit=5)

# Контекст по концепту
context = await bridge.get_context_from_graph(concept="Python", limit=3)
```

---

### `async classify_domain(text: str) -> str`

Классифицировать домен для текста с помощью LM Studio.

**Параметры:**
- `text` (str): Текст для классификации

**Возвращает:**
- `str`: Название домена ("Programming", "AI", "Psychology", "OSINT", "General")

**Пример:**
```python
domain = await bridge.classify_domain("Python error handling best practices")
# Возвращает: "Programming"
```

---

### `async learn_from_result(category, text, confidence=0.9, source_url=None) -> Dict`

Сохранить результат reasoning LM Studio как знание в граф.

**Параметры:**
- `category` (str): Категория знания (например, "BestPractice", "Pattern")
- `text` (str): Текст результата reasoning
- `confidence` (float): Уровень уверенности (0.0-1.0, по умолчанию 0.9)
- `source_url` (str, optional): URL источника

**Возвращает:**
- `Dict`: Информация о сохранённом знании:
  - `saved` (bool): Успешно ли сохранено
  - `domain` (str): Классифицированный домен
  - `facts_count` (int): Количество сохранённых фактов
  - `facts` (List[str]): Список сохранённых фактов

**Пример:**
```python
result = await bridge.learn_from_result(
    category="BestPractice",
    text="Use try-except blocks for error handling in Python",
    confidence=0.9,
    source_url="https://example.com"
)
```

---

### `async reason_with_context(question, domain=None, save_result=True) -> Dict`

Выполнить reasoning с контекстом из графа.

**Параметры:**
- `question` (str): Вопрос для reasoning
- `domain` (str, optional): Домен для фильтрации контекста
- `save_result` (bool): Сохранять ли результат в граф (по умолчанию True)

**Возвращает:**
- `Dict`: Результат reasoning с метаданными:
  - `text` (str): Текст ответа
  - `context_used` (bool): Использовался ли контекст
  - `domain` (str): Домен
  - `learned` (Dict, optional): Информация о сохранённых знаниях

**Пример:**
```python
result = await bridge.reason_with_context(
    question="What are best practices for error handling?",
    domain="Programming",
    save_result=True
)
```

---

### `get_best_practices(domain, limit=3) -> List[Dict]`

Получить "best practices" из графа для домена.

**Параметры:**
- `domain` (str): Домен для поиска
- `limit` (int): Максимальное количество практик (по умолчанию 3)

**Возвращает:**
- `List[Dict]`: Список best practices:
  - `concept` (str): Название концепта
  - `novelty` (float): Оценка новизны
  - `confidence` (float): Уровень уверенности

**Пример:**
```python
practices = bridge.get_best_practices("Programming", limit=5)
```

---

## 🔄 Цикл обучения

После реализации Learning Bridge, TERAG работает в цикле:

```
1. Запрос → Learning Bridge получает контекст из графа
2. LM Studio рассуждает с контекстом → генерирует ответ
3. Learning Bridge сохраняет результат в граф → новые знания
4. Следующий запрос использует обновлённый контекст → улучшенный ответ
```

---

## 🧪 Тестирование

### Запуск теста

```bash
python scripts/tests/test_learning_bridge.py
```

Тест проверяет:
- ✅ Получение контекста из графа
- ✅ Классификацию доменов
- ✅ Reasoning с контекстом
- ✅ Сохранение результатов в граф
- ✅ Получение best practices

---

## 📊 Примеры использования

### Пример 1: Reasoning с контекстом

```python
# Вопрос о best practices
result = await bridge.reason_with_context(
    question="How to handle errors in Python?",
    domain="Programming"
)

# Ответ будет учитывать накопленные знания из графа
print(result['text'])
```

### Пример 2: Сохранение знаний

```python
# Сохранить результат reasoning
learn_result = await bridge.learn_from_result(
    category="BestPractice",
    text="Use context managers for resource management",
    confidence=0.9
)

print(f"Saved {learn_result['facts_count']} facts to graph")
```

### Пример 3: Получение контекста

```python
# Получить контекст для промпта
context = await bridge.get_context_from_graph(
    domain="Programming",
    limit=5
)

# Использовать контекст в промпте
prompt = f"{context}\n\nQuestion: {question}"
```

---

## 🔗 Интеграция

### С MissionRunner

```python
from installer.app.modules.mission_runner import MissionRunner

# В методе _run_reasoning()
bridge = LearningBridge(lm_client, graph_updater)
result = await bridge.reason_with_context(
    question=mission_query,
    domain=detected_domain,
    save_result=True
)
```

### С SignalDiscovery

```python
# Классификация домена для сигнала
domain = await bridge.classify_domain(signal_text)

# Сохранение сигнала с правильным доменом
graph_updater.add_signal(
    concept=signal_concept,
    domain=domain,
    novelty_score=novelty,
    confidence=confidence
)
```

---

## 🧠 Подсказки

* **Кэширование**: Классификация доменов кэшируется для производительности
* **Graceful degradation**: Learning Bridge работает даже если LM Studio или GraphUpdater недоступны
* **Контекст**: Ограничьте контекст 3-5 фактами, чтобы не перегружать промпт
* **Confidence**: Для автоматически созданных связей используйте confidence 0.8 вместо 0.9

---

## 📈 Ожидаемый результат

После использования Learning Bridge:

* ✅ TERAG использует накопленные знания для reasoning
* ✅ LM Studio рассуждает с контекстом из графа
* ✅ Результаты reasoning сохраняются обратно в граф
* ✅ Система самообучается на опыте
* ✅ Появляются best practices по доменам

---

**Готово!** TERAG теперь может самообучаться! 🎯✨













