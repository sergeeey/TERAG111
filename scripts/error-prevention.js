#!/usr/bin/env node
// Error Prevention Script for Cursor
// Запускать перед каждым коммитом

const fs = require('fs');
const path = require('path');

class ErrorPreventionScript {
  constructor() {
    this.errors = [];
    this.patterns = JSON.parse(fs.readFileSync('.memory/project-patterns.json', 'utf8'));
  }

  // Проверка на частые ошибки
  checkCommonErrors() {
    console.log('🔍 Checking for common errors...');
    
    // Проверка на хардкод пароли
    this.checkHardcodedPasswords();
    
    // Проверка на дублирование файлов
    this.checkDuplicates();
    
    // Проверка на кириллицу в неправильных местах
    this.checkCyrillicIssues();
    
    // Проверка на отсутствующие директории
    this.checkMissingDirectories();
  }

  checkHardcodedPasswords() {
    const files = this.getAllFiles('.');
    files.forEach(file => {
      if (file.endsWith('.py') || file.endsWith('.js') || file.endsWith('.ts')) {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('12345') || content.includes('password=')) {
          this.errors.push(`Hardcoded password in ${file}`);
        }
      }
    });
  }

  checkDuplicates() {
    // Проверка на дублирование src/ и app/
    if (fs.existsSync('src') && fs.existsSync('app')) {
      this.errors.push('Duplicate UI structures: src/ and app/ exist');
    }
  }

  checkCyrillicIssues() {
    // Проверка на кириллицу в .js/.ts файлах (кроме переводов)
    const files = this.getAllFiles('src');
    files.forEach(file => {
      if (file.endsWith('.js') || file.endsWith('.ts')) {
        const content = fs.readFileSync(file, 'utf8');
        if (/[а-яё]/i.test(content) && !file.includes('translations')) {
          this.errors.push(`Cyrillic in code file ${file} - consider using edit_file`);
        }
      }
    });
  }

  checkMissingDirectories() {
    const requiredDirs = ['docs', '.memory', 'scripts'];
    requiredDirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        this.errors.push(`Missing required directory: ${dir}`);
      }
    });
  }

  getAllFiles(dir) {
    let files = [];
    const items = fs.readdirSync(dir);
    items.forEach(item => {
      const fullPath = path.join(dir, item);
      if (fs.statSync(fullPath).isDirectory()) {
        files = files.concat(this.getAllFiles(fullPath));
      } else {
        files.push(fullPath);
      }
    });
    return files;
  }

  // Запуск проверок
  run() {
    this.checkCommonErrors();
    
    if (this.errors.length > 0) {
      console.log('❌ Found errors:');
      this.errors.forEach(error => console.log(`  - ${error}`));
      process.exit(1);
    } else {
      console.log('✅ No common errors found');
    }
  }
}

// Запуск скрипта
new ErrorPreventionScript().run();






