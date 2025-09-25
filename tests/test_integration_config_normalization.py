"""
Integration tests for FilterCrop configuration normalization.

These tests verify that the normalize_config method properly handles various
configuration inputs, validates parameters, and provides helpful error messages.
"""

import pytest
import os
from filter_crop.filter import FilterCrop, FilterCropConfig


class TestIntegrationConfigNormalization:
    """Test comprehensive configuration normalization scenarios."""

    def test_string_to_type_conversions(self):
        """Test that string configurations are properly converted to correct types."""
        
        # Test that the normalize_config method preserves string types as-is
        # (The actual conversion happens in the parent class)
        config_with_string_bool = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'mutate_original_frames': 'true',  # String bool
            'output_prefix': 'test_',
            'topic_mode': 'all',
            'detection_key': 'detections',
            'detection_class_field': 'class',
            'detection_roi_field': 'rois',
            'custom_name': 'custom_crop',
            'crop_from_env': 'false',
            'class_name': 'test_class'
        }
        
        normalized = FilterCrop.normalize_config(config_with_string_bool)
        
        # Check that string values are preserved
        assert isinstance(normalized.polygon_points, list)
        assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert isinstance(normalized.output_prefix, str)
        assert normalized.output_prefix == 'test_'
        assert isinstance(normalized.topic_mode, str)
        assert normalized.topic_mode == 'all'
        assert isinstance(normalized.detection_key, str)
        assert normalized.detection_key == 'detections'
        
        # Test with integer string
        config_with_int = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_'
        }
        
        normalized_int = FilterCrop.normalize_config(config_with_int)
        assert isinstance(normalized_int.polygon_points, list)
        assert normalized_int.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]

    def test_required_vs_optional_parameters(self):
        """Test that required parameters are validated correctly."""
        
        # Test minimal valid configuration
        minimal_config = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_'
        }
        
        normalized = FilterCrop.normalize_config(minimal_config)
        assert normalized.polygon_points is not None
        assert normalized.output_prefix == 'test_'
        assert normalized.mutate_original_frames is False  # Default value
        assert normalized.topic_mode == "all"  # Default value
        assert normalized.detection_key == "detections"  # Default value

    def test_polygon_points_validation(self):
        """Test polygon points validation and conversion."""
        
        # Test valid polygon points
        valid_polygon = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_'
        }
        
        normalized = FilterCrop.normalize_config(valid_polygon)
        assert isinstance(normalized.polygon_points, list)
        assert len(normalized.polygon_points) == 1
        assert len(normalized.polygon_points[0]) == 4
        
        # Test invalid polygon (too few points)
        invalid_polygon = {
            'polygon_points': "[[(100, 100), (200, 100)]]",  # Only 2 points
            'output_prefix': 'test_'
        }
        
        with pytest.raises(ValueError, match="Polygon must have at least three vertices"):
            FilterCrop.normalize_config(invalid_polygon)

    def test_topic_mode_configuration(self):
        """Test topic mode configuration options."""
        
        # Test "all" mode
        config_all = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'topic_mode': 'all'
        }
        
        normalized = FilterCrop.normalize_config(config_all)
        assert normalized.topic_mode == 'all'
        assert normalized.topics == ["main"]  # Default value
        
        # Test "main_only" mode
        config_main = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'topic_mode': 'main_only'
        }
        
        normalized = FilterCrop.normalize_config(config_main)
        assert normalized.topic_mode == 'main_only'
        
        # Test "selected" mode with topics
        config_selected = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'topic_mode': 'selected',
            'topics': ['camera1', 'camera2']
        }
        
        normalized = FilterCrop.normalize_config(config_selected)
        assert normalized.topic_mode == 'selected'
        assert normalized.topics == ['camera1', 'camera2']

    def test_detection_configuration(self):
        """Test detection-related configuration."""
        
        config_detection = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'detection_key': 'objects',
            'detection_class_field': 'label',
            'detection_roi_field': 'bounding_boxes'
        }
        
        normalized = FilterCrop.normalize_config(config_detection)
        assert normalized.detection_key == 'objects'
        assert normalized.detection_class_field == 'label'
        assert normalized.detection_roi_field == 'bounding_boxes'

    def test_legacy_parameter_handling(self):
        """Test legacy parameter handling and backward compatibility."""
        
        # Test cropped_frame_prefix mapping to output_prefix
        config_legacy = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'cropped_frame_prefix': 'legacy_'
        }
        
        normalized = FilterCrop.normalize_config(config_legacy)
        assert normalized.output_prefix == 'legacy_'
        assert normalized.cropped_frame_prefix == 'legacy_'

    def test_environment_variable_loading(self):
        """Test environment variable configuration loading."""
        
        # Set environment variables
        os.environ['FILTER_POLYGON_POINTS'] = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        os.environ['FILTER_OUTPUT_PREFIX'] = 'env_'
        os.environ['FILTER_MUTATE_ORIGINAL_FRAMES'] = 'true'
        os.environ['FILTER_TOPIC_MODE'] = 'main_only'
        os.environ['FILTER_CROP_FROM_ENV'] = 'true'
        
        try:
            config = FilterCropConfig()
            normalized = FilterCrop.normalize_config(config)
            
            assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
            assert normalized.output_prefix == 'env_'
            assert normalized.mutate_original_frames is True
            assert normalized.topic_mode == 'main_only'
            assert normalized.crop_from_env is True
            
        finally:
            # Clean up environment variables
            for key in ['FILTER_POLYGON_POINTS', 'FILTER_OUTPUT_PREFIX', 'FILTER_MUTATE_ORIGINAL_FRAMES', 
                       'FILTER_TOPIC_MODE', 'FILTER_CROP_FROM_ENV']:
                if key in os.environ:
                    del os.environ[key]

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling."""
        
        # Test empty string values with mutate_original_frames=True to avoid output_prefix validation
        config_empty_strings = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': '',
            'custom_name': '',
            'class_name': '',
            'mutate_original_frames': True  # This allows empty output_prefix
        }
        
        normalized = FilterCrop.normalize_config(config_empty_strings)
        # Empty strings should be preserved as strings
        assert normalized.output_prefix == ''
        assert normalized.custom_name == ''
        assert normalized.class_name == ''
        
        # Test with very long strings
        long_string = 'a' * 1000
        config_long_strings = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': long_string,
            'custom_name': long_string
        }
        
        normalized = FilterCrop.normalize_config(config_long_strings)
        assert normalized.output_prefix == long_string
        assert normalized.custom_name == long_string

    def test_unknown_config_key_validation(self):
        """Test that unknown configuration keys are handled gracefully."""
        
        # Test with a typo in a common parameter - should not raise error anymore
        config_with_typo = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'mutate_original_frames': True,
            'polygon_point': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"  # Typo: missing 's'
        }
        
        # Should not raise an error - unknown keys are passed through
        config = FilterCrop.normalize_config(config_with_typo)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert config.output_prefix == 'test_'
        
        # Test with completely unknown key - should not raise error
        config_unknown = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'unknown_parameter': 'value'
        }
        
        # Should not raise an error - unknown keys are passed through
        config = FilterCrop.normalize_config(config_unknown)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert config.output_prefix == 'test_'
        
        # Test with multiple typos - should not raise error
        config_multiple_typos = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'mutate_original_frames': True,
            'topic_modes': 'all',  # Typo: should be 'topic_mode'
            'detection_keys': 'detections'  # Typo: should be 'detection_key'
        }
        
        # Should not raise an error - unknown keys are passed through
        config = FilterCrop.normalize_config(config_multiple_typos)
        assert config.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert config.output_prefix == 'test_'

    def test_runtime_keys_ignored(self):
        """Test that OpenFilter runtime keys are ignored during validation."""
        
        # Test with runtime keys that should be ignored
        config_with_runtime_keys = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'output_prefix': 'test_',
            'pipeline_id': 'test_pipeline',  # Runtime key
            'device_name': 'test_device',    # Runtime key
            'log_path': '/tmp/logs',         # Runtime key
            'id': 'test_filter',             # Runtime key
            'sources': 'tcp://localhost:5550',  # Runtime key
            'outputs': 'tcp://localhost:5551',  # Runtime key
            'workdir': '/tmp/work'           # Runtime key
        }
        
        # Should not raise an error
        normalized = FilterCrop.normalize_config(config_with_runtime_keys)
        assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert normalized.output_prefix == 'test_'

    def test_comprehensive_configuration(self):
        """Test a comprehensive configuration with all parameters."""
        
        comprehensive_config = {
            'polygon_points': "[[(100, 100), (200, 100), (200, 200), (100, 200)]]",
            'mutate_original_frames': False,
            'output_prefix': 'comprehensive_',
            'topic_mode': 'selected',
            'topics': ['camera1', 'camera2', 'camera3'],
            'detection_key': 'objects',
            'detection_class_field': 'label',
            'detection_roi_field': 'bounding_boxes',
            'custom_name': 'region_of_interest',
            'crop_from_env': False,
            'class_name': 'custom_class',
            'cropped_frame_prefix': 'legacy_'
        }
        
        normalized = FilterCrop.normalize_config(comprehensive_config)
        
        # Verify all parameters are correctly set
        assert normalized.polygon_points == [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        assert normalized.mutate_original_frames is False
        assert normalized.output_prefix == 'comprehensive_'
        assert normalized.topic_mode == 'selected'
        assert normalized.topics == ['camera1', 'camera2', 'camera3']
        assert normalized.detection_key == 'objects'
        assert normalized.detection_class_field == 'label'
        assert normalized.detection_roi_field == 'bounding_boxes'
        assert normalized.custom_name == 'region_of_interest'
        assert normalized.crop_from_env is False
        assert normalized.class_name == 'custom_class'
        assert normalized.cropped_frame_prefix == 'legacy_'
