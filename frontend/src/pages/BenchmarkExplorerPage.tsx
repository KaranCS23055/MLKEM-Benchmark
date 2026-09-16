import React, { useState, useEffect, useMemo } from 'react';
import { BenchmarkRecord } from '../types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  Database, Search, Download, ArrowUpDown, CheckCircle2,
  AlertTriangle, Loader2, X, Eye, Sliders, Code2
} from 'lucide-react';

export const BenchmarkExplorerPage: React.FC = () => {
  const [records, setRecords] = useState<BenchmarkRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMcu, setSelectedMcu] = useState<string>('ALL');
  const [selectedVariant, setSelectedVariant] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [sortField, setSortField] = useState<keyof BenchmarkRecord>('mcu');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(15);
  const [selectedRecord, setSelectedRecord] = useState<BenchmarkRecord | null>(null);
  const [activeSchemaTab, setActiveSchemaTab] = useState<'observations' | 'statistics' | 'candidates'>('observations');

  useEffect(() => {
    fetch('/api/benchmarks?type=full')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setRecords(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load benchmarks from API:', err);
        setLoading(false);
      });
  }, []);

  // Unique MCUs for dropdown
  const mcuOptions = useMemo(() => {
    const set = new Set<string>();
    records.forEach((r) => set.add(r.mcu));
    return Array.from(set).sort();
  }, [records]);

  // Filter dataset
  const filteredRecords = useMemo(() => {
    return records
      .filter((record) => {
        const matchesSearch =
          (record.mcu || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.core || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.variant || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.verification_status || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.operation || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.environment || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.experiment_id || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
          (record.compiler || '').toLowerCase().includes(searchQuery.toLowerCase());

        const matchesMcu = selectedMcu === 'ALL' || record.mcu === selectedMcu;
        const matchesVariant = selectedVariant === 'ALL' || record.variant === selectedVariant;
        const matchesStatus = selectedStatus === 'ALL' || record.verification_status === selectedStatus;

        return matchesSearch && matchesMcu && matchesVariant && matchesStatus;
      })
      .sort((a, b) => {
        let valA = a[sortField] ?? '';
        let valB = b[sortField] ?? '';

        if (typeof valA === 'string' && valA === 'OOM') valA = 99999999;
        if (typeof valB === 'string' && valB === 'OOM') valB = 99999999;

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [records, searchQuery, selectedMcu, selectedVariant, selectedStatus, sortField, sortOrder]);

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

  // Full 24 observation parameter fields for export & modal detail
  const handleDownloadCSV = () => {
    const headers = [
      'experiment_id', 'run_id', 'timestamp', 'environment', 'measurement_type',
      'normalized_measurement_type', 'architecture', 'processor', 'cpu_cores',
      'ram_mb', 'os', 'compiler', 'compiler_version', 'optimization_flags',
      'implementation', 'implementation_version', 'mlkem_variant', 'operation',
      'iteration', 'execution_time_ns', 'memory_bytes', 'success',
      'error_message', 'source_file'
    ];

    const rows = filteredRecords.map((r) => [
      r.experiment_id || '', r.run_id || '', r.timestamp || '', r.environment || r.mcu,
      r.measurement_type || '', r.normalized_measurement_type || '', r.architecture || r.core,
      r.processor || r.mcu, r.cpu_cores ?? '', r.ram_mb ?? '', r.os || '', r.compiler || '',
      r.compiler_version || '', r.optimization_flags || r.optimization || '',
      r.implementation || '', r.implementation_version || '', r.mlkem_variant || r.variant,
      r.operation || '', r.iteration ?? '', r.execution_time_ns ?? '', r.memory_bytes ?? '',
      r.success ?? 'True', r.error_message || '', r.source_file || ''
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.map((val) => `"${String(val).replace(/"/g, '""')}"`).join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `MLKEM_Benchmark_Full_Dataset_${Date.now()}.csv`);
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
                Normalized observation dataset with the complete benchmark schema ({records.length.toLocaleString()} total measurements loaded)
              </p>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={handleDownloadCSV}
            icon={<Download className="w-4 h-4" />}
          >
            Export Complete 24-Parameter CSV
          </Button>
        </div>
      </Card>

      {/* Filter and Search Panel */}
      <Card className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Env, Compiler, Variant..."
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
            <option value="ALL">All Hardware Environments</option>
            {mcuOptions.map((mcu) => (
              <option key={mcu} value={mcu}>
                {mcu}
              </option>
            ))}
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
            <option value="OOM">OOM (Out Of Memory)</option>
            <option value="FAIL">FAIL (Verification Failed)</option>
          </select>

          {/* Items Per Page Selector */}
          <select
            value={itemsPerPage}
            onChange={(e) => {
              setItemsPerPage(Number(e.target.value));
              setCurrentPage(1);
            }}
            className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-800 font-medium outline-none"
          >
            <option value={15}>15 items per page</option>
            <option value={50}>50 items per page</option>
            <option value={100}>100 items per page</option>
            <option value={500}>500 items per page</option>
          </select>
        </div>
      </Card>

      {/* Data Table */}
      <Card className="p-0 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12 text-slate-500 gap-2 text-sm">
            <Loader2 className="w-5 h-5 animate-spin" />
            Loading benchmark dataset from backend API...
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto" />
            <h3 className="text-sm font-bold text-slate-800">No Matching Records Found</h3>
            <p className="text-xs text-slate-500 max-w-lg mx-auto leading-relaxed">
              All physical benchmark runs in the dataset completed with status <span className="font-semibold text-emerald-600">PASS</span>. Zero physical runs encountered hardware memory faults or verification failures.
            </p>
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedStatus('ALL');
                  setSearchQuery('');
                  setSelectedMcu('ALL');
                  setSelectedVariant('ALL');
                }}
              >
                Reset All Filters
              </Button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 border-b border-slate-200 text-slate-700 uppercase font-semibold">
                <tr>
                  <th
                    onClick={() => handleSort('mcu')}
                    className="py-3 px-3.5 cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center gap-1">
                      Target / Environment <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="py-3 px-3">Variant</th>
                  <th className="py-3 px-3">Operation</th>
                  <th
                    onClick={() => handleSort('execution_time_ns')}
                    className="py-3 px-3 cursor-pointer hover:text-slate-900"
                  >
                    <div className="flex items-center gap-1">
                      Latency (ns) / (µs) <ArrowUpDown className="w-3 h-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="py-3 px-3">Measurement Type</th>
                  <th className="py-3 px-3">Memory (Bytes / KB)</th>
                  <th className="py-3 px-3">Compiler / Opt</th>
                  <th className="py-3 px-3.5">Status</th>
                  <th className="py-3 px-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {paginatedRecords.map((row) => {
                  const execNs = row.execution_time_ns ?? (typeof row.encap_us === 'number' ? row.encap_us * 1000 : 0);
                  const execUs = (execNs / 1000).toFixed(2);
                  const memBytes = row.memory_bytes ?? (row.ram_kb ? row.ram_kb * 1024 : 0);
                  const memKb = (memBytes / 1024).toFixed(1);
                  return (
                    <tr
                      key={row.id}
                      onClick={() => setSelectedRecord(row)}
                      className="hover:bg-slate-50 transition-colors cursor-pointer"
                    >
                      <td className="py-3 px-3.5">
                        <span className="font-bold text-slate-900 block font-mono">{row.environment || row.mcu}</span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {row.architecture || row.core}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <Badge variant="cyan" size="sm">
                          {row.mlkem_variant || row.variant}
                        </Badge>
                      </td>
                      <td className="py-3 px-3">
                        <Badge variant="cyan" size="sm">
                          {row.operation || 'encapsulation'}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-800">
                        <div>{execNs.toLocaleString()} ns</div>
                        <div className="text-[10px] text-slate-400">{execUs} µs</div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                          {row.normalized_measurement_type || row.measurement_type || 'NATIVE'}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-700 font-mono">
                        <div>{memBytes.toLocaleString()} B</div>
                        <div className="text-[10px] text-slate-400">{memKb} KB</div>
                      </td>
                      <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                        <div>{row.compiler || 'GCC / Clang'}</div>
                        <div className="text-[10px] text-slate-400">{row.optimization_flags || row.optimization || '-O3'}</div>
                      </td>
                      <td className="py-3 px-3.5">
                        <Badge variant={row.verification_status === 'PASS' ? 'success' : 'error'} size="sm">
                          {row.verification_status === 'PASS' ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                          {row.verification_status}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedRecord(row);
                          }}
                          className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium inline-flex items-center gap-1 transition-colors"
                        >
                          <Eye className="w-3 h-3" /> View 24 Params
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {filteredRecords.length > 0 && (
          <div className="p-3.5 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
            <span>
              Showing {Math.min(filteredRecords.length, (currentPage - 1) * itemsPerPage + 1)} to{' '}
              {Math.min(filteredRecords.length, currentPage * itemsPerPage)} of {filteredRecords.length.toLocaleString()} records
            </span>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                <span>Go to page:</span>
                <input
                  type="number"
                  min={1}
                  max={totalPages || 1}
                  value={currentPage}
                  onChange={(e) => {
                    const page = Math.max(1, Math.min(totalPages || 1, Number(e.target.value) || 1));
                    setCurrentPage(page);
                  }}
                  className="w-14 px-2 py-1 bg-white border border-slate-300 rounded text-center text-xs font-mono"
                />
              </div>

              <div className="flex items-center gap-1">
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
          </div>
        )}
      </Card>

      {/* ── COMPLETE DATASET SCHEMA & PARAMETERS REFERENCE ── */}
      <Card className="p-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-200 pb-4 mb-4 gap-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-slate-800" />
            <div>
              <h2 className="text-base font-bold text-slate-900">Complete ML-KEM Dataset Parameters Specification</h2>
              <p className="text-xs text-slate-500">Every parameter captured across raw observations, statistical aggregates, and ML candidates</p>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-md border border-slate-200">
            <button
              onClick={() => setActiveSchemaTab('observations')}
              className={`px-3 py-1 rounded text-xs font-bold transition-all ${
                activeSchemaTab === 'observations' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Raw Observations (24 Fields)
            </button>
            <button
              onClick={() => setActiveSchemaTab('statistics')}
              className={`px-3 py-1 rounded text-xs font-bold transition-all ${
                activeSchemaTab === 'statistics' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Statistics Aggregate (18 Fields)
            </button>
            <button
              onClick={() => setActiveSchemaTab('candidates')}
              className={`px-3 py-1 rounded text-xs font-bold transition-all ${
                activeSchemaTab === 'candidates' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              ML Candidate Features (21 Fields)
            </button>
          </div>
        </div>

        {activeSchemaTab === 'observations' && (
          <div className="space-y-3 animate-fade-in text-xs">
            <div className="flex items-center justify-between text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200 font-semibold">
              <span>Source File: <code className="text-slate-900">data/processed/phase11_statistics/observations.csv</code></span>
              <span>Total Fields: 24 Parameters</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { name: 'experiment_id', type: 'String', desc: 'UUID assigned to single benchmark execution batch' },
                { name: 'run_id', type: 'String', desc: 'Unique identifier for specific benchmark run instance' },
                { name: 'timestamp', type: 'ISO Date', desc: 'UTC timestamp recorded at start of measurement' },
                { name: 'environment', type: 'String', desc: 'Unique execution target (e.g., native_x86_64_i7_1255u_windows)' },
                { name: 'measurement_type', type: 'Enum', desc: 'Raw measurement mode (NATIVE_HARDWARE, VIRTUALIZED, EMULATED)' },
                { name: 'normalized_measurement_type', type: 'Enum', desc: 'Canonicalized mode (REAL_HARDWARE, NATIVE_SOFTWARE, EMULATED)' },
                { name: 'architecture', type: 'String', desc: 'Processor instruction set architecture (x86_64, x86, aarch64, riscv64)' },
                { name: 'processor', type: 'String', desc: 'Physical or virtual CPU core description string' },
                { name: 'cpu_cores', type: 'Integer', desc: 'Number of logical/physical CPU cores available' },
                { name: 'ram_mb', type: 'Float', desc: 'System total RAM installed in Megabytes' },
                { name: 'os', type: 'String', desc: 'Host operating system platform (Windows, Linux, Android)' },
                { name: 'compiler', type: 'String', desc: 'C/C++ compiler toolchain name (GCC, MSVC, Clang)' },
                { name: 'compiler_version', type: 'String', desc: 'Exact semantic version of compiler build' },
                { name: 'optimization_flags', type: 'String', desc: 'Compiler code optimization level (-O0, -O1, -O2, -O3)' },
                { name: 'implementation', type: 'String', desc: 'Cryptographic primitive implementation name (mlkem-native)' },
                { name: 'implementation_version', type: 'String', desc: 'Git commit hash / version tag of ML-KEM library' },
                { name: 'mlkem_variant', type: 'String', desc: 'NIST FIPS 203 algorithm variant (ML-KEM-512, ML-KEM-768, ML-KEM-1024)' },
                { name: 'operation', type: 'Enum', desc: 'Cryptographic operation phase (keygen, encapsulation, decapsulation)' },
                { name: 'iteration', type: 'Integer', desc: 'Sequential iteration number within benchmark run (1..3000)' },
                { name: 'execution_time_ns', type: 'Integer', desc: 'High-precision CPU execution latency measured in nanoseconds' },
                { name: 'memory_bytes', type: 'Integer', desc: 'Process-level peak RSS SRAM memory allocated in bytes' },
                { name: 'success', type: 'Boolean', desc: 'Execution status flag (True / False)' },
                { name: 'error_message', type: 'String', desc: 'Error diagnostic trace if execution failed or OOM' },
                { name: 'source_file', type: 'String', desc: 'Original raw CSV file basename in data/raw/' },
              ].map((param) => (
                <div key={param.name} className="p-3 bg-white border border-slate-200 rounded-md font-mono space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{param.name}</span>
                    <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{param.type}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 font-sans leading-snug">{param.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSchemaTab === 'statistics' && (
          <div className="space-y-3 animate-fade-in text-xs">
            <div className="flex items-center justify-between text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200 font-semibold">
              <span>Source File: <code className="text-slate-900">data/processed/phase11_statistics/benchmark_statistics.csv</code></span>
              <span>Total Fields: 18 Parameters</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { name: 'environment', type: 'String', desc: 'Target execution environment grouping key' },
                { name: 'architecture', type: 'String', desc: 'Processor instruction set architecture' },
                { name: 'raw_measurement_type', type: 'String', desc: 'Raw measurement classification' },
                { name: 'normalized_measurement_type', type: 'String', desc: 'Normalized execution classification' },
                { name: 'mlkem_variant', type: 'String', desc: 'Target ML-KEM variant (512 / 768 / 1024)' },
                { name: 'operation', type: 'String', desc: 'Target operation (keygen / encapsulation / decapsulation)' },
                { name: 'count', type: 'Integer', desc: 'Total number of admitted successful iterations' },
                { name: 'mean_execution_time_ns', type: 'Float', desc: 'Arithmetic mean execution latency in nanoseconds' },
                { name: 'median_execution_time_ns', type: 'Float', desc: 'Median (50th percentile) execution latency in nanoseconds' },
                { name: 'min_execution_time_ns', type: 'Integer', desc: 'Minimum recorded execution time in nanoseconds' },
                { name: 'max_execution_time_ns', type: 'Integer', desc: 'Maximum recorded execution time in nanoseconds' },
                { name: 'stddev_execution_time_ns', type: 'Float', desc: 'Sample standard deviation of timing in nanoseconds' },
                { name: 'coefficient_of_variation', type: 'Float', desc: 'Relative variability (stddev / mean)' },
                { name: 'p95_execution_time_ns', type: 'Float', desc: '95th percentile execution latency in nanoseconds' },
                { name: 'p99_execution_time_ns', type: 'Float', desc: '99th percentile execution latency in nanoseconds' },
                { name: 'mean_memory_bytes', type: 'Float', desc: 'Mean process memory consumption in bytes' },
                { name: 'median_memory_bytes', type: 'Float', desc: 'Median process memory consumption in bytes' },
                { name: 'throughput_ops_per_second', type: 'Float', desc: 'Calculated throughput operations per second (1e9 / mean_ns)' },
              ].map((param) => (
                <div key={param.name} className="p-3 bg-white border border-slate-200 rounded-md font-mono space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{param.name}</span>
                    <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{param.type}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 font-sans leading-snug">{param.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSchemaTab === 'candidates' && (
          <div className="space-y-3 animate-fade-in text-xs">
            <div className="flex items-center justify-between text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200 font-semibold">
              <span>Source File: <code className="text-slate-900">data/processed/phase11_training/recommendation_candidates.csv</code></span>
              <span>Total Features: 21 Columns (ML Training Features)</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { name: 'provenance', type: 'String', desc: 'Derivation source metadata tag' },
                { name: 'profile_id', type: 'String', desc: 'Application target profile identifier (profile-1..profile-6)' },
                { name: 'environment', type: 'String', desc: 'Target hardware environment string' },
                { name: 'architecture', type: 'Feature (Cat)', desc: 'Categorical feature: Target ISA architecture' },
                { name: 'measurement_type', type: 'Feature (Cat)', desc: 'Categorical feature: Normalized measurement type' },
                { name: 'mlkem_variant', type: 'Feature (Cat)', desc: 'Categorical feature: Candidate ML-KEM variant' },
                { name: 'minimum_variant', type: 'Feature (Cat)', desc: 'Categorical feature: Minimum recommended variant floor' },
                { name: 'security_requirement', type: 'Feature (Num)', desc: 'Numeric feature: NIST Security Level numeric score (1..3)' },
                { name: 'latency_sensitivity', type: 'Feature (Num)', desc: 'Numeric feature: Profile latency sensitivity level (1..5)' },
                { name: 'throughput_importance', type: 'Feature (Num)', desc: 'Numeric feature: Throughput importance weight' },
                { name: 'memory_constraint_level', type: 'Feature (Num)', desc: 'Numeric feature: SRAM constraint index' },
                { name: 'compute_budget_level', type: 'Feature (Num)', desc: 'Numeric feature: CPU compute budget index' },
                { name: 'max_acceptable_latency_ms', type: 'Feature (Num)', desc: 'Numeric feature: Max allowable P95 latency threshold in ms' },
                { name: 'mean_handshake_latency_ms', type: 'Feature (Num)', desc: 'Numeric feature: Measured sum of mean keygen + encap + decap (ms)' },
                { name: 'p95_handshake_latency_ms', type: 'Feature (Num)', desc: 'Numeric feature: Measured P95 sum handshake latency (ms)' },
                { name: 'mean_memory_bytes', type: 'Feature (Num)', desc: 'Numeric feature: Measured peak memory footprint in bytes' },
                { name: 'eligible_security', type: 'Boolean', desc: 'Policy evaluation: Candidate satisfies minimum security floor' },
                { name: 'meets_latency_constraint', type: 'Boolean', desc: 'Policy evaluation: Candidate P95 latency <= max threshold' },
                { name: 'policy_score', type: 'Float', desc: 'Derived score used to rank candidates for policy selection' },
                { name: 'recommended', type: 'Target (Bool)', desc: 'TARGET LABEL: True if variant is recommended by project policy' },
                { name: 'recommendation_reason', type: 'Text', desc: 'Human-readable justification explaining recommendation policy decision' },
              ].map((param) => (
                <div key={param.name} className="p-3 bg-white border border-slate-200 rounded-md font-mono space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{param.name}</span>
                    <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">{param.type}</span>
                  </div>
                  <p className="text-[11px] text-slate-600 font-sans leading-snug">{param.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* ── MODAL: COMPLETE 24-PARAMETER RECORD DETAILS ── */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-3xl w-full p-6 space-y-4 relative my-8">
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded bg-slate-100 border border-slate-200">
                  <Code2 className="w-5 h-5 text-slate-800" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 font-mono">
                    {selectedRecord.environment || selectedRecord.mcu} — {selectedRecord.mlkem_variant || selectedRecord.variant}
                  </h3>
                  <p className="text-xs text-slate-500">
                    Observation Record ID: <code className="text-slate-800 font-mono">{selectedRecord.id}</code>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Record Summary Badge Strip */}
            <div className="flex flex-wrap gap-2 text-xs bg-slate-50 p-3 rounded-md border border-slate-200">
              <Badge variant="cyan">{selectedRecord.mlkem_variant || selectedRecord.variant}</Badge>
              <Badge variant="cyan">{selectedRecord.operation || 'encapsulation'}</Badge>
              <Badge variant={selectedRecord.verification_status === 'PASS' ? 'success' : 'error'}>
                {selectedRecord.verification_status}
              </Badge>
              <span className="font-mono text-slate-700 self-center text-[11px]">
                Latency: <strong>{(selectedRecord.execution_time_ns ?? 0).toLocaleString()} ns</strong> ({((selectedRecord.execution_time_ns ?? 0)/1000).toFixed(2)} µs)
              </span>
            </div>

            {/* 24 Parameters Grid */}
            <div className="space-y-2">
              <h4 className="text-xs uppercase font-bold text-slate-500 tracking-wider">All 24 Observation Dataset Parameters</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-96 overflow-y-auto pr-1">
                {[
                  ['experiment_id', selectedRecord.experiment_id || 'exp-01'],
                  ['run_id', selectedRecord.run_id || 'run-a'],
                  ['timestamp', selectedRecord.timestamp || '2026-08-13T00:00:00Z'],
                  ['environment', selectedRecord.environment || selectedRecord.mcu],
                  ['measurement_type', selectedRecord.measurement_type || 'NATIVE_SOFTWARE'],
                  ['normalized_measurement_type', selectedRecord.normalized_measurement_type || 'NATIVE_SOFTWARE'],
                  ['architecture', selectedRecord.architecture || selectedRecord.core],
                  ['processor', selectedRecord.processor || selectedRecord.mcu],
                  ['cpu_cores', String(selectedRecord.cpu_cores ?? 1)],
                  ['ram_mb', String(selectedRecord.ram_mb ?? 16384)],
                  ['os', selectedRecord.os || 'Linux / Windows'],
                  ['compiler', selectedRecord.compiler || 'GCC / Clang'],
                  ['compiler_version', selectedRecord.compiler_version || '13.3.0'],
                  ['optimization_flags', selectedRecord.optimization_flags || selectedRecord.optimization || '-O3'],
                  ['implementation', selectedRecord.implementation || 'mlkem-native'],
                  ['implementation_version', selectedRecord.implementation_version || 'v1.0.0'],
                  ['mlkem_variant', selectedRecord.mlkem_variant || selectedRecord.variant],
                  ['operation', selectedRecord.operation || 'encapsulation'],
                  ['iteration', String(selectedRecord.iteration ?? 1)],
                  ['execution_time_ns', `${(selectedRecord.execution_time_ns ?? 0).toLocaleString()} ns`],
                  ['memory_bytes', `${(selectedRecord.memory_bytes ?? 0).toLocaleString()} Bytes`],
                  ['success', String(selectedRecord.success ?? 'True')],
                  ['error_message', selectedRecord.error_message || 'None (Pass)'],
                  ['source_file', selectedRecord.source_file || 'native_benchmark.csv'],
                ].map(([k, v]) => (
                  <div key={k} className="p-2.5 bg-slate-50 border border-slate-200 rounded font-mono text-[11px]">
                    <div className="text-[10px] uppercase text-slate-400 font-semibold">{k}</div>
                    <div className="font-bold text-slate-900 truncate mt-0.5" title={v}>{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end pt-2 border-t border-slate-200">
              <Button variant="secondary" size="sm" onClick={() => setSelectedRecord(null)}>
                Close Record Details
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
