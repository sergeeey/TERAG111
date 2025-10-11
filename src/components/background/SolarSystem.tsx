import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, Sphere } from '@react-three/drei';
import * as THREE from 'three';

interface PlanetProps {
  position: [number, number, number];
  size: number;
  color: string;
  orbitSpeed: number;
  orbitRadius: number;
  rotationSpeed: number;
  hasRing?: boolean;
  ringColor?: string;
  emissive?: string;
  emissiveIntensity?: number;
}

function Planet({
  position,
  size,
  color,
  orbitSpeed,
  orbitRadius,
  rotationSpeed,
  hasRing,
  ringColor,
  emissive,
  emissiveIntensity = 0
}: PlanetProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      const time = clock.getElapsedTime();
      groupRef.current.position.x = Math.cos(time * orbitSpeed) * orbitRadius;
      groupRef.current.position.z = Math.sin(time * orbitSpeed) * orbitRadius;
    }
    if (meshRef.current) {
      meshRef.current.rotation.y += rotationSpeed;
    }
  });

  return (
    <group ref={groupRef} position={position}>
      <Sphere ref={meshRef} args={[size, 32, 32]}>
        <meshStandardMaterial
          color={color}
          emissive={emissive || color}
          emissiveIntensity={emissiveIntensity}
          roughness={0.7}
          metalness={0.3}
        />
      </Sphere>

      {hasRing && (
        <mesh rotation={[Math.PI / 2.5, 0, 0]}>
          <ringGeometry args={[size * 1.5, size * 2.2, 64]} />
          <meshStandardMaterial
            color={ringColor}
            side={THREE.DoubleSide}
            transparent
            opacity={0.6}
            roughness={0.8}
          />
        </mesh>
      )}

      {/* Orbit path */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[orbitRadius - 0.02, orbitRadius + 0.02, 128]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.1} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

function Sun() {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
    }
    if (glowRef.current) {
      glowRef.current.rotation.y -= 0.0005;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Sun core */}
      <Sphere ref={meshRef} args={[2.5, 64, 64]}>
        <meshStandardMaterial
          color="#FDB813"
          emissive="#FDB813"
          emissiveIntensity={2}
          roughness={0.5}
        />
      </Sphere>

      {/* Glow layer 1 */}
      <Sphere args={[3.2, 32, 32]}>
        <meshBasicMaterial
          color="#FFA500"
          transparent
          opacity={0.3}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Glow layer 2 */}
      <Sphere ref={glowRef} args={[4, 32, 32]}>
        <meshBasicMaterial
          color="#FF6B00"
          transparent
          opacity={0.15}
          side={THREE.BackSide}
        />
      </Sphere>

      {/* Point light from sun */}
      <pointLight intensity={3} distance={100} decay={2} color="#FDB813" />
    </group>
  );
}

function AsteroidBelt() {
  const asteroids = useMemo(() => {
    const temp = [];
    for (let i = 0; i < 800; i++) {
      const angle = (i / 800) * Math.PI * 2;
      const radius = 18 + Math.random() * 3;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = (Math.random() - 0.5) * 0.8;
      const size = 0.02 + Math.random() * 0.08;
      const speed = 0.0001 + Math.random() * 0.0002;
      temp.push({ x, y, z, size, speed, angle, radius });
    }
    return temp;
  }, []);

  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <group ref={groupRef}>
      {asteroids.map((asteroid, i) => (
        <mesh key={i} position={[asteroid.x, asteroid.y, asteroid.z]}>
          <sphereGeometry args={[asteroid.size, 6, 6]} />
          <meshStandardMaterial color="#8B7355" roughness={1} metalness={0.1} />
        </mesh>
      ))}
    </group>
  );
}

function SolarSystemScene() {
  return (
    <>
      {/* Ambient light */}
      <ambientLight intensity={0.15} />

      {/* Background stars */}
      <Stars
        radius={300}
        depth={60}
        count={8000}
        factor={6}
        saturation={0}
        fade
        speed={0.5}
      />

      {/* Cosmic nebula effect */}
      <mesh position={[0, 0, -50]}>
        <planeGeometry args={[200, 200]} />
        <meshBasicMaterial
          color="#1a0033"
          transparent
          opacity={0.3}
        />
      </mesh>

      {/* Sun */}
      <Sun />

      {/* Mercury */}
      <Planet
        position={[0, 0, 0]}
        size={0.4}
        color="#8C7853"
        orbitSpeed={0.8}
        orbitRadius={5}
        rotationSpeed={0.005}
      />

      {/* Venus */}
      <Planet
        position={[0, 0, 0]}
        size={0.9}
        color="#FFC649"
        orbitSpeed={0.6}
        orbitRadius={7}
        rotationSpeed={0.003}
        emissive="#CC8800"
        emissiveIntensity={0.2}
      />

      {/* Earth */}
      <Planet
        position={[0, 0, 0]}
        size={1}
        color="#2E8B57"
        orbitSpeed={0.5}
        orbitRadius={10}
        rotationSpeed={0.01}
        emissive="#1E5F3F"
        emissiveIntensity={0.1}
      />

      {/* Moon (orbiting Earth) */}
      <Planet
        position={[10, 0, 0]}
        size={0.27}
        color="#C0C0C0"
        orbitSpeed={2}
        orbitRadius={1.5}
        rotationSpeed={0.005}
      />

      {/* Mars */}
      <Planet
        position={[0, 0, 0]}
        size={0.53}
        color="#CD5C5C"
        orbitSpeed={0.4}
        orbitRadius={13}
        rotationSpeed={0.008}
        emissive="#8B0000"
        emissiveIntensity={0.15}
      />

      {/* Asteroid Belt */}
      <AsteroidBelt />

      {/* Jupiter */}
      <Planet
        position={[0, 0, 0]}
        size={2.2}
        color="#C88B3A"
        orbitSpeed={0.2}
        orbitRadius={22}
        rotationSpeed={0.015}
        emissive="#8B6914"
        emissiveIntensity={0.1}
      />

      {/* Saturn */}
      <Planet
        position={[0, 0, 0]}
        size={1.9}
        color="#FAD5A5"
        orbitSpeed={0.15}
        orbitRadius={28}
        rotationSpeed={0.012}
        hasRing
        ringColor="#D4A574"
        emissive="#C19A6B"
        emissiveIntensity={0.1}
      />

      {/* Uranus */}
      <Planet
        position={[0, 0, 0]}
        size={1.4}
        color="#4FD0E7"
        orbitSpeed={0.1}
        orbitRadius={34}
        rotationSpeed={0.007}
        hasRing
        ringColor="#7FDBFF"
        emissive="#0080FF"
        emissiveIntensity={0.2}
      />

      {/* Neptune */}
      <Planet
        position={[0, 0, 0]}
        size={1.35}
        color="#4169E1"
        orbitSpeed={0.08}
        orbitRadius={39}
        rotationSpeed={0.006}
        emissive="#1E3A8A"
        emissiveIntensity={0.25}
      />
    </>
  );
}

export function SolarSystem() {
  return (
    <div className="fixed inset-0 -z-10">
      <Canvas
        camera={{ position: [0, 35, 45], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
        style={{ background: 'transparent' }}
      >
        <SolarSystemScene />
      </Canvas>

      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0E1A]/60 to-[#0A0E1A] pointer-events-none" />
    </div>
  );
}
