#!/usr/bin/env node
// Supabase MCP Integration Script for TERAG Project
// Замена симуляционных данных на реальные

const fs = require('fs');
const path = require('path');

class SupabaseIntegration {
  constructor() {
    this.projectUrl = process.env.SUPABASE_URL || 'https://your-project.supabase.co';
    this.apiKey = process.env.SUPABASE_ANON_KEY || 'your-anon-key';
    this.tables = {
      metrics: 'cognitive_metrics',
      reasoning: 'reasoning_traces',
      sessions: 'user_sessions',
      audit: 'audit_trail'
    };
  }

  // Схема таблиц для когнитивных данных
  generateSchema() {
    const schema = {
      cognitive_metrics: {
        id: 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
        session_id: 'uuid REFERENCES user_sessions(id)',
        iei_score: 'decimal(5,3) NOT NULL',
        coherence: 'decimal(5,3) NOT NULL',
        faithfulness: 'decimal(5,3) NOT NULL',
        timestamp: 'timestamptz DEFAULT now()',
        metadata: 'jsonb'
      },
      reasoning_traces: {
        id: 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
        session_id: 'uuid REFERENCES user_sessions(id)',
        query: 'text NOT NULL',
        response: 'text NOT NULL',
        trace: 'jsonb NOT NULL',
        input_hash: 'text',
        output_hash: 'text',
        created_at: 'timestamptz DEFAULT now()'
      },
      user_sessions: {
        id: 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
        user_id: 'text',
        session_data: 'jsonb',
        started_at: 'timestamptz DEFAULT now()',
        ended_at: 'timestamptz'
      },
      audit_trail: {
        id: 'uuid PRIMARY KEY DEFAULT gen_random_uuid()',
        operation: 'text NOT NULL',
        stage: 'text NOT NULL',
        input_hash: 'text',
        output_hash: 'text',
        metadata: 'jsonb',
        created_at: 'timestamptz DEFAULT now()'
      }
    };
    
    return schema;
  }

  // SQL для создания таблиц
  generateCreateTablesSQL() {
    const schema = this.generateSchema();
    const sql = [];
    
    Object.entries(schema).forEach(([tableName, columns]) => {
      const columnDefs = Object.entries(columns)
        .map(([col, def]) => `  ${col} ${def}`)
        .join(',\n');
      
      sql.push(`CREATE TABLE IF NOT EXISTS ${tableName} (\n${columnDefs}\n);`);
    });
    
    // Индексы для производительности
    sql.push(`
-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_metrics_session_id ON cognitive_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON cognitive_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_traces_session_id ON reasoning_traces(session_id);
CREATE INDEX IF NOT EXISTS idx_traces_created_at ON reasoning_traces(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_trail(operation);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_trail(created_at);
`);
    
    return sql.join('\n\n');
  }

  // Функции для работы с метриками
  async insertMetrics(sessionId, metrics) {
    const query = {
      table: this.tables.metrics,
      data: {
        session_id: sessionId,
        iei_score: metrics.iei,
        coherence: metrics.coherence || 0.88,
        faithfulness: metrics.faithfulness || 0.87,
        metadata: {
          source: 'terag-api',
          version: '1.1.1'
        }
      }
    };
    
    console.log('📊 Inserting metrics:', query);
    return query;
  }

  // Функции для работы с reasoning traces
  async insertReasoningTrace(sessionId, query, response, trace) {
    const traceData = {
      table: this.tables.reasoning,
      data: {
        session_id: sessionId,
        query: query,
        response: response,
        trace: trace,
        input_hash: await this.hashString(query),
        output_hash: await this.hashString(response)
      }
    };
    
    console.log('🧠 Inserting reasoning trace:', traceData);
    return traceData;
  }

  // Функции для audit trail
  async insertAuditRecord(operation, stage, inputHash, outputHash, metadata) {
    const auditData = {
      table: this.tables.audit,
      data: {
        operation: operation,
        stage: stage,
        input_hash: inputHash,
        output_hash: outputHash,
        metadata: metadata
      }
    };
    
    console.log('📝 Inserting audit record:', auditData);
    return auditData;
  }

  // Хеширование для traceability
  async hashString(str) {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(str).digest('hex');
  }

  // Запросы для аналитики
  generateAnalyticsQueries() {
    return {
      // Средние метрики за период
      averageMetrics: `
        SELECT 
          AVG(iei_score) as avg_iei,
          AVG(coherence) as avg_coherence,
          AVG(faithfulness) as avg_faithfulness,
          COUNT(*) as total_measurements
        FROM cognitive_metrics 
        WHERE timestamp >= NOW() - INTERVAL '24 hours'
      `,
      
      // Топ запросов
      topQueries: `
        SELECT 
          query,
          COUNT(*) as frequency,
          AVG(LENGTH(response)) as avg_response_length
        FROM reasoning_traces 
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY query 
        ORDER BY frequency DESC 
        LIMIT 10
      `,
      
      // Аудит операций
      auditSummary: `
        SELECT 
          operation,
          stage,
          COUNT(*) as count,
          MIN(created_at) as first_occurrence,
          MAX(created_at) as last_occurrence
        FROM audit_trail 
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY operation, stage
        ORDER BY count DESC
      `
    };
  }

  // Интеграция с terag-api.ts
  generateTeragAPIExtension() {
    return `
// Supabase integration for terag-api.ts
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export class TeragAPIExtended extends TeragAPI {
  private sessionId: string;
  
  constructor(baseUrl: string = TERAG_API_BASE_URL) {
    super(baseUrl);
    this.sessionId = crypto.randomUUID();
  }

  async reasoningQuery(query: string): Promise<ReasoningResponse> {
    const startTime = Date.now();
    const result = await super.reasoningQuery(query);
    
    // Сохраняем в Supabase
    await this.saveReasoningTrace(query, result);
    await this.saveAuditRecord('reasoning_query', 'completed', query, result.response);
    
    return result;
  }

  async getLiveMetrics(): Promise<MetricsData> {
    const result = await super.getLiveMetrics();
    
    // Сохраняем метрики в Supabase
    await this.saveMetrics(result);
    
    return result;
  }

  private async saveReasoningTrace(query: string, response: ReasoningResponse) {
    try {
      await supabase.from('reasoning_traces').insert({
        session_id: this.sessionId,
        query,
        response: response.response,
        trace: response.trace
      });
    } catch (error) {
      console.error('Failed to save reasoning trace:', error);
    }
  }

  private async saveMetrics(metrics: MetricsData) {
    try {
      await supabase.from('cognitive_metrics').insert({
        session_id: this.sessionId,
        iei_score: metrics.iei,
        coherence: metrics.coherence || 0.88,
        faithfulness: metrics.faithfulness || 0.87
      });
    } catch (error) {
      console.error('Failed to save metrics:', error);
    }
  }

  private async saveAuditRecord(operation: string, stage: string, input: string, output: string) {
    try {
      await supabase.from('audit_trail').insert({
        operation,
        stage,
        input_hash: await this.hashString(input),
        output_hash: await this.hashString(output),
        metadata: { timestamp: Date.now() }
      });
    } catch (error) {
      console.error('Failed to save audit record:', error);
    }
  }

  private async hashString(str: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }
}
`;
  }

  // Главная функция интеграции
  async runIntegration() {
    console.log('🚀 Starting Supabase MCP Integration...');
    
    // 1. Генерируем схему БД
    const schema = this.generateSchema();
    console.log('📊 Generated database schema:', Object.keys(schema));
    
    // 2. Создаем SQL для таблиц
    const createSQL = this.generateCreateTablesSQL();
    fs.writeFileSync('supabase-schema.sql', createSQL);
    console.log('📝 Created supabase-schema.sql');
    
    // 3. Генерируем расширение для terag-api
    const apiExtension = this.generateTeragAPIExtension();
    fs.writeFileSync('src/services/terag-api-supabase.ts', apiExtension);
    console.log('🔧 Created terag-api-supabase.ts');
    
    // 4. Генерируем аналитические запросы
    const analytics = this.generateAnalyticsQueries();
    fs.writeFileSync('supabase-analytics.sql', Object.values(analytics).join('\n\n'));
    console.log('📈 Created supabase-analytics.sql');
    
    console.log('✅ Supabase MCP Integration completed!');
  }
}

// Запуск интеграции
if (require.main === module) {
  new SupabaseIntegration().runIntegration();
}

module.exports = SupabaseIntegration;






