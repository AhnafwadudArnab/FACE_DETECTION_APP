import requests
url = 'http://127.0.0.1:5000/api/detect'
img = '..\\assets\\girl1.jpg'
import os
if not os.path.exists(img):
    print('Asset not found:', img)
    raise SystemExit(1)
with open(img, 'rb') as fh:
    r = requests.post(url, files={'image': fh}, timeout=60)
    print('Status:', r.status_code)
    try:
        import json
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('Non-json response:')
        print(r.text)
