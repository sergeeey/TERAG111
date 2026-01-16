#!/usr/bin/env python3
"""
Тест модуля System Context
"""
import sys
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.system_context import SystemContext

def main():
    print("🧩 Тестирование System Context...")
    print("=" * 60)
    print()
    
    try:
        context = SystemContext()
        system_info = context.get_system_context()
        
        print("✅ Системная информация собрана:")
        print()
        print(f"Host: {system_info['host']['hostname']}")
        print(f"OS: {system_info['host']['os']} {system_info['host']['os_version'][:50]}")
        print(f"Python: {system_info['python']['version']}")
        print()
        
        # Docker info
        docker_info = system_info['docker']
        if docker_info.get('available'):
            print(f"✅ Docker: {docker_info.get('version', 'unknown')}")
            print(f"   Containers: {docker_info.get('containers_running', 0)}/{docker_info.get('containers_total', 0)} running")
            if docker_info.get('containers'):
                print("   Container list:")
                for container in docker_info['containers'][:5]:  # Показываем первые 5
                    status_emoji = "✅" if container['status'] == 'running' else "⏸️"
                    print(f"     {status_emoji} {container['name']} ({container['status']})")
        else:
            print(f"❌ Docker: {docker_info.get('error', 'not available')}")
        print()
        
        # Resources
        resources = system_info['resources']
        if 'cpu' in resources and 'count' in resources['cpu']:
            print(f"CPU: {resources['cpu']['count']} cores")
        if 'memory' in resources and 'total' in resources['memory']:
            ram_gb = resources['memory']['total'] / (1024**3)
            print(f"RAM: {ram_gb:.1f} GB")
        if 'disk' in resources and 'free' in resources['disk']:
            disk_gb = resources['disk']['free'] / (1024**3)
            print(f"Disk free: {disk_gb:.1f} GB")
        print()
        
        # Services
        services = system_info['services']
        print("Services:")
        for name, info in services.items():
            status = "✅" if info.get('available') else "❌"
            print(f"  {status} {info.get('name', name)}")
        print()
        
        # Format for Telegram
        print("=" * 60)
        print("📱 Форматирование для Telegram:")
        print("=" * 60)
        telegram_format = context.format_for_telegram()
        print(telegram_format)
        print()
        
        # Save to file
        filepath = context.save_to_file()
        print(f"✅ Контекст сохранён в: {filepath}")
        
        print()
        print("=" * 60)
        print("✅ Тест завершён успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())













