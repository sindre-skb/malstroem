from flask import Flask, request, jsonify
import secrets
from datetime import datetime
import sys
import malstroem.scripts.complete as complete



# Define similar functions for other subcommands...

# Now you can call these functions directly from your other Python script

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
    dem = data.get('dem')
    outdir = data.get('outdir')
    mm = data.get('mm')
    filter = data.get('filter')
    zresolution = data.get('zresolution')
    accum = data.get('accum')
    vector = data.get('vector')
    message=complete._process_all(dem, outdir, accum, filter, mm, zresolution, vector)
    return jsonify(
        {   'message': message,
            'outdir': outdir,
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
