import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Lightbulb, Zap, Target, Cpu, Network } from 'lucide-react';

interface CognitiveState {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  color: string;
  intensity: number;
  active: boolean;
}

const cognitiveStates: CognitiveState[] = [
  {
    id: 'learning',
    name: 'Обучение',
    description: 'Анализ и усвоение новой информации',
    icon: Brain,
    color: 'from-blue-500 to-blue-700',
    intensity: 0,
    active: false
  },
  {
    id: 'reasoning',
    name: 'Рассуждение',
    description: 'Логический анализ и выводы',
    icon: Lightbulb,
    color: 'from-yellow-500 to-orange-600',
    intensity: 0,
    active: false
  },
  {
    id: 'processing',
    name: 'Обработка',
    description: 'Активная обработка запросов',
    icon: Cpu,
    color: 'from-green-500 to-emerald-600',
    intensity: 0,
    active: false
  },
  {
    id: 'connecting',
    name: 'Связывание',
    description: 'Создание новых связей в графе знаний',
    icon: Network,
    color: 'from-purple-500 to-violet-600',
    intensity: 0,
    active: false
  },
  {
    id: 'optimizing',
    name: 'Оптимизация',
    description: 'Улучшение производительности системы',
    icon: Target,
    color: 'from-red-500 to-pink-600',
    intensity: 0,
    active: false
  },
  {
    id: 'evolving',
    name: 'Эволюция',
    description: 'Адаптация и самосовершенствование',
    icon: Zap,
    color: 'from-indigo-500 to-purple-600',
    intensity: 0,
    active: false
  }
];

export function CognitiveStates() {
  const [states, setStates] = useState<CognitiveState[]>(cognitiveStates);
  const [globalIntensity, setGlobalIntensity] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStates(prevStates => 
        prevStates.map(state => ({
          ...state,
          intensity: Math.random() * 100,
          active: Math.random() > 0.6
        }))
      );
      
      setGlobalIntensity(Math.random() * 100);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const activeStatesCount = states.filter(state => state.active).length;
  const averageIntensity = states.reduce((sum, state) => sum + state.intensity, 0) / states.length;

  return (
    <div className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold font-display">Когнитивные состояния</h2>
          <p className="text-terag-text-muted">Мониторинг активности ментальных процессов</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-terag-text-muted">Активных состояний</div>
          <div className="text-2xl font-bold text-terag-accent">{activeStatesCount}/6</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {states.map((state) => (
          <motion.div
            key={state.id}
            className={`relative overflow-hidden rounded-lg p-4 bg-gradient-to-br ${state.color} ${
              state.active ? 'opacity-100' : 'opacity-50'
            }`}
            animate={{
              scale: state.active ? 1.02 : 1,
              boxShadow: state.active 
                ? '0 10px 30px rgba(0, 231, 192, 0.3)' 
                : '0 4px 15px rgba(0, 0, 0, 0.2)'
            }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center space-x-3 mb-3">
              <motion.div
                animate={{ rotate: state.active ? 360 : 0 }}
                transition={{ duration: 2, repeat: state.active ? Infinity : 0, ease: "linear" }}
              >
                <state.icon className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h3 className="font-semibold text-white">{state.name}</h3>
                <p className="text-xs text-white/80">{state.description}</p>
              </div>
            </div>
            
            <div className="mb-2">
              <div className="flex justify-between text-xs text-white/80 mb-1">
                <span>Интенсивность</span>
                <span>{state.intensity.toFixed(0)}%</span>
              </div>
              <div className="w-full bg-white/20 rounded-full h-2">
                <motion.div
                  className="bg-white h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${state.intensity}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            <AnimatePresence>
              {state.active && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="absolute top-2 right-2"
                >
                  <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>

      <div className="bg-black/30 backdrop-blur-sm rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Общая когнитивная активность</h3>
          <span className="text-sm text-terag-text-muted">
            {averageIntensity.toFixed(1)}% средняя интенсивность
          </span>
        </div>
        
        <div className="relative h-4 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-terag-accent via-purple-500 to-blue-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${averageIntensity}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
          <motion.div
            className="absolute inset-0 bg-white/30 rounded-full"
            animate={{ x: [`-100%`, `${averageIntensity}%`] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            style={{ width: '20%' }}
          />
        </div>
      </div>
    </div>
  );
}