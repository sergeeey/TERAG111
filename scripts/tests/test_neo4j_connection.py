#!/usr/bin/env python3
"""Быстрая проверка подключения к Neo4j"""
from neo4j import GraphDatabase

try:
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "terag_neo4j_2025"))
    
    with driver.session() as s:
        result = s.run("RETURN 'Neo4j connected ✅' AS status").single()
        print(result["status"])
        
        # Дополнительная проверка - версия Neo4j
        version_result = s.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition").single()
        if version_result:
            print(f"Neo4j {version_result['name']} {version_result['version']} ({version_result['edition']})")
    
    driver.close()
    print("✅ Подключение успешно!")
    
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
