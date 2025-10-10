'use client';

import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';

const services = [
  {
    name: 'API Gateway',
    status: 'healthy',
    uptime: '99.9%',
    responseTime: '45ms',
  },
  {
    name: 'Document Parser',
    status: 'healthy',
    uptime: '99.7%',
    responseTime: '120ms',
  },
  {
    name: 'Knowledge Graph',
    status: 'warning',
    uptime: '98.2%',
    responseTime: '890ms',
  },
  {
    name: 'A/B Testing',
    status: 'healthy',
    uptime: '99.8%',
    responseTime: '67ms',
  },
  {
    name: 'Analytics',
    status: 'healthy',
    uptime: '99.5%',
    responseTime: '134ms',
  },
];

const statusConfig = {
  healthy: {
    icon: CheckCircle,
    color: 'text-accent',
    bgColor: 'bg-accent/10',
    label: 'Healthy',
  },
  warning: {
    icon: AlertCircle,
    color: 'text-warning',
    bgColor: 'bg-warning/10',
    label: 'Warning',
  },
  error: {
    icon: XCircle,
    color: 'text-danger',
    bgColor: 'bg-danger/10',
    label: 'Error',
  },
};

export function SystemHealth() {
  const healthyServices = services.filter(s => s.status === 'healthy').length;
  const overallHealth = Math.round((healthyServices / services.length) * 100);

  return (
    <div className="glass-card space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">System Health</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
          <span className="text-sm text-accent">Live</span>
        </div>
      </div>

      {/* Overall Health */}
      <div className="text-center py-6">
        <motion.div
          className="w-24 h-24 mx-auto mb-4 relative"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", bounce: 0.5, duration: 0.8 }}
        >
          <svg className="w-24 h-24 transform -rotate-90">
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-white/10"
            />
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${overallHealth * 2.51} 251`}
              className="text-accent"
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold">{overallHealth}%</span>
          </div>
        </motion.div>
        <p className="text-muted-foreground">Overall System Health</p>
      </div>

      {/* Services List */}
      <div className="space-y-3">
        {services.map((service, index) => {
          const config = statusConfig[service.status as keyof typeof statusConfig];
          return (
            <motion.div
              key={service.name}
              className="flex items-center justify-between p-3 glass rounded-lg"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-1.5 rounded-full ${config.bgColor}`}>
                  <config.icon className={`w-3 h-3 ${config.color}`} />
                </div>
                <div>
                  <div className="font-medium text-sm">{service.name}</div>
                  <div className="text-xs text-muted-foreground">{config.label}</div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm font-medium">{service.uptime}</div>
                <div className="text-xs text-muted-foreground flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {service.responseTime}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="pt-4 border-t border-white/10">
        <p className="text-xs text-muted-foreground text-center">
          Last updated: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}