import { useEffect, useState } from 'react';
import { Activity, Brain, CheckCircle, TrendingUp } from 'lucide-react';
import type { MetricsData } from '../../services/terag-api';

interface MetricsHUDProps {
  metrics: MetricsData;
  isConnected: boolean;
}

interface MetricGaugeProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function MetricGauge({ label, value, icon, color }: MetricGaugeProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDisplayValue((prev) => {
        const diff = value - prev;
        if (Math.abs(diff) < 0.01) return value;
        return prev + diff * 0.1;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [value]);

  const percentage = displayValue * 100;
  const rotation = (percentage / 100) * 180 - 90;

  return (
    <div className="relative">
      <div className="flex items-center gap-2 mb-2">
        <div className={`text-${color}`}>{icon}</div>
        <span className="text-xs font-medium text-white/70 uppercase tracking-wider">
          {label}
        </span>
      </div>

      <div className="relative w-32 h-16">
        <svg className="w-full h-full" viewBox="0 0 128 64">
          <path
            d="M 10 54 A 54 54 0 0 1 118 54"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
            strokeLinecap="round"
          />

          <path
            d="M 10 54 A 54 54 0 0 1 118 54"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(percentage / 100) * 170} 170`}
            style={{
              filter: `drop-shadow(0 0 8px ${color})`,
            }}
          />

          <circle
            cx="64"
            cy="54"
            r="3"
            fill={color}
            style={{
              transform: `rotate(${rotation}deg)`,
              transformOrigin: '64px 54px',
              filter: `drop-shadow(0 0 4px ${color})`,
            }}
          />
        </svg>

        <div className="absolute inset-0 flex items-end justify-center pb-2">
          <span className="text-2xl font-bold text-white">
            {displayValue.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="mt-1 h-1 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-500 rounded-full"
          style={{
            width: `${percentage}%`,
            backgroundColor: color,
            boxShadow: `0 0 10px ${color}`,
          }}
        />
      </div>
    </div>
  );
}

export function MetricsHUD({ metrics, isConnected }: MetricsHUDProps) {
  const getColorForValue = (value: number) => {
    if (value > 0.9) return '#00FFE0';
    if (value > 0.8) return '#00D4FF';
    if (value > 0.7) return '#0099FF';
    return '#FF6B6B';
  };

  return (
    <div className="fixed top-6 right-6 z-40">
      <div className="bg-gradient-to-br from-[#10131A]/95 to-[#1A1E2E]/95 backdrop-blur-xl rounded-2xl border border-[#00FFE0]/20 shadow-2xl p-6 min-w-[400px]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-[#00FFE0]' : 'bg-red-500'} animate-pulse`} />
              <div className={`absolute inset-0 w-3 h-3 rounded-full ${isConnected ? 'bg-[#00FFE0]' : 'bg-red-500'} animate-ping opacity-75`} />
            </div>
            <h3 className="text-lg font-bold text-white">Cognitive Metrics</h3>
          </div>
          <TrendingUp className="w-5 h-5 text-[#00FFE0]" />
        </div>

        <div className="grid grid-cols-1 gap-6">
          <MetricGauge
            label="IEI Score"
            value={metrics.iei}
            icon={<Brain className="w-4 h-4" />}
            color={getColorForValue(metrics.iei)}
          />

          <MetricGauge
            label="Coherence"
            value={metrics.coherence}
            icon={<Activity className="w-4 h-4" />}
            color={getColorForValue(metrics.coherence)}
          />

          <MetricGauge
            label="Faithfulness"
            value={metrics.faithfulness}
            icon={<CheckCircle className="w-4 h-4" />}
            color={getColorForValue(metrics.faithfulness)}
          />
        </div>

        <div className="mt-6 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/50">System Status</span>
            <span className={`font-semibold ${isConnected ? 'text-[#00FFE0]' : 'text-red-400'}`}>
              {isConnected ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>

          {metrics.timestamp && (
            <div className="flex items-center justify-between text-xs mt-2">
              <span className="text-white/50">Last Update</span>
              <span className="text-white/70">
                {new Date(metrics.timestamp).toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>

        <div className="mt-4 p-3 bg-gradient-to-r from-[#00FFE0]/5 to-[#FF00FF]/5 rounded-lg border border-[#00FFE0]/10">
          <p className="text-xs text-white/60 leading-relaxed">
            {metrics.iei > 0.9
              ? 'Exceptional cognitive performance. System operating at peak efficiency.'
              : metrics.iei > 0.8
              ? 'Strong reasoning coherence. All systems nominal.'
              : metrics.iei > 0.7
              ? 'Moderate performance. Consider optimization.'
              : 'Performance degradation detected. Review required.'}
          </p>
        </div>
      </div>
    </div>
  );
}
