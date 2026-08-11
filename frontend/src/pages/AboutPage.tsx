import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Info, Code2, ShieldCheck, Layers, Users, BookOpen } from 'lucide-react';

export const AboutPage: React.FC = () => {
  const technologies = [
    { name: 'Renode Simulator', category: 'Simulation Environment', desc: 'Antmicro Renode instruction-set simulator for Cortex-M & RISC-V targets' },
    { name: 'PQClean Library', category: 'Post-Quantum Codebase', desc: 'Standalone C implementations of NIST FIPS 203 ML-KEM algorithms' },
    { name: 'ARM GCC Toolchain', category: 'Compiler & Toolchain', desc: 'arm-none-eabi-gcc toolchain with -O0, -O1, -O2, and -O3 optimization flags' },
    { name: 'Python Data Pipeline', category: 'Analysis Module', desc: 'Automated statistical parser using pandas, numpy, seaborn, and matplotlib' },
    { name: 'React 18 & TypeScript', category: 'Frontend Framework', desc: 'Type-safe single-page application built with Vite and React Router' },
    { name: 'Tailwind CSS', category: 'Styling & Design System', desc: 'Light mode academic research design system with warm off-white tones' },
  ];

  const teamMembers = [
    { name: 'Final Year B.Tech Student', role: 'Frontend & UI/UX Developer', task: 'React, TypeScript, Tailwind CSS, Recharts dashboard design' },
    { name: 'Backend & Simulation Teammates', role: 'Embedded Systems & AI Engineers', task: 'Renode firmware compilation, Python dataset analysis & AI modeling' },
  ];

  const references = [
    { title: 'NIST FIPS 203 Standard', desc: 'Module-Lattice-Based Key-Encapsulation Mechanism Standard (August 2024)', url: 'https://csrc.nist.gov/pubs/fips/203/final' },
    { title: 'PQClean Open-Source Repository', desc: 'Clean and portable C implementations of post-quantum cryptography', url: 'https://github.com/PQClean/PQClean' },
    { title: 'Renode Simulation Framework', desc: 'Virtual development framework for multi-node embedded systems', url: 'https://renode.io' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Banner */}
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
            <Info className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              About Project & System Architecture
            </h1>
            <p className="text-xs text-slate-500">
              Final Year B.Tech Computer Science Project in Post-Quantum Cryptography & Embedded Benchmarking
            </p>
          </div>
        </div>
      </Card>

      {/* Project Objective */}
      <Card className="p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-slate-700" /> Project Objective & Research Scope
        </h2>
        <p className="text-xs text-slate-700 leading-relaxed mb-3">
          As the National Institute of Standards and Technology (NIST) standardizes Post-Quantum Cryptography (PQC) under FIPS 203,
          migrating resource-constrained Internet of Things (IoT) hardware to ML-KEM presents severe engineering challenges regarding stack RAM consumption,
          execution latency, and CPU frequency scaling.
        </p>
        <p className="text-xs text-slate-700 leading-relaxed">
          This project implements an empirical micro-benchmarking testbed across microcontroller targets (STM32F0, STM32F4, STM32H7, nRF52840, HiFive1) using Renode simulation.
          It collects physics-calibrated execution profiles (KeyGen, Encapsulation, Decapsulation, CPU Cycles, RAM Usage, Flash Usage, and Energy Consumption) and presents a research-oriented frontend dashboard for data exploration and decision modeling.
        </p>
      </Card>

      {/* System Architecture Workflow */}
      <Card className="p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-slate-700" /> End-to-End System Workflow
        </h2>

        {/* Visual Workflow Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          <div className="p-3 rounded bg-stone-50 border border-slate-200 text-center">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center mx-auto mb-2 font-bold text-xs font-mono">
              1
            </div>
            <h4 className="text-xs font-bold text-slate-900 mb-1">C Codebase & Firmware</h4>
            <p className="text-[11px] text-slate-500 leading-snug">Compile FIPS 203 C implementations using GCC</p>
          </div>

          <div className="p-3 rounded bg-stone-50 border border-slate-200 text-center">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center mx-auto mb-2 font-bold text-xs font-mono">
              2
            </div>
            <h4 className="text-xs font-bold text-slate-900 mb-1">Renode Simulation</h4>
            <p className="text-[11px] text-slate-500 leading-snug">Execute on virtual ARM Cortex-M & RISC-V targets</p>
          </div>

          <div className="p-3 rounded bg-stone-50 border border-slate-200 text-center">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center mx-auto mb-2 font-bold text-xs font-mono">
              3
            </div>
            <h4 className="text-xs font-bold text-slate-900 mb-1">UART Log Extraction</h4>
            <p className="text-[11px] text-slate-500 leading-snug">Extract cycles, microseconds & memory parameters</p>
          </div>

          <div className="p-3 rounded bg-stone-50 border border-slate-200 text-center">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center mx-auto mb-2 font-bold text-xs font-mono">
              4
            </div>
            <h4 className="text-xs font-bold text-slate-900 mb-1">Python Dataset Analysis</h4>
            <p className="text-[11px] text-slate-500 leading-snug">Validate schema, compute stats & plot dataset summary</p>
          </div>

          <div className="p-3 rounded bg-stone-50 border border-slate-200 text-center">
            <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center mx-auto mb-2 font-bold text-xs font-mono">
              5
            </div>
            <h4 className="text-xs font-bold text-slate-900 mb-1">React Research Dashboard</h4>
            <p className="text-[11px] text-slate-500 leading-snug">Explore data, view analytics & recommendation UI</p>
          </div>
        </div>
      </Card>

      {/* Technologies Used Grid */}
      <Card className="p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Code2 className="w-4 h-4 text-slate-700" /> Technologies & Toolchain Stack
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {technologies.map((tech) => (
            <div key={tech.name} className="p-3 rounded bg-stone-50 border border-slate-200">
              <Badge variant="info" size="sm" className="mb-1.5">
                {tech.category}
              </Badge>
              <h4 className="text-xs font-bold text-slate-900 font-mono mb-1">{tech.name}</h4>
              <p className="text-[11px] text-slate-600 leading-snug">{tech.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Team Section */}
      <Card className="p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Users className="w-4 h-4 text-slate-700" /> B.Tech Project Team
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {teamMembers.map((member, idx) => (
            <div key={idx} className="p-3.5 rounded bg-stone-50 border border-slate-200">
              <h4 className="text-xs font-bold text-slate-900">{member.name}</h4>
              <p className="text-[11px] text-slate-500 font-medium mb-1">{member.role}</p>
              <p className="text-[11px] text-slate-600">{member.task}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* References */}
      <Card className="p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-slate-700" /> Key References & Standards
        </h2>
        <div className="space-y-2">
          {references.map((ref, idx) => (
            <div key={idx} className="p-3 rounded bg-stone-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h4 className="text-xs font-bold text-slate-900">{ref.title}</h4>
                <p className="text-[11px] text-slate-500">{ref.desc}</p>
              </div>
              <a
                href={ref.url}
                target="_blank"
                rel="noreferrer"
                className="text-[11px] font-semibold text-blue-700 hover:underline shrink-0"
              >
                {ref.url}
              </a>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
