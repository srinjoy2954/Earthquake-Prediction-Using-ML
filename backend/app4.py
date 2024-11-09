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
    data = pd.read_csv('Earthquake_data_processed.csv')
    
    # Convert date and time to datetime if they exist in your data
    if 'Date' in data.columns and 'Time' in data.columns:
        data['datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    
    print("Model and data loaded successfully")
except Exception as e:
    print(f"Error loading model or data: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get date and time from request
        request_data = request.json
        date_str = request_data.get('date')
        time_str = request_data.get('time')
        
        # Combine date and time for metadata purposes
        target_time = pd.to_datetime(f"{date_str} {time_str}")
        day_of_week = target_time.dayofweek
        hour = target_time.hour

        # Calculate time-based factors (used only for metadata)
        hour_factor = np.sin(2 * np.pi * hour / 24)
        day_factor = np.sin(2 * np.pi * day_of_week / 7)
        
        # Grid setup based on date
        base_lat = data['Latitude(deg)'].mean()
        base_lon = data['Longitude(deg)'].mean()
        grid_size = 10  # Fixed grid size
        grid_spread = 2 + 0.5 * np.sin(2 * np.pi * day_of_week / 7)  # Slight variability by day of week

        lat_range = np.linspace(base_lat - grid_spread, base_lat + grid_spread, int(grid_size))
        lon_range = np.linspace(base_lon - grid_spread, base_lon + grid_spread, int(grid_size))
        
        predictions = []
        
        # Filter data based on date
        if 'datetime' in data.columns:
            relevant_data = data[data['datetime'].dt.date == target_time.date()]
        else:
            relevant_data = data

        avg_stations = relevant_data['No_of_Stations'].mean()
        avg_gap = relevant_data['Gap'].mean()
        avg_close = relevant_data['Close'].mean()
        avg_rms = relevant_data['RMS'].mean()
        avg_magnitude = relevant_data['Magnitude(ergs)'].mean()
        avg_depth = relevant_data['Depth(km)'].mean()

        # Calculate predictions for each point
        for lat in lat_range:
            for lon in lon_range:
                input_data = pd.DataFrame([[lat, lon, avg_depth, avg_magnitude, 
                                            avg_stations, avg_gap, avg_close, avg_rms, 
                                            day_of_week]],
                                          columns=['Latitude(deg)', 'Longitude(deg)', 'Depth(km)', 
                                                   'Magnitude(ergs)', 'No_of_Stations', 'Gap', 
                                                   'Close', 'RMS', 'DayOfWeek'])
                
                base_prediction = model.predict_proba(input_data)[0][1]
                
                if base_prediction > 0.5:  # Threshold for significant predictions
                    estimated_magnitude = avg_magnitude * (0.5 + base_prediction / 2)
                    
                    predictions.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'probability': float(base_prediction),
                        'magnitude': float(estimated_magnitude)
                    })
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'timestamp': target_time.strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': {
                'hour': hour,
                'hour_factor': float(hour_factor),
                'day_of_week': day_of_week,
                'day_factor': float(day_factor),
                'prediction_count': len(predictions)
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
