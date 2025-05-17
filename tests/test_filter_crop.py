import unittest
import numpy as np
import os
import cv2
from openfilter.filter_runtime.filter import Frame

from filter_crop.filter import FilterCrop, FilterCropConfig, SKIP_OCR_FLAG, DEFAULT_CLASS_NAME

class TestFilterCrop(unittest.TestCase):

    def setUp(self):
        raw_config = FilterCropConfig()
        raw_config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        raw_config.output_prefix = "test_"
        raw_config.topic_mode = "all"
        self.config = FilterCrop.normalize_config(raw_config)
        self.filter = FilterCrop(config=self.config)
        self.filter.setup(self.config)
        self.frame_image = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
        self.frame_data = {"meta": {"id": 1}}
        self.frame = Frame(self.frame_image, self.frame_data, 'BGR')

    def test_correct_polygon_input(self):
        self.assertEqual(
            self.config.polygon_points,
            [[(100, 100), (200, 100), (200, 200), (100, 200)]]
        )
    def test_invalid_polygon_points(self):
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100)]]"
        config.output_prefix = "test_"
        with self.assertRaises(ValueError):
            FilterCrop.normalize_config(config)

    def test_polygon_mode_cropping(self):
        frames = {"test": self.frame}
        output_frames = self.filter.process(frames)
        prefixed_key = f"{self.config.output_prefix}test"
        self.assertIn(prefixed_key, output_frames)
        self.assertLess(output_frames[prefixed_key].rw_bgr.image.shape[0], self.frame_image.shape[0])
        self.assertLess(output_frames[prefixed_key].rw_bgr.image.shape[1], self.frame_image.shape[1])

    def test_detection_mode_cropping(self):
        detections = [{"class": "person", "rois": [[50, 50, 150, 150]]}]
        frame_data = {"meta": {"id": 1, "detections": detections}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        output_frames = self.filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("person", output_frames)
        self.assertEqual(output_frames["person"].rw_bgr.image.shape, (100, 100, 3))

    def test_mutate_original_frames(self):
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.mutate_original_frames = True
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        test_frame = self.frame.copy()
        frames = {"test": test_frame}
        output_frames = filter.process(frames)
        self.assertIn("test", output_frames)
        self.assertIn('meta', output_frames["test"].data)
        self.assertFalse(output_frames["test"].data["meta"].get("skip_ocr", True))
        self.assertEqual(output_frames["test"].data["meta"]["topic"], "test")
        cropped_image = output_frames["test"].rw_bgr.image
        self.assertEqual(cropped_image.shape[:2], (101, 101))

    def test_crop_from_env(self):
        config = FilterCropConfig()
        config.crop_from_env = True
        config.class_name = "test_crop"
        config.output_prefix = "env_"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        frames = {"test": self.frame}
        output_frames = filter.process(frames)
        self.assertIn("env_test_crop", output_frames)

    def test_skip_ocr_flag(self):
        frames = {"test": self.frame}
        output_frames = self.filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertFalse(output_frames["main"].data["meta"][SKIP_OCR_FLAG])
        prefixed_key = f"{self.config.output_prefix}test"
        self.assertIn(prefixed_key, output_frames)
        self.assertFalse(output_frames[prefixed_key].data["meta"][SKIP_OCR_FLAG])

    def test_multiple_detections(self):
        detections = [
            {"class": "person", "rois": [[50, 50, 150, 150]]},
            {"class": "car", "rois": [[200, 200, 300, 300]]}
        ]
        frame_data = {"meta": {"id": 1, "detections": detections}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        output_frames = self.filter.process(frames)
        self.assertIn("person", output_frames)
        self.assertIn("car", output_frames)
        self.assertIn("main", output_frames)

    def test_empty_detections(self):
        frame_data = {"meta": {"id": 1, "detections": []}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        output_frames = self.filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertEqual(output_frames["main"].rw_bgr.image.shape, self.frame_image.shape)

    def test_cropped_frame_prefix(self):
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.output_prefix = "cropped_"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        frames = {"test": self.frame}
        output_frames = filter.process(frames)
        self.assertIn("cropped_test", output_frames)

    def test_multiple_topics_with_detections(self):
        detections1 = [{"class": "person", "rois": [[50, 50, 150, 150]]}]
        detections2 = [{"class": "car", "rois": [[200, 200, 300, 300]]}]
        frame1_data = {"meta": {"id": 1, "detections": detections1}}
        frame2_data = {"meta": {"id": 2, "detections": detections2}}
        frame1 = Frame(self.frame_image, frame1_data, 'BGR')
        frame2 = Frame(self.frame_image, frame2_data, 'BGR')
        frames = {"topic1": frame1, "topic2": frame2}
        config = FilterCropConfig()
        config.topic_mode = "all"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        output_frames = filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("person", output_frames)
        self.assertIn("car", output_frames)

    def test_mixed_topics(self):
        detections = [{"class": "person", "rois": [[50, 50, 150, 150]]}]
        frame1_data = {"meta": {"id": 1, "detections": detections}}
        frame2_data = {"meta": {"id": 2}}
        frame1 = Frame(self.frame_image, frame1_data, 'BGR')
        frame2 = Frame(self.frame_image, frame2_data, 'BGR')
        frames = {"detection_topic": frame1, "polygon_topic": frame2}
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.output_prefix = "test_"
        config.topic_mode = "all"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        output_frames = filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("person", output_frames)
        self.assertIn("test_polygon_topic", output_frames)

    def test_environment_variable_config(self):
        os.environ["FILTER_POLYGON_POINTS"] = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        os.environ["FILTER_MUTATE_ORIGINAL_FRAMES"] = "false"
        os.environ["FILTER_OUTPUT_PREFIX"] = "env_"
        os.environ["FILTER_CROP_FROM_ENV"] = "true"
        config = FilterCropConfig()
        config = FilterCrop.normalize_config(config)
        self.assertEqual(config.polygon_points, [[(100, 100), (200, 100), (200, 200), (100, 200)]])
        self.assertFalse(config.mutate_original_frames)
        self.assertEqual(config.output_prefix, "env_")
        self.assertTrue(config.crop_from_env)
        del os.environ["FILTER_POLYGON_POINTS"]
        del os.environ["FILTER_MUTATE_ORIGINAL_FRAMES"]
        del os.environ["FILTER_OUTPUT_PREFIX"]
        del os.environ["FILTER_CROP_FROM_ENV"]

    def test_default_class_name(self):
        config = FilterCropConfig()
        config.crop_from_env = True
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        frames = {"test": self.frame}
        output_frames = filter.process(frames)
        self.assertIn(DEFAULT_CLASS_NAME, output_frames)

    def test_coordinate_handling(self):
        detections = [{"class": "person", "rois": [[50, 50, 150, 150]]}]
        frame_data = {"meta": {"id": 1, "detections": detections}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        output_frames = self.filter.process(frames)
        cropped_frame = output_frames["person"].rw_bgr.image
        self.assertEqual(cropped_frame.shape, (100, 100, 3))

    def test_topic_mode_main_only(self):
        frame1 = Frame(self.frame_image.copy(), {"meta": {"id": 1}}, 'BGR')
        frame2 = Frame(self.frame_image.copy(), {"meta": {"id": 2}}, 'BGR')
        frames = {"main": frame1, "secondary": frame2}
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.output_prefix = "cropped_"
        config.topic_mode = "main_only"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        output_frames = filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("cropped_main", output_frames)
        self.assertNotIn("cropped_secondary", output_frames)

    def test_topic_mode_selected(self):
        frame1 = Frame(self.frame_image.copy(), {"meta": {"id": 1}}, 'BGR')
        frame2 = Frame(self.frame_image.copy(), {"meta": {"id": 2}}, 'BGR')
        frame3 = Frame(self.frame_image.copy(), {"meta": {"id": 3}}, 'BGR')
        frames = {"camera1": frame1, "camera2": frame2, "camera3": frame3}
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.output_prefix = "region_"
        config.topic_mode = "selected"
        config.topics = ["camera1", "camera3"]
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        output_frames = filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("region_camera1", output_frames)
        self.assertIn("region_camera3", output_frames)
        self.assertNotIn("region_camera2", output_frames)

    def test_custom_detection_fields(self):
        detections = [{"label": "vehicle", "bounding_boxes": [[50, 50, 150, 150]]}]
        frame_data = {"meta": {"id": 1, "objects": detections}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        config = FilterCropConfig()
        config.detection_key = "objects"
        config.detection_class_field = "label"
        config.detection_roi_field = "bounding_boxes"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        output_frames = filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("vehicle", output_frames)
        self.assertEqual(output_frames["vehicle"].rw_bgr.image.shape, (100, 100, 3))

    def test_custom_name_output(self):
        config = FilterCropConfig()
        config.polygon_points = "[[(100, 100), (200, 100), (200, 200), (100, 200)]]"
        config.custom_name = "region_of_interest"
        config.output_prefix = "custom_"
        config = FilterCrop.normalize_config(config)
        filter = FilterCrop(config=config)
        filter.setup(config)
        frames = {"test": self.frame}
        output_frames = filter.process(frames)
        self.assertIn("custom_region_of_interest", output_frames)

    def test_multiple_rois_per_detection(self):
        detections = [{
            "class": "person",
            "rois": [
                [50, 50, 150, 150],
                [200, 200, 300, 300]
            ]
        }]
        frame_data = {"meta": {"id": 1, "detections": detections}}
        frame = Frame(self.frame_image, frame_data, 'BGR')
        frames = {"test": frame}
        output_frames = self.filter.process(frames)
        self.assertIn("main", output_frames)
        self.assertIn("person", output_frames)
        self.assertIn("person_2", output_frames)
        self.assertEqual(output_frames["person"].rw_bgr.image.shape, (100, 100, 3))
        self.assertEqual(output_frames["person_2"].rw_bgr.image.shape, (100, 100, 3))

if __name__ == '__main__':
    unittest.main()
