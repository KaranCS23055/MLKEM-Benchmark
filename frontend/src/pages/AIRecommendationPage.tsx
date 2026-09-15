import React, { useState, useEffect } from 'react';
import { RecommendationFormInputs, RecommendationResult, SecurityLevel, OptimizationLevel } from '../types';
import { Card } from '../components/ui/Card';
import { RecommendationCard } from '../components/ui/RecommendationCard';
import { Button } from '../components/ui/Button';
import { BrainCircuit, Cpu, Sliders, Shield, Sparkles, Loader2, ServerOff } from 'lucide-react';

// Default hardware preset: STM32F407 Cortex-M4
const DEFAULT_INPUTS: RecommendationFormInputs = {
  mcu: 'STM32F407VGT6',
  architecture: 'aarch64',
  frequency: 168,
  ram: 192,
  flash: 1024,
  securityLevel: 'Level 3',
  optimization: 'O3',
  cpuLoad: 25,
  latencyBudget: 8000,
};

// Hardware presets matching our benchmark environments
const HARDWARE_PRESETS = [
  { label: 'Intel Core i7-1255U Windows (2600 MHz / 16 GB)', architecture: 'x86_64', mcu: 'i7-1255U-x86_64', frequency: 2600, ram: 16384, flash: 512000 },
  { label: 'Intel Core i7-1255U Single Core (2600 MHz / 16 GB)', architecture: 'x86_64', mcu: 'i7-1255U-single-core', frequency: 2600, ram: 16384, flash: 512000 },
  { label: 'STM32F407 Cortex-M4 (168 MHz / 192 KB)', architecture: 'aarch64', mcu: 'STM32F407VGT6', frequency: 168, ram: 192, flash: 1024 },
  { label: 'AMD Ryzen 5 x86-64 (3000 MHz / 16 GB)', architecture: 'x86_64', mcu: 'Ryzen5-x86_64', frequency: 3000, ram: 16384, flash: 512000 },
  { label: 'AMD Ryzen 5 x86-32 (3000 MHz / 4 GB)', architecture: 'x86_64', mcu: 'Ryzen5-x86_32', frequency: 3000, ram: 4096, flash: 256000 },
  { label: 'MediaTek Helio P65 ARM64 (2000 MHz / 4 GB)', architecture: 'aarch64', mcu: 'VivoY19-aarch64', frequency: 2000, ram: 4096, flash: 128000 },
  { label: 'RISC-V QEMU RV64GC (1000 MHz / 2 GB)', architecture: 'riscv64', mcu: 'RISCV64-QEMU', frequency: 1000, ram: 2096, flash: 64000 },
  { label: 'Custom Target', architecture: 'x86_64', mcu: 'Custom', frequency: 80, ram: 64, flash: 512 },
];

export const AIRecommendationPage: React.FC = () => {
  const [formInputs, setFormInputs] = useState<RecommendationFormInputs>(DEFAULT_INPUTS);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<string>('');

  // Auto-run once on mount with defaults
  useEffect(() => { runRecommendation(DEFAULT_INPUTS); }, []);

  const runRecommendation = async (inputs: RecommendationFormInputs) => {
    setIsLoading(true);
    setApiError(null);
    try {
      const res = await fetch('/api/recommendation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      if (!res.ok) throw new Error(`Backend returned HTTP ${res.status}`);
      const data: RecommendationResult = await res.json();
      setResult(data);
      // Detect which engine was used from the badge
      const engineBadge = data.comparisonBadges?.find((b) => b.label === 'Inference Engine');
      if (engineBadge) setModelInfo(engineBadge.value);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setApiError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMcuChange = (label: string) => {
    const preset = HARDWARE_PRESETS.find((p) => p.label === label);
    if (preset) {
      setFormInputs((prev) => ({
        ...prev,
        mcu: preset.mcu,
        frequency: preset.frequency,
        ram: preset.ram,
        flash: preset.flash,
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runRecommendation(formInputs);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              AI-Based ML-KEM Recommendation Engine
            </h1>
            <p className="text-xs text-slate-500">
              {modelInfo
                ? `Active inference engine: ${modelInfo}`
                : 'Input your target hardware specifications to receive a ML-KEM variant recommendation.'}
            </p>
          </div>
        </div>
      </Card>

      {/* API Error Banner */}
      {apiError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3.5 flex items-start gap-2.5 text-xs text-red-800">
          <ServerOff className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Backend API Error:</span> {apiError}.{' '}
            Make sure the FastAPI backend is running at <code>localhost:8000</code>.
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ── Input Form ── */}
        <div className="lg:col-span-6">
          <Card className="p-5">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2 border-b border-slate-200 pb-3">
              <Sliders className="w-4 h-4 text-slate-700" /> Target Hardware Specifications
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Hardware Preset Selector */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-slate-600" /> Target Hardware Preset
                </label>
                <select
                  onChange={(e) => handleMcuChange(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 font-medium outline-none focus:border-slate-800"
                >
                  {HARDWARE_PRESETS.map((p) => (
                    <option key={p.mcu} value={p.label}>{p.label}</option>
                  ))}
                </select>
              </div>

              {/* Frequency / RAM / Flash row */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Clock (MHz)</label>
                  <input
                    type="number" min={1} max={10000} value={formInputs.frequency}
                    onChange={(e) => setFormInputs({ ...formInputs, frequency: Number(e.target.value) })}
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 font-bold font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">SRAM (KB)</label>
                  <input
                    type="number" min={1} value={formInputs.ram}
                    onChange={(e) => setFormInputs({ ...formInputs, ram: Number(e.target.value) })}
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 font-bold font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Flash (KB)</label>
                  <input
                    type="number" min={1} value={formInputs.flash}
                    onChange={(e) => setFormInputs({ ...formInputs, flash: Number(e.target.value) })}
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 font-bold font-mono"
                  />
                </div>
              </div>

              {/* Security Level */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-slate-600" /> Target NIST Security Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Level 1', 'Level 3', 'Level 5'] as SecurityLevel[]).map((lvl) => (
                    <button
                      type="button" key={lvl}
                      onClick={() => setFormInputs({ ...formInputs, securityLevel: lvl })}
                      className={`py-2 px-3 rounded-md text-xs font-bold border transition-all cursor-pointer text-center ${
                        formInputs.securityLevel === lvl
                          ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  Level 1 → ML-KEM-512 (128-bit) · Level 3 → ML-KEM-768 (192-bit) · Level 5 → ML-KEM-1024 (256-bit)
                </p>
              </div>

              {/* Optimization + CPU Load */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Compiler Optimization (-O)</label>
                  <select
                    value={formInputs.optimization}
                    onChange={(e) => setFormInputs({ ...formInputs, optimization: e.target.value as OptimizationLevel })}
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 outline-none"
                  >
                    <option value="O0">-O0 (No Optimization)</option>
                    <option value="O1">-O1 (Minimal Size)</option>
                    <option value="O2">-O2 (Balanced Speed)</option>
                    <option value="O3">-O3 (Max Speed)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">
                    CPU Load: <span className="font-bold text-slate-900 font-mono">{formInputs.cpuLoad}%</span>
                  </label>
                  <input
                    type="range" min={0} max={75} value={formInputs.cpuLoad}
                    onChange={(e) => setFormInputs({ ...formInputs, cpuLoad: Number(e.target.value) })}
                    className="w-full accent-slate-900 mt-2"
                  />
                </div>
              </div>

              {/* Latency Budget */}
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">
                  Max Latency Budget (µs): <span className="font-bold font-mono text-slate-900">{formInputs.latencyBudget.toLocaleString()} µs</span>
                </label>
                <input
                  type="number" step={500} min={500} value={formInputs.latencyBudget}
                  onChange={(e) => setFormInputs({ ...formInputs, latencyBudget: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 font-bold font-mono"
                />
              </div>

              {/* Submit */}
              <Button
                type="submit" variant="primary" size="md" className="w-full mt-2"
                isLoading={isLoading}
                icon={isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-amber-400" />}
              >
                {isLoading ? 'Running Inference...' : 'Get ML-KEM Recommendation'}
              </Button>
            </form>
          </Card>
        </div>

        {/* ── ML Output Card ── */}
        <div className="lg:col-span-6">
          {isLoading && !result ? (
            <Card className="p-12 flex items-center justify-center gap-3 text-slate-500 text-sm">
              <Loader2 className="w-5 h-5 animate-spin" />
              Running ML inference on backend...
            </Card>
          ) : result ? (
            <RecommendationCard result={result} />
          ) : null}
        </div>
      </div>
    </div>
  );
};
