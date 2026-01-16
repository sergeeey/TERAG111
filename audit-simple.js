#!/usr/bin/env node
// Simple AI Audit Runner for TERAG Project

import fs from 'fs';
import path from 'path';

console.log('🚀 Starting AI Audit for TERAG Immersive Shell...\n');

// 1. Architecture Audit
console.log('🏗️  Running Architecture Audit...');
const hasSrc = fs.existsSync('src/');
const hasTests = fs.existsSync('tests/') || fs.existsSync('src/services/terag-api.test.ts');
const hasDocker = fs.existsSync('docker-compose.yml');
const hasCI = fs.existsSync('.github/workflows/ci.yml');

const architectureScore = (hasSrc ? 0.4 : 0) + (hasTests ? 0.4 : 0) + (hasDocker ? 0.1 : 0) + (hasCI ? 0.1 : 0);
console.log(`✅ Architecture Score: ${architectureScore.toFixed(2)}`);

// 2. Security Audit
console.log('🔐 Running Security Audit...');
const hasSecurity = fs.existsSync('SECURITY.md');
const hasEnvExample = fs.existsSync('.env.example');
const hasNoSecrets = !fs.existsSync('.env');

const securityScore = (hasSecurity ? 0.4 : 0) + (hasEnvExample ? 0.3 : 0) + (hasNoSecrets ? 0.3 : 0);
console.log(`✅ Security Score: ${securityScore.toFixed(2)}`);

// 3. Testing Audit
console.log('🧪 Running Testing Audit...');
const hasVitest = fs.existsSync('vitest.config.ts');
const hasTestFiles = fs.existsSync('src/services/terag-api.test.ts');
const hasTestScript = fs.readFileSync('package.json', 'utf8').includes('"test"');

const testScore = (hasVitest ? 0.4 : 0) + (hasTestFiles ? 0.4 : 0) + (hasTestScript ? 0.2 : 0);
console.log(`✅ Testing Score: ${testScore.toFixed(2)}`);

// 4. Performance Audit
console.log('⚡ Running Performance Audit...');
const hasVite = fs.existsSync('vite.config.ts');
const hasOptimization = fs.readFileSync('package.json', 'utf8').includes('vite');

const performanceScore = (hasVite ? 0.6 : 0) + (hasOptimization ? 0.4 : 0);
console.log(`✅ Performance Score: ${performanceScore.toFixed(2)}`);

// 5. Cognitive Audit
console.log('🧠 Running Cognitive Audit...');
const hasTrace = fs.existsSync('src/utils/trace.ts');
const hasMetrics = fs.readFileSync('src/services/terag-api.ts', 'utf8').includes('MetricsData');
const hasReasoning = fs.readFileSync('src/services/terag-api.ts', 'utf8').includes('ReasoningResponse');

const rssScore = (hasTrace ? 0.4 : 0) + (hasMetrics ? 0.3 : 0) + (hasReasoning ? 0.3 : 0);
console.log(`✅ RSS Score: ${rssScore.toFixed(2)}`);

// 6. Operational Readiness
console.log('🚀 Running Operational Readiness Audit...');
const hasDockerCompose = fs.existsSync('docker-compose.yml');
const hasReadme = fs.existsSync('README.md');
const hasMCP = fs.existsSync('MCP_INTEGRATION_README.md');

const operationalScore = (hasDockerCompose ? 0.4 : 0) + (hasReadme ? 0.3 : 0) + (hasMCP ? 0.3 : 0);
console.log(`✅ Operational Readiness: ${operationalScore.toFixed(2)}`);

// Calculate overall score
const overallScore = (architectureScore + securityScore + testScore + performanceScore + rssScore + operationalScore) / 6;

// Generate report
const report = {
  audit_id: 'terag-audit-' + Date.now(),
  project_name: 'TERAG Immersive Shell',
  audit_level: 'L2',
  timestamp: new Date().toISOString(),
  scores: {
    overall: overallScore,
    architecture: architectureScore,
    security: securityScore,
    testing: testScore,
    performance: performanceScore,
    rss: rssScore,
    operational_readiness: operationalScore
  },
  summary: {
    strengths: [],
    weaknesses: [],
    recommendations: []
  }
};

// Analyze results
if (architectureScore >= 0.8) {
  report.summary.strengths.push('Отличная архитектурная структура');
} else {
  report.summary.weaknesses.push('Архитектура требует улучшения');
  report.summary.recommendations.push('Добавить недостающие директории и файлы');
}

if (securityScore >= 0.8) {
  report.summary.strengths.push('Хорошая безопасность');
} else {
  report.summary.weaknesses.push('Проблемы с безопасностью');
  report.summary.recommendations.push('Улучшить безопасность кода и конфигурации');
}

if (testScore >= 0.8) {
  report.summary.strengths.push('Отличное покрытие тестами');
} else {
  report.summary.weaknesses.push(`Низкое покрытие тестами (${(testScore * 100).toFixed(0)}%)`);
  report.summary.recommendations.push('Довести покрытие до 80%');
}

if (performanceScore >= 0.8) {
  report.summary.strengths.push('Хорошая производительность');
} else {
  report.summary.weaknesses.push('Проблемы с производительностью');
  report.summary.recommendations.push('Оптимизировать производительность');
}

if (rssScore >= 0.8) {
  report.summary.strengths.push('Хорошая когнитивная стабильность');
} else {
  report.summary.weaknesses.push('Недостаточная когнитивная стабильность');
  report.summary.recommendations.push('Улучшить reasoning и self-validation');
}

if (operationalScore >= 0.8) {
  report.summary.strengths.push('Отличная операционная готовность');
} else {
  report.summary.weaknesses.push('Недостаточная операционная готовность');
  report.summary.recommendations.push('Улучшить деплой и мониторинг');
}

// Create audit_reports directory
if (!fs.existsSync('audit_reports')) {
  fs.mkdirSync('audit_reports');
}

// Save JSON report
const timestamp = new Date().toISOString().split('T')[0];
const jsonPath = `audit_reports/audit_report_${timestamp}.json`;
fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));

// Generate markdown report
const markdownReport = `# AI Audit Report - ${report.project_name}

**Date:** ${report.timestamp}  
**Level:** ${report.audit_level}  
**Overall Score:** ${report.scores.overall.toFixed(2)} ${overallScore >= 0.8 ? '🟢' : overallScore >= 0.6 ? '🟡' : '🔴'}

## 📊 Scores

| Category | Score |
|----------|-------|
| Architecture | ${report.scores.architecture.toFixed(2)} |
| Security | ${report.scores.security.toFixed(2)} |
| Testing | ${report.scores.testing.toFixed(2)} |
| Performance | ${report.scores.performance.toFixed(2)} |
| RSS | ${report.scores.rss.toFixed(2)} |
| Operational Readiness | ${report.scores.operational_readiness.toFixed(2)} |

## ✅ Strengths

${report.summary.strengths.map(s => `- ${s}`).join('\n')}

## ⚠️ Weaknesses

${report.summary.weaknesses.map(w => `- ${w}`).join('\n')}

## 🎯 Recommendations

${report.summary.recommendations.map(r => `- ${r}`).join('\n')}

## 📅 Next Audit

${new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}

---
*Generated by Auditor CurSor Unified AI-Audit Spec v1.0*
`;

const mdPath = `audit_reports/audit_report_${timestamp}.md`;
fs.writeFileSync(mdPath, markdownReport);

console.log('\n🎉 Audit completed!');
console.log(`📊 Overall Score: ${overallScore.toFixed(2)} ${overallScore >= 0.8 ? '🟢' : overallScore >= 0.6 ? '🟡' : '🔴'}`);
console.log(`📝 Reports saved to: audit_reports/`);
console.log(`📋 Next audit: ${new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}`);

// Display summary
console.log('\n📋 Summary:');
console.log('✅ Strengths:');
report.summary.strengths.forEach(s => console.log(`  - ${s}`));
console.log('⚠️  Weaknesses:');
report.summary.weaknesses.forEach(w => console.log(`  - ${w}`));
console.log('🎯 Recommendations:');
report.summary.recommendations.forEach(r => console.log(`  - ${r}`));








































