'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface WebSocketContextType {
  socket: WebSocket | null;
  connected: boolean;
  sendMessage: (message: any) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Simulate WebSocket connection
    const ws = {
      send: (data: string) => console.log('Sending:', data),
      close: () => console.log('WebSocket closed'),
      readyState: WebSocket.OPEN,
    } as WebSocket;
    
    setSocket(ws);
    setConnected(true);

    return () => {
      ws.close();
      setConnected(false);
    };
  }, []);

  const sendMessage = (message: any) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message));
    }
  };

  return (
    <WebSocketContext.Provider value={{ socket, connected, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}