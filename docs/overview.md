---
title: Crop Filter
sidebar_label: Overview
sidebar_position: 1
---

The **Crop** filter extracts regions of interest (ROIs) from video frames using either detection metadata or predefined polygon coordinates. It supports multiple output modes and is compatible with [OpenFilter](https://github.com/PlainsightAI/openfilter) pipelines.

This document is automatically published to production documentation on every production release.

---

## ✨ Key Features

- **Polygon-based cropping** using user-defined coordinates
- **Detection-based cropping** using metadata-provided ROIs and class labels
- **In-place or separate frame creation** based on configuration
- **Flexible topic routing** (`all`, `main_only`, or a selected list)
- **Metadata propagation** including support for `skip_ocr` flags
- **Legacy support** for environment-based configuration options
- **Designed for compatibility** with the OpenFilter runtime and CLI

---

## 🚀 Usage Modes

### 1. Detection-Based Cropping

If the frame includes metadata under a configured key (e.g. `"detections"`), the filter will crop one frame per ROI using the specified bounding boxes and class labels.

Each cropped frame is emitted on a topic like:

- `car`, `license_plate`, `face`
- Or `car_1`, `car_2` if multiple objects of the same class are detected

### 2. Polygon-Based Cropping

If no detections are found (or if polygon mode is preferred), the filter crops using a predefined polygon in the format:

```json
[[(x1, y1), (x2, y2), (x3, y3), ...]]
````

The polygon is masked, and the resulting region is cropped from the original frame.

### 3. Environment Mode (Legacy)

For backward compatibility, the filter supports setting configuration values via environment variables (e.g. `FILTER_POLYGON_POINTS`, `FILTER_CLASS_NAME`).

---

## ⚙️ Configuration Options

| Field                    | Type            | Description                                             |
| ------------------------ | --------------- | ------------------------------------------------------- |
| `polygon_points`         | `str` or `list` | Polygon coordinates as a stringified list of tuples     |
| `mutate_original_frames` | `bool`          | If `true`, modifies the input frame in-place            |
| `output_prefix`          | `str`           | Prefix for output topic names (e.g., `"cropped_"`)      |
| `topic_mode`             | `str`           | `"all"` (default), `"main_only"`, or `"selected"`       |
| `topics`                 | `list`          | Topics to include when `topic_mode = "selected"`        |
| `detection_key`          | `str`           | Metadata key for detections (`"detections"` by default) |
| `detection_class_field`  | `str`           | Metadata key for detection class names                  |
| `detection_roi_field`    | `str`           | Metadata key for detection ROI boxes                    |
| `custom_name`            | `str`           | Custom name to use for the output topic                 |
| `crop_from_env`          | `bool`          | Use environment variables for configuration             |
| `class_name`             | `str`           | Legacy: name of the detection class                     |
| `cropped_frame_prefix`   | `str`           | Legacy: alternative to `output_prefix`                  |

---

## 🧪 Example Configurations

### Polygon Crop

```python
FilterCropConfig(
  polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
  output_prefix="cropped_",
  topic_mode="all"
)
```

### Detection Crop

```python
FilterCropConfig(
  detection_key="detections",
  detection_class_field="class",
  detection_roi_field="rois",
  topic_mode="main_only"
)
```

### In-place Modification

```python
FilterCropConfig(
  polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
  mutate_original_frames=True
)
```

---

## 🧠 Output Behavior

* If `mutate_original_frames = True`: The original frame is overwritten with the cropped region.
* If `mutate_original_frames = False`: One or more new frames are emitted on custom topics.
* If no detections and no polygon are available: Frame passes through with `meta.skip_ocr = True`.

---

## 🧩 Integration

The filter can be used standalone:

```python
from filter_crop.filter import FilterCrop
FilterCrop.run()
```

Or inside a multi-stage pipeline:

```python
Filter.run_multi([
    (VideoIn, {...}),
    (FilterCrop, {...}),
    (Webvis, {...})
])
```

---

## 🧼 Notes

* Frames with NumPy arrays in `frame.data` are sanitized automatically before returning
* The filter tags every output frame with a `topic` and a `skip_ocr` flag
* Polygon mode requires at least 3 vertices

---

For contribution and development guidelines, see the [CONTRIBUTING guide](https://github.com/PlainsightAI/filter-crop/blob/main/CONTRIBUTING.md).