import numpy as np
import cv2
import os
os.makedirs('static', exist_ok=True)
img = np.full((300,400,3), 255, dtype=np.uint8)
cv2.putText(img, 'TEST', (50,180), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 5)
cv2.imwrite('static/test.jpg', img)
print('WROTE static/test.jpg')
