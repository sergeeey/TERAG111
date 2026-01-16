# 🧪 TERAG Testing Guide

**Дата:** 2025-01-27

---

## 📋 Обзор Тестирования

TERAG использует два типа тестов:
- **Python тесты** (pytest) - для backend модулей
- **TypeScript/React тесты** (vitest) - для frontend компонентов

---

## 🐍 Python Тесты

### Запуск всех тестов:
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Запуск конкретных тестов:
```bash
# Тесты для core модулей
pytest tests/core/

# Тесты для API
pytest tests/api/

# Бенчмарки производительности
pytest tests/benchmarks/ --benchmark-only
```

### Просмотр coverage:
```bash
# HTML отчет
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Терминальный отчет
pytest tests/ --cov=src --cov-report=term
```

---

## ⚛️ TypeScript/React Тесты

### Запуск всех тестов:
```bash
npm run test
```

### Запуск в watch режиме:
```bash
npm run test:watch
```

### Запуск с UI:
```bash
npm run test:ui
```

### Просмотр coverage:
```bash
npm run test
# Coverage отчет будет в coverage/
```

---

## 📊 Текущее Покрытие

### Python модули:
- ✅ `src/core/kag_builder.py` - тесты созданы
- ✅ `src/core/ollama_client.py` - тесты созданы
- ✅ `src/core/metrics.py` - тесты созданы
- ✅ `src/core/doc_converter.py` - тесты созданы
- ✅ `src/api/server.py` - тесты созданы

### TypeScript компоненты:
- ✅ `src/components/immersive/CognitiveConsole.tsx` - тесты созданы
- ✅ `src/components/immersive/MetricsHUD.tsx` - тесты созданы
- ✅ `src/services/terag-api.ts` - тесты уже были

---

## 🎯 Целевое Покрытие

- **Критические компоненты:** ≥ 60%
- **Core modules:** ≥ 80%
- **UI components:** ≥ 40%

---

## 🔧 Настройка Тестов

### Python зависимости:
```bash
pip install pytest pytest-cov pytest-benchmark
```

### TypeScript зависимости:
```bash
npm install --save-dev vitest @vitest/coverage-v8 jsdom
```

---

## 📝 Написание Новых Тестов

### Python тест (пример):
```python
import pytest
from src.core.module import function

def test_function_success():
    result = function("input")
    assert result == "expected"
```

### TypeScript тест (пример):
```typescript
import { describe, it, expect } from 'vitest';
import { Component } from './Component';

describe('Component', () => {
  it('renders correctly', () => {
    // test code
  });
});
```

---

## 🚀 CI/CD

Тесты автоматически запускаются:
- При push в main/develop
- При создании Pull Request
- См. `.github/workflows/tests.yml`

---

**Последнее обновление:** 2025-01-27














