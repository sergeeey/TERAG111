#!/usr/bin/env node
// Simple MCP Integration Runner
// Запускает интеграцию MCP серверов

import fs from 'fs';
import path from 'path';

console.log('🚀 Starting MCP Integration for TERAG...\n');

// 1. Обновляем MCP конфигурацию
console.log('📝 Updating MCP configuration...');
const mcpConfig = {
  mcpServers: {
    nx: {
      uri: "mcp://nx",
      enabled: false,
      description: "Nx MCP для архитектурного контекста",
      capabilities: ["listProjects", "graph", "runTask"]
    },
    github: {
      uri: "mcp://github",
      enabled: true,
      description: "GitHub MCP для DevOps и CI/CD",
      capabilities: ["repos", "issues", "pullRequests"],
      priority: "critical"
    },
    supabase: {
      uri: "mcp://supabase",
      enabled: true,
      description: "Supabase MCP для когнитивной памяти",
      capabilities: ["query", "insert", "update", "delete"],
      priority: "high"
    },
    notion: {
      uri: "mcp://notion",
      enabled: true,
      description: "Notion MCP для explainability",
      capabilities: ["createPage", "updatePage", "search", "getPage"],
      priority: "medium"
    },
    context7: {
      uri: "mcp://context7",
      enabled: false,
      description: "Context7 MCP для живой документации",
      capabilities: ["fetch", "search", "sync"]
    },
    taskmaster: {
      uri: "mcp://taskmaster",
      enabled: false,
      description: "TaskMaster MCP для управления reasoning-задачами",
      capabilities: ["createTask", "updateTask", "listTasks"]
    },
    docker: {
      uri: "mcp://docker",
      enabled: true,
      description: "Docker MCP для управления контейнерами",
      capabilities: ["listContainers", "runContainer", "buildImage"],
      priority: "medium"
    }
  }
};

const configPath = path.join(process.env.USERPROFILE || process.env.HOME, '.cursor', 'mcp.json');
fs.writeFileSync(configPath, JSON.stringify(mcpConfig, null, 2));
console.log('✅ MCP configuration updated');

// 2. Создаем Docker Compose
console.log('\n🐳 Creating Docker Compose...');
const dockerCompose = `version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_TERAG_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - terag-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=terag_neo4j_2025
    depends_on:
      - neo4j
    networks:
      - terag-network

  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/terag_neo4j_2025
    volumes:
      - neo4j_data:/data
    networks:
      - terag-network

volumes:
  neo4j_data:

networks:
  terag-network:
    driver: bridge
`;

fs.writeFileSync('docker-compose.yml', dockerCompose);
console.log('✅ Docker Compose created');

// 3. Создаем README
console.log('\n📚 Creating documentation...');
const readme = `# MCP Integration for TERAG Project

## 🎯 Active MCP Servers

### ✅ GitHub MCP (Critical)
- CI/CD automation
- Issue tracking
- PR management

### ✅ Supabase MCP (High)
- Real data storage
- Cognitive metrics
- Reasoning traces

### ✅ Notion MCP (Medium)
- Automatic reports
- Documentation
- Analytics

### ✅ Docker MCP (Medium)
- Containerization
- Service orchestration
- Deployment

## 🚀 Quick Start

1. Restart Cursor to load MCP configuration
2. Configure environment variables
3. Run: docker-compose up -d
4. Access: http://localhost:5173

## 📊 Benefits

- Automated CI/CD with GitHub
- Real data instead of simulation
- Smart reporting with Notion
- Easy deployment with Docker
`;

fs.writeFileSync('MCP_INTEGRATION_README.md', readme);
console.log('✅ Documentation created');

// 4. Обновляем package.json
console.log('\n📦 Updating package.json...');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
packageJson.scripts = {
  ...packageJson.scripts,
  'mcp:status': 'echo "MCP servers configured. Restart Cursor to activate."',
  'docker:start': 'docker-compose up -d',
  'docker:stop': 'docker-compose down',
  'docker:logs': 'docker-compose logs -f'
};

fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));
console.log('✅ Package.json updated');

console.log('\n🎉 MCP Integration completed!');
console.log('\n📋 Next steps:');
console.log('1. Restart Cursor IDE');
console.log('2. Configure environment variables');
console.log('3. Run: npm run docker:start');
console.log('4. Access: http://localhost:5173');
console.log('\n🔧 MCP servers activated:');
console.log('- GitHub (Critical)');
console.log('- Supabase (High)');
console.log('- Notion (Medium)');
console.log('- Docker (Medium)');









































