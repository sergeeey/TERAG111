import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp, TrendingDown, DollarSign, CreditCard, Wallet,
  ArrowUpRight, ArrowDownRight, MoreVertical, Eye, EyeOff,
  Zap, Coffee, ShoppingBag, Home, Car, Plane
} from 'lucide-react';

interface Transaction {
  id: string;
  title: string;
  subtitle: string;
  amount: number;
  type: 'expense' | 'income';
  icon: React.ReactNode;
  color: string;
  date: string;
}

interface ChartData {
  value: number;
  timestamp: number;
}

export default function Analytics() {
  const [balance, setBalance] = useState(567.57);
  const [hideBalance, setHideBalance] = useState(false);
  const [chartData, setChartData] = useState<ChartData[]>([]);

  const stats = [
    { label: 'Total Income', value: '$12,847', change: '+23.5%', trend: 'up', color: 'from-green-500 to-emerald-500' },
    { label: 'Total Expense', value: '$8,234', change: '+12.1%', trend: 'up', color: 'from-red-500 to-pink-500' },
    { label: 'Savings', value: '$4,613', change: '+45.2%', trend: 'up', color: 'from-cyan-500 to-blue-500' },
  ];

  const transactions: Transaction[] = [
    {
      id: '1',
      title: 'Morning Coffee',
      subtitle: 'Starbucks • Today',
      amount: -5.50,
      type: 'expense',
      icon: <Coffee className="w-5 h-5" />,
      color: 'from-orange-500 to-amber-500',
      date: '10:23 AM'
    },
    {
      id: '2',
      title: 'Grocery Shopping',
      subtitle: 'Whole Foods • Yesterday',
      amount: -127.34,
      type: 'expense',
      icon: <ShoppingBag className="w-5 h-5" />,
      color: 'from-green-500 to-emerald-500',
      date: '4:12 PM'
    },
    {
      id: '3',
      title: 'Salary Deposit',
      subtitle: 'Monthly Payment • 2 days ago',
      amount: +3500.00,
      type: 'income',
      icon: <DollarSign className="w-5 h-5" />,
      color: 'from-cyan-500 to-blue-500',
      date: '9:00 AM'
    },
    {
      id: '4',
      title: 'Rent Payment',
      subtitle: 'Landlord • 3 days ago',
      amount: -1200.00,
      type: 'expense',
      icon: <Home className="w-5 h-5" />,
      color: 'from-purple-500 to-pink-500',
      date: '12:00 PM'
    },
    {
      id: '5',
      title: 'Car Insurance',
      subtitle: 'Geico • 5 days ago',
      amount: -156.80,
      type: 'expense',
      icon: <Car className="w-5 h-5" />,
      color: 'from-blue-500 to-indigo-500',
      date: '3:45 PM'
    },
  ];

  useEffect(() => {
    const generateChartData = () => {
      const data: ChartData[] = [];
      const now = Date.now();
      for (let i = 50; i >= 0; i--) {
        data.push({
          value: 300 + Math.sin(i / 5) * 100 + Math.random() * 50,
          timestamp: now - i * 60000
        });
      }
      setChartData(data);
    };

    generateChartData();

    const interval = setInterval(() => {
      setChartData(prev => {
        const newData = [...prev.slice(1)];
        newData.push({
          value: 300 + Math.sin(Date.now() / 300000) * 100 + Math.random() * 50,
          timestamp: Date.now()
        });
        return newData;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const WaveChart = () => {
    if (chartData.length === 0) return null;

    const maxValue = Math.max(...chartData.map(d => d.value));
    const minValue = Math.min(...chartData.map(d => d.value));
    const range = maxValue - minValue;

    const points = chartData.map((d, i) => {
      const x = (i / (chartData.length - 1)) * 100;
      const y = 100 - ((d.value - minValue) / range) * 100;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#ff2d87" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#ff2d87" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        <motion.polyline
          points={points}
          fill="none"
          stroke="#ff2d87"
          strokeWidth="2"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeInOut' }}
        />
        <motion.polygon
          points={`${points} 100,100 0,100`}
          fill="url(#waveGradient)"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5 }}
        />
      </svg>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1d28] via-[#252936] to-[#1a1d28] p-6">
      <div className="max-w-[1400px] mx-auto space-y-6">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-400 via-rose-400 to-pink-500 bg-clip-text text-transparent">
            Financial Analytics
          </h1>
          <p className="text-white/50 mt-2">Track your spending and savings</p>
        </motion.div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

          {/* Main Balance Card */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="xl:col-span-1"
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/30 to-purple-500/30 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#2d3139] to-[#1a1d28] p-8 rounded-[32px] border border-pink-500/20 shadow-2xl h-full">
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-white/70 text-sm font-medium">Current Balance</span>
                  </div>
                  <button
                    onClick={() => setHideBalance(!hideBalance)}
                    className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                  >
                    {hideBalance ? <EyeOff className="w-5 h-5 text-white/40" /> : <Eye className="w-5 h-5 text-white/40" />}
                  </button>
                </div>

                <div className="relative">
                  <motion.div
                    key={hideBalance ? 'hidden' : 'visible'}
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="text-center"
                  >
                    {hideBalance ? (
                      <div className="text-5xl font-bold text-white my-8">••••••</div>
                    ) : (
                      <>
                        <div className="text-sm text-white/40 mb-2">USD</div>
                        <div className="text-6xl font-bold bg-gradient-to-br from-pink-400 to-rose-400 bg-clip-text text-transparent">
                          ${balance.toFixed(2)}
                        </div>
                      </>
                    )}
                  </motion.div>
                </div>

                <div className="mt-8 pt-6 border-t border-white/10">
                  <div className="flex items-center justify-between text-sm mb-3">
                    <span className="text-white/50">Card Number</span>
                    <span className="text-white font-mono">•••• 0000</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Expiry</span>
                    <span className="text-white font-mono">12/25</span>
                  </div>
                </div>

                <div className="mt-6">
                  <button className="w-full py-3 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 rounded-2xl text-white font-semibold transition-all duration-300 shadow-lg shadow-pink-500/30">
                    Start Now
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Chart & Stats */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="xl:col-span-2"
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#2d3139] to-[#1a1d28] p-8 rounded-[32px] border border-white/5 shadow-2xl h-full">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white">Spending Overview</h2>
                  <div className="flex items-center gap-2">
                    <div className="px-4 py-2 bg-pink-500/10 rounded-xl">
                      <span className="text-sm text-pink-400 font-semibold">$8,234</span>
                    </div>
                    <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                      <MoreVertical className="w-5 h-5 text-white/40" />
                    </button>
                  </div>
                </div>

                {/* Wave Chart */}
                <div className="h-48 mb-6">
                  <WaveChart />
                </div>

                {/* Sliders/Stats */}
                <div className="space-y-4">
                  {stats.map((stat, index) => (
                    <motion.div
                      key={stat.label}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      className="space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-white/70">{stat.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-white">{stat.value}</span>
                          <div className={`flex items-center gap-1 text-xs font-semibold ${
                            stat.trend === 'up' ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {stat.trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                            {stat.change}
                          </div>
                        </div>
                      </div>
                      <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          className={`h-full bg-gradient-to-r ${stat.color}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${60 + index * 10}%` }}
                          transition={{ duration: 1, delay: 0.4 + index * 0.1 }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Transactions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

            <div className="relative bg-gradient-to-br from-[#2d3139] to-[#1a1d28] p-8 rounded-[32px] border border-white/5 shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Recent Transactions</h2>
                <button className="text-sm text-pink-400 hover:text-pink-300 font-semibold transition-colors">
                  View All
                </button>
              </div>

              <div className="space-y-3">
                {transactions.map((transaction, index) => (
                  <motion.div
                    key={transaction.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 + index * 0.05 }}
                    className="group/item relative"
                  >
                    <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-white/5 to-transparent rounded-2xl hover:from-white/10 transition-all duration-300">
                      <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${transaction.color} flex items-center justify-center shadow-lg`}>
                        {transaction.icon}
                      </div>

                      <div className="flex-1">
                        <p className="text-white font-semibold text-sm">{transaction.title}</p>
                        <p className="text-white/40 text-xs mt-0.5">{transaction.subtitle}</p>
                      </div>

                      <div className="text-right">
                        <p className={`text-lg font-bold ${
                          transaction.type === 'income' ? 'text-green-400' : 'text-white'
                        }`}>
                          {transaction.amount > 0 ? '+' : ''}{transaction.amount.toFixed(2)}
                        </p>
                        <p className="text-xs text-white/30 mt-0.5">{transaction.date}</p>
                      </div>

                      <button className="p-2 hover:bg-white/5 rounded-lg transition-colors opacity-0 group-hover/item:opacity-100">
                        <MoreVertical className="w-4 h-4 text-white/40" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: <CreditCard className="w-6 h-6" />, label: 'Add Card', color: 'from-cyan-500 to-blue-500' },
            { icon: <Zap className="w-6 h-6" />, label: 'Quick Pay', color: 'from-purple-500 to-pink-500' },
            { icon: <TrendingUp className="w-6 h-6" />, label: 'Analytics', color: 'from-green-500 to-emerald-500' },
          ].map((action, index) => (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/0 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-500" />

              <div className="relative bg-gradient-to-br from-[#2d3139] to-[#1a1d28] p-6 rounded-3xl border border-white/5 hover:border-pink-500/30 shadow-xl transition-all duration-300 flex items-center gap-4">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${action.color} flex items-center justify-center shadow-lg`}>
                  {action.icon}
                </div>
                <span className="text-white font-semibold text-lg">{action.label}</span>
                <ArrowUpRight className="w-5 h-5 text-white/30 ml-auto group-hover:text-pink-400 transition-colors" />
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}
