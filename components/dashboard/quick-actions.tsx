'use client';

import { motion } from 'framer-motion';
import { Upload, MessageCircle, Settings, Download, Plus, Zap } from 'lucide-react';
import Link from 'next/link';

const actions = [
  {
    title: 'Upload Document',
    description: 'Add new documents to the system',
    icon: Upload,
    href: '/documents',
    color: 'from-primary to-primary/80',
    hoverColor: 'hover:from-primary/90 hover:to-primary/70',
  },
  {
    title: 'New Query',
    description: 'Ask a question about your data',
    icon: MessageCircle,
    href: '/query',
    color: 'from-secondary to-secondary/80',
    hoverColor: 'hover:from-secondary/90 hover:to-secondary/70',
  },
  {
    title: 'Create Test',
    description: 'Start a new A/B experiment',
    icon: Plus,
    href: '/testing',
    color: 'from-accent to-accent/80',
    hoverColor: 'hover:from-accent/90 hover:to-accent/70',
  },
  {
    title: 'Export Data',
    description: 'Download reports and analytics',
    icon: Download,
    href: '/analytics',
    color: 'from-warning to-warning/80',
    hoverColor: 'hover:from-warning/90 hover:to-warning/70',
  },
  {
    title: 'System Settings',
    description: 'Configure system parameters',
    icon: Settings,
    href: '/settings',
    color: 'from-gray-600 to-gray-700',
    hoverColor: 'hover:from-gray-500 hover:to-gray-600',
  },
  {
    title: 'Quick Optimize',
    description: 'Run system optimization',
    icon: Zap,
    href: '#',
    color: 'from-purple-600 to-purple-700',
    hoverColor: 'hover:from-purple-500 hover:to-purple-600',
  },
];

export function QuickActions() {
  return (
    <div className="glass-card space-y-6">
      <h2 className="text-xl font-bold">Quick Actions</h2>
      
      <div className="grid grid-cols-1 gap-3">
        {actions.map((action, index) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Link href={action.href}>
              <motion.div
                className={`
                  p-4 rounded-lg bg-gradient-to-r ${action.color} ${action.hoverColor}
                  text-white cursor-pointer transition-all duration-200
                `}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <action.icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{action.title}</h3>
                    <p className="text-sm opacity-90">{action.description}</p>
                  </div>
                </div>
              </motion.div>
            </Link>
          </motion.div>
        ))}
      </div>

      <div className="pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Keyboard shortcuts</span>
          <button className="text-primary hover:text-primary/80">
            View all
          </button>
        </div>
        <div className="mt-2 space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Upload Document</span>
            <span className="bg-white/10 px-2 py-1 rounded">Ctrl+U</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">New Query</span>
            <span className="bg-white/10 px-2 py-1 rounded">Ctrl+Q</span>
          </div>
        </div>
      </div>
    </div>
  );
}