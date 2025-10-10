import { useState, useEffect } from 'react';
import { Eye } from 'lucide-react';
import { WelcomeScreen } from '../components/immersive/WelcomeScreen';
import { NeuroSpace, type VoiceState } from '../components/immersive/NeuroSpace';
import { CognitiveConsole } from '../components/immersive/CognitiveConsole';
import { MetricsHUD } from '../components/immersive/MetricsHUD';
import { ReasoningGraphViewer } from '../components/immersive/ReasoningGraphViewer';
import { teragAPI } from '../services/terag-api';
import type { ReasoningGraph, MetricsData } from '../services/terag-api';

export default function TeragImmersive() {
  const [showWelcome, setShowWelcome] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState('');
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [metrics, setMetrics] = useState<MetricsData>({
    iei: 0.85,
    coherence: 0.88,
    faithfulness: 0.87,
  });
  const [graph, setGraph] = useState<ReasoningGraph>({
    nodes: [],
    edges: [],
  });
  const [showGraph, setShowGraph] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    checkConnection();
    loadGraph();

    const stopMetricsStream = teragAPI.createMetricsStream((newMetrics) => {
      setMetrics(newMetrics);
    }, 5000);

    return () => {
      stopMetricsStream();
    };
  }, []);

  const checkConnection = async () => {
    try {
      const health = await teragAPI.checkHealth();
      setIsConnected(health.status === 'ok');
    } catch {
      setIsConnected(false);
    }
  };

  const loadGraph = async () => {
    try {
      const graphData = await teragAPI.getReasoningGraph();
      setGraph(graphData);
    } catch (error) {
      console.error('Failed to load graph:', error);
    }
  };

  const handleQuery = async (query: string) => {
    setIsProcessing(true);
    setResponse('');

    try {
      const result = await teragAPI.reasoningQuery(query);
      setResponse(result.response);

      if (result.iei) {
        setMetrics((prev) => ({
          ...prev,
          iei: result.iei,
          coherence: result.coherence || prev.coherence,
          faithfulness: result.faithfulness || prev.faithfulness,
        }));
      }

      await loadGraph();
    } catch (error) {
      console.error('Query failed:', error);
      setResponse('Failed to process query. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVoiceQuery = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setResponse('');

    try {
      const result = await teragAPI.voiceQuery(audioBlob);
      setResponse(result.response);

      if (result.iei) {
        setMetrics((prev) => ({
          ...prev,
          iei: result.iei,
          coherence: result.coherence || prev.coherence,
          faithfulness: result.faithfulness || prev.faithfulness,
        }));
      }

      await loadGraph();
    } catch (error) {
      console.error('Voice query failed:', error);
      setResponse('Voice processing is currently unavailable.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (showWelcome) {
    return <WelcomeScreen onStart={() => setShowWelcome(false)} />;
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-[#0A0E1A] via-[#10131A] to-[#1A1E2E] overflow-hidden">
      <div className="absolute inset-0">
        <NeuroSpace
          graph={graph}
          isReasoning={isProcessing}
          ieiScore={metrics.iei}
          voiceState={voiceState}
        />
      </div>

      <MetricsHUD metrics={metrics} isConnected={isConnected} />

      <div className="fixed top-6 left-6 z-40">
        <button
          onClick={() => setShowGraph(true)}
          disabled={isProcessing}
          className="group flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-[#10131A]/95 to-[#1A1E2E]/95 backdrop-blur-xl rounded-xl border border-[#00FFE0]/20 hover:border-[#00FFE0]/40 transition-all duration-300 shadow-lg hover:shadow-[#00FFE0]/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Eye className="w-5 h-5 text-[#00FFE0]" />
          <span className="text-white font-semibold">View Reasoning</span>
          {isProcessing && (
            <div className="w-2 h-2 rounded-full bg-[#00FFE0] animate-pulse" />
          )}
        </button>

        <div className="mt-4 px-6 py-3 bg-gradient-to-r from-[#10131A]/95 to-[#1A1E2E]/95 backdrop-blur-xl rounded-xl border border-[#00FFE0]/20">
          <div className="text-xs text-white/50 mb-1">Active Mode</div>
          <div className="text-sm font-semibold text-white">
            {voiceState === 'listening' ? 'Listening' : voiceState === 'processing' ? 'Thinking' : isProcessing ? 'Reasoning' : 'Ready'}
          </div>
        </div>
      </div>

      <CognitiveConsole
        onQuery={handleQuery}
        onVoiceQuery={handleVoiceQuery}
        isProcessing={isProcessing}
        response={response}
        voiceState={voiceState}
        onVoiceStateChange={setVoiceState}
      />

      <ReasoningGraphViewer
        isOpen={showGraph}
        onClose={() => setShowGraph(false)}
        graph={graph}
        isReasoning={isProcessing}
        ieiScore={metrics.iei}
        voiceState={voiceState}
      />
    </div>
  );
}
