import React from 'react';
import {
  LayoutDashboard,
  BrainCircuit,
  Database,
  BarChart3,
  Cpu,
  Layers,
  Info,
  Settings,
  Shield,
} from 'lucide-react';

export type PageId =
  | 'dashboard'
  | 'recommendation'
  | 'benchmarks'
  | 'analytics'
  | 'processors'
  | 'variants'
  | 'about'
  | 'settings';

interface SidebarProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  isOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onNavigate,
  isOpen,
  onCloseMobile,
}) => {
  const navItems = [
    { id: 'dashboard' as PageId, label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'benchmarks' as PageId, label: 'Benchmark Explorer', icon: <Database className="w-4 h-4" /> },
    { id: 'analytics' as PageId, label: 'Analytics & Graphs', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'recommendation' as PageId, label: 'AI Recommendation (UI)', icon: <BrainCircuit className="w-4 h-4 text-amber-400" /> },
    { id: 'processors' as PageId, label: 'Processors', icon: <Cpu className="w-4 h-4" /> },
    { id: 'variants' as PageId, label: 'ML-KEM Variants', icon: <Layers className="w-4 h-4" /> },
    { id: 'about' as PageId, label: 'About Project', icon: <Info className="w-4 h-4" /> },
    { id: 'settings' as PageId, label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-40 lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 h-screen overflow-hidden
          w-64 bg-[#17324D] text-slate-200 border-r border-[#28506F]
          flex flex-col justify-between transition-transform duration-200 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Brand Header */}
        <div>
          <div className="p-5 border-b border-[#28506F] flex items-center gap-3">
            <div className="p-2 rounded bg-[#244A68] border border-[#3A6688] text-white">
              <Shield className="w-5 h-5 text-cyan-300" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight font-mono">
                ML-KEM BENCHMARK
              </h1>
              <p className="text-[11px] text-sky-200/70">Post-Quantum IoT Lab</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1">
              <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-sky-200/70 tracking-wider">
              Research Console
            </div>
            {navItems.map((item) => {
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    onCloseMobile();
                  }}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium
                    transition-colors duration-150 cursor-pointer
                    ${
                      isActive
                        ? 'bg-[#2A607D] text-white font-semibold border-l-2 border-cyan-300'
                        : 'text-sky-100/70 hover:text-white hover:bg-[#244A68]'
                    }
                  `}
                >
                  <span className={isActive ? 'text-cyan-300' : 'text-sky-200/70'}>
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Academic Tag */}
        <div className="p-3 m-3 rounded bg-[#244A68]/70 border border-[#28506F] text-xs">
          <div className="flex items-center gap-2 mb-1 text-sky-100 font-medium text-[11px]">
            <span className="w-2 h-2 rounded-full bg-lime-300" />
            Renode Simulation Pipeline
          </div>
          <p className="text-[10px] text-sky-100/65 leading-snug">
            NIST FIPS 203 Cryptographic Benchmarking Suite
          </p>
        </div>
      </aside>
    </>
  );
};
