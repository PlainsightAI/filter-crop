"""
Smoke tests for FilterCrop basic functionality.

These tests verify that the filter can be initialized, configured, and perform
basic operations without complex pipeline orchestration.
"""

import pytest
import numpy as np
import tempfile
import os
from unittest.mock import patch
from openfilter.filter_runtime.filter import Frame
from filter_crop.filter import FilterCrop, FilterCropConfig, SKIP_OCR_FLAG


class TestSmokeSimple:
    """Test basic filter functionality and lifecycle."""

    @pytest.fixture
    def temp_workdir(self):
        """Create a temporary working directory for tests."""
        with tempfile.TemporaryDirectory(prefix='filter_crop_smoke_') as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_frame(self):
        """Create a sample frame for testing."""
        image = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
        frame_data = {"meta": {"id": 1, "topic": "test"}}
        return Frame(image, frame_data, 'BGR')

    def test_filter_initialization(self, temp_workdir):
        """Test that the filter can be initialized with valid config."""
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'topic_mode': 'all',
            'mutate_original_frames': False
        }
        
        # Test config normalization
        config = FilterCrop.normalize_config(config_data)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert config.output_prefix == 'test_'
        assert config.topic_mode == 'all'
        assert config.mutate_original_frames is False
        
        # Test filter initialization
        filter_instance = FilterCrop(config=config)
        assert filter_instance is not None
        # The config is stored internally, so we just verify the filter was created

    def test_setup_and_shutdown(self, temp_workdir):
        """Test that setup() and shutdown() work correctly."""
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'lifecycle_',
            'topic_mode': 'main_only',
            'mutate_original_frames': True
        }
        
        config = FilterCrop.normalize_config(config_data)
        filter_instance = FilterCrop(config=config)
        
        # Test setup
        filter_instance.setup(config)
        assert filter_instance.polygon_points is not None
        assert filter_instance.output_prefix == 'lifecycle_'
        assert filter_instance.topic_mode == 'main_only'
        assert filter_instance.mutate_original_frames is True
        
        # Test shutdown
        filter_instance.shutdown()  # Should not raise any exceptions

    def test_config_validation(self):
        """Test that configuration validation works correctly."""
        # Test valid configuration
        valid_config = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'valid_'
        }
        
        config = FilterCrop.normalize_config(valid_config)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        
        # Test configuration with typo - should not raise error anymore
        config_with_typo = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'valid_',
            'polygon_point': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"  # Typo
        }
        
        # Should not raise an error - unknown keys are passed through
        config = FilterCrop.normalize_config(config_with_typo)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert config.output_prefix == 'valid_'

    def test_polygon_mode_processing(self, sample_frame):
        """Test basic polygon mode processing."""
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'polygon_',
            'topic_mode': 'all'
        }
        
        config = FilterCrop.normalize_config(config_data)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        # Process frame
        frames = {"test": sample_frame}
        output_frames = filter_instance.process(frames)
        
        # Verify output
        assert "main" in output_frames
        assert "polygon_test" in output_frames
        assert not output_frames["main"].data["meta"][SKIP_OCR_FLAG]
        assert not output_frames["polygon_test"].data["meta"][SKIP_OCR_FLAG]
        
        # Verify cropping occurred
        cropped_image = output_frames["polygon_test"].rw_bgr.image
        assert cropped_image.shape[0] < sample_frame.rw_bgr.image.shape[0]
        assert cropped_image.shape[1] < sample_frame.rw_bgr.image.shape[1]

    def test_detection_mode_processing(self, sample_frame):
        """Test basic detection mode processing."""
        # Create frame with detections
        detections = [{"class": "person", "rois": [[50, 50, 150, 150]]}]
        frame_data = {"meta": {"id": 1, "detections": detections}}
        detection_frame = Frame(sample_frame.rw_bgr.image, frame_data, 'BGR')
        
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'detection_',
            'topic_mode': 'all',
            'detection_key': 'detections',
            'detection_class_field': 'class',
            'detection_roi_field': 'rois'
        }
        
        config = FilterCrop.normalize_config(config_data)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        # Process frame
        frames = {"test": detection_frame}
        output_frames = filter_instance.process(frames)
        
        # Verify output
        assert "main" in output_frames
        assert "person" in output_frames
        assert not output_frames["main"].data["meta"][SKIP_OCR_FLAG]
        assert not output_frames["person"].data["meta"][SKIP_OCR_FLAG]
        
        # Verify cropping occurred
        cropped_image = output_frames["person"].rw_bgr.image
        assert cropped_image.shape == (100, 100, 3)

    def test_mutate_original_frames(self, sample_frame):
        """Test mutate_original_frames mode."""
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'mutate_original_frames': True,
            'topic_mode': 'all'
        }
        
        config = FilterCrop.normalize_config(config_data)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        # Process frame
        frames = {"test": sample_frame}
        output_frames = filter_instance.process(frames)
        
        # Verify output
        assert "test" in output_frames  # Original topic key
        assert not output_frames["test"].data["meta"][SKIP_OCR_FLAG]
        
        # Verify cropping occurred
        cropped_image = output_frames["test"].rw_bgr.image
        assert cropped_image.shape[0] < sample_frame.rw_bgr.image.shape[0]
        assert cropped_image.shape[1] < sample_frame.rw_bgr.image.shape[1]

    def test_topic_mode_selection(self, sample_frame):
        """Test different topic mode selections."""
        # Create multiple frames
        frame1 = Frame(sample_frame.rw_bgr.image.copy(), {"meta": {"id": 1}}, 'BGR')
        frame2 = Frame(sample_frame.rw_bgr.image.copy(), {"meta": {"id": 2}}, 'BGR')
        frame3 = Frame(sample_frame.rw_bgr.image.copy(), {"meta": {"id": 3}}, 'BGR')
        
        # Test "main_only" mode
        config_main = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'main_',
            'topic_mode': 'main_only'
        }
        
        config = FilterCrop.normalize_config(config_main)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        frames = {"main": frame1, "secondary": frame2}
        output_frames = filter_instance.process(frames)
        
        assert "main" in output_frames
        assert "main_main" in output_frames
        assert "main_secondary" not in output_frames
        
        # Test "selected" mode
        config_selected = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'selected_',
            'topic_mode': 'selected',
            'topics': ['camera1', 'camera3']
        }
        
        config = FilterCrop.normalize_config(config_selected)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        frames = {"camera1": frame1, "camera2": frame2, "camera3": frame3}
        output_frames = filter_instance.process(frames)
        
        assert "main" in output_frames
        assert "selected_camera1" in output_frames
        assert "selected_camera3" in output_frames
        assert "selected_camera2" not in output_frames

    def test_legacy_parameter_handling(self, sample_frame):
        """Test legacy parameter handling."""
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'cropped_frame_prefix': 'legacy_',
            'crop_from_env': True,
            'class_name': 'legacy_class'
        }
        
        config = FilterCrop.normalize_config(config_data)
        filter_instance = FilterCrop(config=config)
        filter_instance.setup(config)
        
        # Process frame
        frames = {"test": sample_frame}
        output_frames = filter_instance.process(frames)
        
        # Verify legacy parameters work
        assert "legacy_legacy_class" in output_frames
        assert not output_frames["legacy_legacy_class"].data["meta"][SKIP_OCR_FLAG]

    def test_string_config_conversion(self):
        """Test that string configs are properly converted to types."""
        # Test with string values that should be preserved
        config_data = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'string_',
            'topic_mode': 'all',
            'detection_key': 'objects',
            'detection_class_field': 'label',
            'detection_roi_field': 'bounding_boxes',
            'custom_name': 'custom_region'
        }
        
        normalized = FilterCrop.normalize_config(config_data)
        
        # Check that string values are preserved
        assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert normalized.output_prefix == 'string_'
        assert normalized.topic_mode == 'all'
        assert normalized.detection_key == 'objects'
        assert normalized.detection_class_field == 'label'
        assert normalized.detection_roi_field == 'bounding_boxes'
        assert normalized.custom_name == 'custom_region'

    def test_error_handling_invalid_polygon(self):
        """Test error handling for invalid polygon configurations."""
        # Test polygon with too few points
        config_invalid = {
            'polygon_points': "[[(100, 100), (200, 100)]]",  # Only 2 points
            'output_prefix': 'test_'
        }
        
        with pytest.raises(ValueError, match="Polygon must have at least three vertices"):
            FilterCrop.normalize_config(config_invalid)

    def test_environment_variable_loading(self):
        """Test environment variable configuration loading."""
        # Set environment variables
        os.environ['FILTER_POLYGON_POINTS'] = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        os.environ['FILTER_OUTPUT_PREFIX'] = 'env_'
        os.environ['FILTER_MUTATE_ORIGINAL_FRAMES'] = 'true'
        
        try:
            config = FilterCropConfig()
            normalized = FilterCrop.normalize_config(config)
            
            assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
            assert normalized.output_prefix == 'env_'
            assert normalized.mutate_original_frames is True
            
        finally:
            # Clean up environment variables
            for key in ['FILTER_POLYGON_POINTS', 'FILTER_OUTPUT_PREFIX', 'FILTER_MUTATE_ORIGINAL_FRAMES']:
                if key in os.environ:
                    del os.environ[key]


if __name__ == '__main__':
    pytest.main([__file__])
