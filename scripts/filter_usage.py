#!/usr/bin/env python3
"""
Filter Crop Usage Example

This script demonstrates how to use FilterCrop in a pipeline:
VideoIn → FilterCrop → Webvis

Prerequisites:
- Sample video file in data/sample-video.mp4
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add the filter module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import OpenFilter components
from openfilter.filter_runtime.filter import Filter
from openfilter.filter_runtime.filters.video_in import VideoIn
from openfilter.filter_runtime.filters.webvis import Webvis
from filter_crop.filter import FilterCrop

def main():
    """Run the FilterCrop pipeline."""
    
    # Configuration
    VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "file://./data/sample-video.mp4!loop")
    POLYGON_POINTS = os.getenv("POLYGON_POINTS", "[[(100, 100), (400, 100), (400, 300), (100, 300)]]")
    OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "cropped_")
    TOPIC_MODE = os.getenv("TOPIC_MODE", "all")
    
    # Build the pipeline
    pipeline = [
        # VideoIn: Read local video file
        (
            VideoIn,
            {
                "id": "video_in",
                "sources": VIDEO_SOURCE,
                "outputs": "tcp://*:5550",
            },
        ),
        
        # FilterCrop: Crop the video frames
        (
            FilterCrop,
            {
                "id": "crop_filter",
                "sources": "tcp://127.0.0.1:5550",
                "outputs": "tcp://*:5552",
                "polygon_points": POLYGON_POINTS,
                "output_prefix": OUTPUT_PREFIX,
                "topic_mode": TOPIC_MODE,
                "mq_log": "pretty",
            },
        ),
        
        # Webvis: Display video stream in browser
        (
            Webvis,
            {
                "id": "webvis",
                "sources": "tcp://localhost:5552",
                "port": 8000
            }
        )
    ]

    # Run the pipeline
    print(f"Starting FilterCrop pipeline")
    print(f"Video source: {VIDEO_SOURCE}")
    print(f"Crop region: {POLYGON_POINTS}")
    print(f"Output prefix: {OUTPUT_PREFIX}")
    print(f"Topic mode: {TOPIC_MODE}")
    print(f"Webvis will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the pipeline")
    
    Filter.run_multi(pipeline, exit_time=None)

if __name__ == "__main__":
    main()
