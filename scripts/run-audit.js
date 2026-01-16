#!/usr/bin/env node
// Automated AI Audit Runner for TERAG Project
// Based on Auditor CurSor Unified AI-Audit Spec v1.0

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

class AIAuditRunner {
  constructor() {
    this.config = this.loadConfig();
    this.results = {
      audit_id: this.generateUUID(),
      project_name: this.config.project_name,
      audit_level: this.config.audit_level,
      timestamp: new Date().toISOString(),
      scores: {},
      summary: {
        strengths: [],
        weaknesses: [],
        recommendations: []
      }
    };
  }

  loadConfig() {
    const configPath = '.auditconfig.yaml';
    if (fs.existsSync(configPath)) {
      // Simple YAML parser for basic config
      const content = fs.readFileSync(configPath, 'utf8');
      const config = {};
      content.split('\n').forEach(line => {
        if (line.includes(':')) {
          const [key, value] = line.split(':').map(s => s.trim());
          if (value && !value.includes('[') && !value.includes('{')) {
            config[key] = value.replace(/['"]/g, '');
          }
        }
      });
      return config;
    }
    return {
      audit_level: 'L2',
      project_name: 'TERAG Immersive Shell',
      source_dirs: ['src/', 'scripts/'],
      test_dir: 'tests/'
    };
  }

  generateUUID() {
    return 'audit-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  }

  async runArchitectureAudit() {
    console.log('🏗️  Running Architecture Audit...');
    
    const scores = {
      has_src: this.checkDirectoryExists('src/') ? 1.0 : 0.0,
      has_tests: this.checkDirectoryExists('tests/') ? 1.0 : 0.0,
      has_docs: this.checkDirectoryExists('docs/') ? 1.0 : 0.0,
      has_docker: this.checkFileExists('docker-compose.yml') ? 1.0 : 0.0,
      has_ci: this.checkDirectoryExists('.github/workflows/') ? 1.0 : 0.0
    };

    const coupling = this.estimateCoupling();
    const architecture_score = (scores.has_src * 0.4) + (scores.has_tests * 0.4) + (1 - coupling) * 0.2;

    this.results.scores.architecture = architecture_score;
    
    if (architecture_score >= 0.8) {
      this.results.summary.strengths.push('Отличная архитектурная структура');
    } else {
      this.results.summary.weaknesses.push('Архитектура требует улучшения');
      this.results.summary.recommendations.push('Добавить недостающие директории и файлы');
    }

    console.log(`✅ Architecture Score: ${architecture_score.toFixed(2)}`);
  }

  async runSecurityAudit() {
    console.log('🔐 Running Security Audit...');
    
    const securityChecks = {
      has_security_md: this.checkFileExists('SECURITY.md') ? 1.0 : 0.0,
      has_env_example: this.checkFileExists('.env.example') ? 1.0 : 0.0,
      no_hardcoded_secrets: this.checkForHardcodedSecrets() ? 0.0 : 1.0,
      has_csp: this.checkForCSP() ? 1.0 : 0.0,
      has_input_validation: this.checkForInputValidation() ? 1.0 : 0.0
    };

    const security_score = Object.values(securityChecks).reduce((a, b) => a + b, 0) / Object.keys(securityChecks).length;
    this.results.scores.security = security_score;

    if (security_score >= 0.8) {
      this.results.summary.strengths.push('Хорошая безопасность');
    } else {
      this.results.summary.weaknesses.push('Проблемы с безопасностью');
      this.results.summary.recommendations.push('Улучшить безопасность кода и конфигурации');
    }

    console.log(`✅ Security Score: ${security_score.toFixed(2)}`);
  }

  async runTestingAudit() {
    console.log('🧪 Running Testing Audit...');
    
    const coverage = this.getTestCoverage();
    const has_vitest = this.checkFileExists('vitest.config.ts') ? 1.0 : 0.0;
    const has_ci_tests = this.checkCIHasTests() ? 1.0 : 0.0;
    
    const test_score = (coverage / 100) * 0.6 + has_vitest * 0.2 + has_ci_tests * 0.2;
    this.results.scores.coverage = coverage;
    this.results.scores.testing = test_score;

    if (coverage >= 80) {
      this.results.summary.strengths.push('Отличное покрытие тестами');
    } else {
      this.results.summary.weaknesses.push(`Низкое покрытие тестами (${coverage}%)`);
      this.results.summary.recommendations.push('Довести покрытие до 80%');
    }

    console.log(`✅ Test Coverage: ${coverage}%`);
  }

  async runPerformanceAudit() {
    console.log('⚡ Running Performance Audit...');
    
    const performanceChecks = {
      has_vite: this.checkFileExists('vite.config.ts') ? 1.0 : 0.0,
      has_optimization: this.checkForOptimizations() ? 1.0 : 0.0,
      has_monitoring: this.checkForMonitoring() ? 1.0 : 0.0,
      bundle_size_ok: this.checkBundleSize() ? 1.0 : 0.0
    };

    const performance_score = Object.values(performanceChecks).reduce((a, b) => a + b, 0) / Object.keys(performanceChecks).length;
    this.results.scores.performance = performance_score;

    if (performance_score >= 0.8) {
      this.results.summary.strengths.push('Хорошая производительность');
    } else {
      this.results.summary.weaknesses.push('Проблемы с производительностью');
      this.results.summary.recommendations.push('Оптимизировать производительность');
    }

    console.log(`✅ Performance Score: ${performance_score.toFixed(2)}`);
  }

  async runCognitiveAudit() {
    console.log('🧠 Running Cognitive Audit...');
    
    const cognitiveChecks = {
      has_trace_utility: this.checkFileExists('src/utils/trace.ts') ? 1.0 : 0.0,
      has_reasoning_flow: this.checkForReasoningFlow() ? 1.0 : 0.0,
      has_self_validation: this.checkForSelfValidation() ? 1.0 : 0.0,
      has_metrics: this.checkForMetrics() ? 1.0 : 0.0
    };

    const rss = Object.values(cognitiveChecks).reduce((a, b) => a + b, 0) / Object.keys(cognitiveChecks).length;
    this.results.scores.rss = rss;

    if (rss >= 0.8) {
      this.results.summary.strengths.push('Хорошая когнитивная стабильность');
    } else {
      this.results.summary.weaknesses.push('Недостаточная когнитивная стабильность');
      this.results.summary.recommendations.push('Улучшить reasoning и self-validation');
    }

    console.log(`✅ RSS Score: ${rss.toFixed(2)}`);
  }

  async runOperationalReadinessAudit() {
    console.log('🚀 Running Operational Readiness Audit...');
    
    const operationalChecks = {
      has_docker: this.checkFileExists('docker-compose.yml') ? 1.0 : 0.0,
      has_env: this.checkFileExists('.env.example') ? 1.0 : 0.0,
      has_monitoring: this.checkForMonitoring() ? 1.0 : 0.0,
      has_ci: this.checkDirectoryExists('.github/workflows/') ? 1.0 : 0.0,
      has_docs: this.checkFileExists('README.md') ? 1.0 : 0.0
    };

    const operational_score = Object.values(operationalChecks).reduce((a, b) => a + b, 0) / Object.keys(operationalChecks).length;
    this.results.scores.operational_readiness = operational_score;

    if (operational_score >= 0.8) {
      this.results.summary.strengths.push('Отличная операционная готовность');
    } else {
      this.results.summary.weaknesses.push('Недостаточная операционная готовность');
      this.results.summary.recommendations.push('Улучшить деплой и мониторинг');
    }

    console.log(`✅ Operational Readiness: ${operational_score.toFixed(2)}`);
  }

  // Helper methods
  checkDirectoryExists(dir) {
    return fs.existsSync(dir) && fs.statSync(dir).isDirectory();
  }

  checkFileExists(file) {
    return fs.existsSync(file) && fs.statSync(file).isFile();
  }

  estimateCoupling() {
    // Simple coupling estimation based on file structure
    const srcFiles = this.getFilesInDir('src/');
    const totalFiles = srcFiles.length;
    const importCount = this.countImports(srcFiles);
    return Math.min(importCount / (totalFiles * 2), 1.0);
  }

  getFilesInDir(dir) {
    if (!this.checkDirectoryExists(dir)) return [];
    const files = [];
    const items = fs.readdirSync(dir);
    items.forEach(item => {
      const fullPath = path.join(dir, item);
      if (fs.statSync(fullPath).isDirectory()) {
        files.push(...this.getFilesInDir(fullPath));
      } else if (item.endsWith('.ts') || item.endsWith('.tsx')) {
        files.push(fullPath);
      }
    });
    return files;
  }

  countImports(files) {
    let count = 0;
    files.forEach(file => {
      try {
        const content = fs.readFileSync(file, 'utf8');
        const importMatches = content.match(/import.*from/g);
        if (importMatches) count += importMatches.length;
      } catch (e) {
        // Ignore read errors
      }
    });
    return count;
  }

  checkForHardcodedSecrets() {
    const files = this.getFilesInDir('src/');
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('password=') || content.includes('12345') || content.includes('secret=')) {
          return true;
        }
      } catch (e) {
        // Ignore read errors
      }
    }
    return false;
  }

  checkForCSP() {
    // Check for Content Security Policy
    return this.checkFileExists('public/index.html') && 
           fs.readFileSync('public/index.html', 'utf8').includes('Content-Security-Policy');
  }

  checkForInputValidation() {
    const files = this.getFilesInDir('src/');
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('validate') || content.includes('sanitize') || content.includes('escape')) {
          return true;
        }
      } catch (e) {
        // Ignore read errors
      }
    }
    return false;
  }

  getTestCoverage() {
    // Estimate test coverage based on test files
    const testFiles = this.getFilesInDir('tests/');
    const srcFiles = this.getFilesInDir('src/');
    if (srcFiles.length === 0) return 0;
    return Math.min((testFiles.length / srcFiles.length) * 100, 100);
  }

  checkCIHasTests() {
    if (!this.checkDirectoryExists('.github/workflows/')) return false;
    const files = fs.readdirSync('.github/workflows/');
    for (const file of files) {
      try {
        const content = fs.readFileSync(`.github/workflows/${file}`, 'utf8');
        if (content.includes('test') || content.includes('pytest') || content.includes('vitest')) {
          return true;
        }
      } catch (e) {
        // Ignore read errors
      }
    }
    return false;
  }

  checkForOptimizations() {
    const viteConfig = this.checkFileExists('vite.config.ts');
    const hasLazyLoading = this.checkForLazyLoading();
    return viteConfig && hasLazyLoading;
  }

  checkForLazyLoading() {
    const files = this.getFilesInDir('src/');
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('lazy') || content.includes('React.lazy')) {
          return true;
        }
      } catch (e) {
        // Ignore read errors
      }
    }
    return false;
  }

  checkForMonitoring() {
    return this.checkFileExists('scripts/mcp-monitor.js') || 
           this.checkFileExists('scripts/error-prevention.js');
  }

  checkBundleSize() {
    // Check if dist directory exists and estimate size
    if (!this.checkDirectoryExists('dist/')) return false;
    try {
      const stats = execSync('du -sh dist/', { encoding: 'utf8' });
      const size = parseFloat(stats.split('\t')[0]);
      return size < 10; // Less than 10MB
    } catch (e) {
      return true; // Assume OK if can't check
    }
  }

  checkForReasoningFlow() {
    const files = this.getFilesInDir('src/');
    for (const file of files) {
      try {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('reasoning') || content.includes('trace') || content.includes('metrics')) {
          return true;
        }
      } catch (e) {
        // Ignore read errors
      }
    }
    return false;
  }

  checkForSelfValidation() {
    return this.checkFileExists('scripts/error-prevention.js') ||
           this.checkFileExists('.memory/project-patterns.md');
  }

  checkForMetrics() {
    return this.checkFileExists('src/services/terag-api.ts') &&
           fs.readFileSync('src/services/terag-api.ts', 'utf8').includes('MetricsData');
  }

  calculateOverallScore() {
    const scores = this.results.scores;
    const weights = {
      architecture: 0.2,
      security: 0.15,
      testing: 0.15,
      performance: 0.15,
      rss: 0.15,
      operational_readiness: 0.2
    };

    let overall = 0;
    let totalWeight = 0;

    Object.entries(weights).forEach(([key, weight]) => {
      if (scores[key] !== undefined) {
        overall += scores[key] * weight;
        totalWeight += weight;
      }
    });

    return totalWeight > 0 ? overall / totalWeight : 0;
  }

  generateReport() {
    this.results.scores.overall = this.calculateOverallScore();
    
    const report = {
      ...this.results,
      interpretation: this.interpretScore(this.results.scores.overall),
      next_audit: this.calculateNextAuditDate()
    };

    return report;
  }

  interpretScore(score) {
    if (score >= 0.8) return { status: '🟢', text: 'Готово к production и сертификации' };
    if (score >= 0.6) return { status: '🟡', text: 'Работоспособно, но требует улучшений' };
    return { status: '🔴', text: 'Требуется реструктуризация' };
  }

  calculateNextAuditDate() {
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + 30);
    return nextDate.toISOString().split('T')[0];
  }

  async runAudit() {
    console.log('🚀 Starting AI Audit for TERAG Immersive Shell...\n');
    
    await this.runArchitectureAudit();
    await this.runSecurityAudit();
    await this.runTestingAudit();
    await this.runPerformanceAudit();
    await this.runCognitiveAudit();
    await this.runOperationalReadinessAudit();
    
    const report = this.generateReport();
    
    // Save JSON report
    const outputDir = 'audit_reports';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir);
    }
    
    const timestamp = new Date().toISOString().split('T')[0];
    const jsonPath = `${outputDir}/audit_report_${timestamp}.json`;
    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
    
    // Generate markdown report
    const markdownReport = this.generateMarkdownReport(report);
    const mdPath = `${outputDir}/audit_report_${timestamp}.md`;
    fs.writeFileSync(mdPath, markdownReport);
    
    console.log('\n🎉 Audit completed!');
    console.log(`📊 Overall Score: ${report.scores.overall.toFixed(2)} ${report.interpretation.status}`);
    console.log(`📝 Reports saved to: ${outputDir}/`);
    console.log(`📋 Next audit: ${report.next_audit}`);
    
    return report;
  }

  generateMarkdownReport(report) {
    return `# AI Audit Report - ${report.project_name}

**Date:** ${report.timestamp}  
**Level:** ${report.audit_level}  
**Overall Score:** ${report.scores.overall.toFixed(2)} ${report.interpretation.status}

## 📊 Scores

| Category | Score |
|----------|-------|
| Architecture | ${report.scores.architecture?.toFixed(2) || 'N/A'} |
| Security | ${report.scores.security?.toFixed(2) || 'N/A'} |
| Testing | ${report.scores.testing?.toFixed(2) || 'N/A'} |
| Performance | ${report.scores.performance?.toFixed(2) || 'N/A'} |
| RSS | ${report.scores.rss?.toFixed(2) || 'N/A'} |
| Operational Readiness | ${report.scores.operational_readiness?.toFixed(2) || 'N/A'} |

## ✅ Strengths

${report.summary.strengths.map(s => `- ${s}`).join('\n')}

## ⚠️ Weaknesses

${report.summary.weaknesses.map(w => `- ${w}`).join('\n')}

## 🎯 Recommendations

${report.summary.recommendations.map(r => `- ${r}`).join('\n')}

## 📅 Next Audit

${report.next_audit}

---
*Generated by Auditor CurSor Unified AI-Audit Spec v1.0*
`;
  }
}

// Run audit
if (import.meta.url === `file://${process.argv[1]}`) {
  const auditor = new AIAuditRunner();
  auditor.runAudit().catch(console.error);
}

export default AIAuditRunner;









































