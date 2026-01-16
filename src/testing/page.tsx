'use client';

import { Layout } from '@/components/layout/layout';
import { motion } from 'framer-motion';

export default function TestingPage() {
  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <h1 className="text-3xl font-bold gradient-text mb-8">A/B Testing</h1>
        <p className="text-muted-foreground">A/B testing dashboard coming soon...</p>
      </motion.div>
    </Layout>
  );
}