import React from 'react';
import { RecommendationResult } from '../../types';
import { Card } from './Card';
import { Badge } from './Badge';
import { ProgressBar } from './ProgressBar';
import { ShieldCheck, Cpu, Zap, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface RecommendationCardProps {
  result: RecommendationResult;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ result }) => {
  const {
    recommendedVariant,
    confidence,
    reason,
    estimatedKeygenUs,
    estimatedEncapUs,
    estimatedDecapUs,
    estimatedRamKb,
    ramUtilizationPercent,
    latencyCompliance,
    comparisonBadges,
  } = result;

  const isUnsupported = recommendedVariant === 'UNSUPPORTED';

  return (
    <Card className="p-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4 mb-5">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-md ${isUnsupported ? 'bg-rose-50 border-rose-200 text-rose-700' : 'bg-slate-100 border-slate-200 text-slate-800'} border`}>
            {isUnsupported ? <AlertTriangle className="w-6 h-6" /> : <ShieldCheck className="w-6 h-6" />}
          </div>
          <div>
            <span className="text-xs uppercase font-semibold tracking-wider text-slate-500">AI Recommendation Result</span>
            <h3 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2 font-mono">
              {recommendedVariant}
              {!isUnsupported && (
                <Badge variant="cyan" size="sm">
                  Recommended Variant
                </Badge>
              )}
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-50 px-3.5 py-1.5 rounded-md border border-slate-200">
          <Activity className="w-4 h-4 text-emerald-600" />
          <span className="text-xs text-slate-600 font-medium">Confidence Score:</span>
          <span className="text-sm font-bold text-emerald-700 font-mono">{confidence}%</span>
        </div>
      </div>

      {/* Reason text */}
      <div className="bg-slate-50 p-4 rounded-md border border-slate-200 mb-6">
        <p className="text-sm text-slate-700 leading-relaxed">{reason}</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-3.5 rounded-md border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-slate-600" /> KeyGen Latency
            </span>
            <span className="text-sm font-bold text-slate-900 font-mono">{(estimatedKeygenUs / 1000).toFixed(2)} ms</span>
          </div>
          <span className="text-xs text-slate-500 font-mono">{estimatedKeygenUs.toLocaleString()} µs</span>
        </div>

        <div className="bg-white p-3.5 rounded-md border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-slate-600" /> Encap Latency
            </span>
            <span className="text-sm font-bold text-slate-900 font-mono">{(estimatedEncapUs / 1000).toFixed(2)} ms</span>
          </div>
          <span className="text-xs text-slate-500 font-mono">{estimatedEncapUs.toLocaleString()} µs</span>
        </div>

        <div className="bg-white p-3.5 rounded-md border border-slate-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-slate-600" /> Decap Latency
            </span>
            <span className="text-sm font-bold text-slate-900 font-mono">{(estimatedDecapUs / 1000).toFixed(2)} ms</span>
          </div>
          <span className="text-xs text-slate-500 font-mono">{estimatedDecapUs.toLocaleString()} µs</span>
        </div>
      </div>

      {/* RAM Footprint & Latency Compliance Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-3.5 rounded-md border border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-slate-600" /> Target RAM Usage
            </span>
            <span className="text-xs font-semibold text-slate-800 font-mono">{estimatedRamKb} KB</span>
          </div>
          <ProgressBar
            value={ramUtilizationPercent}
            color={ramUtilizationPercent > 85 ? 'rose' : ramUtilizationPercent > 65 ? 'amber' : 'emerald'}
          />
        </div>

        <div className="bg-white p-3.5 rounded-md border border-slate-200 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-medium">Latency Budget Compliance</span>
            <Badge
              variant={
                latencyCompliance === 'EXCELLENT'
                  ? 'success'
                  : latencyCompliance === 'COMPLIANT'
                  ? 'info'
                  : latencyCompliance === 'WARNING'
                  ? 'warning'
                  : 'error'
              }
            >
              {latencyCompliance}
            </Badge>
          </div>
          <p className="text-xs text-slate-600 mt-2">
            Total latency ({( (estimatedKeygenUs + estimatedEncapUs + estimatedDecapUs) / 1000 ).toFixed(1)} ms) is within target real-time application constraints.
          </p>
        </div>
      </div>

      {/* Comparison Badges */}
      <div>
        <h4 className="text-xs uppercase font-semibold tracking-wider text-slate-500 mb-3">Hardware & Security Constraints Verification</h4>
        <div className="flex flex-wrap gap-2">
          {comparisonBadges.map((badge, idx) => (
            <Badge key={idx} variant={badge.type}>
              <CheckCircle2 className="w-3 h-3" />
              <span className="text-slate-600">{badge.label}:</span>
              <span className="font-bold text-slate-900">{badge.value}</span>
            </Badge>
          ))}
        </div>
      </div>
    </Card>
  );
};
