import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, XCircle, X } from 'lucide-react';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: AlertCircle,
};

const toastColors = {
  success: 'border-terag-status-success/50 bg-terag-status-success/10 text-terag-status-success',
  error: 'border-terag-status-error/50 bg-terag-status-error/10 text-terag-status-error',
  warning: 'border-terag-status-warning/50 bg-terag-status-warning/10 text-terag-status-warning',
  info: 'border-terag-status-info/50 bg-terag-status-info/10 text-terag-status-info',
};

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  useEffect(() => {
    const handleToast = (event: CustomEvent<Toast>) => {
      const toast = { ...event.detail, id: Math.random().toString() };
      setToasts(prev => [...prev, toast]);
      
      setTimeout(() => removeToast(toast.id), 5000);
    };

    window.addEventListener('toast' as any, handleToast);
    return () => window.removeEventListener('toast' as any, handleToast);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon = toastIcons[toast.type];
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 50, scale: 0.3 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -50, scale: 0.5 }}
              className={`
                bg-black/20 backdrop-blur-xl p-4 max-w-sm border ${toastColors[toast.type]}
                shadow-lg rounded-xl
              `}
            >
              <div className="flex items-start space-x-3">
                <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h4 className="font-semibold">{toast.title}</h4>
                  {toast.description && (
                    <p className="text-sm opacity-80 mt-1">{toast.description}</p>
                  )}
                </div>
                <button
                  onClick={() => removeToast(toast.id)}
                  className="opacity-60 hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}