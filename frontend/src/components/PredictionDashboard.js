import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';
import InputSection from './InputSection';
import MapOptions from './MapOptions';
import StatusSection from './StatusSection';
import PredictionMap from './PredictionMap';
import { predictEarthquakes } from '../services/api';

const PredictionDashboard = () => {
  const [predictionData, setPredictionData] = useState(null);
  const [status, setStatus] = useState('ready');
  const [mapStyle, setMapStyle] = useState('open-street-map');
  const [threshold, setThreshold] = useState(0.5);
  const [error, setError] = useState(null);

  const handlePrediction = async (dateTime) => {
    try {
      setStatus('loading');
      const data = await predictEarthquakes(dateTime);
      setPredictionData(data);
      setStatus('success');
    } catch (error) {
      setStatus('error');
      setError(error.message);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Typography variant="h3" gutterBottom align="center">
          Earthquake Prediction System
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <InputSection onPredict={handlePrediction} />
              <MapOptions 
                mapStyle={mapStyle}
                onMapStyleChange={setMapStyle}
                threshold={threshold}
                onThresholdChange={setThreshold}
              />
              <StatusSection status={status} />
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: '700px' }}>
              <PredictionMap 
                data={predictionData}
                mapStyle={mapStyle}
                threshold={threshold}
              />
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      <Snackbar 
        open={!!error} 
        autoHideDuration={6000} 
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PredictionDashboard;