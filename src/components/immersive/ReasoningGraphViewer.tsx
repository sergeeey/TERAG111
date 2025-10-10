import { useState } from 'react';
import { X, Maximize2 } from 'lucide-react';
import { NeuroSpace } from './NeuroSpace';
import type { ReasoningGraph } from '../../services/terag-api';

interface ReasoningGraphViewerProps {
  isOpen: boolean;
  onClose: () => void;
  graph: ReasoningGraph;
  isReasoning: boolean;
  ieiScore: number;
}

export function ReasoningGraphViewer({
  isOpen,
  onClose,
  graph,
  isReasoning,
  ieiScore,
}: ReasoningGraphViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!isOpen) return null;

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div
      className={`fixed z-50 bg-[#0A0E1A]/98 backdrop-blur-xl border border-[#00FFE0]/20 shadow-2xl transition-all duration-300 ${
        isFullscreen
          ? 'inset-0'
          : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] h-[80vh] rounded-2xl'
      }`}
    >
      <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-[#10131A] to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-[#00FFE0] animate-pulse" />
            <h2 className="text-xl font-bold text-white">Reasoning Graph</h2>
            {isReasoning && (
              <span className="px-3 py-1 text-xs font-semibold text-[#00FFE0] bg-[#00FFE0]/10 rounded-full border border-[#00FFE0]/30">
                PROCESSING
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleFullscreen}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              <Maximize2 className="w-5 h-5 text-white" />
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              title="Close"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      <div className="w-full h-full">
        <NeuroSpace graph={graph} isReasoning={isReasoning} ieiScore={ieiScore} />
      </div>

      <div className="absolute bottom-0 left-0 right-0 z-10 p-6 bg-gradient-to-t from-[#10131A] to-transparent">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {graph.nodes.map((node) => (
              <div
                key={node.id}
                className="p-3 rounded-lg bg-[#10131A]/80 backdrop-blur-sm border border-[#00FFE0]/20"
              >
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      node.type === 'controller' ? 'bg-[#FF00FF]' : 'bg-[#00FFE0]'
                    } ${isReasoning ? 'animate-pulse' : ''}`}
                  />
                  <span className="text-sm font-semibold text-white">{node.label}</span>
                </div>
                <span className="text-xs text-white/50 capitalize">{node.type}</span>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-[#00FFE0]/10 to-[#FF00FF]/10 border border-[#00FFE0]/20">
            <p className="text-sm text-white/80 leading-relaxed">
              <span className="font-semibold text-[#00FFE0]">Agent Flow:</span>{' '}
              {graph.nodes.map((n) => n.label).join(' → ')}
            </p>
            <p className="text-xs text-white/50 mt-2">
              {graph.edges.length} connections • IEI Score: {ieiScore.toFixed(3)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
