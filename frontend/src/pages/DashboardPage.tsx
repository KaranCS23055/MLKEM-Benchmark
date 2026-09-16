import React, { useState, useEffect } from 'react';
import { PageId } from '../components/layout/Sidebar';
import { StatCard } from '../components/ui/StatCard';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  ShieldCheck, BrainCircuit, Database, BarChart3, Cpu,
  Zap, CheckCircle2, ArrowRight, Activity, Layers, Info, Loader2,
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (page: PageId) => void;
}

interface AnalyticsData {
  totalBenchmarks: number;
  totalPasses: number;
  totalOOMs: number;
  passRatePercent: number;
  avgEncapLatencyUs: number;
  supportedProcessors: number;
  mlkemVariants: number;
  aiAccuracyPercent: number;
}

interface BenchmarkRow {
  id: string;
  mcu: string;
  core: string;
  clock_mhz: number;
  variant: string;
  encap_us: number;
  ram_kb: number;
  verification_status: string;
}

interface ProcessorRow {
  mcu: string;
  core: string;
  frequency: number;
  ram: number;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentBenchmarks, setRecentBenchmarks] = useState<BenchmarkRow[]>([]);
  const [processors, setProcessors] = useState<ProcessorRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [analyticsRes, benchmarksRes, processorsRes] = await Promise.all([
          fetch('/api/analytics'),
          fetch('/api/benchmarks?type=baseline'),
          fetch('/api/processors'),
        ]);
        if (analyticsRes.ok)  setAnalytics(await analyticsRes.json());
        if (benchmarksRes.ok) setRecentBenchmarks((await benchmarksRes.json()).slice(0, 7));
        if (processorsRes.ok) setProcessors(await processorsRes.json());
      } catch (e) {
        console.error('Dashboard fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const stats = analytics ?? {
    totalBenchmarks: 37914,
    totalPasses: 37914,
    totalOOMs: 0,
    passRatePercent: 100,
    avgEncapLatencyUs: 641.9,
    supportedProcessors: 6,
    mlkemVariants: 3,
    aiAccuracyPercent: 90.48,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Overview Header Card */}
      <Card className="p-6 lg:p-8 bg-white border border-stone-200">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="info">Final Year B.Tech Research Project</Badge>
              <Badge variant="purple">NIST FIPS 203 ML-KEM Standard</Badge>
              <Badge variant="success">Phase 11 — ML Model Active</Badge>
            </div>

            <h1 className="text-2xl lg:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
              Post-Quantum ML-KEM Benchmarking Framework
            </h1>
            <p className="text-xs lg:text-sm text-slate-600 leading-relaxed">
              Empirical characterization of NIST FIPS 203 ML-KEM variants (512, 768, 1024) across
              six processor/device profiles, including native software execution on x86_64 and physical ARM/Xtensa targets.
              {analytics && <span className="text-emerald-700 font-semibold"> {stats.totalBenchmarks.toLocaleString()} benchmark measurements loaded live from backend.</span>}
            </p>

            <div className="flex flex-wrap gap-3 pt-2">
              <Button onClick={() => onNavigate('benchmarks')} variant="primary" size="sm" icon={<Database className="w-4 h-4" />}>
                Explore Benchmark Data
              </Button>
              <Button onClick={() => onNavigate('analytics')} variant="secondary" size="sm" icon={<BarChart3 className="w-4 h-4 text-slate-600" />}>
                View Analytics &amp; Graphs
              </Button>
              <Button onClick={() => onNavigate('recommendation')} variant="outline" size="sm" icon={<BrainCircuit className="w-4 h-4 text-slate-600" />}>
                AI Recommendation Engine
              </Button>
            </div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg lg:w-72 shrink-0">
            <div className="text-xs uppercase font-semibold text-slate-500 mb-2 tracking-wider">Research Objective</div>
            <p className="text-xs text-slate-700 leading-normal">
              Analyze physical memory bounds (SRAM/Flash), CPU execution latency, and multi-architecture
              performance to enable automated post-quantum ML-KEM variant selection using a trained
              Random Forest ML surrogate model.
            </p>
            <div className="mt-3 pt-3 border-t border-slate-200 text-xs text-slate-500">
              <span className="text-emerald-600 font-bold">ML Model:</span> Random Forest · metrics loaded from the current evaluation report · 80/20 split
            </div>
          </div>
        </div>
      </Card>

      {/* Live Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Benchmarks"
          value={stats.totalBenchmarks.toLocaleString()}
          subtitle="Live empirical measurements"
          icon={<Database className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Environments"
          value={stats.supportedProcessors}
          subtitle="x86-64 Win, x86-64 WSL2, x86-32, aarch64, riscv64"
          icon={<Cpu className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="ML-KEM Variants"
          value="512 / 768 / 1024"
          subtitle="NIST Security Levels 1, 3, 5"
          icon={<ShieldCheck className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Avg Encap Latency"
          value={`${stats.avgEncapLatencyUs.toFixed(1)} µs`}
          subtitle="Mean across all environments"
          icon={<Zap className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Pass Rate"
          value={`${stats.passRatePercent}%`}
          subtitle={`${stats.totalPasses.toLocaleString()} PASS · ${stats.totalOOMs} OOM`}
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />}
          trend={{ value: 'All variants verified', isPositive: true }}
        />
      </div>

      {/* Main Grid: Recent Benchmarks + Processors */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Benchmark Table — Live from API */}
        <div className="lg:col-span-8">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4 border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-slate-700" /> Recent Benchmark Execution Records
                </h3>
                <p className="text-xs text-slate-500">
                  Live normalized observations from <code>data/processed/phase11_statistics/</code>
                </p>
              </div>
              <button onClick={() => onNavigate('benchmarks')} className="text-xs text-slate-800 hover:text-black font-semibold flex items-center gap-1 cursor-pointer">
                View All {stats.totalBenchmarks.toLocaleString()} Records <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center p-8 text-slate-400 gap-2 text-xs">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading live benchmark data...
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 uppercase font-semibold bg-slate-50">
                      <th className="py-2.5 px-3">Target Environment</th>
                      <th className="py-2.5 px-3">Architecture</th>
                      <th className="py-2.5 px-3">Variant</th>
                      <th className="py-2.5 px-3">Encap Latency</th>
                      <th className="py-2.5 px-3">SRAM Used</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {recentBenchmarks.map((row) => (
                      <tr key={row.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3 font-semibold text-slate-900 font-mono text-[11px]">{row.mcu}</td>
                        <td className="py-2.5 px-3 text-slate-600">{row.core}</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-900 font-mono">{row.variant}</td>
                        <td className="py-2.5 px-3 text-slate-700 font-mono">
                          {row.encap_us ? `${row.encap_us.toLocaleString()} µs` : '-'}
                        </td>
                        <td className="py-2.5 px-3 text-slate-600 font-mono">{row.ram_kb} KB</td>
                        <td className="py-2.5 px-3">
                          <Badge variant={row.verification_status === 'PASS' ? 'success' : 'error'} size="sm">
                            {row.verification_status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>

        {/* Hardware Environments — Live from /api/processors */}
        <div className="lg:col-span-4 space-y-6">
          <Card className="p-5">
            <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-slate-700" /> Benchmark Environments
            </h3>
            {loading ? (
              <div className="flex items-center justify-center p-4 text-slate-400 gap-2 text-xs">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading...
              </div>
            ) : (
              <div className="space-y-2.5">
                {processors.slice(0, 5).map((env) => (
                  <div
                    key={env.mcu}
                    onClick={() => onNavigate('processors')}
                    className="p-3 rounded-md bg-stone-50 border border-slate-200 hover:border-slate-400 transition-all cursor-pointer flex items-center justify-between"
                  >
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 font-mono">{env.mcu}</h4>
                      <p className="text-[11px] text-slate-500">{env.core} • {env.frequency} MHz</p>
                    </div>
                    <Badge variant="info" size="sm">{env.ram >= 1024 ? `${(env.ram/1024).toFixed(0)} GB` : `${env.ram} KB`}</Badge>
                  </div>
                ))}
              </div>
            )}
            <Button onClick={() => onNavigate('processors')} variant="secondary" size="sm" className="w-full mt-4">
              View All Environments
            </Button>
          </Card>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div>
        <h3 className="text-sm uppercase font-semibold text-slate-500 tracking-wider mb-3">Quick Navigation</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { page: 'benchmarks' as PageId, icon: <Database className="w-5 h-5" />, title: 'Benchmark Explorer', desc: `Filter, sort, and export ${stats.totalBenchmarks.toLocaleString()} measurements` },
            { page: 'analytics'  as PageId, icon: <BarChart3 className="w-5 h-5" />, title: 'Analytics & Graphs', desc: 'Latency, cycles, SRAM, and energy charts' },
            { page: 'variants'   as PageId, icon: <Layers className="w-5 h-5" />, title: 'ML-KEM Variants', desc: 'Compare ML-KEM-512, 768, 1024 specs' },
            { page: 'about'      as PageId, icon: <Info className="w-5 h-5" />, title: 'About Project', desc: 'Architecture, tech stack & team members' },
          ].map(({ page, icon, title, desc }) => (
            <Card key={page} onClick={() => onNavigate(page)} hoverEffect className="p-4 flex items-start gap-3 cursor-pointer">
              <div className="p-2 rounded bg-slate-100 border border-slate-200 text-slate-800">{icon}</div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">{title}</h4>
                <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
