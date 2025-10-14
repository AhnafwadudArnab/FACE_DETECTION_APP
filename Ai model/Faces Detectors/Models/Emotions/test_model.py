"""
Simple test script for emotion detection model
"""

import os
import sys

# Add the current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from emotions_detection_model import EmotionDetectionModel

def test_emotion_detection():
    """Simple test function"""
    print("=== Emotion Detection Test ===")
    
    # Create model
    model = EmotionDetectionModel()
    
    # Load data
    base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
    train_path = os.path.join(base_path, "training.csv")
    test_path = os.path.join(base_path, "test.csv")
    
    print("Loading data...")
    X_train, X_test, y_train, y_test = model.load_data(train_path, test_path)
    
    # Quick training with subset
    print("Training model (quick test with 2000 samples)...")
    model.train(X_train[:2000], y_train[:2000])
    
    # Test with examples
    examples = [
        "I am absolutely thrilled!",
        "This situation makes me furious",
        "I feel so down today",
        "I love spending time with friends",
        "That horror movie terrified me",
        "Wow, what an amazing surprise!"
    ]
    
    print("\n=== Predictions ===")
    predictions = model.predict(examples)
    
    for text, emotion, confidence in predictions:
        print(f"'{text}' -> {emotion.upper()} ({confidence:.3f})")
    
    print("\n=== Model is working! ===")

if __name__ == "__main__":
    test_emotion_detection()