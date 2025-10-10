import React, { Suspense } from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from '../components/dashboard/HeroSection';
import { QuickStats } from '../components/dashboard/QuickStats';
import { RecentActivity } from '../components/dashboard/RecentActivity';
import { SystemHealth } from '../components/dashboard/SystemHealth';
import { QuickActions } from '../components/dashboard/QuickActions';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';

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

export default function Dashboard() {
  return (
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
  );
}