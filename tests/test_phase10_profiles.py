"""Unit tests for Phase 10 Application Profile Loader."""

import unittest
from pathlib import Path
from mlkem_benchmark.profiles import load_application_profiles, ApplicationProfile


class TestPhase10Profiles(unittest.TestCase):
    def test_load_default_profiles(self):
        profiles = load_application_profiles()
        self.assertEqual(len(profiles), 6)
        profile_ids = {p.id for p in profiles}
        expected_ids = {
            "banking_finance",
            "iot_embedded",
            "cloud_datacenter",
            "mobile_edge",
            "healthcare_hipaa",
            "government_defense",
        }
        self.assertEqual(profile_ids, expected_ids)

    def test_profile_scale_bounds(self):
        profiles = load_application_profiles()
        for p in profiles:
            self.assertTrue(1 <= p.security_requirement <= 5)
            self.assertTrue(1 <= p.latency_sensitivity <= 5)
            self.assertTrue(1 <= p.throughput_importance <= 5)
            self.assertTrue(1 <= p.memory_constraint_level <= 5)
            self.assertTrue(1 <= p.compute_budget_level <= 5)
            self.assertIn(p.min_recommended_variant, {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"})


if __name__ == "__main__":
    unittest.main()
