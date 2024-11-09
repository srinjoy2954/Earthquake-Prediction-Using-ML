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
        
        # Combine date and time
        target_time = pd.to_datetime(f"{date_str} {time_str}")
        day_of_week = target_time.dayofweek
        hour = target_time.hour

        # Time-based factors
        hour_factor = np.sin(2 * np.pi * hour / 24)  # Varies throughout the day
        day_factor = np.sin(2 * np.pi * day_of_week / 7)  # Varies throughout the week
        
        # Create dynamic prediction grid based on time
        base_lat = data['Latitude(deg)'].mean()
        base_lon = data['Longitude(deg)'].mean()
        
        # Vary the grid based on time factors
        grid_size = 10 + 5 * abs(hour_factor)  # Grid size varies by hour
        grid_spread = 2 + abs(day_factor)  # Spread varies by day

        lat_range = np.linspace(base_lat - grid_spread, base_lat + grid_spread, int(grid_size))
        lon_range = np.linspace(base_lon - grid_spread, base_lon + grid_spread, int(grid_size))
        
        predictions = []
        
        # Calculate time-sensitive averages
        time_window = 3  # hours
        if 'datetime' in data.columns:
            # Filter data for similar times of day
            time_mask = (data['datetime'].dt.hour >= (hour - time_window) % 24) & \
                       (data['datetime'].dt.hour <= (hour + time_window) % 24)
            relevant_data = data[time_mask]
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
                # Add time-based variations to input parameters
                time_varied_depth = avg_depth * (1 + 0.2 * hour_factor)
                time_varied_magnitude = avg_magnitude * (1 + 0.15 * day_factor)

                input_data = pd.DataFrame([[lat, lon, 
                                          time_varied_depth,
                                          time_varied_magnitude, 
                                          avg_stations, avg_gap, avg_close, avg_rms, 
                                          day_of_week, hour]],
                                        columns=['Latitude(deg)', 'Longitude(deg)', 'Depth(km)', 
                                                'Magnitude(ergs)', 'No_of_Stations', 'Gap', 
                                                'Close', 'RMS', 'DayOfWeek', 'Hour'])
                
                # Get base prediction
                base_prediction = model.predict_proba(input_data)[0][1]
                
                # Modify prediction based on time factors
                time_modified_prediction = base_prediction * (1 + 0.2 * hour_factor + 0.1 * day_factor)
                time_modified_prediction = max(0, min(1, time_modified_prediction))  # Keep between 0 and 1
                
                if time_modified_prediction > 0.5:  # Threshold for significant predictions
                    # Calculate time-sensitive magnitude
                    estimated_magnitude = time_varied_magnitude * (0.5 + time_modified_prediction/2)
                    
                    predictions.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'probability': float(time_modified_prediction),
                        'magnitude': float(estimated_magnitude)
                    })

        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'timestamp': target_time.strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': {
                'hour_factor': float(hour_factor),
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