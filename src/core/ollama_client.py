#!/usr/bin/env python3
"""
Ollama Client для интеграции локальных LLM с TERAG
Позволяет отправлять вопросы в установленные модели Ollama
"""
import requests
import json
from typing import Optional, List

# URL локального API Ollama
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"

def query_ollama(prompt: str, model: str = "qwen2.5:7b-instruct", stream: bool = False) -> str:
    """
    Отправляет запрос в локальную модель Ollama и возвращает ответ.
    
    Args:
        prompt: Текст запроса
        model: Название модели (по умолчанию qwen2.5:7b-instruct)
        stream: Потоковый режим ответа
    
    Returns:
        Текст ответа модели или сообщение об ошибке
    """
    try:
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        response = requests.post(OLLAMA_API_URL, json=data, timeout=180)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
        
    except requests.exceptions.ConnectionError:
        return "[Ошибка]: Не удается подключиться к Ollama API. Убедитесь, что Ollama запущен на http://127.0.0.1:11434"
    except Exception as e:
        return f"[Ошибка Ollama]: {str(e)}"

def list_available_models() -> List[str]:
    """
    Получает список доступных моделей в Ollama.
    
    Returns:
        Список названий доступных моделей
    """
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print(f"[Ошибка]: Не удалось получить список моделей: {e}")
        return []

def query_with_context(question: str, context: str, model: str = "qwen2.5:7b-instruct") -> str:
    """
    Отправляет вопрос с контекстом в модель Ollama.
    
    Args:
        question: Вопрос пользователя
        context: Контекст из графа знаний TERAG
        model: Модель для обработки
    
    Returns:
        Ответ модели с учетом контекста
    """
    prompt = f"""Используй следующую информацию из базы знаний для ответа на вопрос:

Контекст:
{context}

Вопрос: {question}

Ответь на основе предоставленного контекста. Если в контексте нет нужной информации, честно скажи об этом."""
    
    return query_ollama(prompt, model)

def quick_test(model: str = "qwen2.5:7b-instruct"):
    """
    Быстрый тест подключения к Ollama.
    
    Args:
        model: Название модели для теста
    """
    print(f"🧠 Тестирование подключения к Ollama (модель: {model})...")
    test_prompt = "Привет! Расскажи, что ты умеешь делать."
    
    try:
        answer = query_ollama(test_prompt, model)
        print(f"✅ Подключение успешно!")
        print(f"📝 Ответ модели:")
        print(answer)
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    # Проверяем доступные модели
    print("🔍 Проверка доступных моделей Ollama...")
    models = list_available_models()
    
    if models:
        print(f"✅ Найдено моделей: {len(models)}")
        for model in models:
            print(f"   - {model}")
        
        # Тестируем первую модель
        if models:
            test_model = models[0]
            print(f"\n🧪 Тестируем модель: {test_model}")
            quick_test(test_model)
    else:
        print("❌ Модели не найдены. Убедитесь, что Ollama запущен.")
        print("💡 Попробуйте установить модель: ollama pull qwen2.5:7b-instruct")




























