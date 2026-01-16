export interface TraceRecord {
  id: string; // stable uuid for the operation
  stage: string; // e.g., reasoning.query, metrics.fetch
  inputHash?: string; // sha256 of input payload (masked)
  outputHash?: string; // sha256 of output payload (masked)
  startedAt: number;
  finishedAt?: number;
  meta?: Record<string, unknown>;
}

function toHex(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let hex = '';
  for (let i = 0; i < bytes.length; i++) {
    const h = bytes[i].toString(16).padStart(2, '0');
    hex += h;
  }
  return hex;
}

export async function sha256(data: string): Promise<string> {
  const enc = new TextEncoder();
  const digest = await crypto.subtle.digest('SHA-256', enc.encode(data));
  return toHex(digest);
}

export function startTrace(stage: string, meta?: Record<string, unknown>): TraceRecord {
  return {
    id: crypto.randomUUID(),
    stage,
    startedAt: Date.now(),
    meta
  };
}

export function finishTrace(record: TraceRecord, overrides?: Partial<TraceRecord>): TraceRecord {
  return {
    ...record,
    finishedAt: Date.now(),
    ...overrides
  };
}









