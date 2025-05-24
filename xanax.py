import io
import cv2
import numpy as np
import base64
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Configure SocketIO with CORS
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   ping_timeout=60,
                   ping_interval=25,
                   logger=True,
                   engineio_logger=True)

# Simulation matrices
SIM_MATS = {
    "protanopia": np.array([
        [0.56667, 0.43333, 0.0],
        [0.55833, 0.44167, 0.0],
        [0.0,     0.24167, 0.75833],
    ]),
    "deuteranopia": np.array([
        [0.625, 0.375, 0.0],
        [0.7,   0.3,   0.0],
        [0.0,   0.3,   0.7],
    ]),
    "tritanopia": np.array([
        [0.95,  0.05,   0.0],
        [0.0,   0.433,  0.567],
        [0.0,   0.475,  0.525],
    ]),
}

# Daltonization (error‐adding) matrices
DALT_MATS = {
    "protanopia": np.array([
        [0.0,      2.02344, -2.52581],
        [0.0,      1.0,      0.0    ],
        [0.0,      0.0,      1.0    ],
    ]),
    "deuteranopia": np.array([
        [1.0,      0.0,      0.0    ],
        [0.494207, 0.0,      1.24827],
        [0.0,      0.0,      1.0    ],
    ]),
    "tritanopia": np.array([
        [1.0,       0.0,       0.0     ],
        [0.0,       1.0,       0.0     ],
        [-0.395913, 0.801109,  0.0     ],
    ]),
}

def transform_image(img: np.ndarray, mat: np.ndarray) -> np.ndarray:
    f = img.astype(np.float32) / 255.0
    t = np.dot(f, mat.T)
    t = np.clip(t, 0.0, 1.0)
    return (t * 255.0).astype(np.uint8)

def color_recolor(img_rgb: np.ndarray,
                  sim: np.ndarray,
                    dalt: np.ndarray) -> np.ndarray:
    img_dalton = transform_image(img_rgb, dalt)
    img_rec = transform_image(img_dalton, sim)
    return img_rec

def process_frame(frame_data, deficiency):
    """Process a video frame and return the recolored frame"""
    try:
        if not frame_data or not frame_data.startswith('data:image'):
            logger.warning(f"Invalid frame data format: {frame_data[:30] if frame_data else 'None'}")
            return None
            
        # Get the base64 part by splitting on comma
        base64_data = frame_data.split(',', 1)
        if len(base64_data) != 2:
            logger.warning(f"Invalid base64 format, can't split: {frame_data[:30]}")
            return None
            
        # Decode base64 image
        try:
            img_data = base64.b64decode(base64_data[1])
            if not img_data:
                logger.warning("Decoded base64 data is empty")
                return None
                
            # Convert to numpy array
            data = np.frombuffer(img_data, dtype=np.uint8)
            if data.size == 0:
                logger.warning("Converted numpy array is empty")
                return None
                
            img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img_bgr is None:
                logger.warning("OpenCV could not decode the image data")
                return None
                
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            sim_mat = SIM_MATS[deficiency]
            dalt_mat = DALT_MATS[deficiency]
            out_rgb = color_recolor(img_rgb, sim_mat, dalt_mat)
            
            out_bgr = cv2.cvtColor(out_rgb, cv2.COLOR_RGB2BGR)

            _, buffer = cv2.imencode('.jpg', out_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

            encoded_frame = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_frame}"
        except base64.binascii.Error as e:
            logger.error(f"Base64 decoding error: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return None

@app.route('/')
def index():
    return jsonify({
        "message": (
            "CVD Recolorization API. POST to "
            "/correct/<deficiency>?strength ignored "
            "with form‑file 'image'. WebSocket available for real-time video."
        )
    })

@app.route('/correct/<deficiency>', methods=['POST'])
def correct_image(deficiency):
    if deficiency not in SIM_MATS:
        return jsonify({
            "error": ("Invalid deficiency, choose from "
                      f"{list(SIM_MATS.keys())}")
        }), 400

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    try:
        file = request.files['image']
        data = np.frombuffer(file.read(), dtype=np.uint8)
        img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return jsonify({"error": "Cannot decode image"}), 400

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        sim_mat = SIM_MATS[deficiency]
        dalt_mat = DALT_MATS[deficiency]
        out_rgb = color_recolor(img_rgb, sim_mat, dalt_mat)

        out_bgr = cv2.cvtColor(out_rgb, cv2.COLOR_RGB2BGR)
        _, buf = cv2.imencode('.png', out_bgr)

        return send_file(
            io.BytesIO(buf.tobytes()),
            mimetype='image/png',
            as_attachment=True,
            download_name='recolored.png'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    emit('status', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('video_frame')
def handle_video_frame(data):
    try:
        deficiency = data.get('deficiency', 'deuteranopia')
        frame_data = data.get('frame')
        
        if not frame_data:
            logger.warning(f'No frame data received from client {request.sid}')
            emit('error', {'message': 'No frame data received'})
            return
            
        if deficiency not in SIM_MATS:
            logger.warning(f'Invalid deficiency type: {deficiency} from client {request.sid}')
            emit('error', {'message': f'Invalid deficiency type. Choose from {list(SIM_MATS.keys())}'})
            return
        
        processed_frame = process_frame(frame_data, deficiency)
        if processed_frame:
            emit('processed_frame', {'frame': processed_frame})
        else:
            emit('error', {'message': 'Failed to process frame'})
    except Exception as e:
        logger.error(f'Error in video_frame handler: {str(e)}')
        emit('error', {'message': f'Server error: {str(e)}'})

if __name__ == '__main__':
    logger.info("Starting CVD Recolorization server")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
