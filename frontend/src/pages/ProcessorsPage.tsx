import React, { useEffect, useState } from 'react';
import { ProcessorProfile } from '../types';
import { ProcessorCard } from '../components/ui/ProcessorCard';
import { Card } from '../components/ui/Card';
import { Cpu, Filter, Search } from 'lucide-react';

export const ProcessorsPage: React.FC = () => {
  const [processors, setProcessors] = useState<ProcessorProfile[]>([]);
  const [search, setSearch] = useState('');
  const [selectedArch, setSelectedArch] = useState<string>('ALL');

  useEffect(() => {
    fetch('/api/processors').then((response) => response.json()).then(setProcessors).catch(() => setProcessors([]));
  }, []);

  const filteredProcessors = processors.filter((p) => {
    const matchesSearch =
      p.mcu.toLowerCase().includes(search.toLowerCase()) ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.core.toLowerCase().includes(search.toLowerCase());

    const matchesArch = selectedArch === 'ALL' || p.architecture === selectedArch;

    return matchesSearch && matchesArch;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Banner */}
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Evaluated Hardware Silicon Profiles</h1>
            <p className="text-xs text-slate-500">
              Empirical hardware profiles loaded from the benchmark dataset, including the latest ESP32 Xtensa LX6 run
            </p>
          </div>
        </div>
      </Card>

      {/* Filter and Search Bar */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search processor by MCU, core, or features..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-300 rounded-md text-xs text-slate-900 placeholder-slate-400 focus:border-slate-800 outline-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={selectedArch}
              onChange={(e) => setSelectedArch(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-800 font-medium outline-none"
            >
              <option value="ALL">All Architectures (x86_64, aarch64, xtensa_lx106)</option>
              <option value="x86_64">x86-64 (Intel & AMD Processors)</option>
              <option value="aarch64">ARM64 (MediaTek Mobile SoC)</option>
              <option value="xtensa_lx106">Xtensa (ESP8266 Microcontroller)</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Processor Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredProcessors.map((processor) => (
          <ProcessorCard key={processor.mcu} processor={processor} />
        ))}
      </div>
    </div>
  );
};
