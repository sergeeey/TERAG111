#!/usr/bin/env python3
"""
Скрипт для добавления Telegram Chat ID в .env файл
"""
from pathlib import Path

def add_chat_id():
    """Добавить Chat ID в .env файл"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False
    
    chat_id = "792610846"
    
    # Читаем текущий .env
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже TELEGRAM_CHAT_ID
    if "TELEGRAM_CHAT_ID=" in content:
        # Обновляем существующий
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith("TELEGRAM_CHAT_ID="):
                new_lines.append(f"TELEGRAM_CHAT_ID={chat_id}")
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    else:
        # Добавляем после TELEGRAM_BOT_TOKEN
        if "TELEGRAM_BOT_TOKEN=" in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    new_lines.append(f"TELEGRAM_CHAT_ID={chat_id}")
            content = '\n'.join(new_lines)
        else:
            # Добавляем в конец секции Telegram
            telegram_section = f"\nTELEGRAM_CHAT_ID={chat_id}\n"
            content += telegram_section
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Chat ID добавлен в .env: {chat_id}")
    return True

if __name__ == "__main__":
    add_chat_id()













