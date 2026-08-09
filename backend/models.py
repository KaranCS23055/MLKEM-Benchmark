from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class RecommendationFormInputs(BaseModel):
    mcu: Optional[str] = "STM32F407VGT6"
    frequency: int = Field(..., description="Clock frequency in MHz", ge=8, le=1000)
    ram: int = Field(..., description="SRAM capacity in KB", ge=1)
    flash: Optional[int] = Field(default=1024, description="Flash capacity in KB")
    securityLevel: Literal["Level 1", "Level 3", "Level 5"]
    optimization: Literal["O0", "O1", "O2", "O3"]
    cpuLoad: int = Field(..., description="CPU load percentage (0-75)", ge=0, le=100)
    latencyBudget: int = Field(..., description="Max latency budget in us", ge=100)

class ComparisonBadge(BaseModel):
    label: str
    value: str
    type: Literal["success", "warning", "info", "error"]

class RecommendationResult(BaseModel):
    recommendedVariant: Literal["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "UNSUPPORTED"]
    confidence: float
    reason: str
    estimatedKeygenUs: int
    estimatedEncapUs: int
    estimatedDecapUs: int
    estimatedRamKb: int
    ramUtilizationPercent: int
    latencyCompliance: Literal["EXCELLENT", "COMPLIANT", "WARNING", "EXCEEDED"]
    comparisonBadges: List[ComparisonBadge]

class BenchmarkRecord(BaseModel):
    mcu: str
    core: str
    clock_mhz: int
    flash_kb: int
    ram_kb: int
    variant: str
    keygen_cycles: Union[int, str]
    encap_cycles: Union[int, str]
    decap_cycles: Union[int, str]
    keygen_us: Union[float, int, str]
    encap_us: Union[float, int, str]
    decap_us: Union[float, int, str]
    verification_status: Literal["PASS", "OOM", "FAIL"]

class ProcessorProfile(BaseModel):
    mcu: str
    name: str
    core: str
    architecture: str
    frequency: int
    ram: int
    flash: int
    voltage: str
    supportedVariants: List[str]
    description: str
    features: List[str]

class HealthCheck(BaseModel):
    status: str
    version: str
