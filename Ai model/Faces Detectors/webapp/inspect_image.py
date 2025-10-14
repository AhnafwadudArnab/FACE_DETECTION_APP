from PIL import Image
import os
p = r'D:\\Artificial Intelligence project\\Faces Detectors\\webapp\\results\\f1b4852983e644e2b599aa015297a561_annotated.jpg'
if os.path.exists(p):
    print('exists', p, 'size', os.path.getsize(p))
    img = Image.open(p)
    print('format', img.format, 'mode', img.mode, 'size', img.size)
else:
    print('missing')
