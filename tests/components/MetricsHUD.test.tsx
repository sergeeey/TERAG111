import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MetricsHUD } from '../../src/components/immersive/MetricsHUD';

// Mock для teragAPI
vi.mock('../../src/services/terag-api', () => ({
  teragAPI: {
    getLiveMetrics: vi.fn(),
  },
}));

describe('MetricsHUD', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders metrics display', () => {
    render(<MetricsHUD />);
    
    // Проверяем наличие элементов метрик
    expect(screen.getByText(/IEI|iei/i)).toBeDefined();
    expect(screen.getByText(/Coherence|когерентность/i)).toBeDefined();
  });

  it('displays metrics from API', async () => {
    const { teragAPI } = await import('../../src/services/terag-api');
    vi.mocked(teragAPI.getLiveMetrics).mockResolvedValue({
      iei: 0.9,
      coherence: 0.85,
      faithfulness: 0.88,
    });

    render(<MetricsHUD />);

    await waitFor(() => {
      expect(teragAPI.getLiveMetrics).toHaveBeenCalled();
    });
  });

  it('updates metrics periodically', async () => {
    const { teragAPI } = await import('../../src/services/terag-api');
    vi.mocked(teragAPI.getLiveMetrics).mockResolvedValue({
      iei: 0.9,
      coherence: 0.85,
      faithfulness: 0.88,
    });

    vi.useFakeTimers();
    render(<MetricsHUD />);

    // Ждем первый вызов
    await waitFor(() => {
      expect(teragAPI.getLiveMetrics).toHaveBeenCalledTimes(1);
    });

    // Продвигаем время на 5 секунд (период обновления)
    vi.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(teragAPI.getLiveMetrics).toHaveBeenCalledTimes(2);
    });

    vi.useRealTimers();
  });
});














