#!/usr/bin/env python3
"""Enhance assets/girl1.jpg then ask server to detect the enhanced file.

Usage: run from project root or webapp folder. Requires server running at http://127.0.0.1:5000
"""
import os
import sys
import json
import time
import requests

ASSET = os.path.join('..', 'assets', 'girl1.jpg')
SERVERS = [
    'http://127.0.0.1:5000',
    'http://192.168.68.104:5000',
]

if __name__ == '__main__':
    if not os.path.exists(ASSET):
        print('Asset not found:', ASSET)
        sys.exit(2)

    # Try servers in order and fall back
    enhance_url = None
    enhance_resp = None
    for base in SERVERS:
        url = base.rstrip('/') + '/api/enhance'
        try:
            with open(ASSET, 'rb') as fh:
                files = {'image': ('girl1.jpg', fh, 'image/jpeg')}
                data = {'filter': 'clahe'}
                print('POST', url, '...')
                r = requests.post(url, files=files, data=data, timeout=20)
            print('Status:', r.status_code)
            try:
                j = r.json()
            except Exception:
                print('Non-JSON response:', r.text[:400])
                continue
            print('Response JSON:', json.dumps(j, indent=2))
            if r.status_code == 200 and 'enhanced_url' in j:
                enhance_resp = j
                enhance_url = j['enhanced_url']
                break
        except Exception as e:
            print('Error contacting', base, e)

    if not enhance_url:
        print('Enhance failed on all servers')
        sys.exit(3)

    # Extract filename
    from urllib.parse import urlparse
    p = urlparse(enhance_url)
    fname = p.path.split('/')[-1]
    print('Enhanced filename:', fname)

    # call detect_file
    detect_url = None
    detect_resp = None
    for base in SERVERS:
        url = base.rstrip('/') + '/api/detect_file'
        try:
            print('POST', url, '->', {'filename': fname})
            r = requests.post(url, json={'filename': fname}, timeout=15)
            print('Status:', r.status_code)
            try:
                j = r.json()
            except Exception:
                print('Non-JSON response:', r.text[:400])
                continue
            print('Detect response JSON:', json.dumps(j, indent=2))
            if r.status_code == 200:
                detect_resp = j
                detect_url = base
                break
        except Exception as e:
            print('Error contacting', base, e)

    if not detect_resp:
        print('detect_file failed on all servers')
        sys.exit(4)

    print('\nDone. Enhanced URL:', enhance_url)
    print('Detect server:', detect_url)
    print('Faces found:', len(detect_resp.get('faces', [])))
