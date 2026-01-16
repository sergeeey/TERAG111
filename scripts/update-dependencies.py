#!/usr/bin/env python3
"""
Скрипт для безопасного обновления зависимостей
Обновляет только безопасные версии, избегая breaking changes
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Критичные пакеты для обновления (security-related)
CRITICAL_PACKAGES = [
    "cryptography",
    "urllib3",
    "requests",
    "fastapi",
    "pydantic",
    "redis",
    "aiohttp",
    "httpx",
    "certifi",
    "idna",
]


def parse_requirements(file_path: Path) -> List[Tuple[str, str, str]]:
    """Парсинг requirements.txt"""
    requirements = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Парсим формат: package>=version или package==version
            match = re.match(r'^([a-zA-Z0-9_-]+)([>=<!=]+)([0-9.]+)', line)
            if match:
                name, op, version = match.groups()
                requirements.append((name, op, version, line))
            else:
                # Просто имя пакета
                requirements.append((line, "", "", line))
    
    return requirements


def update_requirements(requirements_file: Path, updates: dict) -> bool:
    """Обновить requirements.txt"""
    content = requirements_file.read_text(encoding='utf-8')
    updated = False
    
    for package, new_version in updates.items():
        # Ищем строку с пакетом
        pattern = rf'^{re.escape(package)}([>=<!=]+)([0-9.]+)'
        replacement = f'{package}>={new_version}'
        
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            updated = True
            print(f"  ✅ Обновлен {package} → {new_version}")
    
    if updated:
        requirements_file.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🔄 Обновление критичных зависимостей")
    print("=" * 60)
    print()
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt не найден")
        return 1
    
    # Рекомендуемые обновления (безопасные версии)
    safe_updates = {
        "fastapi": "0.115.0",  # Обновлено с 0.104.0
        "pydantic": "2.10.0",  # Обновлено с 2.5.0
        "redis": "5.2.0",      # Обновлено с 5.0.0
        "aiohttp": "3.11.0",   # Обновлено с 3.9.0
        "httpx": "0.27.0",     # Обновлено с 0.25.0
        "cryptography": "43.0.0",  # Безопасная версия
        "urllib3": "2.2.0",    # Безопасная версия
        "certifi": "2024.12.0",  # Обновление сертификатов
    }
    
    print("Рекомендуемые обновления:")
    for pkg, version in safe_updates.items():
        print(f"  - {pkg}: {version}")
    print()
    
    response = input("Обновить requirements.txt? (y/n): ")
    if response.lower() != 'y':
        print("Отменено")
        return 0
    
    if update_requirements(requirements_file, safe_updates):
        print()
        print("✅ requirements.txt обновлен")
        print()
        print("⚠️  ВАЖНО: После обновления выполните:")
        print("   1. pip install -r requirements.txt --upgrade")
        print("   2. Запустите тесты: pytest tests/")
        print("   3. Проверьте работоспособность приложения")
    else:
        print("ℹ️  Изменений не требуется")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())









