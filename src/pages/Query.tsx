import React from 'react';
import { motion } from 'framer-motion';

export default function Query() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-8"
    >
      <h1 className="text-3xl font-bold bg-terag-pulse bg-clip-text text-transparent mb-8">
        Query Interface
      </h1>
      <p className="text-terag-text-secondary">Query interface functionality coming soon...</p>
    </motion.div>
  );
}