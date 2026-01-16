#!/usr/bin/env python3
"""
Test Neo4j integration with TERAG system (Simple version)
"""

import sys
from neo4j import GraphDatabase
import json

def test_neo4j_connection():
    """Test basic Neo4j connection"""
    print("Testing Neo4j connection...")
    
    try:
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))
        
        with driver.session() as session:
            # Test basic query
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"OK: Connection successful: {record['message']}")
            
            # Get Neo4j version
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in result:
                print(f"OK: Neo4j {record['name']} {record['versions'][0]} ({record['edition']})")
            
            # Check database info
            result = session.run("CALL db.info()")
            for record in result:
                print(f"OK: Database: {record['name']}")
                print(f"OK: Status: {record['currentStatus']}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

def test_graph_operations():
    """Test basic graph operations"""
    print("\nTesting graph operations...")
    
    try:
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))
        
        with driver.session() as session:
            # Create test nodes
            session.run("""
                CREATE (p:Person {name: 'Alice', age: 30})
                CREATE (c:Company {name: 'TERAG', founded: 2024})
                CREATE (p)-[:WORKS_FOR]->(c)
            """)
            print("OK: Created test nodes and relationships")
            
            # Query the graph
            result = session.run("""
                MATCH (p:Person)-[r:WORKS_FOR]->(c:Company)
                RETURN p.name, c.name, type(r)
            """)
            
            for record in result:
                print(f"OK: {record['p.name']} {record['type(r)']} {record['c.name']}")
            
            # Clean up
            session.run("MATCH (n) DETACH DELETE n")
            print("OK: Cleaned up test data")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Graph operations failed: {e}")
        return False

def test_terag_integration():
    """Test TERAG-specific integration"""
    print("\nTesting TERAG integration...")
    
    try:
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))
        
        with driver.session() as session:
            # Create TERAG-specific schema
            session.run("""
                CREATE CONSTRAINT file_name IF NOT EXISTS FOR (f:File) REQUIRE f.name IS UNIQUE
                CREATE CONSTRAINT function_name IF NOT EXISTS FOR (func:Function) REQUIRE func.name IS UNIQUE
            """)
            print("OK: Created TERAG schema constraints")
            
            # Create sample code graph
            session.run("""
                CREATE (f1:File {name: 'App.tsx', type: 'tsx', path: 'src/App.tsx'})
                CREATE (f2:File {name: 'utils.ts', type: 'ts', path: 'src/utils.ts'})
                CREATE (func1:Function {name: 'loadGraph', file: 'App.tsx', line: 42})
                CREATE (func2:Function {name: 'processData', file: 'utils.ts', line: 15})
                CREATE (f1)-[:CONTAINS]->(func1)
                CREATE (f2)-[:CONTAINS]->(func2)
                CREATE (func1)-[:CALLS]->(func2)
            """)
            print("OK: Created sample code graph")
            
            # Query code relationships
            result = session.run("""
                MATCH (f:File)-[:CONTAINS]->(func:Function)
                RETURN f.name, func.name, func.line
                ORDER BY f.name
            """)
            
            print("OK: Code structure:")
            for record in result:
                print(f"   {record['f.name']} -> {record['func.name']} (line {record['func.line']})")
            
            # Query function calls
            result = session.run("""
                MATCH (f1:Function)-[:CALLS]->(f2:Function)
                RETURN f1.name, f2.name
            """)
            
            print("OK: Function calls:")
            for record in result:
                print(f"   {record['f1.name']} -> {record['f2.name']}")
            
            # Clean up
            session.run("MATCH (n) DETACH DELETE n")
            print("OK: Cleaned up TERAG test data")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"ERROR: TERAG integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("TERAG Neo4j Integration Test")
    print("=" * 40)
    
    tests = [
        ("Basic Connection", test_neo4j_connection),
        ("Graph Operations", test_graph_operations),
        ("TERAG Integration", test_terag_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\nTest Results:")
    print("=" * 20)
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nNeo4j is ready for TERAG Graph-RAG integration!")
        print("   - Graph database: Connected")
        print("   - Schema: Created")
        print("   - Operations: Working")
        print("   - TERAG integration: Ready")
    else:
        print("\nSome issues detected. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
