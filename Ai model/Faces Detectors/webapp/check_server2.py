import requests
urls = ['http://127.0.0.1:5000/', 'http://192.168.68.104:5000/']
for u in urls:
    try:
        r = requests.get(u, timeout=3)
        print(u, '->', r.status_code)
    except Exception as e:
        print(u, '-> ERROR', e)
