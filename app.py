from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_data():
    # Example of processing data
    data = request.json
    # Assuming 'run_malstroem_processing' is a function that handles your data
    result = run_malstroem_processing(data)
    return jsonify(result)

def run_malstroem_processing(data):
    # Implement your processing logic here
    return {"status": "Success", "data": data}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
