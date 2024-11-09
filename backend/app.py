from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

app = Flask(__name__)
CORS(app)

# Load your trained model and data
try:
    model = joblib.load('earthquake_prediction_model.joblib')
    data = pd.read_csv('Earthquake_data_processed.csv')  # Replace with your data file
except Exception as e:
    print(f"Error loading model or data: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get date and time from request
        request_data = request.json
        date_str = request_data.get('date')
        time_str = request_data.get('time')
        
        # Combine date and time
        timestamp = pd.to_datetime(f"{date_str} {time_str}")
        day_of_week = timestamp.dayofweek
        hour = timestamp.hour

        # Create prediction grid
        lat_range = np.linspace(data['Latitude(deg)'].min(), data['Latitude(deg)'].max(), 20)
        lon_range = np.linspace(data['Longitude(deg)'].min(), data['Longitude(deg)'].max(), 20)
        
        predictions = []
        
        # Calculate average values for parameters
        avg_stations = data['No_of_Stations'].mean()
        avg_gap = data['Gap'].mean()
        avg_close = data['Close'].mean()
        avg_rms = data['RMS'].mean()

        # Calculate predictions for each point
        for lat in lat_range:
            for lon in lon_range:
                radius = 0.5
                mask = ((data['Latitude(deg)'] - lat).abs() <= radius) & \
                       ((data['Longitude(deg)'] - lon).abs() <= radius)
                local_data = data[mask]
                
                if len(local_data) > 0:
                    depth = local_data['Depth(km)'].mean()
                    magnitude = local_data['Magnitude(ergs)'].mean()
                else:
                    depth = data['Depth(km)'].mean()
                    magnitude = data['Magnitude(ergs)'].mean()

                input_data = pd.DataFrame([[lat, lon, depth, magnitude, 
                                          avg_stations, avg_gap, avg_close, avg_rms, 
                                          day_of_week, hour]],
                                        columns=['Latitude(deg)', 'Longitude(deg)', 'Depth(km)', 
                                                'Magnitude(ergs)', 'No_of_Stations', 'Gap', 
                                                'Close', 'RMS', 'DayOfWeek', 'Hour'])
                
                prediction = model.predict_proba(input_data)[0][1]
                
                if prediction > 0.5:  # Threshold can be adjusted
                    estimated_magnitude = (local_data['Magnitude(ergs)'].max() * prediction 
                                         if len(local_data) > 0 else magnitude * prediction)
                    predictions.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'magnitude': float(estimated_magnitude),
                        'probability': float(prediction)
                    })

        # Prepare historical data
        historical_data = {
            'lat': data['Latitude(deg)'].tolist(),
            'lon': data['Longitude(deg)'].tolist(),
            'magnitude': data['Magnitude(ergs)'].tolist()
        }

        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'historical': historical_data,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)