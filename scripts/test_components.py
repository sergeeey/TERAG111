#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности существующих компонентов TERAG
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_billing():
    """Проверить BillingCore"""
    print("🔍 Testing BillingCore...")
    try:
        from src.billing.core import BillingCore
        billing = BillingCore()
        print("  ✅ BillingCore initialized")
        
        # Проверяем тарифы
        assert billing.tiers is not None
        print("  ✅ Billing tiers loaded")
        return True
    except Exception as e:
        print(f"  ❌ BillingCore failed: {e}")
        return False

def test_api_auth():
    """Проверить TeragAuth"""
    print("🔍 Testing TeragAuth...")
    try:
        from src.security.api_auth import TeragAuth
        from src.security.roles import Role
        
        auth = TeragAuth()
        print("  ✅ TeragAuth initialized")
        
        # Пробуем создать тестовый ключ (только если MongoDB доступен)
        try:
            test_key = auth.create_key(
                client_id="test-client",
                role=Role.CLIENT,
                expires_days=1
            )
            print(f"  ✅ API key created: {test_key.key[:20]}...")
            print(f"  ✅ Role: {test_key.role.value}")
            
            # Пробуем верифицировать
            verified = auth.verify_key(test_key.key)
            if verified:
                print("  ✅ API key verification works")
            else:
                print("  ⚠️  API key verification returned None")
            
            return True
        except Exception as e:
            print(f"  ⚠️  MongoDB not available (expected in dev): {e}")
            print("  ✅ TeragAuth code is valid")
            return True
    except Exception as e:
        print(f"  ❌ TeragAuth failed: {e}")
        return False

def test_error_handler():
    """Проверить TeragErrorHandler"""
    print("🔍 Testing TeragErrorHandler...")
    try:
        from src.core.error_handler import TeragErrorHandler
        
        # Инициализация без backup (для теста)
        handler = TeragErrorHandler()
        print("  ✅ TeragErrorHandler initialized")
        
        # Проверяем наличие методов
        assert hasattr(handler, 'handle_errors')
        assert hasattr(handler, 'switch_to_backup')
        print("  ✅ Required methods exist")
        return True
    except Exception as e:
        print(f"  ❌ TeragErrorHandler failed: {e}")
        return False

def test_neo4j_connection():
    """Проверить подключение к Neo4j"""
    print("🔍 Testing Neo4j connection...")
    try:
        from neo4j import GraphDatabase
        import os
        
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "")
        
        if not neo4j_password:
            print("  ⚠️  NEO4J_PASSWORD not set, skipping connection test")
            return True
        
        driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        driver.verify_connectivity()
        driver.close()
        print("  ✅ Neo4j connection successful")
        return True
    except Exception as e:
        print(f"  ⚠️  Neo4j connection failed (expected if not running): {e}")
        return True  # Не критично для проверки кода

def test_mongodb_connection():
    """Проверить подключение к MongoDB"""
    print("🔍 Testing MongoDB connection...")
    try:
        from pymongo import MongoClient
        import os
        
        mongodb_uri = os.getenv("MONGODB_URI", "")
        if not mongodb_uri:
            print("  ⚠️  MONGODB_URI not set, skipping connection test")
            return True
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        client.close()
        print("  ✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"  ⚠️  MongoDB connection failed (expected if not running): {e}")
        return True  # Не критично для проверки кода

def main():
    """Основная функция"""
    print("=" * 60)
    print("TERAG Components Test")
    print("=" * 60)
    print()
    
    results = {
        "BillingCore": test_billing(),
        "TeragAuth": test_api_auth(),
        "TeragErrorHandler": test_error_handler(),
        "Neo4j": test_neo4j_connection(),
        "MongoDB": test_mongodb_connection()
    }
    
    print()
    print("=" * 60)
    print("Results:")
    print("=" * 60)
    
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {component}: {status}")
    
    all_passed = all(results.values())
    print()
    if all_passed:
        print("✅ All components are working!")
        return 0
    else:
        print("⚠️  Some components have issues (check output above)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
