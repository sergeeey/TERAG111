#!/usr/bin/env python3
"""
Обновление Neo4j настроек в .env файле
"""
from pathlib import Path
import re

def update_neo4j_env():
    """Обновить Neo4j настройки в .env"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False
    
    # Читаем файл
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем пароль (из docker-compose.yml)
    password = "terag_neo4j_2025"
    
    # Обновляем NEO4J_PASSWORD
    pattern = r'^NEO4J_PASSWORD=.*$'
    if re.search(pattern, content, re.MULTILINE):
        content = re.sub(pattern, f'NEO4J_PASSWORD={password}', content, flags=re.MULTILINE)
        print("✅ Обновлён NEO4J_PASSWORD")
    else:
        # Добавляем после NEO4J_USER
        if "NEO4J_USER=" in content:
            content = re.sub(
                r'(NEO4J_USER=.*)',
                rf'\1\nNEO4J_PASSWORD={password}',
                content
            )
            print("✅ Добавлен NEO4J_PASSWORD")
        else:
            # Добавляем в секцию Database
            content = re.sub(
                r'(# ============================================\n# Database Configuration)',
                rf'\1\nNEO4J_PASSWORD={password}',
                content
            )
            print("✅ Добавлен NEO4J_PASSWORD в секцию Database")
    
    # Убеждаемся, что URI и USER правильные
    if "NEO4J_URI=" not in content:
        content = re.sub(
            r'(NEO4J_PASSWORD=.*)',
            r'NEO4J_URI=bolt://localhost:7687\nNEO4J_USER=neo4j\n\1',
            content
        )
        print("✅ Добавлены NEO4J_URI и NEO4J_USER")
    else:
        # Обновляем URI если нужно
        if "bolt://localhost:7687" not in content:
            content = re.sub(
                r'^NEO4J_URI=.*$',
                'NEO4J_URI=bolt://localhost:7687',
                content,
                flags=re.MULTILINE
            )
            print("✅ Обновлён NEO4J_URI")
        
        # Обновляем USER если нужно
        if "NEO4J_USER=neo4j" not in content:
            content = re.sub(
                r'^NEO4J_USER=.*$',
                'NEO4J_USER=neo4j',
                content,
                flags=re.MULTILINE
            )
            print("✅ Обновлён NEO4J_USER")
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Neo4j настройки обновлены в .env")
    print(f"   URI: bolt://localhost:7687")
    print(f"   User: neo4j")
    print(f"   Password: {password}")
    
    return True

if __name__ == "__main__":
    update_neo4j_env()













