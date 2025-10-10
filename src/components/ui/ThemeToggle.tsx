import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { motion } from 'framer-motion';

export function ThemeToggle() {
  const [isDark, setIsDark] = React.useState(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
    // Here you would implement actual theme switching logic
  };

  return (
    <motion.button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-terag-accent/10 transition-colors relative overflow-hidden"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <motion.div
        key={isDark ? 'dark' : 'light'}
        initial={{ y: -30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 30, opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {isDark ? (
          <Sun className="w-5 h-5 text-terag-status-info" />
        ) : (
          <Moon className="w-5 h-5 text-terag-accent-500" />
        )}
      </motion.div>
    </motion.button>
  );
}