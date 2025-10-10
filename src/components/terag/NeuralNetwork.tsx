import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

interface NeuralNodeProps {
  position: [number, number, number];
  active: boolean;
}

function NeuralNode({ position, active }: NeuralNodeProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.5;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
      
      if (active) {
        meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.2);
      }
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.1, 16, 16]} />
      <meshStandardMaterial 
        color={active ? '#00E7C0' : '#7C3AED'} 
        emissive={active ? '#00E7C0' : '#7C3AED'}
        emissiveIntensity={active ? 0.5 : 0.2}
      />
    </mesh>
  );
}

function NeuralConnections() {
  const pointsRef = useRef<THREE.Points>(null);
  const [positions, setPositions] = useState<Float32Array>();

  useEffect(() => {
    const points = new Float32Array(300);
    for (let i = 0; i < 100; i++) {
      points[i * 3] = (Math.random() - 0.5) * 10;
      points[i * 3 + 1] = (Math.random() - 0.5) * 10;
      points[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    setPositions(points);
  }, []);

  useFrame((state) => {
    if (pointsRef.current && positions) {
      const time = state.clock.elapsedTime;
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += Math.sin(time + i) * 0.01;
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  if (!positions) return null;

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#8B5CF6"
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
      />
    </Points>
  );
}

export function NeuralNetwork() {
  const [activeNodes, setActiveNodes] = useState<boolean[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveNodes(prev => 
        Array.from({ length: 20 }, () => Math.random() > 0.7)
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const nodePositions: [number, number, number][] = Array.from({ length: 20 }, () => [
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 8,
    (Math.random() - 0.5) * 8,
  ]);

  return (
    <div className="h-96 w-full bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl overflow-hidden">
      <Canvas camera={{ position: [0, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        <pointLight position={[-10, -10, -10]} intensity={0.3} color="#7C3AED" />
        
        <NeuralConnections />
        
        {nodePositions.map((position, index) => (
          <NeuralNode
            key={index}
            position={position}
            active={activeNodes[index] || false}
          />
        ))}
        
        <mesh rotation={[0, 0, 0]}>
          <torusGeometry args={[3, 0.1, 16, 100]} />
          <meshStandardMaterial color="#00E7C0" transparent opacity={0.3} />
        </mesh>
      </Canvas>
      
      <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
        <div className="text-xs text-terag-text-muted mb-1">Нейронная сеть</div>
        <div className="text-sm font-semibold">
          Активных узлов: {activeNodes.filter(Boolean).length}/20
        </div>
      </div>
    </div>
  );
}