'use client';

import { motion } from 'framer-motion';
import { FileText, MessageCircle, CheckCircle, AlertCircle, Clock } from 'lucide-react';

const activities = [
  {
    id: 1,
    type: 'document',
    title: 'New document uploaded',
    description: 'research-paper-2024.pdf processed successfully',
    time: '2 minutes ago',
    icon: FileText,
    status: 'success',
  },
  {
    id: 2,
    type: 'query',
    title: 'Query processed',
    description: 'What is the main conclusion of the research?',
    time: '5 minutes ago',
    icon: MessageCircle,
    status: 'success',
  },
  {
    id: 3,
    type: 'system',
    title: 'A/B test completed',
    description: 'Experiment #47 finished with 94.2% confidence',
    time: '15 minutes ago',
    icon: CheckCircle,
    status: 'success',
  },
  {
    id: 4,
    type: 'warning',
    title: 'High response time detected',
    description: 'Query processing took 3.2s (threshold: 2.0s)',
    time: '32 minutes ago',
    icon: AlertCircle,
    status: 'warning',
  },
  {
    id: 5,
    type: 'document',
    title: 'Document reindexed',
    description: 'Knowledge graph updated with new connections',
    time: '1 hour ago',
    icon: FileText,
    status: 'processing',
  },
];

const statusColors = {
  success: 'text-accent',
  warning: 'text-warning',
  processing: 'text-primary',
  error: 'text-danger',
};

const statusBgColors = {
  success: 'bg-accent/10',
  warning: 'bg-warning/10',
  processing: 'bg-primary/10',
  error: 'bg-danger/10',
};

export function RecentActivity() {
  return (
    <div className="glass-card space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Recent Activity</h2>
        <button className="text-primary hover:text-primary/80 text-sm">View all</button>
      </div>

      <div className="space-y-4">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            className="flex items-start space-x-4 p-4 glass rounded-lg hover:bg-white/5 transition-colors"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <div className={`p-2 rounded-lg ${statusBgColors[activity.status as keyof typeof statusBgColors]}`}>
              <activity.icon className={`w-4 h-4 ${statusColors[activity.status as keyof typeof statusColors]}`} />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h4 className="font-medium truncate">{activity.title}</h4>
                <span className="text-xs text-muted-foreground flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {activity.time}
                </span>
              </div>
              <p className="text-sm text-muted-foreground truncate">{activity.description}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Showing 5 of 127 activities</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span className="text-accent">Live updates</span>
          </div>
        </div>
      </div>
    </div>
  );
}