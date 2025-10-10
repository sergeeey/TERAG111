import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Home, FileText, MessageCircle, Network, 
  TestTube, BarChart3, Settings, LogOut, Brain,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import { cn } from '../../utils/cn';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'TERAG System', href: '/terag', icon: Brain },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Query', href: '/query', icon: MessageCircle },
  { name: 'Knowledge Graph', href: '/graph', icon: Network },
  { name: 'A/B Testing', href: '/testing', icon: TestTube },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <motion.div 
      className="h-full bg-black/20 backdrop-blur-xl border-r border-terag-accent/20 flex flex-col"
      animate={{ width: isCollapsed ? 80 : 256 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      {/* Logo */}
      <div className="flex items-center justify-between p-6 border-b border-terag-accent/20">
        {!isCollapsed && (
          <motion.div 
            className="flex items-center space-x-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="w-8 h-8 bg-terag-pulse rounded-lg flex items-center justify-center">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div className="font-display font-bold text-lg bg-terag-pulse bg-clip-text text-transparent">
              TERAG
            </div>
          </motion.div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-lg hover:bg-terag-accent/10 transition-colors"
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </motion.div>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 relative group",
                "hover:bg-terag-accent/10",
                isActive && "bg-terag-accent/20 text-terag-accent"
              )}
            >
              <item.icon className={cn(
                "w-5 h-5 flex-shrink-0",
                isActive ? "text-terag-accent" : "text-terag-text-secondary"
              )} />
              {!isCollapsed && (
                <motion.span 
                  className="ml-3 font-medium"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  {item.name}
                </motion.span>
              )}
              
              {isActive && (
                <motion.div
                  layoutId="active-nav"
                  className="absolute inset-0 bg-terag-accent/10 rounded-lg border border-terag-accent/30"
                  initial={false}
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}

              {/* Tooltip for collapsed state */}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-terag-accent/20">
        <button
          className="flex items-center w-full px-3 py-2.5 rounded-lg hover:bg-terag-accent/10 transition-colors text-terag-text-secondary"
        >
          <LogOut className="w-5 h-5" />
          {!isCollapsed && <span className="ml-3">Logout</span>}
        </button>
      </div>
    </motion.div>
  );
}