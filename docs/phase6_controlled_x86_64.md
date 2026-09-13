# Phase 6 controlled x86-64 methodology

The controlled configuration runs the same native ML-KEM implementation on Windows x86-64 while limiting only the benchmark process to logical CPUs 0 and 1. The limit uses the Windows process-affinity API with mask 0x003.

The benchmark remains NATIVE_SOFTWARE: it executes directly on the host CPU and is neither emulated nor virtualized. It is a controlled native condition, not a separate physical device.

The runner reads the system affinity mask before applying the configured mask, rejects unsupported masks, and stores the requested mask, available mask, and controlled logical-CPU count in the metadata manifest. The setting exists only for the benchmark process, which terminates at the end of the run.

## Completed run

The canonical Phase 6 run used 100 iterations per variant/operation and produced 900 validated measurements. The manifest confirms that affinity control was applied with requested mask 0x3 and controlled logical-CPU count 2. All rows, including decapsulation verification rows, succeeded.
