#!/usr/bin/env python3
"""
Basic Neo4j test
"""

from neo4j import GraphDatabase

def test_connection():
    try:
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            print(f"SUCCESS: {record['message']}")
            
            # Get version
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in result:
                print(f"Neo4j {record['name']} {record['versions'][0]} ({record['edition']})")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    success = test_connection()
    if success:
        print("Neo4j is working!")
    else:
        print("Neo4j connection failed!")

