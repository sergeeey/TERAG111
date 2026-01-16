#!/usr/bin/env python3
"""
Быстрый тест Telegram сервиса (без запуска полного бота)
Проверяет подключение и отправляет тестовое сообщение
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot

# Загружаем .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

async def test_telegram_service():
    """Тест подключения и отправки сообщения"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    whitelist = os.getenv("TELEGRAM_WHITELIST", "")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID не найден в .env")
        return False
    
    print(f"✅ Токен найден: {token[:20]}...")
    print(f"✅ Chat ID: {chat_id}")
    print(f"✅ Whitelist: {whitelist or 'открыт для всех'}")
    
    try:
        bot = Bot(token=token)
        
        # Проверяем информацию о боте
        bot_info = await bot.get_me()
        print(f"\n✅ Бот подключён!")
        print(f"   Имя: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   ID: {bot_info.id}")
        
        # Отправляем тестовое сообщение
        test_message = """🧠 *TERAG Telegram Service Test*

✅ Сервис готов к работе!

*Доступные команды:*
/start — список команд
/status — быстрый статус
/health — полный health-check
/find <query> — быстрый поиск
/deep_search <query> — глубокая миссия

*Настройки:*
• Whitelist: {whitelist}
• Daily report: 9:00
• Max concurrent missions: 3

---
_TERAG Cognitive Platform v1.0_""".format(whitelist=whitelist or "открыт для всех")
        
        await bot.send_message(
            chat_id=chat_id,
            text=test_message,
            parse_mode="Markdown"
        )
        print(f"\n✅ Тестовое сообщение отправлено в чат {chat_id}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Тестирование Telegram сервиса...")
    print("=" * 60)
    
    result = asyncio.run(test_telegram_service())
    
    print("\n" + "=" * 60)
    if result:
        print("✅ Тест завершён успешно!")
        print("\n💡 Следующий шаг:")
        print("   Запустите сервис: python src/integration/telegram_service.py")
        print("   Затем отправьте /start боту в Telegram")
    else:
        print("❌ Тест не пройден")
        print("\n💡 Проверьте:")
        print("   - Правильность токена и Chat ID")
        print("   - Интернет-соединение")
        print("   - Установлены ли зависимости: pip install aiogram")













