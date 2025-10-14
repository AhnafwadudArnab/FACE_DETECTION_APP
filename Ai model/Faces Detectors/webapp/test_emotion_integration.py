import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# Load shim to satisfy moviepy.editor import used by fer
try:
    import moviepy_editor_shim  # noqa: F401
except Exception:
    pass

from Models.Emotions.image_emotion_model import ImageEmotionModel
from Models.Age.age_model import AgeGenderDetector
import cv2

img_path = r'D:\Artificial Intelligence project\Faces Detectors\DataSets\object dataset\Images\Image_1.jpg'
print('Loading image:', img_path)
img = cv2.imread(img_path)
if img is None:
    print('Could not read image')
    sys.exit(1)

# Initialize detectors
age_detector = AgeGenderDetector(model_path=str(Path(__file__).resolve().parents[1] / 'Models' / 'Age'))
emotion_model = ImageEmotionModel(mtcnn=False)

# Run the full processing pipeline (detection + age/gender + emotion)
print('Running full pipeline (process_image_array) ...')
res = age_detector.process_image_array(img)
print('Pipeline result summary: total_faces=', res.get('total_faces'))
for d in res.get('detections', []):
    print('detection:', d)
