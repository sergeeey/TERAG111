'use client';

import { motion } from 'framer-motion';
import { Network, Sparkles, TrendingUp, Zap } from 'lucide-react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere, Text } from '@react-three/drei';
import { Suspense } from 'react';

function Logo3D() {
  return (
    <group>
      <Sphere args={[1, 32, 32]} position={[0, 0, 0]}>
        <meshPhongMaterial color="#3B82F6" wireframe />
      </Sphere>
      <Sphere args={[0.5, 16, 16]} position={[2, 1, 0]}>
        <meshPhongMaterial color="#8B5CF6" />
      </Sphere>
      <Sphere args={[0.3, 8, 8]} position={[-1, -0.5, 1]}>
        <meshPhongMaterial color="#10B981" />
      </Sphere>
    </group>
  );
}

const stats = [
  { label: 'Documents Processed', value: '12,543', icon: TrendingUp, color: 'text-accent' },
  { label: 'Active Queries', value: '1,247', icon: Zap, color: 'text-primary' },
  { label: 'Knowledge Nodes', value: '8,932', icon: Network, color: 'text-secondary' },
  { label: 'AI Accuracy', value: '94.2%', icon: Sparkles, color: 'text-warning' },
];

export function HeroSection() {
  return (
    <div className="glass-card relative overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left side - Content */}
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl lg:text-6xl font-bold leading-tight">
              <span className="gradient-text">TERAG MVP</span>
              <br />
              <span className="text-2xl lg:text-4xl font-normal text-muted-foreground">
                Intelligent RAG System
              </span>
            </h1>
          </motion.div>

          <motion.p
            className="text-lg text-muted-foreground leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            Tree-Enhanced Retrieval-Augmented Generation with advanced knowledge 
            graph visualization, real-time A/B testing, and comprehensive analytics.
          </motion.p>

          <motion.div
            className="grid grid-cols-2 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                className="glass p-4 rounded-lg"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", bounce: 0.4 }}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <stat.icon className={`w-4 h-4 ${stat.color}`} />
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                </div>
                <div className="text-2xl font-bold">{stat.value}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Right side - 3D Visual */}
        <motion.div
          className="h-96 relative"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.6 }}
        >
          <div className="w-full h-full rounded-xl overflow-hidden">
            <Suspense fallback={
              <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl animate-pulse" />
            }>
              <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} />
                <directionalLight position={[-10, -10, -5]} intensity={0.5} />
                <Logo3D />
                <OrbitControls 
                  enablePan={false} 
                  enableZoom={false} 
                  autoRotate 
                  autoRotateSpeed={2}
                />
              </Canvas>
            </Suspense>
          </div>
          
          {/* Floating elements */}
          <motion.div
            className="absolute -top-4 -right-4 w-8 h-8 bg-primary rounded-full animate-float"
            animate={{
              y: [0, -20, 0],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute -bottom-4 -left-4 w-6 h-6 bg-secondary rounded-full animate-float"
            animate={{
              y: [0, -15, 0],
              rotate: [360, 180, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1,
            }}
          />
        </motion.div>
      </div>
    </div>
  );
}