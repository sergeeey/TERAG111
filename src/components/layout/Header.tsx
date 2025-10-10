import React from 'react';
import { Menu, Search, Bell, User } from 'lucide-react';
import { ThemeToggle } from '../ui/ThemeToggle';
import { motion } from 'framer-motion';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <motion.header 
      className="bg-black/20 backdrop-blur-xl border-b border-terag-accent/20 m-4 mb-0 lg:mr-4 rounded-xl flex items-center justify-between px-6 py-4"
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Left side */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-terag-accent/10 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-terag-text-muted" />
          <input
            type="text"
            placeholder="Search anything..."
            className="pl-10 pr-4 py-2 bg-black/20 border border-terag-accent/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-terag-accent/50 focus:border-transparent w-64 text-terag-text-primary placeholder-terag-text-muted"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-4">
        <ThemeToggle />
        
        <button className="relative p-2 rounded-lg hover:bg-terag-accent/10 transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-terag-status-warning rounded-full animate-terag-pulse" />
        </button>

        <div className="flex items-center space-x-2 pl-4 border-l border-terag-accent/20">
          <div className="w-8 h-8 bg-terag-pulse rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="hidden sm:block">
            <div className="text-sm font-medium">John Doe</div>
            <div className="text-xs text-terag-text-muted">Admin</div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}