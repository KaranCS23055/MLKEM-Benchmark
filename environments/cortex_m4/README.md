# Cortex-M4 Renode harness

This harness runs the unchanged `mlkem-native` v1.2.0 source on Renode's
STM32F4 Discovery (Cortex-M4) model. It uses the portable C backend because
mlkem-native has no Cortex-M4-specific arithmetic backend.

The harness is a functional integration test for KeyGen, Encapsulation, and
Decapsulation and verifies the two shared secrets. Renode's STM32F4 model
does not implement the Cortex-M DWT cycle counter, so it cannot produce timing
measurements. The `0x20000000` marker is `0x4D4C4B50` (`MLKP`) only after a
successful verification; `0x4D4C4B46` (`MLKF`) indicates failure. This is
functional coverage, not timing data or a claim about a physical STM32F4.

The deterministic `notrandombytes` source is **test-only**. It is used solely
to make the emulator run repeatable and must never be used in a deployed
cryptographic system.
