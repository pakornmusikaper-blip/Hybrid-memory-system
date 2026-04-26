# Changelog

All notable changes to the Substrate Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.4.0] - 2026-04-27

### Added
- `setup.py` for pip installation
- `requirements.txt` with core and optional GPU dependencies
- Example scripts in `examples/` directory
  - `example_01_basic.py` - Basic usage
  - `example_02_growth.py` - Growth system operations
  - `example_03_bridge.py` - Consciousness bridge operations
- Package metadata (author, classifiers, etc.)

### Changed
- Improved error handling in core.py
- Better logging throughout the codebase

## [2.3.0] - 2026-04-27

### Added
- `gpu.py` - GPU acceleration module
- `GPUManager` - Auto-detect CUDA GPUs
- `QuantizationConfig` - NF4 and double quantization
- `auto_configure_for_hardware()` - Auto-tune based on hardware
- GPU CLI command

### Changed
- Improved 4-bit quantization with NF4 format
- Better device selection logic

## [2.2.0] - 2026-04-27

### Added
- `bridge.py` - Consciousness Bridge
- `IntuitionGenerator` - Surface unexpected insights
- Bidirectional communication protocol
- Priority messaging for high-importance intuitions
- intuitions CLI command
- bridge CLI command

## [2.1.0] - 2026-04-27

### Added
- `growth.py` - Growth System
- Automatic belief validation
- Confidence decay for old beliefs
- Contradiction detection
- Pattern recognition
- validate CLI command
- patterns CLI command
- contradictions CLI command
- growth CLI command

## [2.0.0] - 2026-04-26

### Added
- Initial release
- Substrate Agent core architecture
- Qwen model support (0.5B, 1.5B, 1.8B)
- 4-bit and 8-bit quantization
- Belief formation
- Anticipation caching
- Own memory layer
- CLI interface
- Background processing loop
