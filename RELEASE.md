# Changelog
Crop filter release notes

## [Unreleased]

## v0.1.3 - 2025-07-15

### Changed
- Updated dependencies

## v0.1.2 - 2025-05-22

### Changed
- Updated dependencies

## v0.1.1 - 2025-05-22

### Added
- Initial release of the Crop filter for extracting regions of interest from video frames.
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
  - Maintains compatibility with earlier Crop filter configurations.
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

