import urllib.request
import sys
try:
    with urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3) as r:
        print('UP', r.getcode())
except Exception as e:
    print('DOWN', e)
    sys.exit(2)
