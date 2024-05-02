from flask import Flask, request, jsonify
import secrets
from datetime import datetime
import sys
import malstroem.scripts.complete as complete
import os
import logging 
from logging.handlers import RotatingFileHandler

# Create a logger for the current module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level

# Set up file handler0

file_handler = RotatingFileHandler('logs/app.log', maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler

# Add the handler to the logger
logger.addHandler(file_handler)

def generate_api_key(length=32):
    """Generate a random API key."""
    return secrets.token_hex(length)


app = Flask(__name__)

VALID_API_KEYS = [
        '4fa7cd834009d04d2ef62a540017ff47178183752b9266ae3586b91e9111acd9',
        '0bda9764796d68b7b98873bbcd0d04dc49e90271a4ef00738d6238735a7f75b9'
]

# Middleware function to verify API key
@app.before_request
def verify_api_key():
    if request.method == 'POST':
        api_key = request.headers.get('X-API-Key')
        if api_key not in VALID_API_KEYS:
            logger.warning(f"Unauthorized request with API key: {api_key}")    
            return jsonify({'error': 'Unauthorized'}), 401

def run_malstroem_processing(data):
    # Implement your processing logic here
    return {"status": "Success", "data": data}

# Protected endpoint that requires API key authentication
@app.route('/process', methods=['POST'])
def process():

    data = request.json
    return jsonify(run_malstroem_processing(data))
# def process_complete(dem, outdir, mm=20, filter='volume > 2.5', zresolution=0.1, accum=None, vector=None):
@app.route('/complete', methods=['POST'])
def process_complete():
    data=request.json
    logger.debug("Received request: %s", data)
    dem = '/cache/'+data.get('raster_key')
    if not os.path.exists(dem):
        return jsonify({'error': 'Raster file not found'}), 404
    outdir = f"/output/{data.get('outdir')}"
    logger.debug("Output directory: %s", outdir)
    os.makedirs(outdir, exist_ok=True)
    mm = data.get('mm')
    filter = data.get('filter')
    zresolution = data.get('zresolution')
    accum = data.get('accum')
    vector = data.get('vector')
    logger.debug("Starting the computation")
    message=complete._process_all(dem, outdir, accum, filter, mm, zresolution, vector)
    return jsonify(
        {   'message': message,
            'outdir': data.get('outdir'),
            'dem': dem,
            'mm': mm,
            'filter': filter,
            'zresolution': zresolution,
            'accum': accum,
            'vector': vector,
            'finished': datetime.now().isoformat(),
            'status': 'Success'
        }
    ), 200

@app.route('/logrotate', methods=['GET'])
def logrotate():
    """Rotate the log file."""
    file_handler.doRollover()
    return jsonify({'message': 'Log file rotated'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
