import React from 'react';
import { MLKEM_VARIANTS } from '../data/mockData';
import { VariantCard } from '../components/ui/VariantCard';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ShieldCheck, BookOpen, Layers } from 'lucide-react';

export const MLKEMVariantsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Banner */}
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              NIST FIPS 203 ML-KEM Variant Specifications & Comparison
            </h1>
            <p className="text-xs text-slate-500">
              Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM-512, ML-KEM-768, ML-KEM-1024) comparison table
            </p>
          </div>
        </div>
      </Card>

      {/* Side-by-Side Direct Comparison Table */}
      <Card className="p-5">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-slate-700" /> Variant Comparison Matrix
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border border-slate-200">
            <thead className="bg-slate-100 text-slate-700 uppercase font-semibold">
              <tr className="border-b border-slate-200">
                <th className="py-3 px-4 border-r border-slate-200">Specification Parameter</th>
                <th className="py-3 px-4 border-r border-slate-200">ML-KEM-512</th>
                <th className="py-3 px-4 border-r border-slate-200">ML-KEM-768 (Default)</th>
                <th className="py-3 px-4">ML-KEM-1024 (Max Security)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  NIST Claimed Security Category
                </td>
                <td className="py-2.5 px-4 border-r border-slate-200">
                  <Badge variant="info">Category 1 (AES-128)</Badge>
                </td>
                <td className="py-2.5 px-4 border-r border-slate-200">
                  <Badge variant="purple">Category 3 (AES-192)</Badge>
                </td>
                <td className="py-2.5 px-4">
                  <Badge variant="emerald">Category 5 (AES-256)</Badge>
                </td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Module Matrix Dimension ($k$)
                </td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">$k = 2$</td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">$k = 3$</td>
                <td className="py-2.5 px-4 font-mono">$k = 4$</td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Public Key Size ($pk$)
                </td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">800 Bytes</td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">1,184 Bytes</td>
                <td className="py-2.5 px-4 font-mono">1,568 Bytes</td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Secret Key Size ($sk$)
                </td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">1,632 Bytes</td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">2,400 Bytes</td>
                <td className="py-2.5 px-4 font-mono">3,168 Bytes</td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Ciphertext Size ($c$)
                </td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">768 Bytes</td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200">1,088 Bytes</td>
                <td className="py-2.5 px-4 font-mono">1,568 Bytes</td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Minimum SRAM Boundary
                </td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200 text-slate-900 font-bold">&ge; 16 KB SRAM</td>
                <td className="py-2.5 px-4 font-mono border-r border-slate-200 text-slate-900 font-bold">&ge; 24 KB SRAM</td>
                <td className="py-2.5 px-4 font-mono text-slate-900 font-bold">&ge; 32 KB SRAM</td>
              </tr>

              <tr>
                <td className="py-2.5 px-4 font-semibold text-slate-700 bg-slate-50 border-r border-slate-200">
                  Target Microcontroller Range
                </td>
                <td className="py-2.5 px-4 border-r border-slate-200">Cortex-M0 / Low-Memory IoT</td>
                <td className="py-2.5 px-4 border-r border-slate-200">Cortex-M4 / Standard Endpoints</td>
                <td className="py-2.5 px-4">Cortex-M7 / High-Perf Gateways</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Comparison Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {MLKEM_VARIANTS.map((spec) => (
          <VariantCard key={spec.variant} spec={spec} />
        ))}
      </div>

      {/* Technical Reference Note */}
      <Card className="p-5">
        <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-slate-700" /> NIST FIPS 203 Standard Overview
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed mb-4">
          NIST FIPS 203 specifies the Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM), derived from the CRYSTALS-Kyber algorithm.
          It provides quantum-resistant public-key encryption. On resource-constrained IoT microcontrollers, the primary implementation challenge
          is managing the stack memory required during Number Theoretic Transform (NTT) polynomial multiplication without triggering Out-Of-Memory (OOM) stack collisions.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded bg-stone-50 border border-slate-200">
            <span className="font-bold text-slate-900 font-mono block mb-1">ML-KEM-512</span>
            <span className="text-slate-600">Uses $2 \times 2$ module matrix ($k=2$). Operates reliably on 16 KB SRAM targets like STM32F0.</span>
          </div>
          <div className="p-3 rounded bg-stone-50 border border-slate-200">
            <span className="font-bold text-slate-900 font-mono block mb-1">ML-KEM-768</span>
            <span className="text-slate-600">Uses $3 \times 3$ module matrix ($k=3$). Recommended NIST default for general post-quantum security.</span>
          </div>
          <div className="p-3 rounded bg-stone-50 border border-slate-200">
            <span className="font-bold text-slate-900 font-mono block mb-1">ML-KEM-1024</span>
            <span className="text-slate-600">Uses $4 \times 4$ module matrix ($k=4$). Maximum security grade requiring high-end Cortex-M7/RISC-V targets.</span>
          </div>
        </div>
      </Card>
    </div>
  );
};
