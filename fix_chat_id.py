#!/usr/bin/env python3
"""
Надёжный скрипт для добавления/обновления Telegram Chat ID
"""
from pathlib import Path
import re

def fix_chat_id():
    """Добавить или обновить Chat ID в .env"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False
    
    chat_id = "792610846"
    
    # Читаем файл
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже TELEGRAM_CHAT_ID
    pattern = r'^TELEGRAM_CHAT_ID=.*$'
    
    if re.search(pattern, content, re.MULTILINE):
        # Заменяем существующий
        content = re.sub(
            pattern,
            f'TELEGRAM_CHAT_ID={chat_id}',
            content,
            flags=re.MULTILINE
        )
        print("✅ Обновлён существующий TELEGRAM_CHAT_ID")
    else:
        # Ищем место после TELEGRAM_BOT_TOKEN
        if "TELEGRAM_BOT_TOKEN=" in content:
            # Добавляем после TELEGRAM_BOT_TOKEN
            content = re.sub(
                r'(TELEGRAM_BOT_TOKEN=.*)',
                rf'\1\nTELEGRAM_CHAT_ID={chat_id}',
                content
            )
            print("✅ Добавлен TELEGRAM_CHAT_ID после TELEGRAM_BOT_TOKEN")
        else:
            # Добавляем в конец
            content += f"\nTELEGRAM_CHAT_ID={chat_id}\n"
            print("✅ Добавлен TELEGRAM_CHAT_ID в конец файла")
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Chat ID установлен: {chat_id}")
    
    # Проверяем результат
    if f"TELEGRAM_CHAT_ID={chat_id}" in content:
        print("✅ Проверка: Chat ID найден в файле")
        return True
    else:
        print("❌ Ошибка: Chat ID не найден после записи")
        return False

if __name__ == "__main__":
    fix_chat_id()













