from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data or basic route for your taxi meter API
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Taximetro API!",
        "status": "running"
    })

# Example endpoint for calculating fare or receiving taximeter data
@app.route('/calculate', methods=['POST'])
def calculate_fare():
    data = request.get_json()
    
    # Simple placeholder logic for distance / fare
    distance = data.get('distance_km', 0.0)
    base_fare = 5.00
    per_km_rate = 2.50
    
    total_fare = base_fare + (distance * per_km_rate)
    
    return jsonify({
        "distance_km": distance,
        "total_fare": round(total_fare, 2)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)