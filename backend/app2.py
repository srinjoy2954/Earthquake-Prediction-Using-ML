from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import kagglehub

app = Flask(__name__)
CORS(app)

# Load the dataset from Kaggle
try:
    # Download and load the dataset
    dataset_path = kagglehub.dataset_download(
        "alessandrolobello/the-ultimate-earthquake-dataset-from-1990-2023"
    )
    
    # Load the data
    data = pd.read_csv(dataset_path)  # Using first file in the dataset
    
    # Convert time to datetime
    data['datetime'] = pd.to_datetime(data['time'], unit='ms')
    
    # Extract day of week and hour for predictions
    data['DayOfWeek'] = data['datetime'].dt.dayofweek
    data['Hour'] = data['datetime'].dt.hour
    
    # Load the trained model
    model = joblib.load('earthquake_prediction_model.joblib')
    
    print("Dataset and model loaded successfully")
    print(f"Total earthquakes in dataset: {len(data)}")
    print(f"Date range: {data['datetime'].min()} to {data['datetime'].max()}")
    
except Exception as e:
    print(f"Error loading dataset or model: {e}")

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
        lat_range = np.linspace(data['latitude'].min(), data['latitude'].max(), 20)
        lon_range = np.linspace(data['longitude'].min(), data['longitude'].max(), 20)
        
        predictions = []
        
        # Calculate average values
        avg_significance = data['significance'].mean()
        avg_depth = data['depth'].mean()
        avg_magnitude = data['magnitudo'].mean()
        
        # Get recent data (last 30 days from selected date)
        recent_mask = (data['datetime'] <= timestamp) & \
                     (data['datetime'] >= timestamp - pd.Timedelta(days=30))
        recent_data = data[recent_mask]

        # Calculate predictions for each point
        for lat in lat_range:
            for lon in lon_range:
                # Check for nearby earthquakes in recent data
                radius = 0.5
                mask = ((recent_data['latitude'] - lat).abs() <= radius) & \
                       ((recent_data['longitude'] - lon).abs() <= radius)
                local_data = recent_data[mask]
                
                if len(local_data) > 0:
                    depth = local_data['depth'].mean()
                    magnitude = local_data['magnitudo'].mean()
                    significance = local_data['significance'].mean()
                    tsunami_risk = local_data['tsunami'].mean() > 0
                else:
                    depth = avg_depth
                    magnitude = avg_magnitude
                    significance = avg_significance
                    tsunami_risk = False

                # Prepare input data for model
                input_data = pd.DataFrame([[
                    lat, 
                    lon, 
                    depth,
                    magnitude,
                    significance,
                    day_of_week,
                    hour
                ]], columns=[
                    'latitude',
                    'longitude',
                    'depth',
                    'magnitudo',
                    'significance',
                    'DayOfWeek',
                    'Hour'
                ])
                
                prediction = model.predict_proba(input_data)[0][1]
                
                if prediction > 0.5:  # Threshold can be adjusted
                    estimated_magnitude = (local_data['magnitudo'].max() * prediction 
                                         if len(local_data) > 0 else magnitude * prediction)
                    predictions.append({
                        'lat': float(lat),
                        'lon': float(lon),
                        'magnitude': float(estimated_magnitude),
                        'probability': float(prediction),
                        'depth': float(depth),
                        'tsunami_risk': bool(tsunami_risk),
                        'significance': float(significance)
                    })

        # Prepare historical data (last 90 days)
        historical_mask = (data['datetime'] <= timestamp) & \
                         (data['datetime'] >= timestamp - pd.Timedelta(days=90))
        historical_data = data[historical_mask]
        
        historical = {
            'lat': historical_data['latitude'].tolist(),
            'lon': historical_data['longitude'].tolist(),
            'magnitude': historical_data['magnitudo'].tolist(),
            'depth': historical_data['depth'].tolist(),
            'place': historical_data['place'].tolist(),
            'tsunami': historical_data['tsunami'].tolist(),
            'significance': historical_data['significance'].tolist(),
            'dates': historical_data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        }

        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'historical': historical,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': {
                'total_events': len(historical_data),
                'avg_magnitude': float(historical_data['magnitudo'].mean()),
                'max_magnitude': float(historical_data['magnitudo'].max()),
                'tsunami_events': int(historical_data['tsunami'].sum())
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)