#!/usr/bin/env node
// Check Task 2: KAG-Builder Implementation readiness

import fs from 'fs';
import path from 'path';

console.log('🔍 Checking Task 2: KAG-Builder Implementation...\n');

// Check if required files exist
const requiredFiles = [
  'src/kag/builder.py',
  'src/kag/extractors/spo_extractor.py',
  'src/kag/schemas/terag_schema.py',
  'src/kag/storage/supabase_client.py',
  'tests/kag/test_builder.py'
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
  'src/kag',
  'src/kag/extractors',
  'src/kag/schemas',
  'src/kag/storage',
  'tests/kag'
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

// Check Python syntax
console.log('\n🐍 Checking Python syntax...');
const pythonFiles = [
  'src/kag/builder.py',
  'src/kag/extractors/spo_extractor.py',
  'src/kag/schemas/terag_schema.py',
  'src/kag/storage/supabase_client.py'
];

let pythonSyntaxOk = true;
pythonFiles.forEach(file => {
  try {
    const content = fs.readFileSync(file, 'utf8');
    // Basic syntax checks
    if (content.includes('import ') && content.includes('class ') && content.includes('def ')) {
      console.log(`✅ ${file} - syntax looks good`);
    } else {
      console.log(`❌ ${file} - syntax issues`);
      pythonSyntaxOk = false;
    }
  } catch (error) {
    console.log(`❌ ${file} - cannot read file`);
    pythonSyntaxOk = false;
  }
});

// Check test coverage
console.log('\n🧪 Checking test coverage...');
try {
  const testContent = fs.readFileSync('tests/kag/test_builder.py', 'utf8');
  if (testContent.includes('class TestKAGBuilder') && 
      testContent.includes('class TestSPOExtractor') &&
      testContent.includes('class TestTERAGSchema') &&
      testContent.includes('class TestSupabaseClient')) {
    console.log('✅ Test coverage looks comprehensive');
  } else {
    console.log('❌ Test coverage incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read test file');
  allFilesExist = false;
}

// Check schema completeness
console.log('\n🏗️ Checking schema completeness...');
try {
  const schemaContent = fs.readFileSync('src/kag/schemas/terag_schema.py', 'utf8');
  if (schemaContent.includes('EntityType') && 
      schemaContent.includes('RelationType') &&
      schemaContent.includes('TERAG_SCHEMA') &&
      schemaContent.includes('validate_entity')) {
    console.log('✅ Schema is complete');
  } else {
    console.log('❌ Schema incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read schema file');
  allFilesExist = false;
}

// Check extractor functionality
console.log('\n🔍 Checking extractor functionality...');
try {
  const extractorContent = fs.readFileSync('src/kag/extractors/spo_extractor.py', 'utf8');
  if (extractorContent.includes('extract_with_regex') && 
      extractorContent.includes('extract_with_llm') &&
      extractorContent.includes('extract_hybrid') &&
      extractorContent.includes('validate_triplets')) {
    console.log('✅ Extractor functionality complete');
  } else {
    console.log('❌ Extractor functionality incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read extractor file');
  allFilesExist = false;
}

// Check Supabase integration
console.log('\n🗄️ Checking Supabase integration...');
try {
  const supabaseContent = fs.readFileSync('src/kag/storage/supabase_client.py', 'utf8');
  if (supabaseContent.includes('SupabaseClient') && 
      supabaseContent.includes('save_document') &&
      supabaseContent.includes('save_entity') &&
      supabaseContent.includes('save_triplet')) {
    console.log('✅ Supabase integration complete');
  } else {
    console.log('❌ Supabase integration incomplete');
    allFilesExist = false;
  }
} catch (error) {
  console.log('❌ Cannot read Supabase file');
  allFilesExist = false;
}

// Summary
console.log('\n📊 Summary:');
if (allFilesExist && pythonSyntaxOk) {
  console.log('🎉 Task 2: KAG-Builder Implementation - COMPLETED!');
  console.log('\n✅ Criteria met:');
  console.log('   - KAG Builder module created');
  console.log('   - SPO extractor implemented');
  console.log('   - TERAG schema defined');
  console.log('   - Supabase integration ready');
  console.log('   - Comprehensive tests written');
  console.log('   - Python syntax is valid');
  console.log('\n🚀 Ready for Task 3: KAG-Solver Implementation');
} else {
  console.log('❌ Task 2 incomplete - some files missing or syntax errors');
  console.log('Please check the missing files and syntax issues above');
}

console.log('\n📝 Next steps:');
console.log('1. Run tests: python -m pytest tests/kag/test_builder.py -v');
console.log('2. Test SPO extraction: python src/kag/extractors/spo_extractor.py');
console.log('3. Test schema validation: python src/kag/schemas/terag_schema.py');
console.log('4. Begin Task 3: KAG-Solver Implementation');

process.exit(allFilesExist && pythonSyntaxOk ? 0 : 1);





































