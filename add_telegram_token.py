#!/usr/bin/env python3
"""
Скрипт для добавления Telegram токена в .env файл
"""
import os
from pathlib import Path

def add_telegram_token():
    """Добавить Telegram токен в .env файл"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("💡 Сначала запустите: python scripts/setup/setup_env.py")
        return False
    
    # Токен от пользователя
    token = "8010267972:AAFVfgd1e__Mkb6Z9NdWc_WGN-uecucUTGQ"
    
    # Читаем текущий .env
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, есть ли уже Telegram секция
    if "TELEGRAM_BOT_TOKEN" in content:
        # Обновляем существующий токен
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                new_lines.append(f"TELEGRAM_BOT_TOKEN={token}")
            elif line.startswith("TELEGRAM_CHAT_ID=") and "TELEGRAM_CHAT_ID" not in '\n'.join(new_lines):
                # Оставляем существующий chat_id или добавляем заглушку
                if "=" in line:
                    new_lines.append(line)
                else:
                    new_lines.append("# TELEGRAM_CHAT_ID=your_chat_id_here  # Получите через @userinfobot")
            else:
                new_lines.append(line)
        
        # Если не было TELEGRAM_CHAT_ID, добавляем
        if not any("TELEGRAM_CHAT_ID" in line for line in new_lines):
            # Находим место после TELEGRAM_BOT_TOKEN
            for i, line in enumerate(new_lines):
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    new_lines.insert(i + 1, "# TELEGRAM_CHAT_ID=your_chat_id_here  # Получите через @userinfobot")
                    break
        
        content = '\n'.join(new_lines)
    else:
        # Добавляем новую секцию Telegram
        telegram_section = """
# ============================================
# Telegram Bot Configuration
# ============================================
# Telegram Bot Token (получен от @BotFather)
TELEGRAM_BOT_TOKEN={token}
# Telegram Chat ID (получите через @userinfobot или создайте группу)
# TELEGRAM_CHAT_ID=your_chat_id_here
"""
        # Вставляем перед секцией Security Warnings
        if "# ============================================" in content and "Security Warnings" in content:
            parts = content.split("# ============================================")
            if len(parts) >= 2:
                # Находим секцию Security Warnings
                for i, part in enumerate(parts):
                    if "Security Warnings" in part:
                        # Вставляем перед этой секцией
                        telegram_section = telegram_section.format(token=token)
                        parts.insert(i, telegram_section + "\n# ============================================")
                        content = "# ============================================".join(parts)
                        break
        else:
            # Просто добавляем в конец
            content += telegram_section.format(token=token)
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Telegram токен добавлен в .env")
    print(f"📋 Токен: {token[:20]}...")
    print("\n💡 Следующие шаги:")
    print("   1. Получите CHAT_ID через @userinfobot в Telegram")
    print("   2. Добавьте TELEGRAM_CHAT_ID в .env")
    print("   3. Запустите тест: python test_telegram_connection.py")
    
    return True

if __name__ == "__main__":
    add_telegram_token()













