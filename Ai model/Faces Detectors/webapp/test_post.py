import requests
import os
img_path = 'static/test.jpg'
if not os.path.exists(img_path):
    print('No test image found at', img_path)
    raise SystemExit(1)
url = 'http://127.0.0.1:5000/api/detect'
with open(img_path, 'rb') as fh:
    files = {'image': fh}
    r = requests.post(url, files=files, timeout=30)
    print('Status:', r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print('Response not JSON:')
        print(r.text)
