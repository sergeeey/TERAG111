'use client';

import { Suspense } from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from '@/components/dashboard/hero-section';
import { QuickStats } from '@/components/dashboard/quick-stats';
import { RecentActivity } from '@/components/dashboard/recent-activity';
import { SystemHealth } from '@/components/dashboard/system-health';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { Layout } from '@/components/layout/layout';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -20 }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.5
};

export default function HomePage() {
  return (
    <Layout>
      <motion.div
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
        className="space-y-8"
      >
        <Suspense fallback={<LoadingSpinner />}>
          <HeroSection />
        </Suspense>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Suspense fallback={<LoadingSpinner />}>
              <QuickStats />
            </Suspense>
            <Suspense fallback={<LoadingSpinner />}>
              <RecentActivity />
            </Suspense>
          </div>
          
          <div className="space-y-8">
            <Suspense fallback={<LoadingSpinner />}>
              <SystemHealth />
            </Suspense>
            <Suspense fallback={<LoadingSpinner />}>
              <QuickActions />
            </Suspense>
          </div>
        </div>
      </motion.div>
    </Layout>
  );
}