# 🪚 Crop Filter

**Crop Filter** is a modular [OpenFilter](https://github.com/PlainsightAI/openfilter)-based filter for extracting regions of interest (ROIs) from video frames using either detection metadata or predefined polygons.

It supports polygon-based cropping, detection-based cropping, and legacy environment-based configurations — all while integrating seamlessly into OpenFilter pipelines.

[![PyPI version](https://img.shields.io/pypi/v/filter-crop.svg?style=flat-square)](https://pypi.org/project/filter-crop/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/PlainsightAI/filter-crop/blob/main/LICENSE)
![Build Status](https://github.com/PlainsightAI/filter-crop/actions/workflows/ci.yaml/badge.svg)

---

## ✨ Features

- 🎯 Crop using polygon coordinates or detection bounding boxes
- 🔀 Supports in-place modification or creation of new cropped frames
- 🧠 Configurable via CLI args, code, or environment variables
- 🧩 Plug-and-play compatibility with [OpenFilter](https://github.com/PlainsightAI/openfilter)
- ⚙️ Supports topic selection modes and legacy configuration

---

## 📦 Installation

Install the latest version from PyPI:

```bash
pip install filter-crop
````

Or install from source:

```bash
# Clone the repo
git clone https://github.com/PlainsightAI/filter-crop.git
cd filter-crop

# (Optional but recommended) create a virtual environemnt:
python -m venv venv && source venv/bin/activate

# Install the filter
make install
```

---

## 🚀 Quick Start (CLI)

Use the OpenFilter CLI to run the Crop Filter in a processing pipeline:

```bash
openfilter run \
  - VideoIn --sources file://filter_example_video.mp4!loop \
  - filter_crop.filter.FilterCrop \
      --polygon_points "[[(0, 500), (0, 720), (1280, 720), (1280, 500)]]" \
      --mutate_original_frames true \
      --topic_mode main_only \
  - Webvis
```

Or simply:

```bash
make run
```

Then open [http://localhost:8000](http://localhost:8000) to view the output.

---

## 🧰 Using from PyPI

After installing with:

```bash
pip install filter-crop
```

You can use the Crop Filter directly in code:

### Standalone usage

```python
from filter_crop.filter import FilterCrop

if __name__ == "__main__":
    FilterCrop.run()
```

### In a multi-filter OpenFilter pipeline

```python
from openfilter.filter_runtime.filter import Filter
from openfilter.filter_runtime.filters.video_in import VideoIn
from openfilter.filter_runtime.filters.webvis import Webvis
from filter_crop.filter import FilterCrop

if __name__ == "__main__":
Filter.run_multi([
    (VideoIn, dict(
        sources='file://example_video.mp4!loop',
        outputs='tcp://*:5550'
    )),
    (FilterCrop, dict(
        sources='tcp://localhost:5550',
        polygon_points="[[(0, 500), (0, 720), (1280, 720), (1280, 500)]]",
        mutate_original_frames=True,
        topic_mode='main_only',
        outputs='tcp://*:5552'
    )),
    (Webvis, dict(
        sources='tcp://localhost:5552'
    )),
]) 
```

---

## 🧪 Testing

Run tests locally:

```bash
make test
```

Or run a specific file:

```bash
pytest -v tests/test_filter_crop.py
```

Tests cover:

* Polygon cropping
* Detection metadata
* ROI handling
* Edge cases (missing metadata, malformed inputs)

---

## 🔧 Example Configs

### Polygon Crop

```python
FilterCropConfig(
  polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
  output_prefix="cropped_",
  topic_mode="all"
)
```

### Detection-based Crop

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

## 🧩 How it Works

The filter supports three main cropping strategies:

| Mode               | Input Needed                      | Output Behavior                            |
| ------------------ | --------------------------------- | ------------------------------------------ |
| Detection          | Metadata with `rois` and `class`  | Crops and emits one frame per detection    |
| Polygon            | List of polygon points            | Applies polygon mask and crops the region  |
| Env-based (legacy) | ENV vars like `FILTER_CLASS_NAME` | Emits a labeled copy of the original frame |

---

## 🤝 Contributing

We welcome PRs! Please read our [CONTRIBUTING.md](https://github.com/PlainsightAI/filter-crop/blob/main/CONTRIBUTING.md) for instructions.

**Highlights**:

* Format code with `black`
* Lint with `ruff`
* Use type hints on public methods
* Sign commits using DCO (`git commit -s`)
* Include tests when relevant

---

## 📄 License

Licensed under the [Apache 2.0 License](https://github.com/PlainsightAI/filter-crop/blob/main/LICENSE).

---

## 🙏 Acknowledgements

Thanks for using and improving the Crop Filter!
For issues or suggestions, [open a GitHub issue](https://github.com/PlainsightAI/filter-crop/issues/new/choose).