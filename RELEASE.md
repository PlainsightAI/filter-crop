# Changelog
Clipper release notes

## [Unreleased]

## v0.1.12 - 2026-01-21
### Fixed
- Updated dependencies to latest versions
- CVE: update `opencv-python-headless` to 4.13.0 (fixes ffmpeg security vulnerability) via OpenFilter 0.1.18

## v0.1.11 - 2026-01-14
### Fixed
- Add missing Dockerfile
- Fix workflow dependencies (publish-to-pypi -> publish-docker)
- Fix image name in create release workflow

## v0.1.10 - 2026-01-14
### Fixed
- docker push in create release workflow

## v0.1.9 - 2026-01-12
### Added
- security scan workflow
- create release workflow
- update dependencies

## v0.1.8 - 2025-09-27
### Updated
- **Documentation**: Updated documentation

## v0.1.7 - 2025-09-15
### Updated
- **Documentation**: Completely updated `overview.md` with comprehensive sample pipelines, use cases, and configuration examples
- **Test Suite**: Improved test coverage with better error handling and validation testing
- **README**: Complete rewrite with quick start guide and configuration examples

### Added
- **Documentation**:
  - 4 complete sample pipeline examples showing real-world usage
  - 4 detailed use case scenarios (Security, Object Detection, Multi-Camera, Content Creation)
  - Environment variable configuration examples
  - Best practices and troubleshooting guides
- **Enhanced Test Coverage**:
  - Integration tests for configuration normalization
  - Smoke tests for filter lifecycle management
  - Comprehensive validation testing for all configuration parameters
- **Usage Scripts**:
  - Example pipeline usage script with multiple configuration modes
  - Environment variable support for easy customization

## v0.1.6 - 2025-08-12

### Changed
- Added Python 3.13 support

## v0.1.5 - 2025-08-06

### Changed
- Updated dependencies

## v0.1.4 - 2025-07-31

### Changed
- Updated dependencies

## v0.1.3 - 2025-07-15

### Changed
- Updated dependencies

## v0.1.2 - 2025-05-22

### Changed
- Updated dependencies

## v0.1.1 - 2025-05-22

### Added
- Initial release of Clipper for extracting regions of interest from video frames.
- Supports three cropping modes:
  - **Polygon Mode**: Uses user-defined polygon coordinates to crop regions.
  - **Detection Mode**: Extracts crops from detection ROIs provided in frame metadata.
  - **Environment Mode**: Enables cropping configuration via environment variables for legacy use.
- Flexible output options:
  - Ability to mutate original frames (`mutate_original_frames`) or emit new cropped frames.
  - Configurable `output_prefix` to name output topics dynamically.
  - Support for custom detection `class_name` and `custom_name` for output labeling.
- Detection-based cropping:
  - Uses configurable `detection_key`, `detection_class_field`, and `detection_roi_field`.
  - Automatically tags each detection crop with a unique key (e.g., `label`, `label_2`, ...).
- Polygon cropping:
  - Accepts polygon definitions via `polygon_points` in string format.
  - Uses mask-based cropping bounded by the computed polygon bounding box.
- Frame topic selection:
  - `topic_mode` supports `"all"`, `"main_only"`, and `"selected"` topics.
  - `topics` list configurable for `"selected"` mode.
- Metadata tagging:
  - Frames that are not processed for cropping are marked with `meta['skip_ocr'] = True`.
- Config normalization:
  - Supports `.env` and `FILTER_*` environment variable overrides.
  - Includes conversion and validation of booleans, strings, lists, and polygon structures.
- Legacy compatibility:
  - Maintains compatibility with earlier filter configurations.
  - Legacy keys like `class_name`, `cropped_frame_prefix`, and `crop_from_env` are supported.
- Debugging support:
  - Includes logging at key stages of setup and processing.
  - Warns about unserializable frame metadata like NumPy arrays.

### Changed
- Refactored setup logic to centralize configuration parsing and polygon validation.
- Improved handling of configuration overrides from environment variables.
- Unified detection and polygon cropping paths with shared processing steps.
- Enhanced frame metadata tagging to ensure OCR skip flags are set appropriately.
- Internal API cleaned for consistent use of `Frame`, `rw_bgr`, and `meta` accessors.

### Fixed
- Fixed incorrect handling of output prefix logic when legacy parameters are used.
- Resolved issues with improperly parsed polygon formats (tuple vs list).
- Fixed potential frame overwrite in detection mode when using non-unique topic keys.
- Sanitized output frame metadata to remove unserializable values (e.g., NumPy arrays).
- Fixed fallback logic for "main_only" topic mode when the 'main' topic is missing.

### Internal
- Added complete docstrings for all config fields and methods.
- Added multiple configuration examples for clarity.
- Improved shutdown handling with safe logging.
- Updated logging to clearly show setup stages and configuration state.

### Experimental
- Support for mask-based polygon cropping (subject to optimization in future versions).
