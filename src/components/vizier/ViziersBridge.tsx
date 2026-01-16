/**
 * Vizier's Bridge — 3D визуализация ReasonGraph
 * React Three Fiber компонент для интерактивного отображения reasoning процесса
 */
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import type { OrbitControls as OrbitControlsType } from 'three-stdlib';
import { useReasonGraph } from './hooks/useReasonGraph';
import type { ReasonGraph, ReasonGraphNode, ReasonGraphEdge } from './types/reasonGraph';

interface ViziersBridgeProps {
  query: string;
  show?: string[];
  threadId?: string;
  autoStart?: boolean;
}

// Компонент узла
function Node3D({ node, isActive }: { node: ReasonGraphNode; isActive: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  // Анимация пульсации для активного узла
  useFrame((state) => {
    if (meshRef.current && isActive) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  // Цвет узла в зависимости от типа и статуса
  const getNodeColor = () => {
    if (node.status === 'failed') return '#ff0000';
    if (node.status === 'active') return '#00ff00';
    if (node.status === 'completed') {
      switch (node.type) {
        case 'guardrail': return '#ffaa00';
        case 'planner': return '#00aaff';
        case 'solver': return '#aa00ff';
        case 'verifier': return '#ff00aa';
        case 'ethical': return '#00ffaa';
        default: return '#888888';
      }
    }
    return '#666666';
  };

  return (
    <group position={[node.position.x, node.position.y, node.position.z]}>
      <Sphere ref={meshRef} args={[0.3, 16, 16]}>
        <meshStandardMaterial
          color={getNodeColor()}
          emissive={isActive ? getNodeColor() : '#000000'}
          emissiveIntensity={isActive ? 0.5 : 0}
        />
      </Sphere>
      <Text
        position={[0, 0.5, 0]}
        fontSize={0.2}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {node.label}
      </Text>
      {node.confidence !== undefined && (
        <Text
          position={[0, -0.5, 0]}
          fontSize={0.15}
          color="#aaaaaa"
          anchorX="center"
          anchorY="middle"
        >
          {Math.round(node.confidence * 100)}%
        </Text>
      )}
    </group>
  );
}

// Компонент связи
function Edge3D({ edge, nodes }: { edge: ReasonGraphEdge; nodes: ReasonGraphNode[] }) {
  const sourceNode = nodes.find(n => n.id === edge.source);
  const targetNode = nodes.find(n => n.id === edge.target);

  if (!sourceNode || !targetNode) return null;

  const start = new THREE.Vector3(
    sourceNode.position.x,
    sourceNode.position.y,
    sourceNode.position.z
  );
  const end = new THREE.Vector3(
    targetNode.position.x,
    targetNode.position.y,
    targetNode.position.z
  );

  // Цвет связи в зависимости от типа
  const getEdgeColor = () => {
    switch (edge.type) {
      case 'guardrail_check': return '#ffaa00';
      case 'reasoning_flow': return '#00aaff';
      case 'reject': return '#ff0000';
      default: return '#888888';
    }
  };

  return (
    <Line
      points={[start, end]}
      color={getEdgeColor()}
      lineWidth={2}
      opacity={0.6}
    />
  );
}

// Основной компонент визуализации
function ReasonGraphScene({ reasonGraph }: { reasonGraph: ReasonGraph }) {
  const controlsRef = useRef<OrbitControlsType | null>(null);

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <pointLight position={[-10, -10, -10]} color="#00aaff" />

      {/* Рендерим узлы */}
      {reasonGraph.nodes.map((node) => (
        <Node3D
          key={node.id}
          node={node}
          isActive={node.status === 'active'}
        />
      ))}

      {/* Рендерим связи */}
      {reasonGraph.edges.map((edge) => (
        <Edge3D
          key={edge.id}
          edge={edge}
          nodes={reasonGraph.nodes}
        />
      ))}

      <OrbitControls
        ref={controlsRef}
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
      />
    </>
  );
}

// Панель метрик
function MetricsPanel({ reasonGraph }: { reasonGraph: ReasonGraph }) {
  const { metadata } = reasonGraph;

  return (
    <div className="absolute top-4 right-4 bg-black/80 text-white p-4 rounded-lg min-w-[300px]">
      <h3 className="text-lg font-bold mb-2">Reasoning Metrics</h3>
      <div className="space-y-2 text-sm">
        <div>
          <span className="text-gray-400">Confidence:</span>{' '}
          <span className="font-bold">{Math.round(metadata.confidence * 100)}%</span>
        </div>
        <div>
          <span className="text-gray-400">Ethical Score:</span>{' '}
          <span className="font-bold">{Math.round(metadata.ethical_score * 100)}%</span>
        </div>
        <div>
          <span className="text-gray-400">SRI:</span>{' '}
          <span className="font-bold">{Math.round(metadata.secure_reasoning_index * 100)}%</span>
        </div>
        <div>
          <span className="text-gray-400">Alignment:</span>{' '}
          <span className={`font-bold ${
            metadata.alignment_status === 'ethical' ? 'text-green-400' :
            metadata.alignment_status === 'questionable' ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {metadata.alignment_status}
          </span>
        </div>
      </div>
    </div>
  );
}

// Главный компонент
export function ViziersBridge({ query, show, threadId, autoStart = true }: ViziersBridgeProps) {
  const { reasonGraph, isStreaming, error, start, stop, reconnect } = useReasonGraph({
    query,
    show,
    threadId,
    autoStart
  });

  const [showControls, setShowControls] = useState(true);

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 text-white">
        <div className="text-center">
          <p className="text-red-400 mb-4">Error: {error}</p>
          <button
            onClick={reconnect}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
          >
            Reconnect
          </button>
        </div>
      </div>
    );
  }

  if (!reasonGraph) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900 text-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Connecting to reasoning stream...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full bg-gray-900">
      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ReasonGraphScene reasonGraph={reasonGraph} />
      </Canvas>

      {/* Панель метрик */}
      <MetricsPanel reasonGraph={reasonGraph} />

      {/* Панель управления */}
      {showControls && (
        <div className="absolute bottom-4 left-4 bg-black/80 text-white p-4 rounded-lg">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isStreaming ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-sm">{isStreaming ? 'Streaming...' : 'Completed'}</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={isStreaming ? stop : start}
                className="px-3 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700"
              >
                {isStreaming ? 'Stop' : 'Start'}
              </button>
              <button
                onClick={() => setShowControls(false)}
                className="px-3 py-1 bg-gray-600 rounded text-sm hover:bg-gray-700"
              >
                Hide
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Кнопка показа контролов */}
      {!showControls && (
        <button
          onClick={() => setShowControls(true)}
          className="absolute bottom-4 left-4 px-3 py-1 bg-black/80 text-white rounded text-sm hover:bg-black"
        >
          Show Controls
        </button>
      )}
    </div>
  );
}

