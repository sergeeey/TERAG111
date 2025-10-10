const TERAG_API_BASE_URL = import.meta.env.VITE_TERAG_API_URL || 'http://localhost:8000';

export interface ReasoningResponse {
  response: string;
  trace: string[];
  iei: number;
  coherence?: number;
  faithfulness?: number;
}

export interface MetricsData {
  iei: number;
  coherence: number;
  faithfulness: number;
  timestamp?: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  x?: number;
  y?: number;
  z?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
}

export interface ReasoningGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface HealthStatus {
  status: string;
  iei?: number;
}

class TeragAPI {
  private baseUrl: string;

  constructor(baseUrl: string = TERAG_API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async reasoningQuery(query: string): Promise<ReasoningResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/reasoning/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Reasoning query failed:', error);
      return {
        response: 'TERAG system is currently offline. Using simulation mode.',
        trace: ['Simulated reasoning trace'],
        iei: 0.85,
        coherence: 0.88,
        faithfulness: 0.87,
      };
    }
  }

  async getLiveMetrics(): Promise<MetricsData> {
    try {
      const response = await fetch(`${this.baseUrl}/metrics/live`);

      if (!response.ok) {
        throw new Error(`Metrics request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Metrics fetch failed:', error);
      return {
        iei: 0.85 + Math.random() * 0.1,
        coherence: 0.88 + Math.random() * 0.08,
        faithfulness: 0.87 + Math.random() * 0.09,
        timestamp: Date.now(),
      };
    }
  }

  async getReasoningGraph(): Promise<ReasoningGraph> {
    try {
      const response = await fetch(`${this.baseUrl}/graph/state`);

      if (!response.ok) {
        throw new Error(`Graph request failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Graph fetch failed:', error);
      return this.getSimulatedGraph();
    }
  }

  async voiceQuery(audioBlob: Blob): Promise<ReasoningResponse> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'query.wav');

      const response = await fetch(`${this.baseUrl}/voice/query`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Voice query failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Voice query failed:', error);
      throw error;
    }
  }

  async checkHealth(): Promise<HealthStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/healthz`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'offline' };
    }
  }

  private getSimulatedGraph(): ReasoningGraph {
    const agents = [
      { id: 'planner', label: 'Planner', type: 'agent' },
      { id: 'intuit', label: 'Intuit', type: 'agent' },
      { id: 'critic', label: 'Critic', type: 'agent' },
      { id: 'verifier', label: 'Verifier', type: 'agent' },
      { id: 'curator', label: 'Curator', type: 'agent' },
      { id: 'reflector', label: 'Reflector', type: 'agent' },
      { id: 'meta', label: 'Meta-Controller', type: 'controller' },
    ];

    const radius = 3;
    const nodes: GraphNode[] = agents.map((agent, index) => {
      const angle = (index / agents.length) * Math.PI * 2;
      return {
        ...agent,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        z: (Math.random() - 0.5) * 2,
      };
    });

    const edges: GraphEdge[] = [
      { source: 'planner', target: 'intuit', weight: 0.9 },
      { source: 'intuit', target: 'critic', weight: 0.85 },
      { source: 'critic', target: 'verifier', weight: 0.88 },
      { source: 'verifier', target: 'curator', weight: 0.92 },
      { source: 'curator', target: 'reflector', weight: 0.87 },
      { source: 'reflector', target: 'meta', weight: 0.91 },
      { source: 'meta', target: 'planner', weight: 0.86 },
    ];

    return { nodes, edges };
  }

  createMetricsStream(callback: (metrics: MetricsData) => void, interval: number = 5000): () => void {
    const intervalId = setInterval(async () => {
      const metrics = await this.getLiveMetrics();
      callback(metrics);
    }, interval);

    return () => clearInterval(intervalId);
  }
}

export const teragAPI = new TeragAPI();
