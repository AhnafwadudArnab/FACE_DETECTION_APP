import requests

url = 'http://127.0.0.1:5000/api/detect'
img_path = r'D:\\Artificial Intelligence project\\Faces Detectors\\DataSets\\object dataset\\Images\\Image_1.jpg'
with open(img_path, 'rb') as f:
    files = {'image': ('Image_1.jpg', f, 'image/jpeg')}
    r = requests.post(url, files=files, timeout=30)
    print('status', r.status_code)
    try:
        print(r.json())
    except Exception as e:
        print('Response text:', r.text)
