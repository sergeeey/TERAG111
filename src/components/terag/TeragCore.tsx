import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Cpu, Network, Zap, Activity, Shield } from 'lucide-react';

interface TeragState {
  mode: 'idle' | 'processing' | 'learning' | 'evolving';
  cognitiveLoad: number;
  neuralActivity: number;
  systemHealth: number;
  activeConnections: number;
}

export function TeragCore() {
  const [teragState, setTeragState] = useState<TeragState>({
    mode: 'idle',
    cognitiveLoad: 0,
    neuralActivity: 0,
    systemHealth: 100,
    activeConnections: 0
  });

  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setTeragState(prev => ({
        ...prev,
        cognitiveLoad: Math.random() * 100,
        neuralActivity: Math.random() * 100,
        systemHealth: 95 + Math.random() * 5,
        activeConnections: Math.floor(Math.random() * 50) + 10
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleActivation = () => {
    setIsActive(!isActive);
    setTeragState(prev => ({
      ...prev,
      mode: isActive ? 'idle' : 'processing'
    }));
  };

  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'processing': return 'text-blue-400';
      case 'learning': return 'text-purple-400';
      case 'evolving': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <motion.div
            className="relative"
            animate={{ rotate: isActive ? 360 : 0 }}
            transition={{ duration: 2, repeat: isActive ? Infinity : 0, ease: "linear" }}
          >
            <Brain className="w-8 h-8 text-terag-accent" />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-terag-accent/30"
              animate={{ scale: isActive ? [1, 1.2, 1] : 1 }}
              transition={{ duration: 1.5, repeat: isActive ? Infinity : 0 }}
            />
          </motion.div>
          <div>
            <h2 className="text-2xl font-bold font-display">TERAG Core</h2>
            <p className={`text-sm ${getModeColor(teragState.mode)}`}>
              Status: {teragState.mode.toUpperCase()}
            </p>
          </div>
        </div>
        
        <motion.button
          onClick={handleActivation}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            isActive 
              ? 'bg-red-500 hover:bg-red-600 text-white' 
              : 'bg-terag-accent hover:bg-terag-accent/80 text-black'
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isActive ? 'Деактивировать' : 'Активировать'}
        </motion.button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          className="bg-black/20 backdrop-blur-xl border border-terag-accent/10 rounded-lg p-4"
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center space-x-3 mb-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span className="text-sm font-medium">Когнитивная нагрузка</span>
          </div>
          <div className="text-2xl font-bold">{teragState.cognitiveLoad.toFixed(1)}%</div>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
            <motion.div
              className="bg-blue-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${teragState.cognitiveLoad}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        <motion.div
          className="bg-black/20 backdrop-blur-xl border border-terag-accent/10 rounded-lg p-4"
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center space-x-3 mb-2">
            <Activity className="w-5 h-5 text-purple-400" />
            <span className="text-sm font-medium">Нейронная активность</span>
          </div>
          <div className="text-2xl font-bold">{teragState.neuralActivity.toFixed(1)}%</div>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
            <motion.div
              className="bg-purple-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${teragState.neuralActivity}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        <motion.div
          className="bg-black/20 backdrop-blur-xl border border-terag-accent/10 rounded-lg p-4"
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center space-x-3 mb-2">
            <Shield className="w-5 h-5 text-green-400" />
            <span className="text-sm font-medium">Здоровье системы</span>
          </div>
          <div className="text-2xl font-bold">{teragState.systemHealth.toFixed(1)}%</div>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
            <motion.div
              className="bg-green-400 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${teragState.systemHealth}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>

        <motion.div
          className="bg-black/20 backdrop-blur-xl border border-terag-accent/10 rounded-lg p-4"
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center space-x-3 mb-2">
            <Network className="w-5 h-5 text-terag-accent" />
            <span className="text-sm font-medium">Активные связи</span>
          </div>
          <div className="text-2xl font-bold">{teragState.activeConnections}</div>
          <div className="flex items-center mt-2">
            <motion.div
              className="w-2 h-2 bg-terag-accent rounded-full mr-2"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <span className="text-xs text-terag-text-muted">В реальном времени</span>
          </div>
        </motion.div>
      </div>

      <AnimatePresence>
        {isActive && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-black/30 backdrop-blur-xl border border-terag-accent/20 rounded-lg p-6"
          >
            <div className="flex items-center space-x-3 mb-4">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h3 className="text-lg font-semibold">Активный режим TERAG</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-sm text-terag-text-muted mb-1">Обработано запросов</div>
                <div className="text-xl font-bold text-terag-accent">1,247</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-terag-text-muted mb-1">Изучено документов</div>
                <div className="text-xl font-bold text-purple-400">8,932</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-terag-text-muted mb-1">Создано связей</div>
                <div className="text-xl font-bold text-green-400">15,678</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}