import React from 'react';

interface ProgressBarProps {
  value: number; // 0 - 100
  label?: string;
  showValue?: boolean;
  color?: 'blue' | 'emerald' | 'amber' | 'rose' | 'cyan' | 'purple';
  size?: 'sm' | 'md';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  label,
  showValue = true,
  color = 'blue',
  size = 'md',
}) => {
  const cappedValue = Math.min(100, Math.max(0, value));

  const colorStyles = {
    blue: 'bg-blue-600',
    emerald: 'bg-emerald-600',
    amber: 'bg-amber-600',
    rose: 'bg-rose-600',
    cyan: 'bg-sky-600',
    purple: 'bg-indigo-600',
  };

  const heightStyles = {
    sm: 'h-1.5',
    md: 'h-2.5',
  };

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center text-xs mb-1 font-medium">
          {label && <span className="text-slate-700">{label}</span>}
          {showValue && <span className="text-slate-500 font-mono">{cappedValue}%</span>}
        </div>
      )}
      <div className={`w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200 ${heightStyles[size]}`}>
        <div
          className={`h-full rounded-full transition-all duration-300 ease-out ${colorStyles[color]}`}
          style={{ width: `${cappedValue}%` }}
        />
      </div>
    </div>
  );
};
