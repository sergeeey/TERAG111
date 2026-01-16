#!/usr/bin/env node
// Docker MCP Integration Script for TERAG Project
// Контейнеризация и управление сервисами

const fs = require('fs');
const path = require('path');

class DockerIntegration {
  constructor() {
    this.services = {
      frontend: 'terag-frontend',
      backend: 'terag-backend',
      rag: 'terag-rag',
      neo4j: 'terag-neo4j',
      supabase: 'terag-supabase'
    };
  }

  // Docker Compose конфигурация
  generateDockerCompose() {
    return `version: '3.8'

services:
  # Frontend - React/Vite
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_TERAG_API_URL=http://backend:8000
      - VITE_SUPABASE_URL=\${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=\${SUPABASE_ANON_KEY}
    depends_on:
      - backend
    volumes:
      - ./src:/app/src
      - ./public:/app/public
    networks:
      - terag-network

  # Backend - TERAG API
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=\${NEO4J_PASSWORD}
      - SUPABASE_URL=\${SUPABASE_URL}
      - SUPABASE_ANON_KEY=\${SUPABASE_ANON_KEY}
    depends_on:
      - neo4j
      - supabase
    volumes:
      - ./backend:/app
    networks:
      - terag-network

  # RAG Service - ChromaDB + Python
  rag:
    build:
      context: .
      dockerfile: Dockerfile.rag
    ports:
      - "8001:8001"
    environment:
      - CHROMA_PERSIST_DIRECTORY=/app/chroma_db
      - EMBEDDING_MODEL=nomic-embed-text
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./scripts:/app/scripts
    networks:
      - terag-network

  # Neo4j Database
  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/\${NEO4J_PASSWORD}
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - terag-network

  # Supabase Local
  supabase:
    image: supabase/postgres:15.1.1.147
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=\${SUPABASE_DB_PASSWORD}
      - POSTGRES_DB=postgres
    volumes:
      - supabase_data:/var/lib/postgresql/data
      - ./supabase-schema.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - terag-network

  # Ollama for local LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - terag-network

volumes:
  neo4j_data:
  neo4j_logs:
  supabase_data:
  ollama_data:

networks:
  terag-network:
    driver: bridge
`;
  }

  // Dockerfile для Frontend
  generateFrontendDockerfile() {
    return `# Frontend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 5173

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
`;
  }

  // Dockerfile для Backend
  generateBackendDockerfile() {
    return `# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 terag && chown -R terag:terag /app
USER terag

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/healthz || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
`;
  }

  // Dockerfile для RAG
  generateRAGDockerfile() {
    return `# RAG Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-rag.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-rag.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/chroma_db

# Create non-root user
RUN useradd -m -u 1000 rag && chown -R rag:rag /app
USER rag

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8001/health || exit 1

# Start RAG service
CMD ["python", "scripts/rag-server.py"]
`;
  }

  // Nginx конфигурация
  generateNginxConfig() {
    return `events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    server {
        listen 5173;
        server_name localhost;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # RAG proxy
        location /rag/ {
            proxy_pass http://rag:8001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
`;
  }

  // Environment файл для Docker
  generateDockerEnv() {
    return `# Docker Environment Variables
# Neo4j
NEO4J_PASSWORD=terag_neo4j_2025

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_DB_PASSWORD=terag_supabase_2025

# Ollama
OLLAMA_MODEL=deepseek-coder:6.7b

# RAG
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=nomic-embed-text

# Backend
TERAG_API_URL=http://backend:8000
LOG_LEVEL=INFO
`;
  }

  // Скрипты управления
  generateManagementScripts() {
    return {
      'docker-start.sh': `#!/bin/bash
# Start TERAG services
echo "🚀 Starting TERAG services..."

# Create network
docker network create terag-network 2>/dev/null || true

# Start services
docker-compose up -d

echo "✅ TERAG services started!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000"
echo "Neo4j: http://localhost:7474"
echo "Supabase: http://localhost:5432"
`,

      'docker-stop.sh': `#!/bin/bash
# Stop TERAG services
echo "🛑 Stopping TERAG services..."

docker-compose down

echo "✅ TERAG services stopped!"
`,

      'docker-logs.sh': `#!/bin/bash
# View logs
SERVICE=${1:-all}

if [ "$SERVICE" = "all" ]; then
    docker-compose logs -f
else
    docker-compose logs -f $SERVICE
fi
`,

      'docker-rebuild.sh': `#!/bin/bash
# Rebuild and restart
echo "🔄 Rebuilding TERAG services..."

docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "✅ TERAG services rebuilt and restarted!"
`
    };
  }

  // Главная функция интеграции
  async runIntegration() {
    console.log('🚀 Starting Docker MCP Integration...');
    
    // 1. Создаем Docker Compose
    const dockerCompose = this.generateDockerCompose();
    fs.writeFileSync('docker-compose.yml', dockerCompose);
    console.log('📝 Created docker-compose.yml');
    
    // 2. Создаем Dockerfiles
    const frontendDockerfile = this.generateFrontendDockerfile();
    fs.writeFileSync('Dockerfile.frontend', frontendDockerfile);
    console.log('📝 Created Dockerfile.frontend');
    
    const backendDockerfile = this.generateBackendDockerfile();
    fs.writeFileSync('Dockerfile.backend', backendDockerfile);
    console.log('📝 Created Dockerfile.backend');
    
    const ragDockerfile = this.generateRAGDockerfile();
    fs.writeFileSync('Dockerfile.rag', ragDockerfile);
    console.log('📝 Created Dockerfile.rag');
    
    // 3. Создаем Nginx конфигурацию
    const nginxConfig = this.generateNginxConfig();
    fs.writeFileSync('nginx.conf', nginxConfig);
    console.log('📝 Created nginx.conf');
    
    // 4. Создаем .env файл для Docker
    const dockerEnv = this.generateDockerEnv();
    fs.writeFileSync('.env.docker', dockerEnv);
    console.log('📝 Created .env.docker');
    
    // 5. Создаем скрипты управления
    const scripts = this.generateManagementScripts();
    Object.entries(scripts).forEach(([filename, content]) => {
      fs.writeFileSync(filename, content);
      // Делаем исполняемым на Unix системах
      if (process.platform !== 'win32') {
        fs.chmodSync(filename, '755');
      }
      console.log(`📝 Created ${filename}`);
    });
    
    // 6. Создаем requirements файлы
    const requirements = {
      'requirements.txt': `# Backend requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
neo4j==5.15.0
chromadb==0.4.18
langchain==0.1.0
ollama==0.1.7
supabase==2.3.0
`,
      'requirements-rag.txt': `# RAG requirements
chromadb==0.4.18
langchain==0.1.0
langchain-community==0.0.10
ollama==0.1.7
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
networkx==3.1
pyvis==0.3.2
`
    };
    
    Object.entries(requirements).forEach(([filename, content]) => {
      fs.writeFileSync(filename, content);
      console.log(`📝 Created ${filename}`);
    });
    
    console.log('✅ Docker MCP Integration completed!');
    console.log('\n🎯 Next steps:');
    console.log('1. Copy .env.docker to .env and configure your values');
    console.log('2. Run: chmod +x *.sh (on Unix)');
    console.log('3. Run: ./docker-start.sh');
    console.log('4. Access: http://localhost:5173');
  }
}

// Запуск интеграции
if (require.main === module) {
  new DockerIntegration().runIntegration();
}

module.exports = DockerIntegration;






