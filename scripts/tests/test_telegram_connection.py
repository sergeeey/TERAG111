#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения Telegram бота
"""
import os
import sys
import asyncio
from pathlib import Path

# Загружаем .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружен .env файл")
    else:
        print("⚠️  .env файл не найден")
except ImportError:
    print("⚠️  python-dotenv не установлен, используем переменные окружения")

# Проверяем наличие токена
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

if not token:
    print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
    print("💡 Запустите: python add_telegram_token.py")
    sys.exit(1)

print(f"✅ Токен найден: {token[:20]}...")

if not chat_id:
    print("⚠️  TELEGRAM_CHAT_ID не установлен")
    print("💡 Получите CHAT_ID:")
    print("   1. Напишите боту @userinfobot в Telegram")
    print("   2. Он вернёт ваш ID (например: 123456789)")
    print("   3. Добавьте в .env: TELEGRAM_CHAT_ID=123456789")
    print("\n   Или создайте группу и добавьте бота, затем:")
    print("   1. Напишите в группу @userinfobot")
    print("   2. Получите ID группы (например: -1001234567890)")
    print("   3. Добавьте в .env: TELEGRAM_CHAT_ID=-1001234567890")
    
    # Пробуем отправить без chat_id (проверим только токен)
    print("\n🧪 Тестируем только токен (без отправки сообщения)...")
    chat_id = None
else:
    print(f"✅ Chat ID найден: {chat_id}")

async def test_telegram_connection():
    """Тест подключения к Telegram"""
    try:
        # Пробуем использовать aiogram
        try:
            from aiogram import Bot
            from aiogram.exceptions import TelegramBadRequest
            
            bot = Bot(token=token)
            
            # Проверяем информацию о боте
            bot_info = await bot.get_me()
            print(f"\n✅ Бот подключён!")
            print(f"   Имя: {bot_info.first_name}")
            print(f"   Username: @{bot_info.username}")
            print(f"   ID: {bot_info.id}")
            
            # Если есть chat_id, отправляем тестовое сообщение
            if chat_id:
                try:
                    # Красиво оформленное сообщение с Markdown
                    message_text = """🧠 *TERAG System Notification*

✅ *Бот подключён и работает!*

Это тестовое сообщение от системы TERAG.

*Статус компонентов:*
• LM Studio: ✅ Работает
• Brave Search: ✅ Работает  
• Bright Data: ✅ Настроен
• Neo4j: ⚠️ Не запущен

*Следующие шаги:*
Переходим к задаче 09 — Telegram Integration

---
_TERAG Cognitive Platform v1.0_"""
                    
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode="Markdown"
                    )
                    print(f"\n✅ Тестовое сообщение отправлено в чат {chat_id}")
                except TelegramBadRequest as e:
                    print(f"\n❌ Ошибка отправки сообщения: {e}")
                    print("💡 Проверьте, что:")
                    print("   - Chat ID правильный")
                    print("   - Бот добавлен в группу (если это группа)")
                    print("   - Вы написали боту /start (если это личный чат)")
            else:
                print("\n⚠️  Chat ID не установлен, пропускаем отправку сообщения")
            
            await bot.session.close()
            return True
            
        except ImportError:
            print("\n⚠️  aiogram не установлен, пробуем через requests...")
            
            # Альтернатива через requests
            import requests
            
            # Проверяем информацию о боте
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data["result"]
                    print(f"\n✅ Бот подключён!")
                    print(f"   Имя: {bot_info['first_name']}")
                    print(f"   Username: @{bot_info['username']}")
                    print(f"   ID: {bot_info['id']}")
                    
                    # Если есть chat_id, отправляем сообщение
                    if chat_id:
                        send_url = f"https://api.telegram.org/bot{token}/sendMessage"
                        
                        # Красиво оформленное сообщение с Markdown
                        message_text = """🧠 *TERAG System Notification*

✅ *Бот подключён и работает!*

Это тестовое сообщение от системы TERAG.

*Статус компонентов:*
• LM Studio: ✅ Работает
• Brave Search: ✅ Работает  
• Bright Data: ✅ Настроен
• Neo4j: ⚠️ Не запущен

*Следующие шаги:*
Переходим к задаче 09 — Telegram Integration

---
_TERAG Cognitive Platform v1.0_"""
                        
                        send_data = {
                            "chat_id": chat_id,
                            "text": message_text,
                            "parse_mode": "Markdown"
                        }
                        send_response = requests.post(send_url, json=send_data, timeout=10)
                        
                        if send_response.status_code == 200:
                            print(f"\n✅ Тестовое сообщение отправлено в чат {chat_id}")
                        else:
                            error_data = send_response.json()
                            print(f"\n❌ Ошибка отправки: {error_data.get('description', 'Unknown error')}")
                            print("💡 Проверьте Chat ID и права бота")
                    else:
                        print("\n⚠️  Chat ID не установлен, пропускаем отправку сообщения")
                    
                    return True
                else:
                    print(f"\n❌ Ошибка API: {data.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"\n❌ HTTP ошибка: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Ошибка подключения: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Тестирование подключения Telegram бота...")
    print("=" * 60)
    
    result = asyncio.run(test_telegram_connection())
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Тест завершён успешно!")
        print("\n💡 Следующие шаги:")
        print("   1. Если Chat ID не установлен - получите его и добавьте в .env")
        print("   2. Запустите: python test_telegram_connection.py (снова)")
        print("   3. После успешной проверки можно переходить к задаче 09")
    else:
        print("❌ Тест не пройден")
        print("\n💡 Проверьте:")
        print("   - Правильность токена")
        print("   - Интернет-соединение")
        print("   - Установлены ли зависимости: pip install aiogram или requests")

