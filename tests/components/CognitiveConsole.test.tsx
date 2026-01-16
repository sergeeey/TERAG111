import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CognitiveConsole } from '../../src/components/immersive/CognitiveConsole';

// Mock для teragAPI
vi.mock('../../src/services/terag-api', () => ({
  teragAPI: {
    reasoningQuery: vi.fn(),
  },
}));

describe('CognitiveConsole', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders input field', () => {
    render(<CognitiveConsole />);
    const input = screen.getByPlaceholderText(/спросите|ask/i);
    expect(input).toBeDefined();
  });

  it('handles text input', async () => {
    render(<CognitiveConsole />);
    const input = screen.getByPlaceholderText(/спросите|ask/i);
    
    fireEvent.change(input, { target: { value: 'test query' } });
    
    await waitFor(() => {
      expect(input).toHaveValue('test query');
    });
  });

  it('submits query on button click', async () => {
    const { teragAPI } = await import('../../src/services/terag-api');
    vi.mocked(teragAPI.reasoningQuery).mockResolvedValue({
      response: 'Test response',
      trace: [],
      iei: 0.9,
    });

    render(<CognitiveConsole />);
    const input = screen.getByPlaceholderText(/спросите|ask/i);
    const button = screen.getByRole('button', { name: /отправить|send/i });

    fireEvent.change(input, { target: { value: 'test' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(teragAPI.reasoningQuery).toHaveBeenCalledWith('test');
    });
  });
});














