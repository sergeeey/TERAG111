import { describe, it, expect, beforeEach, vi } from 'vitest';
import { teragAPI } from './terag-api';

// Minimal fetch mock
declare const global: any;

describe('TeragAPI', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('reasoningQuery returns JSON on success', async () => {
    const mock = { response: 'ok', trace: [], iei: 0.9 };
    global.fetch.mockResolvedValue({ ok: true, json: async () => mock });
    const res = await teragAPI.reasoningQuery('hello');
    expect(res.response).toBe('ok');
    expect(res.iei).toBeGreaterThan(0);
  });

  it('reasoningQuery falls back to simulation on failure', async () => {
    global.fetch.mockResolvedValue({ ok: false, statusText: 'Bad Request' });
    const res = await teragAPI.reasoningQuery('hello');
    expect(res.response).toContain('simulation');
  });

  it('getLiveMetrics returns JSON on success', async () => {
    const mock = { iei: 0.9, coherence: 0.9, faithfulness: 0.9 };
    global.fetch.mockResolvedValue({ ok: true, json: async () => mock });
    const res = await teragAPI.getLiveMetrics();
    expect(res.iei).toBeGreaterThan(0);
  });

  it('getReasoningGraph returns JSON on success', async () => {
    const mock = { nodes: [], edges: [] };
    global.fetch.mockResolvedValue({ ok: true, json: async () => mock });
    const res = await teragAPI.getReasoningGraph();
    expect(res.nodes).toBeDefined();
  });

  it('checkHealth returns status on success', async () => {
    const mock = { status: 'ok' };
    global.fetch.mockResolvedValue({ ok: true, json: async () => mock });
    const res = await teragAPI.checkHealth();
    expect(res.status).toBe('ok');
  });
});









