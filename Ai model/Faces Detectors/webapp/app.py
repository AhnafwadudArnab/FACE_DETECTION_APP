from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask import make_response
import requests
import os
from pathlib import Path
import sys
import uuid
import cv2
import numpy as np

# Ensure project root is on sys.path so sibling packages can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure the local moviepy shim is loaded early so FER's import of moviepy.editor succeeds
try:
    # webapp is the current package folder; shim file is webapp/moviepy_editor_shim.py
    import moviepy_editor_shim  # noqa: F401
except Exception:
    pass

# Import models from existing project
# Import models from existing project
from Models.Age.age_model import AgeGenderDetector
from Models.Face.face_detection_model import FaceDetectionModel
def download_dnn_models():
    """Download DNN model files for age/gender and face detection if not present."""
    age_dir = PROJECT_ROOT / 'Models' / 'Age'
    face_dir = PROJECT_ROOT / 'Models' / 'Face'
    # Face detection DNN
    face_proto_url = 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt'
    face_model_url = 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel'
    # Age/gender DNN
    age_proto_url = 'https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector.pbtxt'
    age_model_url = 'https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector_uint8.pb'
    age_net_proto_url = 'https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/age_deploy.prototxt'
    age_net_model_url = 'https://github.com/spmallick/learnopencv/raw/master/AgeGender/age_net.caffemodel'
    gender_net_proto_url = 'https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/gender_deploy.prototxt'
    gender_net_model_url = 'https://github.com/spmallick/learnopencv/raw/master/AgeGender/gender_net.caffemodel'

    downloads = [
        (face_proto_url, face_dir / 'deploy.prototxt'),
        (face_model_url, face_dir / 'res10_300x300_ssd_iter_140000.caffemodel'),
        (age_proto_url, age_dir / 'opencv_face_detector.pbtxt'),
        (age_model_url, age_dir / 'opencv_face_detector_uint8.pb'),
        (age_net_proto_url, age_dir / 'age_deploy.prototxt'),
        (age_net_model_url, age_dir / 'age_net.caffemodel'),
        (gender_net_proto_url, age_dir / 'gender_deploy.prototxt'),
        (gender_net_model_url, age_dir / 'gender_net.caffemodel'),
    ]
    for url, path in downloads:
        if not path.exists():
            print(f"Downloading {url} to {path}")
            r = requests.get(url)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
            else:
                print(f"Failed to download {url}")



# Flask app initialization and all setup must come first
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Try to enable CORS if Flask-CORS is available; otherwise we'll add simple headers on responses
try:
    from flask_cors import CORS
    CORS(app)
    _CORS_ENABLED = True
except Exception:
    _CORS_ENABLED = False

# Initialize shared detectors (loaded once)
age_gender_detector = AgeGenderDetector(model_path=str(PROJECT_ROOT / 'Models' / 'Age'))
face_detector = FaceDetectionModel(detection_method='haar')

# Simple in-memory overrides (face-level). Keyed by upload uid + face_id; stores emotion label.
emotion_overrides = {}

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'uploads'
RESULTS_DIR = BASE_DIR / 'results'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def cleanup_old_results(days: int = 7) -> None:
    """Remove files older than `days` from RESULTS_DIR."""
    try:
        import time
        now = time.time()
        cutoff = now - days * 86400
        for p in RESULTS_DIR.iterdir():
            try:
                if p.is_file() and p.stat().st_mtime < cutoff:
                    p.unlink()
            except Exception:
                pass
    except Exception:
        # non-fatal
        pass

# Place API route after app is defined
@app.route('/api/detect', methods=['POST']) # type: ignore
def api_detect():
    file = request.files.get('image')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Please upload a valid image file (png/jpg/jpeg/bmp).'}), 400
    # Save to temp
    uid = uuid.uuid4().hex
    infile = UPLOAD_DIR / f"api_{uid}_{file.filename}"
    file.save(str(infile))
    img = cv2.imread(str(infile))
    if img is None:
        return jsonify({'error': 'Could not read uploaded image'}), 400
    result = age_gender_detector.process_image_array(img)
    detections = result.get('detections', [])
    # Optionally save annotated image to results and return URL so clients can display it
    annotated_path = None
    if 'annotated_image' in result and result['annotated_image'] is not None:
        annotated_path = RESULTS_DIR / f"{uid}_annotated.jpg"
        try:
            cv2.imwrite(str(annotated_path), result['annotated_image'])
        except Exception:
            annotated_path = None

    # Only return relevant fields
    faces = [
        {
            'face_id': d.get('face_id'),
            'bbox': d.get('bbox'),
            'age': d.get('age'),
            'gender': d.get('gender'),
            'age_confidence': d.get('age_confidence', 0.0),
            'gender_confidence': d.get('gender_confidence', 0.0),
            'emotion': d.get('emotion', 'Unknown'),
            'emotion_confidence': d.get('emotion_confidence', 0.0)
        } for d in detections
    ]

    response = {'uid': uid, 'faces': faces, 'total_faces': len(faces)}
    if annotated_path is not None and annotated_path.exists():
        # Return a URL that the client can fetch to display the annotated result
        try:
            response['annotated_url'] = url_for('get_result', filename=annotated_path.name, _external=True)
        except Exception:
            # Fallback to relative URL
            response['annotated_url'] = url_for('get_result', filename=annotated_path.name)

    resp = make_response(jsonify(response))
    if not _CORS_ENABLED:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'bmp'}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '' or not allowed_file(file.filename):
            return render_template('index.html', error='Please upload a valid image file (png/jpg/jpeg/bmp).')

        # Save uploaded file
        uid = uuid.uuid4().hex
        infile = UPLOAD_DIR / f"{uid}_{file.filename}"
        file.save(str(infile))

        # Run detections
        img = cv2.imread(str(infile))
        if img is None:
            return render_template('index.html', error='Could not read uploaded image')

        # Use AgeGenderDetector for processing (it will call haar or dnn internally)
        result = age_gender_detector.process_image_array(img)
        # Save annotated image
        annotated_path = RESULTS_DIR / f"{uid}_annotated.jpg"
        if 'annotated_image' in result:
            cv2.imwrite(str(annotated_path), result['annotated_image'])
        else:
            # If no annotated image, draw bounding boxes from face_detector
            faces = face_detector.detect_faces(img)
            out = face_detector.draw_faces(img, faces)
            cv2.imwrite(str(annotated_path), out)

        # Build a summary for the template
        detections = result.get('detections', [])

        return render_template('index.html', detections=detections, image_url=url_for('get_result', filename=annotated_path.name))

    return render_template('index.html')


@app.route('/results/<filename>')
def get_result(filename):
    path = RESULTS_DIR / filename
    if not path.exists():
        return 'File not found', 404
    resp = make_response(send_file(str(path), mimetype='image/jpeg'))


    if not _CORS_ENABLED:
        # allow all origins for simplicity; adjust for production
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/override', methods=['POST'])
def api_override():
    data = request.json or {}
    uid = data.get('uid')
    face_id = data.get('face_id')
    emotion = data.get('emotion')
    if not uid or not face_id or emotion is None:
        return jsonify({'error': 'uid, face_id and emotion required'}), 400
    key = f"{uid}:{face_id}"
    emotion_overrides[key] = emotion
    # persist to disk could be added here
    return jsonify({'ok': True, 'key': key})


@app.route('/api/enhance', methods=['POST'])
def api_enhance():
    """Apply a selected enhancement filter to an uploaded image and return URL to enhanced image.
    Supported filters: sharpen, clahe, denoise, contrast
    Accepts multipart 'image' and optional form field 'filter'."""
    file = request.files.get('image')
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Please upload a valid image file (png/jpg/jpeg/bmp).'}), 400

    filt = (request.form.get('filter') or request.args.get('filter') or 'sharpen').lower()
    uid = uuid.uuid4().hex
    infile = UPLOAD_DIR / f"enh_{uid}_{file.filename}"
    file.save(str(infile))
    img = cv2.imread(str(infile))
    if img is None:
        return jsonify({'error': 'Could not read uploaded image'}), 400

    out = img.copy()
    try:
        if filt == 'sharpen':
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            out = cv2.filter2D(img, -1, kernel)
        elif filt == 'clahe':
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl,a,b))
            out = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        elif filt == 'denoise':
            out = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        elif filt == 'contrast':
            alpha = 1.4  # contrast control
            beta = 10    # brightness control
            out = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        else:
            # unknown filter
            return jsonify({'error': f'Unknown filter: {filt}'}), 400
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

    enhanced_path = RESULTS_DIR / f"{uid}_enhanced.jpg"
    try:
        cv2.imwrite(str(enhanced_path), out)
    except Exception:
        return jsonify({'error': 'Failed to save enhanced image'}), 500

    resp = {'uid': uid, 'filter': filt}
    try:
        resp['enhanced_url'] = url_for('get_result', filename=enhanced_path.name, _external=True)
    except Exception:
        resp['enhanced_url'] = url_for('get_result', filename=enhanced_path.name)

    response = make_response(jsonify(resp))
    if not _CORS_ENABLED:
        response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/api/detect_file', methods=['POST'])
def api_detect_file():
    """Run detection on a file already stored in RESULTS_DIR. POST JSON { filename: '...' }"""
    data = request.json or {}
    fn = data.get('filename')
    if not fn:
        return jsonify({'error': 'filename required'}), 400
    path = RESULTS_DIR / fn
    if not path.exists():
        return jsonify({'error': 'file not found'}), 404
    img = cv2.imread(str(path))
    if img is None:
        return jsonify({'error': 'could not read file'}), 400
    result = age_gender_detector.process_image_array(img)
    detections = result.get('detections', [])
    faces = [
        {
            'face_id': d.get('face_id'),
            'bbox': d.get('bbox'),
            'age': d.get('age'),
            'gender': d.get('gender'),
            'age_confidence': d.get('age_confidence', 0.0),
            'gender_confidence': d.get('gender_confidence', 0.0),
            'emotion': d.get('emotion', 'Unknown'),
            'emotion_confidence': d.get('emotion_confidence', 0.0)
        } for d in detections
    ]
    resp = {'faces': faces, 'total_faces': len(faces), 'filename': fn}
    r = make_response(jsonify(resp))
    if not _CORS_ENABLED:
        r.headers['Access-Control-Allow-Origin'] = '*'
    return r


if __name__ == '__main__':
    print("Downloading DNN models if needed...")
    download_dnn_models()
    # cleanup old results older than 7 days
    cleanup_old_results(days=7)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
