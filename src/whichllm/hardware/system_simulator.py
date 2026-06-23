"""Create synthetic HardwareInfo for full system simulation.

This module allows users to simulate CPU, RAM, disk, and OS specifications
for testing and planning purposes without requiring actual hardware.
"""

from __future__ import annotations

import logging
import platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from whichllm.hardware.types import GPUInfo

from whichllm.hardware.types import HardwareInfo

logger = logging.getLogger(__name__)

# Common CPU presets with typical core counts
_CPU_PRESETS: dict[str, int] = {
    # Intel CPUs
    "i3-10100": 4,
    "i3-12100": 4,
    "i5-10400": 6,
    "i5-12400": 6,
    "i5-13600K": 14,
    "i7-10700K": 8,
    "i7-12700K": 12,
    "i7-13700K": 16,
    "i9-10900K": 10,
    "i9-12900K": 16,
    "i9-13900K": 24,
    "i9-14900K": 24,
    # AMD Ryzen CPUs
    "Ryzen 3 3100": 4,
    "Ryzen 3 5300G": 4,
    "Ryzen 5 3600": 6,
    "Ryzen 5 5600X": 6,
    "Ryzen 5 7600X": 6,
    "Ryzen 7 3700X": 8,
    "Ryzen 7 5700X": 8,
    "Ryzen 7 5800X3D": 8,
    "Ryzen 7 7700X": 8,
    "Ryzen 9 3900X": 12,
    "Ryzen 9 5900X": 12,
    "Ryzen 9 5950X": 16,
    "Ryzen 9 7900X": 12,
    "Ryzen 9 7950X": 16,
    "Ryzen 9 7950X3D": 16,
    # Threadripper
    "Threadripper 3960X": 24,
    "Threadripper 3970X": 32,
    "Threadripper 3990X": 64,
    # Apple Silicon
    "Apple M1": 8,
    "Apple M1 Pro": 10,
    "Apple M1 Max": 10,
    "Apple M1 Ultra": 20,
    "Apple M2": 8,
    "Apple M2 Pro": 10,
    "Apple M2 Max": 12,
    "Apple M2 Ultra": 24,
    "Apple M3": 8,
    "Apple M3 Pro": 12,
    "Apple M3 Max": 16,
    "Apple M4": 10,
    "Apple M4 Pro": 14,
    "Apple M4 Max": 16,
    # Generic fallbacks
    "Unknown CPU": 4,
}

# RAM presets in GB
_RAM_PRESETS: list[float] = [
    2,
    4,
    8,
    16,
    24,
    32,
    48,
    64,
    96,
    128,
    192,
    256,
    512,
    1024,
]

# Disk presets in GB
_DISK_PRESETS: list[float] = [
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
]

# OS options
_OS_OPTIONS = ["linux", "darwin", "windows"]


def _parse_cpu_name(name: str) -> str:
    """Normalize CPU name from user input."""
    return name.strip()


def _parse_cpu_cores(name: str, cores: int | None) -> int:
    """Get CPU cores either from explicit value or preset lookup."""
    if cores is not None and cores > 0:
        return cores

    # Try exact match first
    if name in _CPU_PRESETS:
        return _CPU_PRESETS[name]

    # Try case-insensitive partial match
    name_lower = name.lower()
    for preset_name, preset_cores in _CPU_PRESETS.items():
        if preset_name.lower() == name_lower:
            return preset_cores

    # Default to 4 cores for unknown CPUs
    logger.debug(f"Unknown CPU '{name}', defaulting to 4 cores")
    return 4


def _parse_ram_bytes(value: str) -> int:
    """Parse RAM value from string (e.g., '16GB', '32', '8.5GB')."""
    from whichllm.constants import _GiB

    value = value.strip().upper()

    # Handle plain number as GB
    if value.replace(".", "").isdigit():
        return int(float(value) * _GiB)

    # Handle GB suffix
    if value.endswith("GB"):
        return int(float(value[:-2]) * _GiB)

    # Handle GiB suffix
    if value.endswith("GIB"):
        return int(float(value[:-3]) * _GiB)

    # Handle MB suffix
    if value.endswith("MB"):
        return int(float(value[:-2]) * 1024**2)

    # Handle MiB suffix
    if value.endswith("MIB"):
        return int(float(value[:-3]) * 1024**2)

    raise ValueError(
        f"Invalid RAM value: {value!r}. Use formats like '16GB', '32', or '8.5GB'."
    )


def _parse_disk_bytes(value: str) -> int:
    """Parse disk value from string (e.g., '512GB', '1TB', '256')."""
    from whichllm.constants import _GiB

    value = value.strip().upper()

    # Handle plain number as GB
    if value.replace(".", "").isdigit():
        return int(float(value) * _GiB)

    # Handle TB suffix
    if value.endswith("TB"):
        return int(float(value[:-2]) * _GiB * 1024)

    # Handle TiB suffix
    if value.endswith("TIB"):
        return int(float(value[:-3]) * _GiB * 1024)

    # Handle GB suffix
    if value.endswith("GB"):
        return int(float(value[:-2]) * _GiB)

    # Handle GiB suffix
    if value.endswith("GIB"):
        return int(float(value[:-3]) * _GiB)

    # Handle MB suffix
    if value.endswith("MB"):
        return int(float(value[:-2]) * 1024**2)

    # Handle MiB suffix
    if value.endswith("MIB"):
        return int(float(value[:-3]) * 1024**2)

    raise ValueError(
        f"Invalid disk value: {value!r}. Use formats like '512GB', '1TB', or '256'."
    )


def _validate_os(os_name: str) -> str:
    """Validate and normalize OS name."""
    os_lower = os_name.strip().lower()
    if os_lower not in _OS_OPTIONS:
        raise ValueError(
            f"Invalid OS: {os_name!r}. Must be one of: {', '.join(_OS_OPTIONS)}."
        )
    return os_lower


def create_synthetic_hardware(
    cpu: str | None = None,
    cpu_cores: int | None = None,
    ram: str | None = None,
    disk: str | None = None,
    os_name: str | None = None,
    gpus: list[GPUInfo] | None = None,
) -> HardwareInfo:
    """Create a synthetic HardwareInfo from user-specified values.

    This allows simulating a complete system configuration for testing
    or planning purposes.

    Args:
        cpu: CPU model name (e.g., "i9-13900K", "Ryzen 9 7950X", "Apple M3").
        cpu_cores: Number of CPU cores (auto-detected from preset if not provided).
        ram: RAM size string (e.g., "32GB", "64", "16.5GB").
        disk: Free disk space string (e.g., "512GB", "1TB", "256").
        os_name: Operating system ("linux", "darwin", or "windows").
        gpus: Optional list of GPUInfo objects (for combined GPU+system simulation).

    Returns:
        HardwareInfo with simulated specifications.

    Raises:
        ValueError: If any provided value is invalid.
    """
    # Get current hardware as base for unspecified values
    from whichllm.hardware.detector import detect_hardware

    base_hw = detect_hardware()

    # CPU
    if cpu is not None:
        cpu_name = _parse_cpu_name(cpu)
        detected_cores = _parse_cpu_cores(cpu_name, cpu_cores)
        has_avx2 = True  # Assume AVX2 on modern CPUs
        has_avx512 = False  # Conservative default
    else:
        cpu_name = base_hw.cpu_name
        detected_cores = base_hw.cpu_cores if cpu_cores is None else cpu_cores
        has_avx2 = base_hw.has_avx2
        has_avx512 = base_hw.has_avx512

    # RAM
    if ram is not None:
        ram_bytes = _parse_ram_bytes(ram)
    else:
        ram_bytes = base_hw.ram_bytes

    # Disk
    if disk is not None:
        disk_free_bytes = _parse_disk_bytes(disk)
    else:
        disk_free_bytes = base_hw.disk_free_bytes

    # OS
    if os_name is not None:
        os_val = _validate_os(os_name)
    else:
        os_val = base_hw.os

    # GPUs
    if gpus is None:
        gpus = base_hw.gpus

    return HardwareInfo(
        gpus=gpus,
        cpu_name=cpu_name,
        cpu_cores=detected_cores,
        has_avx2=has_avx2,
        has_avx512=has_avx512,
        ram_bytes=ram_bytes,
        disk_free_bytes=disk_free_bytes,
        os=os_val,
    )


def suggest_compatible_parts(
    cpu: str | None = None,
    ram: str | None = None,
    disk: str | None = None,
    os_name: str | None = None,
    gpus: list[GPUInfo] | None = None,
) -> dict:
    """Suggest compatible parts based on provided specifications.
    
    This function analyzes the provided hardware components and suggests
    compatible or sensible defaults for missing components.
    
    Args:
        cpu: CPU model name (if provided).
        ram: RAM size string (if provided).
        disk: Disk space string (if provided).
        os_name: Operating system name (if provided).
        gpus: Optional list of GPUInfo objects.
    
    Returns:
        Dictionary with suggested values for missing components.
    """
    from whichllm.constants import _GiB
    
    suggestions: dict = {}
    
    # Determine OS based on CPU or GPU
    if os_name is None:
        if cpu is not None:
            cpu_lower = cpu.lower()
            # Apple Silicon implies macOS
            if "apple m" in cpu_lower or "m1" in cpu_lower or "m2" in cpu_lower or \
               "m3" in cpu_lower or "m4" in cpu_lower or "m5" in cpu_lower:
                suggestions["os"] = "darwin"
            # Some CPUs are more common with specific OSes
            elif "ryzen" in cpu_lower or "threadripper" in cpu_lower:
                # AMD CPUs work well with Linux, but also Windows
                suggestions["os"] = "linux"
            else:
                # Intel CPUs - default to Linux as a neutral choice
                suggestions["os"] = "linux"
        elif gpus is not None and len(gpus) > 0:
            # Check if any GPU is Apple Silicon
            for gpu in gpus:
                if gpu.vendor == "apple":
                    suggestions["os"] = "darwin"
                    break
            else:
                suggestions["os"] = "linux"
        else:
            suggestions["os"] = "linux"
    
    # Suggest RAM based on CPU tier or GPU VRAM
    if ram is None:
        suggested_ram_gb = 16  # Default
        
        if cpu is not None:
            cpu_lower = cpu.lower()
            # High-end CPUs deserve more RAM
            if any(x in cpu_lower for x in ["i9", "ryzen 9", "threadripper", "m4 max", "m4 ultra", "m3 max", "m3 ultra"]):
                suggested_ram_gb = 64
            elif any(x in cpu_lower for x in ["i7", "ryzen 7", "m4 pro", "m3 pro", "m2 max"]):
                suggested_ram_gb = 32
            elif any(x in cpu_lower for x in ["i5", "ryzen 5", "m4", "m3", "m2"]):
                suggested_ram_gb = 16
            else:
                suggested_ram_gb = 8
        
        # GPU VRAM can also guide RAM suggestion
        if gpus is not None and len(gpus) > 0:
            total_vram_gb = sum(g.vram_bytes for g in gpus) / _GiB
            # Rule of thumb: system RAM should be at least 2x total VRAM
            min_ram_for_gpu = total_vram_gb * 2
            if min_ram_for_gpu > suggested_ram_gb:
                # Round up to nearest standard size
                for preset in _RAM_PRESETS:
                    if preset >= min_ram_for_gpu:
                        suggested_ram_gb = preset
                        break
        
        suggestions["ram"] = f"{int(suggested_ram_gb)}GB"
    
    # Suggest disk based on RAM and use case
    if disk is None:
        # Parse RAM to get GB value
        ram_gb = 16
        if ram is not None or "ram" in suggestions:
            ram_str = ram or suggestions.get("ram", "16GB")
            try:
                ram_gb = float(ram_str.replace("GB", "").replace("gb", ""))
            except ValueError:
                pass
        
        # Base disk suggestion on RAM size (for swap/hibernation) and modern standards
        if ram_gb <= 8:
            suggested_disk_gb = 256
        elif ram_gb <= 16:
            suggested_disk_gb = 512
        elif ram_gb <= 32:
            suggested_disk_gb = 1024
        else:
            suggested_disk_gb = 2048
        
        suggestions["disk"] = f"{int(suggested_disk_gb)}GB"
    
    # Suggest CPU if only RAM/disk/os provided
    if cpu is None:
        # Default to a reasonable mid-range CPU
        if os_name == "darwin" or suggestions.get("os") == "darwin":
            # Apple Silicon default
            suggestions["cpu"] = "Apple M3"
        else:
            # Default to Intel i5 or Ryzen 5 equivalent
            suggestions["cpu"] = "i5-13600K"
    
    return suggestions


def parse_system_specs(
    cpu: str | None = None,
    cpu_cores: int | None = None,
    ram: str | None = None,
    disk: str | None = None,
    os_name: str | None = None,
) -> dict:
    """Parse and validate system specification parameters.

    This is a helper function for CLI argument parsing that returns
    validated parameters ready to pass to create_synthetic_hardware().

    Args:
        cpu: CPU model name.
        cpu_cores: Number of CPU cores.
        ram: RAM size string.
        disk: Disk space string.
        os_name: Operating system name.

    Returns:
        Dictionary with parsed and validated values.

    Raises:
        ValueError: If any provided value is invalid.
    """
    result: dict = {}

    if cpu is not None:
        result["cpu"] = _parse_cpu_name(cpu)
        result["cpu_cores"] = _parse_cpu_cores(result["cpu"], cpu_cores)

    if ram is not None:
        result["ram"] = _parse_ram_bytes(ram)

    if disk is not None:
        result["disk"] = _parse_disk_bytes(disk)

    if os_name is not None:
        result["os"] = _validate_os(os_name)

    return result
