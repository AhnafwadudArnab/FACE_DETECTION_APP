import argparse
import sys
import os
from face_detection_model import RealTimeFaceDetector, FaceDetectionModel
import cv2

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Real-time Face Detection Demo")
    
    parser.add_argument('--camera_id', type=int, default=0,
                       help='Camera device ID (default: 0)')
    
    parser.add_argument('--method', choices=['haar', 'dnn'], default='haar',
                       help='Face detection method (default: haar)')
    
    parser.add_argument('--image', type=str,
                       help='Process a single image file instead of real-time detection')
    
    parser.add_argument('--output', type=str,
                       help='Output path for processed image (only with --image)')
    
    parser.add_argument('--save', action='store_true',
                       help='Save frames with face detections')
    
    parser.add_argument('--no-display', action='store_true',
                       help='Run without displaying video window')
    
    parser.add_argument('--output_dir', type=str, default='output',
                       help='Directory to save output files (default: output)')
    
    return parser.parse_args()


def demo_real_time_detection(args):
    """Run real-time face detection demo."""
    print("Starting Real-time Face Detection Demo")
    print("=====================================")
    print(f"Camera ID: {args.camera_id}")
    print(f"Detection Method: {args.method}")
    print(f"Display Window: {not args.no_display}")
    print(f"Save Frames: {args.save}")
    print()
    
    if not args.no_display:
        print("Controls:")
        print("  - Press 'q' or ESC to quit")
        print("  - Press 's' to save screenshot")
        print()
    
    try:
        # Create detector
        detector = RealTimeFaceDetector(
            camera_id=args.camera_id,
            detection_method=args.method,
            display_window=not args.no_display,
            save_frames=args.save,
            output_dir=args.output_dir
        )
        
        # Start detection
        detector.start_detection()
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


def demo_image_detection(args):
    """Run single image face detection demo."""
    print("Starting Image Face Detection Demo")
    print("=================================")
    print(f"Input Image: {args.image}")
    print(f"Detection Method: {args.method}")
    print(f"Output Image: {args.output or 'Not specified'}")
    print()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        return False
    
    try:
        # Create detector
        detector = RealTimeFaceDetector(
            camera_id=0,  # Not used for image processing
            detection_method=args.method,
            display_window=False,
            save_frames=False
        )
        
        # Process image
        faces = detector.detect_single_image(args.image, args.output)
        
        print(f"Detection completed!")
        print(f"Number of faces detected: {len(faces)}")
        
        # Print face details
        for i, face in enumerate(faces, 1):
            x, y, w, h = face['bbox']
            confidence = face['confidence']
            print(f"  Face {i}: Position=({x}, {y}), Size=({w}x{h}), Confidence={confidence:.2f}")
        
        if args.output:
            print(f"Result saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


def test_camera_availability():
    """Test if camera is available."""
    print("Testing camera availability...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not available or accessible")
        return False
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Camera opened but cannot read frames")
        return False
    
    print("✅ Camera is available and working")
    return True


def main():
    """Main demo function."""
    args = parse_arguments()
    
    print("Face Detection Model Demo")
    print("========================")
    print()
    
    # Check if processing single image or real-time
    if args.image:
        success = demo_image_detection(args)
    else:
        # Test camera first
        if not test_camera_availability():
            print("\nTrying to continue anyway...")
        
        success = demo_real_time_detection(args)
    
    if success:
        print("\nDemo completed successfully!")
    else:
        print("\nDemo failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()