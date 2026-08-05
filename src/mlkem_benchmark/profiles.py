"""Application profile loader and validator for Phase 10."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApplicationProfile:
    id: str
    name: str
    category: str
    description: str
    security_requirement: int  # 1-5 scale
    latency_sensitivity: int   # 1-5 scale
    throughput_importance: int # 1-5 scale
    memory_constraint_level: int # 1-5 scale
    compute_budget_level: int    # 1-5 scale
    max_acceptable_latency_ms: float
    min_recommended_variant: str

    def validate(self) -> None:
        for field_name in [
            "security_requirement",
            "latency_sensitivity",
            "throughput_importance",
            "memory_constraint_level",
            "compute_budget_level",
        ]:
            val = getattr(self, field_name)
            if not isinstance(val, int) or not (1 <= val <= 5):
                raise ValueError(f"Profile {self.id}: {field_name} must be integer between 1 and 5 (got {val})")

        if self.max_acceptable_latency_ms <= 0:
            raise ValueError(f"Profile {self.id}: max_acceptable_latency_ms must be positive")

        if self.min_recommended_variant not in {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"}:
            raise ValueError(f"Profile {self.id}: invalid min_recommended_variant {self.min_recommended_variant}")


def load_application_profiles(config_path: Path | None = None) -> list[ApplicationProfile]:
    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "configs" / "application_profiles.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Application profiles config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    profiles = []
    for raw in data.get("profiles", []):
        prof = ApplicationProfile(
            id=raw["id"],
            name=raw["name"],
            category=raw["category"],
            description=raw["description"],
            security_requirement=int(raw["security_requirement"]),
            latency_sensitivity=int(raw["latency_sensitivity"]),
            throughput_importance=int(raw["throughput_importance"]),
            memory_constraint_level=int(raw["memory_constraint_level"]),
            compute_budget_level=int(raw["compute_budget_level"]),
            max_acceptable_latency_ms=float(raw["max_acceptable_latency_ms"]),
            min_recommended_variant=raw["min_recommended_variant"],
        )
        prof.validate()
        profiles.append(prof)

    return profiles
