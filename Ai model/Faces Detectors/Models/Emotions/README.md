# Emotion Detection Model

A text-based emotion classification model that can detect 6 different emotions from text input.

## Supported Emotions

The model can classify text into the following emotions:
- **Sadness** (0): Expressions of sorrow, disappointment, or unhappiness
- **Joy** (1): Expressions of happiness, excitement, or positive feelings  
- **Love** (2): Expressions of affection, care, or romantic feelings
- **Anger** (3): Expressions of frustration, rage, or irritation
- **Fear** (4): Expressions of worry, anxiety, or being scared
- **Surprise** (5): Expressions of amazement, shock, or unexpected reactions

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Test
To quickly verify the model works:
```bash
python emotion_demo.py
# Choose option 1 for quick test
```

### Interactive Demo
To test with your own text:
```bash
python emotion_demo.py
# Choose option 3 for interactive mode
```

### Using the Model in Code

```python
from emotions_detection_model import EmotionDetectionModel
import os

# Set up paths
base_path = r"c:\flutter\projects\Ai models\DataSets\emotion dataset"
train_path = os.path.join(base_path, "training.csv")
test_path = os.path.join(base_path, "test.csv")

# Create and train model
model = EmotionDetectionModel(model_type='logistic_regression')
X_train, X_test, y_train, y_test = model.load_data(train_path, test_path)
model.train(X_train, y_train)

# Predict single text
emotion, confidence = model.predict_single("I am so happy today!")
print(f"Emotion: {emotion}, Confidence: {confidence:.3f}")

# Predict multiple texts
texts = ["I love this!", "This makes me angry", "I'm scared"]
predictions = model.predict(texts)
for text, emotion, confidence in predictions:
    print(f"'{text}' -> {emotion} ({confidence:.3f})")
```

## Model Types

Two model types are supported:
- `'logistic_regression'` (default): Fast and efficient
- `'random_forest'`: More complex, potentially higher accuracy

## Files

- `emotions_detection_model.py`: Main model implementation
- `emotion_demo.py`: Interactive demonstration script
- `requirements.txt`: Required Python packages
- `README.md`: This documentation

## Dataset

The model uses the emotion dataset located in:
- Training data: `DataSets/emotion dataset/training.csv` (16,000+ samples)
- Test data: `DataSets/emotion dataset/test.csv` (2,000+ samples)
- Validation data: `DataSets/emotion dataset/validation.csv`

## Performance

The model achieves good accuracy on the emotion classification task. Performance metrics are displayed during training and evaluation.

## Example Output

```
Text: 'I am so happy today!'
Predicted Emotion: joy (confidence: 0.856)

Text: 'This makes me really angry'
Predicted Emotion: anger (confidence: 0.734)

Text: 'I'm feeling quite sad about this'
Predicted Emotion: sadness (confidence: 0.612)
```