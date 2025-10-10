import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './providers/ThemeProvider';
import { AuthProvider } from './providers/AuthProvider';
import { WebSocketProvider } from './providers/WebSocketProvider';
import { Layout } from './components/layout/Layout';
import { LoadingSpinner } from './components/ui/LoadingSpinner';
import { Toaster } from './components/ui/Toaster';

// Lazy load pages
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Documents = React.lazy(() => import('./pages/Documents'));
const Query = React.lazy(() => import('./pages/Query'));
const KnowledgeGraph = React.lazy(() => import('./pages/KnowledgeGraph'));
const ABTesting = React.lazy(() => import('./pages/ABTesting'));
const Analytics = React.lazy(() => import('./pages/Analytics'));
const Settings = React.lazy(() => import('./pages/Settings'));
const TeragSystem = React.lazy(() => import('./pages/TeragSystem'));


function App() {
  return (
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <Router>
              <div className="min-h-screen bg-terag-gradient text-terag-text-primary">
                <Layout>
                  <Suspense fallback={<LoadingSpinner />}>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/documents" element={<Documents />} />
                      <Route path="/query" element={<Query />} />
                      <Route path="/graph" element={<KnowledgeGraph />} />
                      <Route path="/testing" element={<ABTesting />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/terag" element={<TeragSystem />} />
                    </Routes>
                  </Suspense>
                </Layout>
                <Toaster />
              </div>
            </Router>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
  );
}

export default App;