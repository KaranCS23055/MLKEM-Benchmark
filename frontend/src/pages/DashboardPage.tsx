import React from 'react';
import { PageId } from '../components/layout/Sidebar';
import { StatCard } from '../components/ui/StatCard';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { DASHBOARD_STATS, BENCHMARK_DATASET, PROCESSOR_PROFILES } from '../data/mockData';
import {
  ShieldCheck,
  BrainCircuit,
  Database,
  BarChart3,
  Cpu,
  Zap,
  CheckCircle2,
  ArrowRight,
  Activity,
  Layers,
  Info,
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (page: PageId) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Overview Header Card */}
      <Card className="p-6 lg:p-8 bg-white border border-stone-200">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="info">Final Year B.Tech Research Project</Badge>
              <Badge variant="purple">NIST FIPS 203 ML-KEM Standard</Badge>
            </div>

            <h1 className="text-2xl lg:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
              Post-Quantum ML-KEM Benchmarking Framework with AI-Based Recommendation System
            </h1>

            <p className="text-xs lg:text-sm text-slate-600 leading-relaxed">
              Empirical characterization of NIST FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)
              variants (512, 768, 1024) across resource-constrained IoT microcontrollers (ARM Cortex-M, RISC-V, Xtensa)
              using Renode physical cycle simulation and AI recommendation UI modeling.
            </p>

            <div className="flex flex-wrap gap-3 pt-2">
              <Button
                onClick={() => onNavigate('benchmarks')}
                variant="primary"
                size="sm"
                icon={<Database className="w-4 h-4" />}
              >
                Explore Benchmark Data
              </Button>

              <Button
                onClick={() => onNavigate('analytics')}
                variant="secondary"
                size="sm"
                icon={<BarChart3 className="w-4 h-4 text-slate-600" />}
              >
                View Analytics & Graphs
              </Button>

              <Button
                onClick={() => onNavigate('recommendation')}
                variant="outline"
                size="sm"
                icon={<BrainCircuit className="w-4 h-4 text-slate-600" />}
              >
                AI Recommender UI
              </Button>
            </div>
          </div>

          <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg lg:w-72 shrink-0">
            <div className="text-xs uppercase font-semibold text-slate-500 mb-2 tracking-wider">
              Research Objective
            </div>
            <p className="text-xs text-slate-700 leading-normal">
              Analyze physical memory bounds (SRAM/Flash), CPU clock cycles, and execution latency to enable automated post-quantum variant selection for embedded security.
            </p>
          </div>
        </div>
      </Card>

      {/* Statistics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Benchmarks"
          value={DASHBOARD_STATS.totalBenchmarks.toLocaleString()}
          subtitle="Empirical Renode runs"
          icon={<Database className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Supported Processors"
          value={DASHBOARD_STATS.processorsSupported}
          subtitle="ARM Cortex-M, RISC-V, Xtensa"
          icon={<Cpu className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="ML-KEM Variants"
          value="512 / 768 / 1024"
          subtitle="NIST Security Levels 1, 3, 5"
          icon={<ShieldCheck className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Avg Latency"
          value={`${(DASHBOARD_STATS.avgExecutionTimeUs / 1000).toFixed(1)} ms`}
          subtitle="KeyGen + Encap + Decap"
          icon={<Zap className="w-5 h-5 text-slate-700" />}
        />
        <StatCard
          title="Verification Status"
          value={`${DASHBOARD_STATS.totalPasses} PASS`}
          subtitle={`${DASHBOARD_STATS.totalOOMs} OOM bounds recorded`}
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-600" />}
          trend={{ value: '100% Verified', isPositive: true }}
        />
      </div>

      {/* Main Grid: Recent Activity & Processor Profiles */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recent Benchmark Activity Table */}
        <div className="lg:col-span-8">
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4 border-b border-slate-200 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-slate-700" /> Recent Benchmark Execution Runs
                </h3>
                <p className="text-xs text-slate-500">Selected empirical measurements from benchmark.csv</p>
              </div>
              <button
                onClick={() => onNavigate('benchmarks')}
                className="text-xs text-slate-800 hover:text-black font-semibold flex items-center gap-1 cursor-pointer"
              >
                View All Records <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 uppercase font-semibold bg-slate-50">
                    <th className="py-2.5 px-3">Target MCU</th>
                    <th className="py-2.5 px-3">Core & Clock</th>
                    <th className="py-2.5 px-3">Variant</th>
                    <th className="py-2.5 px-3">Encap Latency</th>
                    <th className="py-2.5 px-3">RAM</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {BENCHMARK_DATASET.slice(0, 7).map((row) => (
                    <tr key={row.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2.5 px-3 font-semibold text-slate-900 font-mono">{row.mcu}</td>
                      <td className="py-2.5 px-3 text-slate-600">
                        {row.core} ({row.clock_mhz} MHz)
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-slate-900 font-mono">{row.variant}</td>
                      <td className="py-2.5 px-3 text-slate-700 font-mono">
                        {row.encap_us === 'OOM' ? 'OOM' : `${(row.encap_us / 1000).toFixed(2)} ms`}
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
          </Card>
        </div>

        {/* Quick Hardware Profiles List */}
        <div className="lg:col-span-4 space-y-6">
          <Card className="p-5">
            <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-slate-700" /> Supported Processors
            </h3>
            <div className="space-y-2.5">
              {PROCESSOR_PROFILES.slice(0, 4).map((mcu) => (
                <div
                  key={mcu.mcu}
                  onClick={() => onNavigate('processors')}
                  className="p-3 rounded-md bg-stone-50 border border-slate-200 hover:border-slate-400 transition-all cursor-pointer flex items-center justify-between"
                >
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 font-mono">{mcu.mcu}</h4>
                    <p className="text-[11px] text-slate-500">
                      {mcu.core} • {mcu.frequency} MHz
                    </p>
                  </div>
                  <Badge variant="info" size="sm">
                    {mcu.ram} KB RAM
                  </Badge>
                </div>
              ))}
            </div>

            <Button
              onClick={() => onNavigate('processors')}
              variant="secondary"
              size="sm"
              className="w-full mt-4"
            >
              View All Processors
            </Button>
          </Card>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div>
        <h3 className="text-sm uppercase font-semibold text-slate-500 tracking-wider mb-3">
          Quick Navigation
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card
            onClick={() => onNavigate('benchmarks')}
            hoverEffect
            className="p-4 flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 rounded bg-slate-100 border border-slate-200 text-slate-800">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">Benchmark Explorer</h4>
              <p className="text-xs text-slate-500 mt-0.5">Filter, sort, and export benchmark data</p>
            </div>
          </Card>

          <Card
            onClick={() => onNavigate('analytics')}
            hoverEffect
            className="p-4 flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 rounded bg-slate-100 border border-slate-200 text-slate-800">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">Analytics & Graphs</h4>
              <p className="text-xs text-slate-500 mt-0.5">Cycles, time, RAM, flash & energy charts</p>
            </div>
          </Card>

          <Card
            onClick={() => onNavigate('variants')}
            hoverEffect
            className="p-4 flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 rounded bg-slate-100 border border-slate-200 text-slate-800">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">ML-KEM Variants</h4>
              <p className="text-xs text-slate-500 mt-0.5">Compare ML-KEM-512, 768, 1024 specifications</p>
            </div>
          </Card>

          <Card
            onClick={() => onNavigate('about')}
            hoverEffect
            className="p-4 flex items-start gap-3 cursor-pointer"
          >
            <div className="p-2 rounded bg-slate-100 border border-slate-200 text-slate-800">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900">About Project</h4>
              <p className="text-xs text-slate-500 mt-0.5">Architecture, tech stack & project team</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
