#!/usr/bin/env node
// Test script for KAG dependencies

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

console.log('🧪 Testing KAG Dependencies...\n');

async function testDocker() {
  try {
    console.log('🐳 Testing Docker...');
    const { stdout } = await execAsync('docker --version');
    console.log(`✅ Docker: ${stdout.trim()}`);
    
    // Check if Docker Desktop is running
    try {
      await execAsync('docker ps');
      console.log('✅ Docker Desktop is running');
      return true;
    } catch (error) {
      console.log('❌ Docker Desktop is not running');
      console.log('   Please start Docker Desktop and try again');
      return false;
    }
  } catch (error) {
    console.log('❌ Docker not found');
    console.log('   Please install Docker Desktop');
    return false;
  }
}

async function testNeo4j() {
  try {
    console.log('\n🔗 Testing Neo4j connection...');
    const { stdout } = await execAsync('curl -s http://localhost:7474');
    if (stdout.includes('Neo4j')) {
      console.log('✅ Neo4j is accessible');
      return true;
    } else {
      console.log('❌ Neo4j not responding');
      return false;
    }
  } catch (error) {
    console.log('❌ Neo4j not accessible');
    console.log('   Run: docker compose -f docker-compose.kag-simple.yml up -d');
    return false;
  }
}

async function testSupabase() {
  try {
    console.log('\n🗄️ Testing Supabase connection...');
    const { stdout } = await execAsync('curl -s http://localhost:5432');
    console.log('✅ Supabase is accessible');
    return true;
  } catch (error) {
    console.log('❌ Supabase not accessible');
    console.log('   Run: docker compose -f docker-compose.kag-simple.yml up -d');
    return false;
  }
}

async function testRedis() {
  try {
    console.log('\n🔴 Testing Redis connection...');
    const { stdout } = await execAsync('curl -s http://localhost:6379');
    console.log('✅ Redis is accessible');
    return true;
  } catch (error) {
    console.log('❌ Redis not accessible');
    console.log('   Run: docker compose -f docker-compose.kag-simple.yml up -d');
    return false;
  }
}

async function main() {
  const dockerOk = await testDocker();
  
  if (!dockerOk) {
    console.log('\n❌ Cannot proceed without Docker');
    process.exit(1);
  }
  
  const neo4jOk = await testNeo4j();
  const supabaseOk = await testSupabase();
  const redisOk = await testRedis();
  
  console.log('\n📊 Test Results:');
  console.log(`Docker: ${dockerOk ? '✅' : '❌'}`);
  console.log(`Neo4j: ${neo4jOk ? '✅' : '❌'}`);
  console.log(`Supabase: ${supabaseOk ? '✅' : '❌'}`);
  console.log(`Redis: ${redisOk ? '✅' : '❌'}`);
  
  const allOk = dockerOk && neo4jOk && supabaseOk && redisOk;
  
  if (allOk) {
    console.log('\n🎉 All dependencies are ready!');
    console.log('✅ Task 1 criteria met:');
    console.log('   - Docker Compose configuration created');
    console.log('   - All services accessible');
    console.log('   - Ready for KAG implementation');
  } else {
    console.log('\n⚠️ Some dependencies are missing');
    console.log('Run: docker compose -f docker-compose.kag-simple.yml up -d');
  }
  
  process.exit(allOk ? 0 : 1);
}

main().catch(console.error);





































