import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib
import os
import re
from typing import List, Tuple, Optional

class EmotionDetectionModel:
    """
    Emotion Detection Model for text classification
    
    Based on the emotion dataset with 6 emotion categories:
    0: sadness
    1: joy  
    2: love
    3: anger
    4: fear
    5: surprise
    """
    
    def __init__(self, model_type='logistic_regression'):
        """
        Initialize the emotion detection model
        
        Args:
            model_type (str): Type of model to use ('logistic_regression' or 'random_forest')
        """
        self.model_type = model_type
        self.emotion_labels = {
            0: 'sadness',
            1: 'joy', 
            2: 'love',
            3: 'anger',
            4: 'fear',
            5: 'surprise'
        }
        
        # Create the pipeline based on model type
        if model_type == 'logistic_regression':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    stop_words='english',
                    lowercase=True
                )),
                ('classifier', LogisticRegression(random_state=42, max_iter=1000))
            ])
        elif model_type == 'random_forest':
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    stop_words='english',
                    lowercase=True
                )),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
        else:
            raise ValueError("model_type must be 'logistic_regression' or 'random_forest'")
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text data
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def load_data(self, train_path: str, test_path: str = None, validation_path: str = None) -> Tuple: # type: ignore
        """
        Load data from CSV files
        
        Args:
            train_path (str): Path to training CSV file
            test_path (str, optional): Path to test CSV file
            validation_path (str, optional): Path to validation CSV file
            
        Returns:
            Tuple: Training and testing data
        """
        print("Loading training data...")
        train_df = pd.read_csv(train_path)
        
        # Preprocess training data
        train_df['text'] = train_df['text'].apply(self.preprocess_text)
        
        X_train = train_df['text'].values
        y_train = train_df['label'].values
        
        # Load test data if provided
        if test_path and os.path.exists(test_path):
            print("Loading test data...")
            test_df = pd.read_csv(test_path)
            test_df['text'] = test_df['text'].apply(self.preprocess_text)
            X_test = test_df['text'].values
            y_test = test_df['label'].values
        else:
            # Split training data if no separate test data
            print("Splitting training data...")
            X_train, X_test, y_train, y_test = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42, stratify=y_train # type: ignore
            )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Testing samples: {len(X_test)}")
        print(f"Label distribution in training data:")
        unique, counts = np.unique(y_train, return_counts=True) # type: ignore
        for label, count in zip(unique, counts):
            print(f"  {self.emotion_labels[label]} ({label}): {count}")
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the emotion detection model
        
        Args:
            X_train (np.ndarray): Training text data
            y_train (np.ndarray): Training labels
        """
        print(f"Training {self.model_type} model...")
        self.pipeline.fit(X_train, y_train)
        print("Training completed!")
    
    def predict(self, texts: List[str]) -> List[Tuple[str, str, float]]:
        """
        Predict emotions for given texts
        
        Args:
            texts (List[str]): List of texts to predict
            
        Returns:
            List[Tuple[str, str, float]]: List of (text, emotion, confidence) tuples
        """
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Get predictions and probabilities
        predictions = self.pipeline.predict(processed_texts)
        probabilities = self.pipeline.predict_proba(processed_texts)
        
        results = []
        for i, (text, pred) in enumerate(zip(texts, predictions)):
            emotion = self.emotion_labels[pred]
            confidence = float(np.max(probabilities[i]))
            results.append((text, emotion, confidence))
        
        return results
    
    def predict_single(self, text: str) -> Tuple[str, float]:
        """
        Predict emotion for a single text
        
        Args:
            text (str): Text to predict
            
        Returns:
            Tuple[str, float]: (emotion, confidence)
        """
        result = self.predict([text])
        return result[0][1], result[0][2]  # emotion, confidence
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        Evaluate the model performance
        
        Args:
            X_test (np.ndarray): Test text data
            y_test (np.ndarray): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        print("Evaluating model...")
        y_pred = self.pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nModel Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        target_names = [self.emotion_labels[i] for i in sorted(self.emotion_labels.keys())]
        print(classification_report(y_test, y_pred, target_names=target_names))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, target_names=target_names, output_dict=True),
            'confusion_matrix': cm
        }
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model
        
        Args:
            filepath (str): Path to save the model
        """
        joblib.dump(self.pipeline, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load a trained model
        
        Args:
            filepath (str): Path to the saved model
        """
        self.pipeline = joblib.load(filepath)
        print(f"Model loaded from {filepath}")

def main():
    """
    Main function to demonstrate the emotion detection model
    """
    # Set up paths
    base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
    train_path = os.path.join(base_path, "training.csv")
    test_path = os.path.join(base_path, "test.csv")
    validation_path = os.path.join(base_path, "validation.csv")
    
    # Create and train model
    print("=== Emotion Detection Model ===")
    model = EmotionDetectionModel(model_type='logistic_regression')
    
    # Load data
    X_train, X_test, y_train, y_test = model.load_data(train_path, test_path)
    
    # Train model
    model.train(X_train, y_train)
    
    # Evaluate model
    metrics = model.evaluate(X_test, y_test)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "emotion_model.joblib")
    model.save_model(model_path)
    
    # Test with sample texts
    print("\n=== Sample Predictions ===")
    sample_texts = [
        "I am so happy today!",
        "This makes me really angry",
        "I'm feeling quite sad about this",
        "I love spending time with my family",
        "That was a scary movie",
        "What a surprise! I didn't expect that"
    ]
    
    predictions = model.predict(sample_texts)
    for text, emotion, confidence in predictions:
        print(f"Text: '{text}'")
        print(f"Predicted Emotion: {emotion} (confidence: {confidence:.3f})")
        print("-" * 50)

if __name__ == "__main__":
    main()
