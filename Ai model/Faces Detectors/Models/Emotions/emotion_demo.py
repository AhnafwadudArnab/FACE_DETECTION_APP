"""
Emotion Detection Demo
Simple demonstration of the emotion detection model
"""

import os
import sys
from emotions_detection_model import EmotionDetectionModel

def interactive_demo():
    """
    Interactive demo for testing emotion detection
    """
    print("=== Interactive Emotion Detection Demo ===")
    print("Loading model...")
    
    # Set up paths
    base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
    train_path = os.path.join(base_path, "training.csv")
    test_path = os.path.join(base_path, "test.csv")
    
    # Create and train model (using a smaller subset for quick demo)
    model = EmotionDetectionModel(model_type='logistic_regression')
    
    print("Loading data (this may take a moment)...")
    X_train, X_test, y_train, y_test = model.load_data(train_path, test_path)
    
    # Use only a subset for quick training in demo
    print("Training model with subset of data for quick demo...")
    subset_size = min(5000, len(X_train))
    model.train(X_train[:subset_size], y_train[:subset_size])
    
    print("\nModel ready! Available emotions:")
    for label, emotion in model.emotion_labels.items():
        print(f"  {emotion}")
    
    print("\nEnter text to analyze emotion (type 'quit' to exit):")
    
    while True:
        text = input("\n> ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        if not text:
            continue
        
        try:
            emotion, confidence = model.predict_single(text)
            print(f"Emotion: {emotion.upper()} (confidence: {confidence:.3f})")
        except Exception as e:
            print(f"Error: {e}")
    
    print("Demo ended. Thank you!")

def batch_demo():
    """
    Batch demo with predefined examples
    """
    print("=== Batch Emotion Detection Demo ===")
    
    # Sample texts covering different emotions
    test_texts = [
        "I am so excited about this new opportunity!",
        "This situation makes me furious and upset",
        "I feel really down and disappointed today",
        "I absolutely love spending time with my friends",
        "That horror movie scared me so much",
        "Wow, I never expected that to happen!",
        "I feel so grateful for all the support",
        "This is the worst day of my life",
        "I can't believe how amazing this is",
        "I'm worried about what might happen next"
    ]
    
    # Set up paths
    base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
    train_path = os.path.join(base_path, "training.csv")
    test_path = os.path.join(base_path, "test.csv")
    
    # Create and train model
    model = EmotionDetectionModel(model_type='logistic_regression')
    
    print("Loading and training model...")
    X_train, X_test, y_train, y_test = model.load_data(train_path, test_path)
    
    # Use subset for quick demo
    subset_size = min(5000, len(X_train))
    model.train(X_train[:subset_size], y_train[:subset_size])
    
    print("\n=== Emotion Analysis Results ===")
    predictions = model.predict(test_texts)
    
    for i, (text, emotion, confidence) in enumerate(predictions, 1):
        print(f"{i:2d}. Text: '{text}'")
        print(f"    Emotion: {emotion.upper()} (confidence: {confidence:.3f})")
        print()

def quick_test():
    """
    Quick test to verify the model works
    """
    print("=== Quick Model Test ===")
    
    try:
        # Set up paths
        base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
        train_path = os.path.join(base_path, "training.csv")
        
        # Create model
        model = EmotionDetectionModel(model_type='logistic_regression')
        
        print("Loading minimal data for quick test...")
        X_train, X_test, y_train, y_test = model.load_data(train_path)
        
        # Train with very small subset
        print("Training with 1000 samples...")
        model.train(X_train[:1000], y_train[:1000])
        
        # Test with simple examples
        test_cases = [
            "I am happy",
            "I am sad",
            "I am angry"
        ]
        
        print("\nTesting predictions:")
        for text in test_cases:
            emotion, confidence = model.predict_single(text)
            print(f"'{text}' -> {emotion} ({confidence:.3f})")
        
        print("\n✓ Model is working correctly!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Emotion Detection Model Demo")
    print("Choose an option:")
    print("1. Quick Test (fast)")
    print("2. Batch Demo (predefined examples)")
    print("3. Interactive Demo (type your own text)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        batch_demo()
    elif choice == "3":
        interactive_demo()
    else:
        print("Invalid choice. Running quick test...")
        quick_test()