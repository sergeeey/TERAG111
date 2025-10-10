import React from 'react';
import { motion } from 'framer-motion';
import { Upload, MessageCircle, Settings, Download, Plus, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

const actions = [
  {
    title: 'Upload Document',
    description: 'Add new documents to the system',
    icon: Upload,
    href: '/documents',
    color: 'from-terag-accent-500 to-terag-accent-600',
    hoverColor: 'hover:from-terag-accent-400 hover:to-terag-accent-500',
  },
  {
    title: 'New Query',
    description: 'Ask a question about your data',
    icon: MessageCircle,
    href: '/query',
    color: 'from-terag-purple-500 to-terag-purple-600',
    hoverColor: 'hover:from-terag-purple-400 hover:to-terag-purple-500',
  },
  {
    title: 'Create Test',
    description: 'Start a new A/B experiment',
    icon: Plus,
    href: '/testing',
    color: 'from-terag-status-success to-green-600',
    hoverColor: 'hover:from-green-400 hover:to-green-500',
  },
  {
    title: 'Export Data',
    description: 'Download reports and analytics',
    icon: Download,
    href: '/analytics',
    color: 'from-terag-status-info to-blue-600',
    hoverColor: 'hover:from-blue-400 hover:to-blue-500',
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
    <div className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-6 space-y-6">
      <h2 className="text-xl font-bold">Quick Actions</h2>
      
      <div className="grid grid-cols-1 gap-3">
        {actions.map((action, index) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Link to={action.href}>
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

      <div className="pt-4 border-t border-terag-accent/20">
        <div className="flex items-center justify-between text-sm">
          <span className="text-terag-text-muted">Keyboard shortcuts</span>
          <button className="text-terag-accent-500 hover:text-terag-accent-400">
            View all
          </button>
        </div>
        <div className="mt-2 space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-terag-text-muted">Upload Document</span>
            <span className="bg-terag-accent/10 px-2 py-1 rounded">Ctrl+U</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-terag-text-muted">New Query</span>
            <span className="bg-terag-accent/10 px-2 py-1 rounded">Ctrl+Q</span>
          </div>
        </div>
      </div>
    </div>
  );
}