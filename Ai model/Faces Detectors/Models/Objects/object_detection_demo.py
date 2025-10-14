"""
Object Detection Demo Script
Demonstrates real-time object detection capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object_detection_model import RealTimeObjectDetector
import cv2
import argparse
import logging

def demo_realtime_detection():
    """Demo real-time detection from camera"""
    print("=== Real-Time Detection Demo ===")
    print("Starting camera-based object detection...")
    print("Press 'q' to quit, 's' to save screenshot")
    
    detector = RealTimeObjectDetector(confidence_threshold=0.3)
    detector.run_detection(save_video=False)

def demo_image_detection(image_path: str):
    """Demo detection on a single image"""
    print(f"=== Image Detection Demo ===")
    print(f"Processing image: {image_path}")
    
    detector = RealTimeObjectDetector(confidence_threshold=0.3)
    detections = detector.detect_from_image(image_path)
    
    print(f"\nDetection Results:")
    print(f"Total objects detected: {len(detections)}")
    
    # Group by category
    categories = {}
    for detection in detections:
        category = detection['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(detection)
    
    for category, items in categories.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  - {item['class_name']}: {item['confidence']:.2f}")

def demo_batch_processing(image_folder: str):
    """Demo batch processing of multiple images"""
    print(f"=== Batch Processing Demo ===")
    print(f"Processing images in folder: {image_folder}")
    
    detector = RealTimeObjectDetector(confidence_threshold=0.3)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = []
    
    for file in os.listdir(image_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(image_folder, file))
    
    print(f"Found {len(image_files)} images")
    
    total_detections = 0
    category_counts = {'persons': 0, 'animals': 0, 'devices': 0}
    
    for i, image_path in enumerate(image_files[:10]):  # Process first 10 images
        print(f"Processing {i+1}/{min(10, len(image_files))}: {os.path.basename(image_path)}")
        
        detections = detector.detect_from_image(image_path)
        total_detections += len(detections)
        
        for detection in detections:
            category_counts[detection['category']] += 1
    
    print(f"\nBatch Processing Results:")
    print(f"Images processed: {min(10, len(image_files))}")
    print(f"Total detections: {total_detections}")
    print(f"Persons detected: {category_counts['persons']}")
    print(f"Animals detected: {category_counts['animals']}")
    print(f"Devices detected: {category_counts['devices']}")

def test_camera_access():
    """Test if camera is accessible"""
    print("=== Camera Access Test ===")
    
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Camera is accessible and working")
            print(f"Frame size: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("✗ Camera opened but cannot read frames")
        cap.release()
    else:
        print("✗ Cannot access camera")
        print("Please check if:")
        print("  - Camera is connected")
        print("  - No other application is using the camera")
        print("  - Camera permissions are granted")

def main():
    """Main demo function with command line interface"""
    parser = argparse.ArgumentParser(description="Object Detection Demo")
    parser.add_argument('--mode', choices=['realtime', 'image', 'batch', 'test'], 
                       default='realtime', help='Demo mode to run')
    parser.add_argument('--image', type=str, help='Path to image file (for image mode)')
    parser.add_argument('--folder', type=str, help='Path to image folder (for batch mode)')
    parser.add_argument('--confidence', type=float, default=0.3, 
                       help='Confidence threshold (0.0-1.0)')
    
    args = parser.parse_args()
    
    print("Object Detection System Demo")
    print("============================")
    print("This system can detect:")
    print("  🟢 Persons (Green boxes)")
    print("  🟠 Animals (Orange boxes)")
    print("  🔵 Devices (Blue boxes)")
    print()
    
    if args.mode == 'realtime':
        demo_realtime_detection()
    elif args.mode == 'image':
        if not args.image:
            print("Error: --image parameter required for image mode")
            return
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}")
            return
        demo_image_detection(args.image)
    elif args.mode == 'batch':
        if not args.folder:
            print("Error: --folder parameter required for batch mode")
            return
        if not os.path.exists(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            return
        demo_batch_processing(args.folder)
    elif args.mode == 'test':
        test_camera_access()

def quick_demo():
    """Quick demo using available images in the dataset"""
    print("=== Quick Demo ===")
    
    # Try to find some sample images
    dataset_path = "../../DataSets/object dataset/Images"
    if os.path.exists(dataset_path):
        print("Using sample images from dataset...")
        demo_batch_processing(dataset_path)
    else:
        print("Dataset not found, starting real-time detection...")
        demo_realtime_detection()

if __name__ == "__main__":
    # If no command line arguments, run quick demo
    if len(sys.argv) == 1:
        quick_demo()
    else:
        main()