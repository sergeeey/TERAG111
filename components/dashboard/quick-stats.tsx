'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { LineChart, Line, ResponsiveContainer, AreaChart, Area, XAxis, YAxis } from 'recharts';

const data = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 600 },
  { name: 'Apr', value: 800 },
  { name: 'May', value: 500 },
  { name: 'Jun', value: 900 },
];

const metrics = [
  {
    title: 'Quality Score',
    value: '94.2%',
    trend: 5.2,
    type: 'increase',
    color: 'text-accent',
    bgColor: 'bg-accent/10',
  },
  {
    title: 'Response Time',
    value: '1.2s',
    trend: -0.3,
    type: 'decrease',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  {
    title: 'Success Rate',
    value: '99.1%',
    trend: 0.8,
    type: 'increase',
    color: 'text-secondary',
    bgColor: 'bg-secondary/10',
  },
  {
    title: 'Active Users',
    value: '2,847',
    trend: 0,
    type: 'neutral',
    color: 'text-warning',
    bgColor: 'bg-warning/10',
  },
];

export function QuickStats() {
  return (
    <div className="glass-card space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Performance Overview</h2>
        <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1 text-sm">
          <option>Last 7 days</option>
          <option>Last 30 days</option>
          <option>Last 3 months</option>
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            className="glass p-6 rounded-xl relative overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                {metric.type === 'increase' && <TrendingUp className={`w-4 h-4 ${metric.color}`} />}
                {metric.type === 'decrease' && <TrendingDown className={`w-4 h-4 ${metric.color}`} />}
                {metric.type === 'neutral' && <Minus className={`w-4 h-4 ${metric.color}`} />}
              </div>
              <div className={`text-sm ${
                metric.type === 'increase' ? 'text-accent' :
                metric.type === 'decrease' ? 'text-danger' : 'text-muted-foreground'
              }`}>
                {metric.trend > 0 && '+'}
                {metric.trend !== 0 && `${metric.trend}%`}
                {metric.trend === 0 && 'No change'}
              </div>
            </div>
            
            <div className="mb-2">
              <div className="text-2xl font-bold">{metric.value}</div>
              <div className="text-sm text-muted-foreground">{metric.title}</div>
            </div>

            <div className="h-16 -mx-2 -mb-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id={`gradient-${index}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={metric.color.replace('text-', '#')} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={metric.color.replace('text-', '#')} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={metric.color.replace('text-', '#')}
                    strokeWidth={2}
                    fill={`url(#gradient-${index})`}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Chart */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">System Performance</h3>
          <div className="flex space-x-2">
            <button className="px-3 py-1 bg-primary/20 text-primary rounded-lg text-sm">Quality</button>
            <button className="px-3 py-1 text-muted-foreground hover:bg-white/5 rounded-lg text-sm">Speed</button>
            <button className="px-3 py-1 text-muted-foreground hover:bg-white/5 rounded-lg text-sm">Usage</button>
          </div>
        </div>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3B82F6" 
                strokeWidth={3}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}