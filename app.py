from flask import Flask, request, jsonify
import secrets
from datetime import datetime
import sys
from malstroem.scripts import complete as malstroem_complete



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

@app.route('/complete', methods=['POST'])
def complete():
    data = request.json
    dem = data['dem']
    outdir = data['outdir']
    mm = data['mm']
    filter = data['filter']
    zresolution = data['zresolution']
    accum = None
    vector = None
    return malstroem_complete._process_all(dem, outdir, accum, filter, mm, zresolution, vector)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
