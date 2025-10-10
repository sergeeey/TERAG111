import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Home, FileText, MessageCircle, Network, TestTube, BarChart3 } from 'lucide-react';
import { cn } from '../../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Query', href: '/query', icon: MessageCircle },
  { name: 'Knowledge Graph', href: '/graph', icon: Network },
  { name: 'A/B Testing', href: '/testing', icon: TestTube },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
];

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileNav({ isOpen, onClose }: MobileNavProps) {
  const location = useLocation();

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
            className="lg:hidden fixed left-0 top-0 bottom-0 w-80 bg-black/20 backdrop-blur-xl border-r border-terag-accent/20 z-50 flex flex-col"
          >
            <div className="flex items-center justify-between p-6 border-b border-terag-accent/20">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-terag-pulse rounded-lg flex items-center justify-center">
                  <Network className="w-5 h-5 text-white" />
                </div>
                <div className="font-display font-bold text-lg bg-terag-pulse bg-clip-text text-transparent">
                  TERAG
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-terag-accent/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="flex-1 p-4 space-y-2">
              {navigation.map((item, index) => {
                const isActive = location.pathname === item.href;
                return (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Link
                      to={item.href}
                      onClick={onClose}
                      className={cn(
                        "flex items-center px-3 py-2.5 rounded-lg transition-all duration-200",
                        "hover:bg-terag-accent/10 group",
                        isActive ? "bg-terag-accent/20 text-terag-accent" : "text-terag-text-secondary"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="ml-3 font-medium">{item.name}</span>
                    </Link>
                  </motion.div>
                );
              })}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}