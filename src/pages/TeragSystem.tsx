import React from 'react';
import { motion } from 'framer-motion';
import { TeragCore } from '../components/terag/TeragCore';
import { NeuralNetwork } from '../components/terag/NeuralNetwork';
import { CognitiveStates } from '../components/terag/CognitiveStates';
import { TeragInterface } from '../components/terag/TeragInterface';

export default function TeragSystem() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold font-display bg-terag-pulse bg-clip-text text-transparent mb-4">
          TERAG Cognitive System
        </h1>
        <p className="text-terag-text-secondary text-lg max-w-2xl mx-auto">
          Интеллектуальная когнитивная операционная система с нейронными сетями, 
          обработкой естественного языка и адаптивным обучением
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <TeragCore />
          <TeragInterface />
        </div>
        
        <div className="space-y-8">
          <NeuralNetwork />
          <CognitiveStates />
        </div>
      </div>
    </motion.div>
  );
}