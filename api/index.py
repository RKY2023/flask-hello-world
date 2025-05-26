from flask import Flask, request, jsonify

app = Flask(__name__)
@app.route('/')
def index():
    return "Welcome to the Flask app!"  
@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        "message": "This is a sample response from the Flask app."
    }
    return jsonify(data)
@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.json
    response = {
        "message": "Data received successfully.",
        "data": data
    }
    return jsonify(response), 201
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    data = request.json
    response = {
        "message": f"Data with ID {id} updated successfully.",
        "data": data
    }
    return jsonify(response), 200
if __name__ == '__main__':
    app.run(debug=True)
