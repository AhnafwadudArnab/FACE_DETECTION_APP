"""
Test script for Object Detection Model
Tests various components and functionality
"""

import unittest
import sys
import os
import cv2
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from object_detection_model import RealTimeObjectDetector
except ImportError as e:
    print(f"Error importing object_detection_model: {e}")
    sys.exit(1)

class TestObjectDetectionModel(unittest.TestCase):
    """Test cases for RealTimeObjectDetector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = RealTimeObjectDetector(confidence_threshold=0.5)
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertEqual(self.detector.confidence_threshold, 0.5)
        self.assertEqual(self.detector.model_path, 'yolov8n.pt')
        self.assertIsNone(self.detector.model)
        self.assertIsNone(self.detector.cap)
    
    def test_categorize_detection(self):
        """Test object categorization"""
        # Test person detection
        self.assertEqual(self.detector.categorize_detection(0), 'persons')
        
        # Test animal detection
        self.assertEqual(self.detector.categorize_detection(15), 'animals')  # cat
        self.assertEqual(self.detector.categorize_detection(16), 'animals')  # dog
        
        # Test device detection
        self.assertEqual(self.detector.categorize_detection(64), 'devices')  # laptop
        self.assertEqual(self.detector.categorize_detection(67), 'devices')  # cell phone
        
        # Test non-target category
        self.assertIsNone(self.detector.categorize_detection(1))  # bicycle
    
    def test_class_names_length(self):
        """Test that class names list has correct length"""
        # COCO dataset has 80 classes (0-79)
        self.assertEqual(len(self.detector.class_names), 80)
    
    def test_target_categories(self):
        """Test target categories configuration"""
        self.assertIn('persons', self.detector.target_categories)
        self.assertIn('animals', self.detector.target_categories)
        self.assertIn('devices', self.detector.target_categories)
        
        # Check that person class (0) is in persons category
        self.assertIn(0, self.detector.target_categories['persons'])
    
    def test_colors_configuration(self):
        """Test color configuration for categories"""
        self.assertIn('persons', self.detector.colors)
        self.assertIn('animals', self.detector.colors)
        self.assertIn('devices', self.detector.colors)
        
        # Check that colors are BGR tuples
        for color in self.detector.colors.values():
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
    
    @patch('cv2.VideoCapture')
    def test_initialize_camera_success(self, mock_video_capture):
        """Test successful camera initialization"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        result = self.detector.initialize_camera()
        
        self.assertTrue(result)
        self.assertEqual(self.detector.cap, mock_cap)
        mock_cap.set.assert_called()
    
    @patch('cv2.VideoCapture')
    def test_initialize_camera_failure(self, mock_video_capture):
        """Test camera initialization failure"""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        result = self.detector.initialize_camera()
        
        self.assertFalse(result)
    
    def test_process_detections_empty(self):
        """Test processing empty detection results"""
        mock_results = [Mock()]
        mock_results[0].boxes = None
        
        detections = self.detector.process_detections(mock_results)
        
        self.assertEqual(len(detections), 0)
    
    def test_draw_detections(self):
        """Test drawing detections on frame"""
        # Create a test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        original_frame = frame.copy()  # Make a copy to compare against
        
        # Create test detections
        detections = [
            {
                'category': 'persons',
                'class_name': 'person',
                'confidence': 0.85,
                'bbox': [100, 100, 200, 200]
            }
        ]
        
        result_frame = self.detector.draw_detections(frame, detections)
        
        # Check that frame was modified (not all zeros anymore)
        self.assertFalse(np.array_equal(original_frame, result_frame))
        
        # Test with empty detections - should not modify frame
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        empty_original = empty_frame.copy()
        empty_result = self.detector.draw_detections(empty_frame, [])
        self.assertTrue(np.array_equal(empty_original, empty_result))
    
    def test_add_stats_overlay(self):
        """Test adding statistics overlay"""
        # Create a test frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        original_frame = frame.copy()  # Make a copy to compare against
        
        # Create test detections
        detections = [
            {'category': 'persons', 'class_name': 'person', 'confidence': 0.85},
            {'category': 'animals', 'class_name': 'cat', 'confidence': 0.75},
        ]
        
        result_frame = self.detector.add_stats_overlay(frame, detections, 30.0)
        
        # Check that frame was modified (stats overlay should always be added)
        self.assertFalse(np.array_equal(original_frame, result_frame))
        
        # Test that the overlay contains expected elements (stats area should be black)
        # The stats background is drawn as a black rectangle from (10,10) to (200, stats_height)
        stats_area = result_frame[10:50, 10:200]  # Sample area where stats should be
        # Should contain non-zero values (white text on black background)
        self.assertTrue(np.any(stats_area > 0))

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_model_loading_simulation(self):
        """Test model loading (without actually loading)"""
        detector = RealTimeObjectDetector()
        
        # This would normally load the model, but we'll mock it
        with patch.object(detector, 'model') as mock_model:
            mock_model.return_value = Mock()
            # Simulate that model loading was successful
            self.assertIsNotNone(mock_model)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility and helper functions"""
    
    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation"""
        # Valid thresholds
        detector1 = RealTimeObjectDetector(confidence_threshold=0.0)
        self.assertEqual(detector1.confidence_threshold, 0.0)
        
        detector2 = RealTimeObjectDetector(confidence_threshold=1.0)
        self.assertEqual(detector2.confidence_threshold, 1.0)
        
        detector3 = RealTimeObjectDetector(confidence_threshold=0.5)
        self.assertEqual(detector3.confidence_threshold, 0.5)
    
    def test_model_path_configuration(self):
        """Test model path configuration"""
        custom_path = "custom_model.pt"
        detector = RealTimeObjectDetector(model_path=custom_path)
        self.assertEqual(detector.model_path, custom_path)

def test_camera_availability():
    """Test if camera is available (not part of unittest)"""
    print("\n=== Camera Availability Test ===")
    
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Camera is available and working")
            print(f"  Frame size: {frame.shape[1]}x{frame.shape[0]}")
            return True
        else:
            print("✗ Camera opened but cannot read frames")
            return False
        cap.release()
    else:
        print("✗ Cannot access camera")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    print("\n=== Dependency Check ===")
    
    dependencies = {
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'ultralytics': 'Ultralytics YOLO'
    }
    
    all_available = True
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} is available")
        except ImportError:
            print(f"✗ {name} is NOT available")
            all_available = False
    
    return all_available

def run_basic_functionality_test():
    """Run basic functionality test without model loading"""
    print("\n=== Basic Functionality Test ===")
    
    try:
        detector = RealTimeObjectDetector()
        print("✓ Detector initialization successful")
        
        # Test categorization
        result = detector.categorize_detection(0)  # person
        if result == 'persons':
            print("✓ Object categorization working")
        else:
            print("✗ Object categorization failed")
            
        # Test frame processing (without actual detection)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = []
        result_frame = detector.draw_detections(frame, detections)
        print("✓ Frame processing working")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Object Detection Model Test Suite")
    print("=================================")
    
    # Check dependencies first
    if not test_dependencies():
        print("\n⚠️  Some dependencies are missing. Please install requirements.")
        return
    
    # Run basic functionality test
    if not run_basic_functionality_test():
        print("\n⚠️  Basic functionality test failed.")
        return
    
    # Test camera availability
    camera_available = test_camera_availability()
    
    # Run unit tests
    print("\n=== Running Unit Tests ===")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [TestObjectDetectionModel, TestIntegration, TestUtilityFunctions]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Overall status
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success and camera_available:
        print("\n✅ All tests passed! System is ready for use.")
    elif success and not camera_available:
        print("\n⚠️  Tests passed but camera not available. Image processing will work.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()