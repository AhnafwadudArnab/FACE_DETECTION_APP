import requests  
url='http://127.0.0.1:5000/api/detect'  
import os  
img_path='static/test.jpg'  
if os.path.exists(img_path):  
    files={'image': open(img_path,'rb')}  
    r=requests.post(url,files=files)  
    print('Status',r.status_code)  
    try:  
        print(r.json())  
    except Exception as e:  
        print('Non-json response')  
        print(r.text)  
else:  
    print('No test image at static/test.jpg - skipping POST')  
