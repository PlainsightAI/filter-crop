import logging
import cv2
import numpy as np
import ast
from openfilter.filter_runtime.filter import FilterConfig, Filter, Frame
from typing import List, Tuple, Dict, Any, Optional
import os

__all__ = ['FilterCropConfig', 'FilterCrop']

logger = logging.getLogger(__name__)

SKIP_OCR_FLAG = 'skip_ocr'
DEFAULT_CLASS_NAME = 'cropped'

class FilterCropConfig(FilterConfig):
    """
    Configuration class for the FilterCrop.
    
    Attributes:
        polygon_points (str): String representation of polygon coordinates for cropping.
                             Format: "[[(x1,y1), (x2,y2), ...]]"
        mutate_original_frames (bool): If True, modify original frames instead of creating new ones.
        output_prefix (Optional[str]): Prefix for output topics when not mutating original frames.
        
        # Topic handling modes
        topic_mode (str): How to handle multiple topics:
            - "all": Process all topics
            - "main_only": Only process 'main' topic
            - "selected": Only process topics in 'topics' list
        topics (List[str]): List of topics to process when topic_mode='selected'.
        
        # Detection handling
        detection_key (str): Key to look for in frame.data['meta'] for detections.
        detection_class_field (str): Field name for detection class in metadata.
        detection_roi_field (str): Field name for detection ROIs in metadata.
        
        # Custom naming
        custom_name (Optional[str]): Custom name for output when not using detection classes.

        # For backward compatibility 
        crop_from_env (bool): Legacy parameter for environment-based configuration.
        class_name (Optional[str]): Legacy parameter for custom class name.
        cropped_frame_prefix (Optional[str]): Legacy parameter for output_prefix.
    """
    # Basic configuration
    polygon_points:             Optional[str]         = None
    mutate_original_frames:     bool                  = False
    output_prefix:              Optional[str]         = None
    
    # Topic handling
    topic_mode:                 str                   = "all"
    topics:                     List[str]             = ["main"]
    
    # Detection handling
    detection_key:              str                   = "detections"
    detection_class_field:      str                   = "class"
    detection_roi_field:        str                   = "rois"
    
    # Custom naming
    custom_name:                Optional[str]         = None

    # Legacy support
    crop_from_env:              bool                  = False
    class_name:                 Optional[str]         = None
    cropped_frame_prefix:       Optional[str]         = None


class FilterCrop(Filter):
    """
    A filter that crops video frames based on polygon coordinates or detection ROIs.
    
    This filter is designed to work within a video processing pipeline, supporting both real-time and batch processing.
    It provides flexible cropping capabilities with multiple operation modes and output options.

    Features:
    1. Multiple Operation Modes:
       - Polygon Mode: Crop frames using predefined polygon coordinates
       - Detection Mode: Crop frames based on detection ROIs with class labels
       - Environment Mode: Configure cropping through environment variables

    2. Flexible Output Options:
       - Create new frames for cropped regions
       - Modify original frames in-place
       - Support for labeled output topics
       - Maintain original frame as "main" stream

    3. Configuration Options:
       - Polygon coordinates can be provided as string or through environment
       - Customizable output topic prefixes
       - Configurable class names for labeled detections
       - Customizable detection metadata keys for class and ROIs
       
    4. Topic Selection Modes:
       - "all": Process all incoming topic frames
       - "main_only": Only process the 'main' topic frame
       - "selected": Only process frames from topics specified in configuration
       
    5. Frame Processing Behavior:
       - For frames with detections: Creates separate output frames for each detection
       - For frames without detections: Uses polygon-based cropping
       - Sets appropriate metadata for downstream processing (e.g., SKIP_OCR_FLAG)
       
    6. Backward Compatibility:
       - Supports legacy configuration via environment variables
       - Maintains compatibility with previous crop filter implementations
    
    Parameters:
        polygon_points (str, optional): String representation of polygon coordinates for cropping
            Format: "[[(x1,y1), (x2,y2), ...]]"
        mutate_original_frames (bool): If True, modify original frames instead of creating new ones
        output_prefix (str, optional): Prefix for output topics when not mutating original frames
        topic_mode (str): How to handle multiple topics ("all", "main_only", or "selected")
        topics (List[str]): List of topics to process when topic_mode='selected'
        detection_key (str): Key to look for in frame.data['meta'] for detections
        detection_class_field (str): Field name for detection class in metadata
        detection_roi_field (str): Field name for detection ROIs in metadata
        custom_name (str, optional): Custom name for output when not using detection classes
        crop_from_env (bool): Legacy parameter for environment-based configuration
        class_name (str, optional): Legacy parameter for custom class name
        cropped_frame_prefix (str, optional): Legacy parameter for output_prefix
    
    Example Configurations:
    
    1. Basic Polygon Crop:
    ```python
    config = FilterCropConfig(
        polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
        output_prefix="cropped_",
        topic_mode="all"
    )
    ```
    
    2. Detection-based Cropping:
    ```python
    config = FilterCropConfig(
        detection_key="detections",
        detection_class_field="class",
        detection_roi_field="rois",
        topic_mode="main_only"
    )
    ```
    
    3. In-place Modification:
    ```python
    config = FilterCropConfig(
        polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
        mutate_original_frames=True
    )
    ```
    
    4. Topic-selective Processing:
    ```python
    config = FilterCropConfig(
        polygon_points="[[(100, 100), (400, 100), (400, 300), (100, 300)]]",
        topic_mode="selected",
        topics=["camera1", "camera2"],
        output_prefix="region_"
    )
    ```
    
    5. Custom Detection Fields:
    ```python
    config = FilterCropConfig(
        detection_key="objects",
        detection_class_field="label",
        detection_roi_field="bounding_boxes",
        topic_mode="all"
    )
    ```
    """

    @classmethod
    def normalize_config(cls, config: FilterCropConfig) -> FilterCropConfig:
        """
        Normalize and validate the filter configuration.
        
        This method:
        1. Loads configuration from environment variables if specified
        2. Converts polygon points from string to list format
        3. Validates polygon points and configuration parameters
        4. Ensures required parameters are present based on operation mode
        
        Args:
            config (FilterCropConfig): The configuration to normalize
            
        Returns:
            FilterCropConfig: The normalized configuration
            
        Raises:
            ValueError: If polygon points are invalid or required parameters are missing
        """
        config = FilterCropConfig(super().normalize_config(config))

        # Handle legacy parameters
        if config.cropped_frame_prefix and not config.output_prefix:
            config.output_prefix = config.cropped_frame_prefix

        env_mapping = {
            "mutate_original_frames": bool,
            "output_prefix": str,
            "polygon_points": str,
            "topic_mode": str,
            "topics": list,
            "detection_key": str,
            "detection_class_field": str,
            "detection_roi_field": str,
            "custom_name": str,
            "crop_from_env": bool,
            "class_name": str,
        }

        for key, expected_type in env_mapping.items():
            env_key = f"FILTER_{key.upper()}"
            env_val = os.getenv(env_key)
            if env_val is not None:
                if expected_type is bool:
                    setattr(config, key, env_val.strip().lower() == "true")
                else:
                    setattr(config, key, env_val.strip())

        # Convert polygon_points from string to list if it is a string
        if isinstance(config.polygon_points, str):
            config.polygon_points = ast.literal_eval(config.polygon_points)
            if isinstance(config.polygon_points[0], tuple):
                config.polygon_points = [config.polygon_points]
            if len(config.polygon_points[0]) < 3:
                raise ValueError("Polygon must have at least three vertices.")
        else:
            # Assume polygon will be provided elsewhere or not used
            config.polygon_points = None

        # Only validate output_prefix if we're not using detections and not mutating frames
        if not config.mutate_original_frames and not config.output_prefix and config.polygon_points is not None:
            raise ValueError("output_prefix cannot be empty when mutate_original_frames is False and using polygon mode.")

        return config

    def setup(self, config: FilterCropConfig):
        """
        Initialize the filter with the given configuration.
        
        This method:
        1. Sets up instance variables from the configuration
        2. Processes polygon points if provided
        3. Computes bounding box for cropping
        
        Args:
            config (FilterCropConfig): The configuration to use for setup
        """
        logger.info("===========================================")
        logger.info(f"FilterPolygonCrop setup: {config}")
        logger.info("===========================================")

        self.mutate_original_frames = config.mutate_original_frames
        self.output_prefix = config.output_prefix
        self.polygon_points = config.polygon_points
        self.topic_mode = config.topic_mode
        self.topics = config.topics
        self.detection_key = config.detection_key
        self.detection_class_field = config.detection_class_field
        self.detection_roi_field = config.detection_roi_field
        self.custom_name = config.custom_name
        
        # Legacy support
        self.crop_from_env = config.crop_from_env
        self.class_name = config.class_name

        self.config = config

        if config.polygon_points is None:
            self.polygon_points = None
        else:
            # Parse the string into a list of points
            if isinstance(config.polygon_points, str):
                self.polygon_points = ast.literal_eval(config.polygon_points)
            else:
                self.polygon_points = config.polygon_points
                
            # Convert to numpy array
            self.polygon_points = np.array(self.polygon_points, dtype=np.int32)
            
            # Compute bounding box around the polygon for crop dimensions
            self.x, self.y, self.w, self.h = self.polygon_to_bbox(self.polygon_points)
                
        logger.info("Setup Completed for Crop Filter")

    def shutdown(self):
        """Clean up resources when the filter is shut down."""
        logger.info("Shutdown completed!")

    def process(self, frames: Dict[str, Frame]) -> Dict[str, Frame]:
        """Process incoming frames and apply cropping based on configuration.
        
        The filter operates in three modes:
        1. Detection Mode: Uses detection ROIs to crop frames
        2. Polygon Mode: Uses predefined polygon coordinates to crop frames
        3. Environment Mode: Uses environment configuration for cropping
        
        Args:
            frames: Dictionary of input frames
            
        Returns:
            Dictionary of processed frames with appropriate keys
        """
        output_frames = {}
        
        # Tag frames with their topics and identify frames with detections
        for topic, frame in frames.items():
            if 'meta' not in frame.data:
                frame.data['meta'] = {}
            frame.data['meta']['topic'] = topic
            
            # Always return original frames if mutating
            if self.mutate_original_frames:
                output_frames[topic] = frame
        
        # Filter frames based on topic_mode
        filtered_frames = {}
        for topic, frame in frames.items():
            if self.topic_mode == "main_only":
                if topic == "main":
                    filtered_frames[topic] = frame
                # If no 'main' topic exists, use the first frame
                elif 'main' not in frames and len(filtered_frames) == 0:
                    filtered_frames[topic] = frame
            elif self.topic_mode == "selected":
                if topic in self.topics:
                    filtered_frames[topic] = frame
            else:  # "all" mode
                filtered_frames[topic] = frame
        
        # Group frames by detection presence
        detection_frames = {}
        non_detection_frames = {}
        
        for topic, frame in filtered_frames.items():
            # Use configured metadata key to check for detections
            has_detections = (
                self.detection_key in frame.data.get('meta', {}) and 
                frame.data['meta'][self.detection_key]
            )
            
            if has_detections:
                detection_frames[topic] = frame
            else:
                non_detection_frames[topic] = frame
        
        # Process frames with detections
        for topic, frame in detection_frames.items():
            processed = self._process_detection_frame(frame)
            output_frames.update(processed)
        
        # Process frames without detections
        for topic, frame in non_detection_frames.items():
            processed = self._process_polygon_frame(frame)
            output_frames.update(processed)
        
        def sanitize_frame_data(frames: Dict[str, Frame]):
            for frame in frames.values():
                for k, v in list(frame.data.items()):
                    if isinstance(v, np.ndarray):
                        logger.warning(f"Removing unserializable key '{k}' from frame.data")
                        del frame.data[k]

        sanitize_frame_data(output_frames)
        return output_frames

    def _process_detection_frame(self, frame: Frame) -> Dict[str, Frame]:
        """Process a frame with detections."""
        output_frames = {}
        image = frame.rw_bgr.image
        topic = frame.data.get('meta', {}).get('topic', 'main')
        
        # Always create main frame first
        if self.mutate_original_frames:
            frame.data['meta'][SKIP_OCR_FLAG] = False
        else:
            main_frame = Frame(image, {**frame.data}, 'BGR')
            main_frame.data['meta'][SKIP_OCR_FLAG] = False
            output_frames['main'] = main_frame

        
        # Get detections using configured key
        detections = frame.data['meta'].get(self.detection_key, [])
        
        if detections:
            # Track class counts to generate unique keys
            class_counts = {}
            
            # Process each detection
            for detection in detections:
                # Use configured keys for class and ROI
                class_name = detection.get(self.detection_class_field, DEFAULT_CLASS_NAME)
                rois = detection.get(self.detection_roi_field, [])

                # Normalize: single ROI → list of ROIs
                if isinstance(rois, list):
                    if all(isinstance(coord, int) for coord in rois):
                        rois = [rois]
                elif isinstance(rois, tuple):
                    rois = [list(rois)]
                else:
                    logger.warning(f"Unexpected ROI format for detection: {rois} — skipping")
                    continue
                
                for roi in rois:
                    # Update count for this class
                    count = class_counts.get(class_name, 0) + 1
                    class_counts[class_name] = count
                    
                    # Create a unique key for this detection
                    unique_key = class_name if count == 1 else f"{class_name}_{count}"
                    
                    # Crop the frame using the ROI coordinates
                    x1, y1, x2, y2 = roi
                    cropped_frame = image[y1:y2, x1:x2]
                    
                    if self.mutate_original_frames:
                        frame = Frame(cropped_frame, {**frame.data}, 'BGR')
                        frame.data['meta'][SKIP_OCR_FLAG] = False
                        output_frames[topic] = frame
                    else:
                        # Create a new frame for the cropped image
                        crop_frame = Frame(cropped_frame, {**frame.data}, 'BGR')
                        crop_frame.data['meta'][SKIP_OCR_FLAG] = False
                        output_frames[unique_key] = crop_frame
        else:
            # No detections, just set SKIP_OCR_FLAG
            frame.data['meta'][SKIP_OCR_FLAG] = True
            
        return output_frames

    def _process_polygon_frame(self, frame: Frame) -> Dict[str, Frame]:
        """Process a frame without detections using polygon mode or environment mode."""
        output_frames = {}
        image = frame.rw_bgr.image
        topic = frame.data.get('meta', {}).get('topic', 'main')
        
        # Always create main frame first
        if self.mutate_original_frames:
            frame.data['meta'][SKIP_OCR_FLAG] = False
        else:
            main_frame = Frame(image, {**frame.data}, 'BGR')
            main_frame.data['meta'][SKIP_OCR_FLAG] = False
            output_frames['main'] = main_frame
        
        # Handle environment mode (for legacy support)
        if self.crop_from_env:
            # Use class_name if specified, otherwise use DEFAULT_CLASS_NAME
            class_name = self.class_name or DEFAULT_CLASS_NAME
            
            # Apply output prefix if specified
            if self.output_prefix:
                output_key = f"{self.output_prefix}{class_name}"
            else:
                output_key = class_name
                
            # Create a new frame with the original image
            env_frame = Frame(image, {**frame.data}, 'BGR')
            env_frame.data['meta'][SKIP_OCR_FLAG] = False
            output_frames[output_key] = env_frame
            return output_frames
        
        # Handle polygon mode
        if self.polygon_points is not None:
            # Create mask from polygon
            mask = np.zeros_like(image, dtype=np.uint8)
            cv2.fillPoly(mask, [self.polygon_points], (255, 255, 255))
            
            # Apply mask and crop
            masked_frame = cv2.bitwise_and(image, mask)
            cropped_frame = masked_frame[self.y:self.y + self.h, self.x:self.x + self.w]
            
            if self.mutate_original_frames:
                frame = Frame(cropped_frame, {**frame.data}, 'BGR')
                frame.data['meta'][SKIP_OCR_FLAG] = False
                output_frames[topic] = frame
            else:
                # Create a new frame with the cropped image
                if self.custom_name:
                    output_key = self.custom_name
                else:
                    output_key = topic
                
                if self.output_prefix:
                    output_key = f"{self.output_prefix}{output_key}"
                
                crop_frame = Frame(cropped_frame, {**frame.data}, 'BGR')
                crop_frame.data['meta'][SKIP_OCR_FLAG] = False
                output_frames[output_key] = crop_frame
        else:
            # No polygon points, just pass through the frame
            frame.data['meta'][SKIP_OCR_FLAG] = True
            output_frames[topic] = frame
            
        return output_frames

    @classmethod
    def polygon_to_bbox(cls, polygon_points: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        """
        Convert a list of polygon points to a bounding box.
        
        This method:
        1. Computes the minimum bounding rectangle that contains all polygon points
        2. Returns the top-left corner coordinates and dimensions of the rectangle
        
        Args:
            polygon_points (List[Tuple[int, int]]): List of (x, y) coordinates defining the polygon
            
        Returns:
            Tuple[int, int, int, int]: (x, y, width, height) of the bounding box
        """
        x, y, w, h = cv2.boundingRect(polygon_points)
        return x, y, w, h


if __name__ == '__main__':
    FilterCrop.run()