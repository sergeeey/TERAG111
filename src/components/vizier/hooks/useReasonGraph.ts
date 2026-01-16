/**
 * React Hook для работы с ReasonGraph через SSE
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import type { ReasonGraph, SSEEvent } from '../types/reasonGraph';

interface UseReasonGraphOptions {
  query: string;
  show?: string[];
  threadId?: string;
  autoStart?: boolean;
}

interface UseReasonGraphReturn {
  reasonGraph: ReasonGraph | null;
  isStreaming: boolean;
  error: string | null;
  start: () => void;
  stop: () => void;
  reconnect: () => void;
}

export function useReasonGraph(options: UseReasonGraphOptions): UseReasonGraphReturn {
  const { query, show, threadId, autoStart = true } = options;
  
  const [reasonGraph, setReasonGraph] = useState<ReasonGraph | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const start = useCallback(() => {
    if (eventSourceRef.current) {
      return; // Уже запущен
    }

    setIsStreaming(true);
    setError(null);

    // Формируем URL для SSE
    const params = new URLSearchParams({
      query,
      ...(show && show.length > 0 && { show: show.join(',') }),
      ...(threadId && { thread_id: threadId })
    });

    const url = `/api/stream/reasoning?${params.toString()}`;
    
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const sseEvent: SSEEvent = JSON.parse(event.data);
        
        switch (sseEvent.type) {
          case 'init':
          case 'update':
            if (sseEvent.data) {
              setReasonGraph(sseEvent.data);
            }
            break;
          
          case 'complete':
            if (sseEvent.data) {
              setReasonGraph(sseEvent.data);
            }
            setIsStreaming(false);
            eventSource.close();
            eventSourceRef.current = null;
            break;
          
          case 'error':
            setError(sseEvent.message || 'Unknown error');
            setIsStreaming(false);
            eventSource.close();
            eventSourceRef.current = null;
            break;
        }
      } catch (e) {
        console.error('Error parsing SSE event:', e);
        setError('Failed to parse event');
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE error:', err);
      setError('Connection error');
      setIsStreaming(false);
      
      // Попытка переподключения через 3 секунды
      reconnectTimeoutRef.current = setTimeout(() => {
        if (eventSourceRef.current) {
          reconnect();
        }
      }, 3000);
    };
  }, [query, show, threadId]);

  const stop = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const reconnect = useCallback(() => {
    stop();
    setTimeout(() => {
      start();
    }, 1000);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [start, stop]);

  useEffect(() => {
    if (autoStart) {
      start();
    }

    return () => {
      stop();
    };
  }, [autoStart, start, stop]);

  return {
    reasonGraph,
    isStreaming,
    error,
    start,
    stop,
    reconnect
  };
}


