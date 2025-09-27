---
title: Clipper
sidebar_label: Overview
sidebar_position: 1
---

import Admonition from '@theme/Admonition';

# Clipper

Clipper is a specialized OpenFilter component that extracts regions of interest (ROIs) from video frames using either detection metadata or predefined polygons. It supports multiple cropping modes, flexible output options, and seamless integration into OpenFilter pipelines.

## Features

- **Multiple Cropping Modes**: 
  - Polygon-based cropping using predefined coordinates
  - Detection-based cropping using bounding boxes from metadata
  - Legacy environment-based configuration

- **Flexible Output Options**:
  - Create new frames for cropped regions
  - Modify original frames in-place
  - Support for labeled output topics
  - Maintain original frame as "main" stream

- **Topic Selection Modes**:
  - Process all incoming topic frames
  - Process only the 'main' topic frame
  - Process selected topics from a configured list

- **Configuration Validation**:
  - Validates user-provided configuration keys to prevent typos
  - Provides helpful error messages with suggestions for correct key names
  - Distinguishes between user-configurable and runtime-managed keys

- **Backward Compatibility**:
  - Supports legacy configuration via environment variables
  - Maintains compatibility with previous crop filter implementations

## Example Configuration

```python
# Basic polygon cropping
{
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "output_prefix": "cropped_",
    "topic_mode": "all"
}

# Detection-based cropping
{
    "detection_key": "detections",
    "detection_class_field": "class",
    "detection_roi_field": "rois",
    "topic_mode": "main_only"
}

# In-place modification
{
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "mutate_original_frames": True
}

# Topic-selective processing
{
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "topic_mode": "selected",
    "topics": ["camera1", "camera2"],
    "output_prefix": "region_"
}
```

## Sample Pipelines

### 1. Basic Polygon Cropping Pipeline

**Use Case**: Extract a specific region from video frames

```python
# Pipeline: VideoIn → FilterCrop → Webvis
from openfilter import Filter

# Video source configuration
video_config = {
    "sources": "file://sample_video.mp4",
    "outputs": "tcp://127.0.0.1:5550"
}

# Crop filter configuration
crop_config = {
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "output_prefix": "cropped_",
    "topic_mode": "all"
}

# Webvis for monitoring
webvis_config = {
    "sources": "tcp://127.0.0.1:5551",
    "outputs": "tcp://127.0.0.1:8080"
}

# Run the pipeline
filters = [
    Filter("VideoIn", video_config),
    Filter("FilterCrop", crop_config),
    Filter("Webvis", webvis_config)
]

Filter.run_multi(filters, exit_time=30.0)

# View results in Webvis at: http://localhost:8080/cropped_main
```

### 2. Detection-Based Cropping Pipeline

**Use Case**: Extract regions based on object detection results

```python
# Pipeline: VideoIn → ObjectDetection → FilterCrop → Webvis
from openfilter import Filter

# Video input
video_config = {
    "sources": "rtsp://camera.local:554/stream",
    "outputs": "tcp://127.0.0.1:5550"
}

# Object detection
detection_config = {
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "model": "yolov8n.pt",
    "confidence": 0.5
}

# Crop filter with detection mode
crop_config = {
    "sources": "tcp://127.0.0.1:5551",
    "outputs": "tcp://127.0.0.1:5552",
    "detection_key": "detections",
    "detection_class_field": "class",
    "detection_roi_field": "rois",
    "topic_mode": "main_only"
}

# Webvis for monitoring
webvis_config = {
    "sources": "tcp://127.0.0.1:5552",
    "outputs": "tcp://127.0.0.1:8080"
}

filters = [
    Filter("VideoIn", video_config),
    Filter("FilterObjectDetection", detection_config),
    Filter("FilterCrop", crop_config),
    Filter("Webvis", webvis_config)
]

Filter.run_multi(filters, exit_time=300.0)  # 5 minutes

# View results in Webvis at: http://localhost:8080/main
```

### 3. Multi-Camera Processing Pipeline

**Use Case**: Process multiple camera feeds with selective cropping

```python
# Pipeline: VideoIn (multiple) → FilterCrop → Webvis
from openfilter import Filter

# Multiple video inputs
video_configs = [
    {
        "id": "camera1",
        "sources": "rtsp://camera1.local:554/stream",
        "outputs": "tcp://127.0.0.1:5550"
    },
    {
        "id": "camera2", 
        "sources": "rtsp://camera2.local:554/stream",
        "outputs": "tcp://127.0.0.1:5551"
    }
]

# Crop filter for specific cameras
crop_config = {
    "sources": ["tcp://127.0.0.1:5550", "tcp://127.0.0.1:5551"],
    "outputs": "tcp://127.0.0.1:5552",
    "polygon_points": "[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
    "topic_mode": "selected",
    "topics": ["camera1", "camera2"],
    "output_prefix": "region_"
}

# Webvis for monitoring
webvis_config = {
    "sources": "tcp://127.0.0.1:5552",
    "outputs": "tcp://127.0.0.1:8080"
}

filters = [
    Filter("VideoIn", video_configs[0]),
    Filter("VideoIn", video_configs[1]),
    Filter("FilterCrop", crop_config),
    Filter("Webvis", webvis_config)
]

Filter.run_multi(filters, exit_time=600.0)  # 10 minutes

# View results in Webvis at: http://localhost:8080/region_camera1 and http://localhost:8080/region_camera2
```

### 4. In-Place Processing Pipeline

**Use Case**: Modify frames directly without creating new outputs

```python
# Pipeline: VideoIn → FilterCrop (in-place) → Webvis
from openfilter import Filter

# Video input
video_config = {
    "sources": "file://security_camera.mp4",
    "outputs": "tcp://127.0.0.1:5550"
}

# In-place crop filter
crop_config = {
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(200, 200), (600, 200), (600, 400), (200, 400)]]",
    "mutate_original_frames": True,
    "topic_mode": "main_only"
}

# Webvis for monitoring
webvis_config = {
    "sources": "tcp://127.0.0.1:5551",
    "outputs": "tcp://127.0.0.1:8080"
}

filters = [
    Filter("VideoIn", video_config),
    Filter("FilterCrop", crop_config),
    Filter("Webvis", webvis_config)
]

Filter.run_multi(filters, exit_time=300.0)  # 5 minutes

# View results in Webvis at: http://localhost:8080/main
```

## Use Cases

### 1. Security Camera Monitoring

**Scenario**: Extract specific regions from security camera feeds for focused analysis

```bash
# Environment variables
export CAMERA_RTSP="rtsp://security-camera.company.com:554/stream"
export CROP_REGION="[[(100, 100), (800, 100), (800, 600), (100, 600)]]"

# Configuration
{
    "id": "security_crop",
    "sources": "rtsp://security-camera.company.com:554/stream",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(100, 100), (800, 100), (800, 600), (100, 600)]]",
    "output_prefix": "security_region_",
    "topic_mode": "main_only"
}
```

**Key Variables Used**:
- `polygon_points`: Defines the region of interest to extract
- `output_prefix`: Labels the cropped output for identification
- `topic_mode`: Processes only the main video stream

**View Results**: Access the cropped security region at `http://localhost:8080/security_region_main`

### 2. Object Detection and Extraction

**Scenario**: Extract detected objects for further analysis or processing

```bash
# Environment variables
export DETECTION_MODEL="yolov8n.pt"
export CONFIDENCE_THRESHOLD="0.5"

# Configuration
{
    "id": "object_extractor",
    "sources": "tcp://127.0.0.1:5550",
    "outputs": "tcp://127.0.0.1:5551",
    "detection_key": "detections",
    "detection_class_field": "class",
    "detection_roi_field": "rois",
    "topic_mode": "main_only"
}
```

**Key Variables Used**:
- `detection_key`: Metadata key containing detection results
- `detection_class_field`: Field name for object class labels
- `detection_roi_field`: Field name for bounding box coordinates

**View Results**: Access detected object crops at `http://localhost:8080/person`, `http://localhost:8080/car`, etc. (based on detection classes)

### 3. Multi-Camera Surveillance

**Scenario**: Process multiple camera feeds with selective region extraction

```bash
# Environment variables
export CAMERA1_RTSP="rtsp://camera1.local:554/stream"
export CAMERA2_RTSP="rtsp://camera2.local:554/stream"
export CROP_REGION="[[(50, 50), (400, 50), (400, 300), (50, 300)]]"

# Configuration
{
    "id": "multi_camera_crop",
    "sources": ["tcp://127.0.0.1:5550", "tcp://127.0.0.1:5551"],
    "outputs": "tcp://127.0.0.1:5552",
    "polygon_points": "[[(50, 50), (400, 50), (400, 300), (50, 300)]]",
    "topic_mode": "selected",
    "topics": ["camera1", "camera2"],
    "output_prefix": "surveillance_"
}
```

**Key Variables Used**:
- `sources`: Multiple input streams from different cameras
- `topic_mode`: Selective processing of specific camera feeds
- `topics`: List of camera topics to process

**View Results**: Access cropped regions at `http://localhost:8080/surveillance_camera1` and `http://localhost:8080/surveillance_camera2`

### 4. Content Creation and Editing

**Scenario**: Extract specific regions for content creation or video editing

```bash
# Environment variables
export CONTENT_VIDEO="file://content_video.mp4"
export CROP_REGION="[[(100, 100), (500, 100), (500, 400), (100, 400)]]"

# Configuration
{
    "id": "content_cropper",
    "sources": "file://content_video.mp4",
    "outputs": "tcp://127.0.0.1:5551",
    "polygon_points": "[[(100, 100), (500, 100), (500, 400), (100, 400)]]",
    "mutate_original_frames": True,
    "topic_mode": "main_only"
}
```

**Key Variables Used**:
- `mutate_original_frames`: Modifies frames in-place for content editing
- `polygon_points`: Defines the content region to focus on

**View Results**: Access the modified content at `http://localhost:8080/main`

## Configuration Reference

### Required Configuration

| Key | Type | Description |
|-----|------|-------------|
| `sources` | `string[]` | Input sources (e.g., `tcp://127.0.0.1:5550`) |

### Optional Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `id` | `string` | _auto_ | Filter instance identifier |
| `outputs` | `string[]` | _required_ | Output destinations |
| `polygon_points` | `string` | `null` | Polygon coordinates for cropping (format: `"[[(x1,y1), (x2,y2), ...]]"`) |
| `mutate_original_frames` | `bool` | `false` | If true, modify original frames instead of creating new ones |
| `output_prefix` | `string` | `null` | Prefix for output topics when not mutating original frames |
| `topic_mode` | `string` | `"all"` | How to handle multiple topics (`"all"`, `"main_only"`, `"selected"`) |
| `topics` | `string[]` | `["main"]` | List of topics to process when `topic_mode="selected"` |
| `detection_key` | `string` | `"detections"` | Key to look for in frame metadata for detections |
| `detection_class_field` | `string` | `"class"` | Field name for detection class in metadata |
| `detection_roi_field` | `string` | `"rois"` | Field name for detection ROIs in metadata |
| `custom_name` | `string` | `null` | Custom name for output when not using detection classes |
| `crop_from_env` | `bool` | `false` | Legacy parameter for environment-based configuration |
| `class_name` | `string` | `null` | Legacy parameter for custom class name |
| `cropped_frame_prefix` | `string` | `null` | Legacy parameter for output_prefix |

### Polygon Points Format

Polygon points support the following format:
```
"[[(x1,y1), (x2,y2), (x3,y3), ...]]"
```

Where:
- `(x,y)` - Coordinate pairs defining the polygon vertices
- Must have at least 3 vertices to form a valid polygon
- Coordinates are in pixels relative to the frame dimensions

### Topic Mode Options

| Mode | Description | Use Case |
|------|-------------|----------|
| `"all"` | Process all incoming topic frames | Multi-camera setups, comprehensive processing |
| `"main_only"` | Only process the 'main' topic frame | Single camera focus, performance optimization |
| `"selected"` | Only process topics in the `topics` list | Selective camera processing, specific feeds |

### Detection Metadata Format

The filter expects detection metadata in the following format:
```json
{
  "meta": {
    "detections": [
      {
        "class": "person",
        "rois": [[x1, y1, x2, y2]]
      },
      {
        "class": "car", 
        "rois": [[x1, y1, x2, y2], [x3, y3, x4, y4]]
      }
    ]
  }
}
```

<Admonition type="note" title="Note">
All polygon coordinates must be valid integers and form a closed polygon with at least 3 vertices. The filter will validate polygon points during configuration normalization.
</Admonition>

<Admonition type="tip" title="Tip">
For optimal performance:
- Use `topic_mode="main_only"` when processing single camera feeds
- Use `mutate_original_frames=true` to avoid creating additional frame copies
- Define polygon points that are well within frame boundaries
- Use descriptive output prefixes for better organization
</Admonition>

<Admonition type="warning" title="Configuration Validation">
The filter validates user-provided configuration keys to prevent typos. Common mistakes:
- `polygon_point` → should be `polygon_points`
- `topic_modes` → should be `topic_mode`
- `detection_keys` → should be `detection_key`
- Unknown keys will show helpful error messages with suggestions
- Runtime keys (`pipeline_id`, `device_name`, etc.) are automatically added and ignored
</Admonition>

## Error Handling and Troubleshooting

### Common Configuration Errors

**Typo in configuration key:**
```
ValueError: Unknown config key "polygon_point". Did you mean "polygon_points"?
```

**Invalid polygon points:**
```
ValueError: Polygon must have at least three vertices.
```

**Missing required output prefix:**
```
ValueError: output_prefix cannot be empty when mutate_original_frames is False and using polygon mode.
```

**Invalid topic mode:**
```
ValueError: topic_mode must be one of: all, main_only, selected
```

### Detection Processing Issues

**Missing detection metadata:**
- Frames without detections will use polygon mode or pass through unchanged
- Check that upstream filters are providing detection metadata in the expected format

**Invalid ROI format:**
- ROIs must be lists of 4 integers: `[x1, y1, x2, y2]`
- Multiple ROIs per detection are supported
- Invalid ROIs will be skipped with a warning

### Performance Considerations

- **Memory Usage**: Creating new frames uses more memory than in-place modification
- **Processing Speed**: Polygon mode is faster than detection mode
- **Topic Selection**: Use `main_only` mode for single-camera setups to improve performance
- **Frame Size**: Larger crop regions require more processing time

## How It Works

```shell
        ┌────────────────────┐
        │   FilterRuntime    │
        │  (manages pipeline)│
        └─────────┬──────────┘
                  │
             [new frame arrives]
                  │
                  ▼
        ┌────────────────────┐
        │   FilterCrop.process│
        │   (main processing) │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │  Topic Selection   │
        │  (filter by mode)  │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │ Detection Check    │
        │ (has detections?)  │
        └─────────┬──────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌─────────────┐    ┌─────────────────┐
│ Detection   │    │ Polygon Mode    │
│ Mode        │    │ (predefined     │
│ (use ROIs)  │    │  coordinates)   │
└─────────────┘    └─────────────────┘
        │                    │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │  Output Frames     │
        │  (cropped regions) │
        └────────────────────┘
```

### Processing Modes

**Detection Mode:**
1. Check frame metadata for detections
2. Extract ROIs for each detection
3. Create cropped frames for each ROI
4. Label frames with detection class names

**Polygon Mode:**
1. Apply polygon mask to frame
2. Crop to bounding box of polygon
3. Create output frame with cropped region
4. Apply custom naming if specified

**Environment Mode (Legacy):**
1. Use environment variables for configuration
2. Create labeled copy of original frame
3. Apply legacy naming conventions

## Performance Considerations

- **Polygon Processing**: Faster than detection mode, suitable for static regions
- **Detection Processing**: More flexible but requires upstream detection metadata
- **Memory Management**: In-place modification uses less memory than creating new frames
- **Topic Filtering**: Selective topic processing improves performance for multi-camera setups
- **Frame Size**: Larger crop regions require more processing time and memory