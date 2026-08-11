import React, { useState, useMemo } from 'react';
import { BENCHMARK_DATASET } from '../data/mockData';
import { BenchmarkRecord } from '../types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Database, Search, Download, ArrowUpDown, CheckCircle2, AlertTriangle } from 'lucide-react';

export const BenchmarkExplorerPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMcu, setSelectedMcu] = useState<string>('ALL');
  const [selectedVariant, setSelectedVariant] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [sortField, setSortField] = useState<keyof BenchmarkRecord>('mcu');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filter dataset
  const filteredRecords = useMemo(() => {
    return BENCHMARK_DATASET.filter((record) => {
      const matchesSearch =
        record.mcu.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.core.toLowerCase().includes(searchQuery.toLowerCase()) ||
        record.variant.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesMcu = selectedMcu === 'ALL' || record.mcu === selectedMcu;
      const matchesVariant = selectedVariant === 'ALL' || record.variant === selectedVariant;
      const matchesStatus = selectedStatus === 'ALL' || record.verification_status === selectedStatus;

      return matchesSearch && matchesMcu && matchesVariant && matchesStatus;
    }).sort((a, b) => {
      let valA = a[sortField] ?? '';
      let valB = b[sortField] ?? '';

      if (typeof valA === 'string' && valA === 'OOM') valA = 99999999;
      if (typeof valB === 'string' && valB === 'OOM') valB = 99999999;

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [searchQuery, selectedMcu, selectedVariant, selectedStatus, sortField, sortOrder]);

  // Paginated records
  const paginatedRecords = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredRecords.slice(start, start + itemsPerPage);
  }, [filteredRecords, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredRecords.length / itemsPerPage);

  const handleSort = (field: keyof BenchmarkRecord) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  // CSV Export handler
  const handleDownloadCSV = () => {
    const headers = [
      'mcu',
      'core',
      'clock_mhz',
      'flash_kb',
      'ram_kb',
      'variant',
      'keygen_us',
      'encap_us',
      'decap_us',
      'verification_status',
    ];
    const rows = filteredRecords.map((r) => [
      r.mcu,
      r.core,
      r.clock_mhz,
      r.flash_kb,
      r.ram_kb,
      r.variant,
      r.keygen_us,
      r.encap_us,
      r.decap_us,
      r.verification_status,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `MLKEM_Benchmark_Dataset_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Banner */}
      <Card className="p-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Empirical Benchmark Data Explorer</h1>
              <p className="text-xs text-slate-500">
                Search, filter, and inspect physical microsecond execution latencies, clock cycles, and SRAM bounds
              </p>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={handleDownloadCSV}
            icon={<Download className="w-4 h-4" />}
          >
            Export CSV Dataset
          </Button>
        </div>
      </Card>

      {/* Filter and Search Panel */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Search input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search MCU, Core, Variant..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-9 pr-3 py-1.5 bg-white border border-slate-300 rounded-md text-xs text-slate-900 placeholder-slate-400 focus:border-slate-800 outline-none"
            />
          </div>

          {/* MCU Filter */}
          <select
            value={selectedMcu}
            onChange={(e) => {
              setSelectedMcu(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-800 font-medium outline-none"
          >
            <option value="ALL">All Microcontrollers</option>
            <option value="STM32F072RBT6">STM32F072RBT6 (Cortex-M0)</option>
            <option value="STM32F407VGT6">STM32F407VGT6 (Cortex-M4)</option>
            <option value="STM32H753ZIT6">STM32H753ZIT6 (Cortex-M7)</option>
            <option value="nRF52840">nRF52840 (Cortex-M4)</option>
            <option value="HiFive1">HiFive1 (RISC-V)</option>
          </select>

          {/* Variant Filter */}
          <select
            value={selectedVariant}
            onChange={(e) => {
              setSelectedVariant(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-800 font-medium outline-none"
          >
            <option value="ALL">All ML-KEM Variants</option>
            <option value="ML-KEM-512">ML-KEM-512 (Level 1)</option>
            <option value="ML-KEM-768">ML-KEM-768 (Level 3)</option>
            <option value="ML-KEM-1024">ML-KEM-1024 (Level 5)</option>
          </select>

          {/* Verification Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => {
              setSelectedStatus(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-800 font-medium outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="PASS">PASS (Execution Success)</option>
            <option value="OOM">OOM (Out-Of-Memory)</option>
          </select>
        </div>
      </Card>

      {/* Data Table */}
      <Card className="p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 uppercase font-semibold">
              <tr>
                <th
                  onClick={() => handleSort('mcu')}
                  className="py-3 px-3.5 cursor-pointer hover:text-slate-900"
                >
                  <div className="flex items-center gap-1">
                    Processor <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3 px-3">Variant</th>
                <th
                  onClick={() => handleSort('keygen_us')}
                  className="py-3 px-3 cursor-pointer hover:text-slate-900"
                >
                  <div className="flex items-center gap-1">
                    KeyGen <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('encap_us')}
                  className="py-3 px-3 cursor-pointer hover:text-slate-900"
                >
                  <div className="flex items-center gap-1">
                    Encapsulation <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => handleSort('decap_us')}
                  className="py-3 px-3 cursor-pointer hover:text-slate-900"
                >
                  <div className="flex items-center gap-1">
                    Decapsulation <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3 px-3">SRAM</th>
                <th className="py-3 px-3">Flash</th>
                <th className="py-3 px-3">CPU Cycles</th>
                <th className="py-3 px-3">Energy (µJ)</th>
                <th className="py-3 px-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {paginatedRecords.map((row) => (
                <tr key={row.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3.5">
                    <span className="font-bold text-slate-900 block font-mono">{row.mcu}</span>
                    <span className="text-[10px] text-slate-500">
                      {row.core} @ {row.clock_mhz} MHz
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <Badge variant="cyan" size="sm">
                      {row.variant}
                    </Badge>
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-800">
                    {row.keygen_us === 'OOM' ? (
                      <span className="text-rose-700 font-bold">OOM</span>
                    ) : (
                      `${row.keygen_us.toLocaleString()} µs`
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-800">
                    {row.encap_us === 'OOM' ? (
                      <span className="text-rose-700 font-bold">OOM</span>
                    ) : (
                      `${row.encap_us.toLocaleString()} µs`
                    )}
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-800">
                    {row.decap_us === 'OOM' ? (
                      <span className="text-rose-700 font-bold">OOM</span>
                    ) : (
                      `${row.decap_us.toLocaleString()} µs`
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-700 font-mono">{row.ram_kb} KB</td>
                  <td className="py-3 px-3 text-slate-600 font-mono">{row.flash_kb} KB</td>
                  <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                    {row.encap_cycles === 'OOM' ? 'OOM' : row.encap_cycles.toLocaleString()}
                  </td>
                  <td className="py-3 px-3 text-slate-800 font-mono font-medium">
                    {row.energy_uj ? `${row.energy_uj} µJ` : '-'}
                  </td>
                  <td className="py-3 px-3.5">
                    <Badge variant={row.verification_status === 'PASS' ? 'success' : 'error'} size="sm">
                      {row.verification_status === 'PASS' ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                      {row.verification_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <span>
            Showing {Math.min(filteredRecords.length, (currentPage - 1) * itemsPerPage + 1)} to{' '}
            {Math.min(filteredRecords.length, currentPage * itemsPerPage)} of {filteredRecords.length} records
          </span>

          <div className="flex items-center gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1 rounded bg-white border border-slate-300 text-slate-700 disabled:opacity-40 cursor-pointer hover:bg-slate-50"
            >
              Previous
            </button>
            <span className="font-semibold text-slate-800 px-2">
              Page {currentPage} of {totalPages || 1}
            </span>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1 rounded bg-white border border-slate-300 text-slate-700 disabled:opacity-40 cursor-pointer hover:bg-slate-50"
            >
              Next
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
};
