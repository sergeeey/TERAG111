#!/usr/bin/env python3
"""
Тест генерации OSINT дайджеста
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.integration.osint_digest import generate_daily_digest

def main():
    print("🔍 Тестирование генерации OSINT дайджеста...")
    print("=" * 60)
    print()
    
    try:
        digest = generate_daily_digest()
        print(digest)
        print()
        print("=" * 60)
        print("✅ Дайджест сгенерирован успешно!")
        print()
        print("💡 Этот дайджест будет автоматически добавляться")
        print("   в ежедневный отчёт TERAG через Telegram")
    except Exception as e:
        print(f"❌ Ошибка генерации дайджеста: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())













