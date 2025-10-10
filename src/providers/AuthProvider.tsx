import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate auth check
    const token = localStorage.getItem('token');
    if (token) {
      setUser({
        id: '1',
        email: 'admin@terag.com',
        name: 'John Doe',
        role: 'admin',
      });
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    // Simulate login
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    localStorage.setItem('token', 'fake-token');
    setUser({
      id: '1',
      email,
      name: 'John Doe',
      role: 'admin',
    });
    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}