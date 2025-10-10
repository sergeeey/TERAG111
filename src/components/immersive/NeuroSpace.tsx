import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Line } from '@react-three/drei';
import * as THREE from 'three';
import type { GraphNode, GraphEdge } from '../../services/terag-api';

export type VoiceState = 'idle' | 'listening' | 'processing';

interface NeuroSpaceProps {
  graph: { nodes: GraphNode[]; edges: GraphEdge[] };
  isReasoning: boolean;
  ieiScore: number;
  voiceState?: VoiceState;
}

function TeragCore({
  isReasoning,
  ieiScore,
  voiceState = 'idle',
}: {
  isReasoning: boolean;
  ieiScore: number;
  voiceState?: VoiceState;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.z += 0.001;

      if (isReasoning) {
        const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.1 + 1;
        meshRef.current.scale.setScalar(pulse);
      } else {
        meshRef.current.scale.setScalar(1);
      }
    }

    if (glowRef.current) {
      const glowPulse = Math.sin(state.clock.elapsedTime * 2) * 0.3 + 0.7;
      glowRef.current.scale.setScalar(1.2 + glowPulse * 0.2);
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = glowPulse * 0.3;
    }
  });

  const coreColor = useMemo(() => {
    if (voiceState === 'listening') return '#4A9EFF';
    if (voiceState === 'processing') return '#FFD700';
    if (ieiScore > 0.9) return '#00FFE0';
    if (ieiScore > 0.8) return '#00D4FF';
    if (ieiScore > 0.7) return '#0099FF';
    return '#FF6B6B';
  }, [ieiScore, voiceState]);

  const emissiveIntensity = useMemo(() => {
    if (voiceState === 'listening') return 0.7;
    if (voiceState === 'processing') return 0.9;
    return 0.5;
  }, [voiceState]);

  return (
    <group>
      <Sphere ref={meshRef} args={[1, 64, 64]}>
        <meshStandardMaterial
          color={coreColor}
          emissive={coreColor}
          emissiveIntensity={emissiveIntensity}
          metalness={0.8}
          roughness={0.2}
        />
      </Sphere>

      <Sphere ref={glowRef} args={[1.2, 32, 32]}>
        <meshBasicMaterial
          color={coreColor}
          transparent
          opacity={0.3}
          side={THREE.BackSide}
        />
      </Sphere>
    </group>
  );
}

function AgentNode({
  node,
  isActive,
  ieiScore,
  voiceState = 'idle',
}: {
  node: GraphNode;
  isActive: boolean;
  ieiScore: number;
  voiceState?: VoiceState;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && isActive) {
      const pulse = Math.sin(state.clock.elapsedTime * 4 + (node.x || 0)) * 0.05 + 1;
      meshRef.current.scale.setScalar(pulse);
    }
  });

  const position = useMemo<[number, number, number]>(() => [
    node.x || 0,
    node.y || 0,
    node.z || 0,
  ], [node]);

  const nodeColor = useMemo(() => {
    if (voiceState === 'listening') return '#4A9EFF';
    if (voiceState === 'processing') return '#FFD700';
    return node.type === 'controller' ? '#FF00FF' : '#00FFE0';
  }, [node.type, voiceState]);

  return (
    <group position={position}>
      <Sphere ref={meshRef} args={[0.3, 32, 32]}>
        <meshStandardMaterial
          color={nodeColor}
          emissive={nodeColor}
          emissiveIntensity={isActive ? 0.8 : 0.3}
          metalness={0.6}
          roughness={0.3}
        />
      </Sphere>

      <mesh position={[0, 0.6, 0]}>
        <planeGeometry args={[1.5, 0.3]} />
        <meshBasicMaterial color="#00FFE0" transparent opacity={0.8} />
      </mesh>
    </group>
  );
}

function ConnectionLine({
  start,
  end,
  isActive,
  weight = 0.8
}: {
  start: [number, number, number];
  end: [number, number, number];
  isActive: boolean;
  weight?: number;
}) {
  const lineRef = useRef<THREE.Line>(null);

  useFrame((state) => {
    if (lineRef.current && isActive) {
      const material = lineRef.current.material as THREE.LineBasicMaterial;
      material.opacity = 0.3 + Math.sin(state.clock.elapsedTime * 5) * 0.2;
    }
  });

  const points = useMemo(() => [
    new THREE.Vector3(...start),
    new THREE.Vector3(...end),
  ], [start, end]);

  const lineColor = weight > 0.85 ? '#00FFE0' : '#0099FF';

  return (
    <Line
      ref={lineRef}
      points={points}
      color={lineColor}
      lineWidth={2}
      transparent
      opacity={isActive ? 0.5 : 0.2}
    />
  );
}

function ParticleField() {
  const particlesRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const positions = new Float32Array(1000 * 3);
    for (let i = 0; i < 1000; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return positions;
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y += 0.0002;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.02}
        color="#00FFE0"
        transparent
        opacity={0.3}
        sizeAttenuation
      />
    </points>
  );
}

export function NeuroSpace({ graph, isReasoning, ieiScore, voiceState }: NeuroSpaceProps) {
  return (
    <div className="w-full h-full bg-[#0A0E1A]">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance'
        }}
      >
        <color attach="background" args={['#0A0E1A']} />

        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} color="#00FFE0" />
        <pointLight position={[-10, -10, -10]} intensity={0.3} color="#FF00FF" />

        <TeragCore isReasoning={isReasoning} ieiScore={ieiScore} voiceState={voiceState} />

        {graph.nodes.map((node) => (
          <AgentNode
            key={node.id}
            node={node}
            isActive={isReasoning}
            ieiScore={ieiScore}
            voiceState={voiceState}
          />
        ))}

        {graph.edges.map((edge, index) => {
          const sourceNode = graph.nodes.find((n) => n.id === edge.source);
          const targetNode = graph.nodes.find((n) => n.id === edge.target);

          if (!sourceNode || !targetNode) return null;

          return (
            <ConnectionLine
              key={`${edge.source}-${edge.target}-${index}`}
              start={[sourceNode.x || 0, sourceNode.y || 0, sourceNode.z || 0]}
              end={[targetNode.x || 0, targetNode.y || 0, targetNode.z || 0]}
              isActive={isReasoning}
              weight={edge.weight}
            />
          );
        })}

        <ParticleField />

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          minDistance={3}
          maxDistance={15}
          autoRotate={!isReasoning}
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  );
}
