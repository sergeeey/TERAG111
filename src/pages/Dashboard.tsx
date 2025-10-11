import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Brain, Activity, Zap, TrendingUp, Globe, Cpu, Network,
  Database, Clock, ChevronRight, Play, Pause, Settings,
  BarChart3, Radio, Waves
} from 'lucide-react';
import { useLanguage } from '../i18n/LanguageContext';
import { SolarSystem } from '../components/background/SolarSystem';

interface AgentStatus {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'processing';
  load: number;
  queries: number;
}

interface MetricCard {
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: string;
}

export default function Dashboard() {
  const { t } = useLanguage();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemStatus, setSystemStatus] = useState<'online' | 'processing' | 'idle'>('online');
  const [activeQueries, setActiveQueries] = useState(47);
  const [ieiScore, setIeiScore] = useState(0.89);

  const [agents] = useState<AgentStatus[]>([
    { id: '1', name: 'Planner', status: 'active', load: 85, queries: 342 },
    { id: '2', name: 'Intuit', status: 'processing', load: 72, queries: 289 },
    { id: '3', name: 'Critic', status: 'active', load: 91, queries: 425 },
    { id: '4', name: 'Verifier', status: 'idle', load: 34, queries: 156 },
    { id: '5', name: 'Curator', status: 'active', load: 78, queries: 318 },
    { id: '6', name: 'Reflector', status: 'processing', load: 66, queries: 201 },
  ]);

  const metrics: MetricCard[] = [
    {
      label: 'Total Queries',
      value: '12,847',
      change: '+23%',
      trend: 'up',
      icon: <Zap className="w-6 h-6" />,
      color: 'from-cyan-500 to-blue-500'
    },
    {
      label: 'Avg Response',
      value: '1.2s',
      change: '-15%',
      trend: 'down',
      icon: <Clock className="w-6 h-6" />,
      color: 'from-purple-500 to-pink-500'
    },
    {
      label: 'Active Agents',
      value: '6/7',
      change: '100%',
      trend: 'up',
      icon: <Network className="w-6 h-6" />,
      color: 'from-green-500 to-emerald-500'
    },
    {
      label: 'Knowledge Base',
      value: '2.4TB',
      change: '+8%',
      trend: 'up',
      icon: <Database className="w-6 h-6" />,
      color: 'from-orange-500 to-red-500'
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      setActiveQueries(prev => prev + Math.floor(Math.random() * 3) - 1);
      setIeiScore(prev => Math.min(0.99, Math.max(0.75, prev + (Math.random() - 0.5) * 0.02)));
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  const WaveVisualization = () => {
    return (
      <svg className="w-full h-20" viewBox="0 0 300 80" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#0099ff" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#00d4ff" stopOpacity="0.8" />
          </linearGradient>
        </defs>
        {[0, 1, 2].map((i) => (
          <motion.path
            key={i}
            d={`M0,40 Q75,${20 + i * 5} 150,40 T300,40`}
            fill="none"
            stroke="url(#waveGradient)"
            strokeWidth="2"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.4 - i * 0.1 }}
            transition={{
              duration: 2,
              delay: i * 0.2,
              repeat: Infinity,
              repeatType: 'loop',
              ease: 'easeInOut'
            }}
          />
        ))}
      </svg>
    );
  };

  return (
    <div className="min-h-screen bg-[#000000] p-6 relative overflow-hidden">
      {/* Solar System Background */}
      <SolarSystem />

      {/* Content */}
      <div className="max-w-[1800px] mx-auto space-y-6 relative z-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <div className="flex items-center gap-3">
              <div className="text-sm text-cyan-400 font-mono">
                {currentTime.toLocaleTimeString()}
              </div>
              <div className="text-sm text-white/40">
                {currentTime.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })}
              </div>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              TERAG Control Center
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="px-6 py-3 bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl rounded-2xl border border-cyan-500/20 shadow-lg shadow-cyan-500/10">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${systemStatus === 'online' ? 'bg-cyan-400' : 'bg-purple-400'} animate-pulse`} />
                <span className="text-white/80 text-sm font-medium">
                  {systemStatus === 'online' ? 'All Systems Operational' : 'Processing'}
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-500" />

              <div className="relative bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl p-6 rounded-3xl border border-white/5 shadow-2xl hover:shadow-cyan-500/20 transition-all duration-500">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 bg-gradient-to-br ${metric.color} rounded-2xl shadow-lg`}>
                    {metric.icon}
                  </div>
                  <div className={`flex items-center gap-1 text-sm font-semibold ${
                    metric.trend === 'up' ? 'text-green-400' : 'text-cyan-400'
                  }`}>
                    <TrendingUp className={`w-4 h-4 ${metric.trend === 'down' ? 'rotate-180' : ''}`} />
                    {metric.change}
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-white/50 text-sm font-medium">{metric.label}</p>
                  <p className="text-3xl font-bold text-white">{metric.value}</p>
                </div>

                <div className="mt-4 h-1 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full bg-gradient-to-r ${metric.color}`}
                    initial={{ width: 0 }}
                    animate={{ width: '70%' }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                  />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

          {/* Central IEI Score Display */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="xl:col-span-1"
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl p-8 rounded-[32px] border border-cyan-500/20 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-cyan-400" />
                    <span className="text-white/70 text-sm font-medium">Intelligence Index</span>
                  </div>
                  <Settings className="w-5 h-5 text-white/30 hover:text-cyan-400 cursor-pointer transition-colors" />
                </div>

                <div className="relative flex items-center justify-center h-64">
                  {/* Circular Progress */}
                  <svg className="absolute inset-0 w-full h-full -rotate-90">
                    <circle
                      cx="50%"
                      cy="50%"
                      r="45%"
                      fill="none"
                      stroke="rgba(255,255,255,0.05)"
                      strokeWidth="12"
                    />
                    <motion.circle
                      cx="50%"
                      cy="50%"
                      r="45%"
                      fill="none"
                      stroke="url(#ieiGradient)"
                      strokeWidth="12"
                      strokeLinecap="round"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: ieiScore }}
                      transition={{ duration: 1.5, ease: 'easeOut' }}
                      style={{
                        strokeDasharray: `${2 * Math.PI * 45}%`,
                      }}
                    />
                    <defs>
                      <linearGradient id="ieiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#00d4ff" />
                        <stop offset="50%" stopColor="#0099ff" />
                        <stop offset="100%" stopColor="#7b3ff2" />
                      </linearGradient>
                    </defs>
                  </svg>

                  {/* Center Display */}
                  <div className="relative z-10 text-center">
                    <div className="mb-2">
                      <Activity className="w-8 h-8 text-cyan-400 mx-auto animate-pulse" />
                    </div>
                    <motion.div
                      key={ieiScore}
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="text-6xl font-bold bg-gradient-to-br from-cyan-400 to-purple-400 bg-clip-text text-transparent"
                    >
                      {(ieiScore * 100).toFixed(1)}
                    </motion.div>
                    <p className="text-white/50 text-sm mt-2 font-medium">IEI Score</p>
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Coherence</span>
                    <span className="text-white font-semibold">92%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Faithfulness</span>
                    <span className="text-white font-semibold">88%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/50">Reasoning Depth</span>
                    <span className="text-white font-semibold">7 layers</span>
                  </div>
                </div>

                <div className="mt-6">
                  <WaveVisualization />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Agent Status Grid */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="xl:col-span-2"
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl p-8 rounded-[32px] border border-white/5 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-3">
                    <Cpu className="w-6 h-6 text-purple-400" />
                    Cognitive Agents
                  </h2>
                  <div className="flex items-center gap-2">
                    <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                      <Play className="w-4 h-4 text-green-400" />
                    </button>
                    <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                      <Pause className="w-4 h-4 text-cyan-400" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {agents.map((agent, index) => (
                    <motion.div
                      key={agent.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 + index * 0.05 }}
                      className="relative group/agent"
                    >
                      <div className="bg-gradient-to-br from-[#10131A]/70 to-[#1A1E2E]/70 backdrop-blur-md p-5 rounded-2xl border border-white/5 hover:border-cyan-500/30 transition-all duration-300">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`w-2 h-2 rounded-full ${
                              agent.status === 'active' ? 'bg-cyan-400' :
                              agent.status === 'processing' ? 'bg-purple-400 animate-pulse' :
                              'bg-white/20'
                            }`} />
                            <span className="font-semibold text-white">{agent.name}</span>
                          </div>
                          <span className="text-xs text-white/40 capitalize">{agent.status}</span>
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-white/50">Load</span>
                            <span className="text-white font-medium">{agent.load}%</span>
                          </div>
                          <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                              className={`h-full ${
                                agent.load > 80 ? 'bg-gradient-to-r from-red-500 to-orange-500' :
                                agent.load > 60 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                                'bg-gradient-to-r from-cyan-500 to-blue-500'
                              }`}
                              initial={{ width: 0 }}
                              animate={{ width: `${agent.load}%` }}
                              transition={{ duration: 1, delay: 0.7 + index * 0.05 }}
                            />
                          </div>

                          <div className="flex items-center justify-between text-xs pt-2">
                            <span className="text-white/40">Queries</span>
                            <span className="text-cyan-400 font-semibold">{agent.queries.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Bottom Row - Activity & Globe */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {/* Real-time Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl p-8 rounded-[32px] border border-white/5 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-3">
                    <Radio className="w-6 h-6 text-green-400" />
                    Real-time Activity
                  </h2>
                  <div className="flex items-center gap-2 text-sm text-white/50">
                    <Waves className="w-4 h-4" />
                    <span>Live</span>
                  </div>
                </div>

                <div className="space-y-4">
                  {[
                    { user: 'User #4231', action: 'Complex reasoning query', time: '2s ago', type: 'query' },
                    { user: 'System', action: 'Knowledge base updated', time: '15s ago', type: 'system' },
                    { user: 'User #4189', action: 'Voice query processed', time: '32s ago', type: 'voice' },
                    { user: 'Meta Agent', action: 'Optimization cycle complete', time: '1m ago', type: 'agent' },
                    { user: 'User #4156', action: 'Graph visualization rendered', time: '2m ago', type: 'visual' },
                  ].map((activity, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + index * 0.1 }}
                      className="flex items-center gap-4 p-4 bg-gradient-to-r from-white/5 to-transparent rounded-xl hover:from-white/10 transition-all duration-300 group/activity"
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        activity.type === 'query' ? 'bg-gradient-to-br from-cyan-500/20 to-blue-500/20' :
                        activity.type === 'voice' ? 'bg-gradient-to-br from-purple-500/20 to-pink-500/20' :
                        activity.type === 'system' ? 'bg-gradient-to-br from-green-500/20 to-emerald-500/20' :
                        activity.type === 'agent' ? 'bg-gradient-to-br from-orange-500/20 to-red-500/20' :
                        'bg-gradient-to-br from-yellow-500/20 to-orange-500/20'
                      }`}>
                        {activity.type === 'query' && <Zap className="w-5 h-5 text-cyan-400" />}
                        {activity.type === 'voice' && <Radio className="w-5 h-5 text-purple-400" />}
                        {activity.type === 'system' && <Database className="w-5 h-5 text-green-400" />}
                        {activity.type === 'agent' && <Cpu className="w-5 h-5 text-orange-400" />}
                        {activity.type === 'visual' && <BarChart3 className="w-5 h-5 text-yellow-400" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium text-sm">{activity.action}</p>
                        <p className="text-white/40 text-xs mt-0.5">{activity.user}</p>
                      </div>
                      <div className="text-xs text-white/30">{activity.time}</div>
                      <ChevronRight className="w-4 h-4 text-white/20 group-hover/activity:text-cyan-400 transition-colors" />
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Global Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-[32px] blur-2xl group-hover:blur-3xl transition-all duration-700" />

              <div className="relative bg-gradient-to-br from-[#1a1d3f]/80 to-[#252936]/80 backdrop-blur-xl p-8 rounded-[32px] border border-white/5 shadow-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white flex items-center gap-3">
                    <Globe className="w-6 h-6 text-cyan-400" />
                    Global Distribution
                  </h2>
                  <span className="text-sm text-cyan-400 font-semibold">{activeQueries} active</span>
                </div>

                <div className="relative h-64 flex items-center justify-center">
                  {/* Globe Visualization Placeholder */}
                  <div className="relative w-48 h-48">
                    <motion.div
                      className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20 blur-2xl"
                      animate={{
                        scale: [1, 1.1, 1],
                        opacity: [0.5, 0.8, 0.5]
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: 'easeInOut'
                      }}
                    />
                    <div className="absolute inset-0 rounded-full border-2 border-cyan-400/30" />
                    <div className="absolute inset-4 rounded-full border border-cyan-400/20" />
                    <div className="absolute inset-8 rounded-full border border-cyan-400/10" />

                    {/* Rotating rings */}
                    <motion.div
                      className="absolute inset-0 rounded-full border border-cyan-400/40"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                    />
                    <motion.div
                      className="absolute inset-0 rounded-full border border-purple-400/40"
                      animate={{ rotate: -360 }}
                      transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
                    />

                    {/* Center glow */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <motion.div
                        className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-400 to-purple-400"
                        animate={{
                          scale: [1, 1.2, 1],
                          opacity: [0.8, 1, 0.8]
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: 'easeInOut'
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-6">
                  {[
                    { region: 'Americas', count: 8429, color: 'from-cyan-500 to-blue-500' },
                    { region: 'Europe', count: 6234, color: 'from-purple-500 to-pink-500' },
                    { region: 'Asia-Pacific', count: 12847, color: 'from-green-500 to-emerald-500' },
                  ].map((region, index) => (
                    <div key={region.region} className="text-center">
                      <div className={`text-2xl font-bold bg-gradient-to-r ${region.color} bg-clip-text text-transparent`}>
                        {region.count.toLocaleString()}
                      </div>
                      <div className="text-xs text-white/50 mt-1">{region.region}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
