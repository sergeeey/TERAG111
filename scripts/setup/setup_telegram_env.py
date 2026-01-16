#!/usr/bin/env python3
"""
Скрипт для добавления Telegram настроек в .env файл
"""
from pathlib import Path
import re

def setup_telegram_env():
    """Добавить/обновить Telegram настройки в .env"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("💡 Сначала запустите: python scripts/setup/setup_env.py")
        return False
    
    # Читаем файл
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Настройки для добавления
    settings = {
        "TELEGRAM_WHITELIST": "792610846",
        "TERAG_DAILY_REPORT_HOUR": "9",
        "TERAG_DAILY_REPORT_MINUTE": "0",
        "TERAG_MAX_CONCURRENT_MISSIONS": "3",
        "TERAG_MISSION_RUNNER": "python installer/start_mission.py",
        "TERAG_HEALTHCHECK_CMD": "python check_terag_full_stack.py"
    }
    
    # Обновляем или добавляем каждую настройку
    for key, value in settings.items():
        pattern = rf'^{key}=.*$'
        if re.search(pattern, content, re.MULTILINE):
            # Заменяем существующую
            content = re.sub(pattern, f'{key}={value}', content, flags=re.MULTILINE)
            print(f"✅ Обновлено: {key}")
        else:
            # Добавляем после TELEGRAM_CHAT_ID или в конец секции Telegram
            if "TELEGRAM_CHAT_ID=" in content:
                content = re.sub(
                    r'(TELEGRAM_CHAT_ID=.*)',
                    rf'\1\n{key}={value}',
                    content
                )
                print(f"✅ Добавлено: {key}")
            else:
                # Добавляем в конец
                content += f"\n{key}={value}\n"
                print(f"✅ Добавлено: {key}")
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Все Telegram настройки добавлены в .env")
    print("\n📋 Добавленные настройки:")
    for key, value in settings.items():
        print(f"   {key}={value}")
    
    return True

if __name__ == "__main__":
    setup_telegram_env()













