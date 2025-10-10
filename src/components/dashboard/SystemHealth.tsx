import React from 'react';
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
    color: 'text-terag-status-success',
    bgColor: 'bg-terag-status-success/10',
    label: 'Healthy',
  },
  warning: {
    icon: AlertCircle,
    color: 'text-terag-status-warning',
    bgColor: 'bg-terag-status-warning/10',
    label: 'Warning',
  },
  error: {
    icon: XCircle,
    color: 'text-terag-status-error',
    bgColor: 'bg-terag-status-error/10',
    label: 'Error',
  },
};

export function SystemHealth() {
  const healthyServices = services.filter(s => s.status === 'healthy').length;
  const overallHealth = Math.round((healthyServices / services.length) * 100);

  return (
    <div className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">System Health</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-terag-status-success rounded-full animate-terag-pulse"></div>
          <span className="text-sm text-terag-status-success">Live</span>
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
              className="text-terag-accent/10"
            />
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${overallHealth * 2.51} 251`}
              className="text-terag-status-success"
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-2xl font-bold">{overallHealth}%</span>
          </div>
        </motion.div>
        <p className="text-terag-text-muted">Overall System Health</p>
      </div>

      {/* Services List */}
      <div className="space-y-3">
        {services.map((service, index) => {
          const config = statusConfig[service.status as keyof typeof statusConfig];
          return (
            <motion.div
              key={service.name}
              className="flex items-center justify-between p-3 bg-black/20 backdrop-blur-xl border border-terag-accent/10 rounded-lg"
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
                  <div className="text-xs text-terag-text-muted">{config.label}</div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm font-medium">{service.uptime}</div>
                <div className="text-xs text-terag-text-muted flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {service.responseTime}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="pt-4 border-t border-terag-accent/20">
        <p className="text-xs text-terag-text-muted text-center">
          Last updated: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}