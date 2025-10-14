import sys
import os
from pathlib import Path

# Add the model path to sys.path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from age_model import AgeGenderDetector, download_models, demo_interface

def main():
    print("Age & Gender Detection Model - Test Script")
    print("="*50)
    
    # Initialize the detector
    print("Initializing detector...")
    detector = AgeGenderDetector()
    print("Detector initialized successfully!")
    
    # Check what detection methods are available
    has_dnn = detector.face_net is not None
    has_haar = detector.face_cascade is not None
    
    print(f"\nAvailable detection methods:")
    print(f"- DNN Face Detection: {'Yes' if has_dnn else 'No (models not found)'}")
    print(f"- Haar Cascade Detection: {'Yes' if has_haar else 'No'}")
    print(f"- Age/Gender DNN Models: {'Yes' if detector.age_net and detector.gender_net else 'No (models not found)'}")
    
    # Test with a synthetic image
    print(f"\nTesting with synthetic image...")
    import numpy as np
    test_image = np.ones((400, 600, 3), dtype=np.uint8) * 200  # Light gray image
    
    result = detector.process_image_array(test_image)
    print(f"Faces detected: {result.get('total_faces', 0)}")
    
    # Create demo visualization
    print(f"\nCreating demo image...")
    demo_path = str(current_dir / "demo_output.jpg")
    demo_image = detector.create_demo_image(demo_path)
    
    if demo_image is not None:
        print(f"Demo image saved to: {demo_path}")
    
    # Show instructions for getting better results
    print(f"\nTo get better results:")
    print(f"1. Download the OpenCV DNN models (see instructions below)")
    print(f"2. Test with real images containing faces")
    print(f"3. Use the interactive demo interface")
    
    print(f"\nModel download instructions:")
    download_models()
    
    # Offer to start interactive demo
    print(f"\nWould you like to start the interactive demo? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        demo_interface()
    else:
        print("Test completed successfully!")

if __name__ == "__main__":
    main()