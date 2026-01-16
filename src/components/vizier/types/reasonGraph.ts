/**
 * TypeScript типы для ReasonGraph
 */

export type NodeType = "guardrail" | "planner" | "solver" | "verifier" | "ethical" | "reject";

export type NodeStatus = "pending" | "active" | "completed" | "failed";

export type EdgeType = "reasoning_flow" | "guardrail_check" | "reject" | "data_flow";

export type AlignmentStatus = "ethical" | "questionable" | "harmful";

export interface Position3D {
  x: number;
  y: number;
  z: number;
}

export interface ReasonGraphNode {
  id: string;
  type: NodeType;
  label: string;
  status: NodeStatus;
  confidence: number;
  timestamp: string;
  data?: Record<string, unknown>;
  position: Position3D;
}

export interface ReasonGraphEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  confidence: number;
  data_flow?: Record<string, unknown>;
}

export interface ReasonGraphMetadata {
  query: string;
  final_answer?: string;
  confidence: number;
  ethical_score: number;
  alignment_status: AlignmentStatus;
  secure_reasoning_index: number;
  timestamp: string;
  version: string;
  mlflow_run_id?: string;
  langsmith_run_id?: string;
}

export interface TimelineStep {
  step: string;
  timestamp: string;
  duration: number;
}

export interface ReasonGraph {
  nodes: ReasonGraphNode[];
  edges: ReasonGraphEdge[];
  metadata: ReasonGraphMetadata;
  scratchpad?: string[];
  timeline: TimelineStep[];
}

export interface SSEEvent {
  type: "init" | "update" | "complete" | "error";
  data?: ReasonGraph;
  message?: string;
}


