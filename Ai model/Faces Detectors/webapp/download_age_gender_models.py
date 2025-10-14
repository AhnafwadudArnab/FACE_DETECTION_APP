import requests
import os
import sys
from pathlib import Path

base_age = Path(r"D:\Artificial Intelligence project\Faces Detectors\Models\Age")
base_face = Path(r"D:\Artificial Intelligence project\Faces Detectors\Models\Face")
base_age.mkdir(parents=True, exist_ok=True)
base_face.mkdir(parents=True, exist_ok=True)

# Files to download (age/gender + face DNN)
files = {
    # Age/Gender models
    'https://github.com/GilLevi/AgeGenderDeepLearning/raw/master/models/age_net.caffemodel': (base_age / 'age_net.caffemodel'),
    'https://github.com/GilLevi/AgeGenderDeepLearning/raw/master/models/gender_net.caffemodel': (base_age / 'gender_net.caffemodel'),
    # Face detection DNN (OpenCV sample)
    'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel': (base_face / 'res10_300x300_ssd_iter_140000.caffemodel'),
    'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt': (base_face / 'deploy.prototxt')
}

for url, path in files.items():
    if path.exists():
        print(f'already exists {path}')
        continue
    print(f'downloading {url} -> {path}')
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            if r.status_code != 200:
                print(f'Failed to download {url}: status {r.status_code}')
                continue
            total = int(r.headers.get('content-length', 0))
            with open(path, 'wb') as f:
                dl = 0
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        if total:
                            print(f'{path.name}: {dl}/{total} bytes', end='\r')
            print(f'\nSaved {path}')
    except Exception as e:
        print(f'Error downloading {url}: {e}')

print('\nAge model directory:')
for fn in sorted(os.listdir(str(base_age))):
    print(fn)

print('\nFace model directory:')
for fn in sorted(os.listdir(str(base_face))):
    print(fn)

print('\nNote: For image-based emotions install the FER package and TensorFlow (cpu or gpu) e.g.:')
print('  pip install fer tensorflow-cpu')
