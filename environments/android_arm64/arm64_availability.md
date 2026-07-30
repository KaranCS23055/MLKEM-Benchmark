# ARM64/AArch64 availability assessment

Assessment date: 2026-08-12.

## Result

No usable ARM64 execution environment is available in the current workspace.

## Evidence

- Host operating system architecture: AMD64.
- Python machine architecture: AMD64.
- Processor reported by the host: AMD Family 23 Model 96, AuthenticAMD.
- No qemu-aarch64 or qemu-system-aarch64 command is installed.
- The Windows Subsystem for Linux launcher is present, but WSL reports that no installation is configured.
- No ARM64 device, remote host, or ARM64 benchmark configuration was provided.

## Integrity decision

No ARM64 benchmark was run and no ARM64 data was created. Installing a large emulator or provisioned cloud system is outside this phase without a supplied environment or explicit authorization.

## Requirement to proceed

Provide access to a real ARM64 machine, such as a Raspberry Pi 4/5, ARM64 laptop, ARM server, or authorized ARM cloud VM. The project can then be copied to that environment, the pinned pqcrypto dependency installed in a local virtual environment, and the same native benchmark run with execution type NATIVE_SOFTWARE.
