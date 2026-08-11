import React from 'react';
import { ProcessorProfile } from '../../types';
import { Card } from './Card';
import { Badge } from './Badge';
import { Cpu, HardDrive, Zap, Layers } from 'lucide-react';

interface ProcessorCardProps {
  processor: ProcessorProfile;
}

export const ProcessorCard: React.FC<ProcessorCardProps> = ({ processor }) => {
  const { mcu, name, core, architecture, frequency, ram, flash, supportedVariants, description, features } = processor;

  const archColor = architecture === 'ARM Cortex-M' ? 'info' : architecture === 'RISC-V' ? 'purple' : 'cyan';

  return (
    <Card className="flex flex-col justify-between h-full">
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div>
            <Badge variant={archColor} size="sm" className="mb-2">
              {architecture}
            </Badge>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight font-mono">{mcu}</h3>
            <p className="text-xs text-slate-500 font-medium">{name} ({core})</p>
          </div>
          <div className="p-2 rounded-md bg-slate-100 border border-slate-200 text-slate-700">
            <Cpu className="w-5 h-5" />
          </div>
        </div>

        <p className="text-xs text-slate-600 mb-4 line-clamp-2 leading-relaxed">{description}</p>

        {/* Technical Specs Grid */}
        <div className="grid grid-cols-3 gap-2 bg-slate-50 p-2.5 rounded-md border border-slate-200 mb-4">
          <div className="text-center">
            <span className="text-[10px] uppercase font-semibold text-slate-500 flex items-center justify-center gap-1">
              <Zap className="w-3 h-3 text-amber-600" /> Clock
            </span>
            <span className="text-xs font-bold text-slate-900 font-mono">{frequency} MHz</span>
          </div>

          <div className="text-center border-x border-slate-200">
            <span className="text-[10px] uppercase font-semibold text-slate-500 flex items-center justify-center gap-1">
              <Cpu className="w-3 h-3 text-emerald-600" /> SRAM
            </span>
            <span className="text-xs font-bold text-slate-900 font-mono">{ram} KB</span>
          </div>

          <div className="text-center">
            <span className="text-[10px] uppercase font-semibold text-slate-500 flex items-center justify-center gap-1">
              <HardDrive className="w-3 h-3 text-blue-600" /> Flash
            </span>
            <span className="text-xs font-bold text-slate-900 font-mono">{flash >= 1024 ? `${flash / 1024} MB` : `${flash} KB`}</span>
          </div>
        </div>

        {/* Supported ML-KEM Variants */}
        <div className="mb-4">
          <span className="text-[11px] uppercase font-semibold tracking-wider text-slate-500 mb-2 block flex items-center gap-1">
            <Layers className="w-3 h-3 text-slate-600" /> Supported Variants
          </span>
          <div className="flex flex-wrap gap-1.5">
            {['ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024'].map((varName) => {
              const isSupported = supportedVariants.includes(varName as any);
              return (
                <Badge
                  key={varName}
                  variant={isSupported ? 'success' : 'default'}
                  size="sm"
                  className={!isSupported ? 'opacity-40 line-through' : ''}
                >
                  {varName}
                </Badge>
              );
            })}
          </div>
        </div>
      </div>

      {/* Feature Bullet Points */}
      <div className="pt-3 border-t border-slate-200">
        <ul className="grid grid-cols-2 gap-1.5 text-[11px] text-slate-600">
          {features.map((feat, idx) => (
            <li key={idx} className="flex items-center gap-1 truncate">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
              {feat}
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
};
