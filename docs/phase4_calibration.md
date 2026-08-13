# Phase 4 calibration decision

## Input

Calibration used only the validated native x86-64 raw CSV with 900 successful measurements: 100 iterations for each combination of three ML-KEM variants and three operations. The earlier CSV with missing memory values was not used.

## Method

For each variant/operation group, the analysis calculates the sample standard deviation, coefficient of variation (CV), relative standard error, and Tukey 1.5-IQR outlier count. It estimates a future sample size for the mean using:

n = ceil((1.96 * CV / 0.05)^2)

This is a normal-approximation planning estimate for a two-sided 95% confidence interval with a relative margin of 5%. It does not remove, alter, or hide outliers.

## Decision

The largest estimate is 978 iterations for ML-KEM-512 KeyGen, whose observed CV is approximately 0.798. The next native experiment should therefore use 1,000 iterations for every configuration.

The higher variation is visible in ML-KEM-512 KeyGen: its maximum was 1,586,400 ns while its median was 160,600 ns. This likely reflects normal operating-system scheduling or runtime noise, but the project does not assume a cause without controlled experimentation. All measurements remain included.

## Scope

This calibration decision applies only to the current native Windows x86-64 setup and pinned pqcrypto implementation. A new environment or implementation requires a separate 100-iteration calibration before it is scaled.
