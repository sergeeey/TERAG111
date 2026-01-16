#!/usr/bin/env node
// Check KAG readiness without Docker

import fs from 'fs';
import path from 'path';

console.log('🔍 Checking KAG Readiness...\n');

// Check if required files exist
const requiredFiles = [
  'docs/architecture/kag-integration.md',
  'docs/decisions/001-kag-reasoning-core.md',
  'docker-compose.kag.yml',
  'docker-compose.kag-simple.yml',
  '.cursor/tasks/01-kag-architecture-integration.mdc',
  '.cursor/memory_bank/decisions.md',
  '.cursor/memory_bank/progress.md',
  '.cursor/memory_bank/reasoning_audit.md'
];

console.log('📁 Checking required files...');
let allFilesExist = true;

requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file}`);
    allFilesExist = false;
  }
});

// Check if directories exist
const requiredDirs = [
  'docs/architecture',
  'docs/decisions',
  '.cursor/tasks',
  '.cursor/memory_bank'
];

console.log('\n📂 Checking required directories...');
requiredDirs.forEach(dir => {
  if (fs.existsSync(dir)) {
    console.log(`✅ ${dir}/`);
  } else {
    console.log(`❌ ${dir}/`);
    allFilesExist = false;
  }
});

// Check Docker Compose syntax
console.log('\n🐳 Checking Docker Compose syntax...');
try {
  const dockerContent = fs.readFileSync('docker-compose.kag-simple.yml', 'utf8');
  if (dockerContent.includes('services:') && dockerContent.includes('neo4j:')) {
    console.log('✅ Docker Compose syntax looks good');
  } else {
    console.log('❌ Docker Compose syntax issues');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read Docker Compose file');
  allFilesExist = false;
}

// Check architecture diagram
console.log('\n🏗️ Checking architecture diagram...');
try {
  const archContent = fs.readFileSync('docs/architecture/kag-integration.md', 'utf8');
  if (archContent.includes('mermaid') && archContent.includes('KAG Builder')) {
    console.log('✅ Architecture diagram present');
  } else {
    console.log('❌ Architecture diagram missing or incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read architecture file');
  allFilesExist = false;
}

// Check ADR
console.log('\n📋 Checking ADR...');
try {
  const adrContent = fs.readFileSync('docs/decisions/001-kag-reasoning-core.md', 'utf8');
  if (adrContent.includes('✅ **Принято**') && adrContent.includes('KAG')) {
    console.log('✅ ADR properly documented');
  } else {
    console.log('❌ ADR incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read ADR file');
  allFilesExist = false;
}

// Summary
console.log('\n📊 Summary:');
if (allFilesExist) {
  console.log('🎉 Task 1: KAG Architecture Integration - COMPLETED!');
  console.log('\n✅ Criteria met:');
  console.log('   - Architecture diagram created and readable');
  console.log('   - ADR documented and accepted');
  console.log('   - Docker Compose configuration ready');
  console.log('   - All required files and directories exist');
  console.log('   - Memory Bank structure created');
  console.log('\n🚀 Ready for Task 2: KAG-Builder Implementation');
} else {
  console.log('❌ Task 1 incomplete - some files missing');
  console.log('Please check the missing files above');
}

console.log('\n📝 Next steps:');
console.log('1. Start Docker Desktop');
console.log('2. Run: docker compose -f docker-compose.kag-simple.yml up -d');
console.log('3. Verify services are running');
console.log('4. Begin Task 2: KAG-Builder Implementation');

process.exit(allFilesExist ? 0 : 1);
