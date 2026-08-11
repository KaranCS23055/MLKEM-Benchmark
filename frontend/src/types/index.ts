export type SecurityLevel = 'Level 1' | 'Level 3' | 'Level 5';
export type OptimizationLevel = 'O0' | 'O1' | 'O2' | 'O3';
export type MLKEMVariant = 'ML-KEM-512' | 'ML-KEM-768' | 'ML-KEM-1024';

export interface BenchmarkRecord {
  id: string;
  mcu: string;
  core: string;
  clock_mhz: number;
  flash_kb: number;
  ram_kb: number;
  latency_budget_us?: number;
  variant: MLKEMVariant;
  keygen_cycles: number | 'OOM';
  encap_cycles: number | 'OOM';
  decap_cycles: number | 'OOM';
  keygen_us: number | 'OOM';
  encap_us: number | 'OOM';
  decap_us: number | 'OOM';
  keygen_stddev_us?: number;
  encap_stddev_us?: number;
  decap_stddev_us?: number;
  energy_uj?: number; // Estimated microjoules
  optimization?: OptimizationLevel;
  verification_status: 'PASS' | 'OOM' | 'FAIL';
  recommended_variant?: string;
}

export interface ProcessorProfile {
  mcu: string;
  name: string;
  core: string;
  architecture: 'ARM Cortex-M' | 'RISC-V' | 'Xtensa';
  frequency: number; // MHz
  ram: number; // KB
  flash: number; // KB
  voltage: string;
  supportedVariants: MLKEMVariant[];
  description: string;
  features: string[];
}

export interface MLKEMVariantSpec {
  variant: MLKEMVariant;
  claimedNistLevel: SecurityLevel;
  securityBits: number;
  publicKeySize: number; // Bytes
  secretKeySize: number; // Bytes
  ciphertextSize: number; // Bytes
  minRamRequirement: number; // KB
  performanceRating: 'High' | 'Medium' | 'Maximum Security';
  memoryUsageRating: 'Compact' | 'Moderate' | 'Heavy';
  recommendedUseCases: string[];
}

export interface RecommendationFormInputs {
  mcu: string;
  frequency: number; // MHz
  ram: number; // KB
  flash: number; // KB
  securityLevel: SecurityLevel;
  optimization: OptimizationLevel;
  cpuLoad: number; // Percentage 0-75%
  latencyBudget: number; // us
}

export interface RecommendationResult {
  recommendedVariant: MLKEMVariant | 'UNSUPPORTED';
  confidence: number; // Percentage, e.g. 96
  reason: string;
  estimatedKeygenUs: number;
  estimatedEncapUs: number;
  estimatedDecapUs: number;
  estimatedRamKb: number;
  ramUtilizationPercent: number;
  latencyCompliance: 'EXCELLENT' | 'COMPLIANT' | 'WARNING' | 'EXCEEDED';
  comparisonBadges: {
    label: string;
    value: string;
    type: 'success' | 'warning' | 'info' | 'error';
  }[];
}

export interface DashboardStats {
  totalBenchmarks: number;
  processorsSupported: number;
  mlkemVariantsCount: number;
  avgExecutionTimeUs: number;
  aiAccuracyPercent: number;
  totalPasses: number;
  totalOOMs: number;
}
