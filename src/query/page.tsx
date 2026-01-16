'use client';

import { Layout } from '@/components/layout/layout';
import { motion } from 'framer-motion';

export default function QueryPage() {
  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <h1 className="text-3xl font-bold gradient-text mb-8">Query Interface</h1>
        <p className="text-muted-foreground">Query interface functionality coming soon...</p>
      </motion.div>
    </Layout>
  );
}