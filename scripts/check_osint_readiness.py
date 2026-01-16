#!/usr/bin/env python3
"""
Проверка готовности OSINT модулей TERAG
Проверяет наличие API ключей и доступность модулей
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Загружен .env файл: {env_path}")
else:
    print(f"⚠️  .env файл не найден: {env_path}")
    print("💡 Создайте .env файл с помощью: python scripts/setup/setup_env.py")

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "installer" / "app" / "modules"))

def check_env_var(var_name: str, required: bool = True) -> tuple[bool, str]:
    """Проверка наличия переменной окружения"""
    value = os.getenv(var_name)
    if value:
        # Скрываем чувствительные данные
        if "KEY" in var_name or "PASSWORD" in var_name or "PROXY" in var_name:
            display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
        else:
            display_value = value
        return True, display_value
    else:
        if required:
            return False, "не найден"
        else:
            return False, "не установлен (опционально)"


def check_module(module_name: str, import_path: str) -> bool:
    """Проверка доступности модуля"""
    try:
        __import__(import_path)
        return True
    except ImportError:
        return False


def check_directory(path: Path, create_if_missing: bool = False) -> bool:
    """Проверка существования директории"""
    if path.exists():
        return True
    elif create_if_missing:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    return False


def main():
    """Главная функция проверки"""
    print("\n" + "=" * 60)
    print("🔍 Проверка готовности OSINT модулей TERAG")
    print("=" * 60 + "\n")
    
    all_checks_passed = True
    
    # Проверка переменных окружения
    print("📋 Проверка переменных окружения:")
    print("-" * 60)
    
    env_checks = [
        ("BRAVE_API_KEY", True),
        ("BRIGHTDATA_PROXY_HTTP", False),
        ("BRIGHTDATA_PROXY_WS", False),
        ("SUPABASE_URL", False),
        ("SUPABASE_ANON_KEY", False),
    ]
    
    for var_name, required in env_checks:
        found, value = check_env_var(var_name, required)
        status = "✅" if found else ("⚠️" if not required else "❌")
        req_text = "(обязательно)" if required else "(опционально)"
        print(f"{status} {var_name:25} {value:30} {req_text}")
        if required and not found:
            all_checks_passed = False
    
    # Проверка модулей
    print("\n📦 Проверка модулей:")
    print("-" * 60)
    
    module_checks = [
        ("Brave Search", "installer.app.modules.brave_search", "BraveSearchClient"),
        ("Bright Data", "installer.app.modules.bright_extractor", "BrightDataExtractor"),
        ("Graph Updater", "installer.app.modules.graph_updater", "GraphUpdater"),
        ("LM Studio Client", "src.integration.lmstudio_client", "LMStudioClient"),
    ]
    
    for name, import_path, class_name in module_checks:
        available = check_module(name, import_path)
        status = "✅" if available else "❌"
        print(f"{status} {name:25} {'доступен' if available else 'не найден'}")
        if not available:
            all_checks_passed = False
    
    # Проверка директорий
    print("\n📁 Проверка директорий:")
    print("-" * 60)
    
    base_path = Path(__file__).parent.parent
    dir_checks = [
        (base_path / "installer" / "app" / "modules", True, False),
        (base_path / "src" / "integration", True, True),
        (base_path / "data", False, True),
        (base_path / "logs", False, True),
    ]
    
    for dir_path, required, create in dir_checks:
        exists = check_directory(dir_path, create_if_missing=create)
        status = "✅" if exists else ("⚠️" if not required else "❌")
        action = "создана" if create and not dir_path.exists() and exists else ("существует" if exists else "не найдена")
        print(f"{status} {dir_path.name:25} {action}")
        if required and not exists:
            all_checks_passed = False
    
    # Итоговый результат
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("🎉 TERAG готов к OSINT операциям!")
        return 0
    else:
        print("⚠️  Некоторые проверки не пройдены")
        print("💡 Проверьте ошибки выше и настройте недостающие компоненты")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)













