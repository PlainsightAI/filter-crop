# Crop Filter

A specialized OpenFilter component that extracts regions of interest (ROIs) from video frames using either detection metadata or predefined polygons. Supports multiple cropping modes, flexible output options, and comprehensive configuration validation.

## Features

- **Multiple Cropping Modes**: Polygon-based cropping, detection-based cropping, and legacy environment-based configuration
- **Flexible Output Options**: Create new frames for cropped regions or modify original frames in-place
- **Topic Selection Modes**: Process all topics, main only, or selected topics from a configured list
- **Configuration Validation**: Prevents typos with helpful error messages and suggestions
- **Backward Compatibility**: Supports legacy configuration via environment variables

## Quick Start

### Prerequisites

**IMPORTANT!** You need access to OpenFilter and the required dependencies:

```bash
# Install OpenFilter (if not already installed)
pip install openfilter

# Install the crop filter
pip install filter-crop
```

### Installation

```bash
# Create virtual environment
virtualenv venv
source venv/bin/activate

# Install the filter
make install
```

### Basic Usage

```python
from openfilter import Filter

# Simple polygon cropping pipeline
filters = [
    Filter("VideoIn", {
        "sources": "file://sample_video.mp4",
        "outputs": "tcp://127.0.0.1:5550"
    }),
    Filter("FilterCrop", {
        "sources": "tcp://127.0.0.1:5550",
        "outputs": "tcp://127.0.0.1:5551",
        "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
        "output_prefix": "cropped_",
        "topic_mode": "all"
    }),
    Filter("Webvis", {
        "sources": "tcp://127.0.0.1:5551",
        "outputs": "tcp://127.0.0.1:8080"
    })
]

Filter.run_multi(filters, exit_time=30.0)
```

## Documentation

For comprehensive documentation including:
- Complete configuration reference
- Sample pipelines and use cases
- Troubleshooting guides
- API documentation

**Refer to [docs/overview.md](docs/overview.md)**

## Development

### Running Locally

```bash
# Run the filter locally
make run

# Navigate to http://localhost:8000 to see the output
```

### Running in Docker

```bash
# Build the filter docker image
make build-image

# Generate docker-compose.yaml (if needed)
make compose

# Run the containerized filter
make run-image
```

### Testing

```bash
# Run unit tests
make test

# Run specific test files
pytest tests/test_filter_crop.py -v
pytest tests/test_smoke_simple.py -v
pytest tests/test_integration_config_normalization.py -v
```

## Configuration Examples

### Basic Polygon Crop
```json
{
    "id": "polygon_cropper",
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "output_prefix": "cropped_",
    "topic_mode": "all"
}
```

### Detection-Based Crop
```json
{
    "id": "detection_cropper",
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "detection_key": "detections",
    "detection_class_field": "class",
    "detection_roi_field": "rois",
    "topic_mode": "main_only"
}
```

### In-Place Modification
```json
{
    "id": "inplace_cropper",
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "mutate_original_frames": true,
    "topic_mode": "main_only"
}
```

### Multi-Camera Processing
```json
{
    "id": "multi_camera_cropper",
    "sources": ["tcp://127.0.0.1:5550", "tcp://127.0.0.1:5551"],
    "outputs": "tcp://127.0.0.1:5552",
    "polygon_points": "[[(50, 50), (300, 50), (300, 250), (50, 250)]]",
    "topic_mode": "selected",
    "topics": ["camera1", "camera2"],
    "output_prefix": "region_"
}
```

## Use Cases

- **Security Camera Monitoring**: Extract specific regions from security camera feeds
- **Object Detection and Extraction**: Extract detected objects for further analysis
- **Multi-Camera Surveillance**: Process multiple camera feeds with selective region extraction
- **Content Creation and Editing**: Extract specific regions for content creation

See [docs/overview.md](docs/overview.md) for detailed use case examples and sample pipelines.

## Configuration Reference

### Required Configuration

| Key | Type | Description |
|-----|------|-------------|
| `sources` | `string[]` | Input sources (e.g., `tcp://127.0.0.1:5550`) |

### Optional Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `polygon_points` | `string` | `null` | Polygon coordinates for cropping |
| `mutate_original_frames` | `bool` | `false` | Modify original frames instead of creating new ones |
| `output_prefix` | `string` | `null` | Prefix for output topics |
| `topic_mode` | `string` | `"all"` | How to handle multiple topics |
| `topics` | `string[]` | `["main"]` | List of topics to process when `topic_mode="selected"` |
| `detection_key` | `string` | `"detections"` | Key for detection metadata |
| `detection_class_field` | `string` | `"class"` | Field name for detection class |
| `detection_roi_field` | `string` | `"rois"` | Field name for detection ROIs |

## Error Handling

The filter provides helpful error messages for common configuration mistakes:

- **Typo Prevention**: `Unknown config key "polygon_point". Did you mean "polygon_points"?`
- **Invalid Polygon**: `Polygon must have at least three vertices.`
- **Missing Output Prefix**: `output_prefix cannot be empty when mutate_original_frames is False`
