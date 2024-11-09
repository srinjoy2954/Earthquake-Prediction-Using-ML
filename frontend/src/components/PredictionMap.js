import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import { Box, Typography } from '@mui/material';

const PredictionMap = ({ data, mapStyle, threshold }) => {
  const mapContainer = useRef(null);
  const plotRef = useRef(null);

  useEffect(() => {
    // Clean up function for previous plot
    return () => {
      if (plotRef.current) {
        Plotly.purge(plotRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!data || !data.predictions || !mapContainer.current) return;

    const { predictions, timestamp } = data;

    if (predictions.length === 0) return;

    // Create traces for the plot
    const magnitudeTrace = {
      type: 'scattermapbox',
      lat: predictions.map(p => p.lat),
      lon: predictions.map(p => p.lon),
      mode: 'markers',
      marker: {
        size: predictions.map(p => Math.max(8, p.magnitude * 3)),
        color: predictions.map(p => p.magnitude),
        colorscale: 'Viridis',
        opacity: 0.8,
        colorbar: {
          title: 'Magnitude',
          x: -0.15
        }
      },
      name: 'Predicted Magnitude',
      hovertemplate: 
        '<b>Predicted Earthquake</b><br>' +
        'Magnitude: %{marker.color:.1f}<br>' +
        'Probability: %{text:.0%}<br>' +
        'Latitude: %{lat:.4f}°<br>' +
        'Longitude: %{lon:.4f}°<br>' +
        '<extra></extra>',
      text: predictions.map(p => p.probability)
    };

    const probabilityTrace = {
      type: 'scattermapbox',
      lat: predictions.map(p => p.lat),
      lon: predictions.map(p => p.lon),
      mode: 'markers',
      marker: {
        size: 12,
        color: predictions.map(p => p.probability),
        colorscale: 'Reds',
        opacity: 0.6,
        colorbar: {
          title: 'Probability',
          x: 1.15
        }
      },
      name: 'Probability',
      hovertemplate: 
        '<b>Prediction Probability</b><br>' +
        'Probability: %{marker.color:.0%}<br>' +
        'Magnitude: %{text:.1f}<br>' +
        'Latitude: %{lat:.4f}°<br>' +
        'Longitude: %{lon:.4f}°<br>' +
        '<extra></extra>',
      text: predictions.map(p => p.magnitude)
    };

    const layout = {
      mapbox: {
        style: mapStyle || 'carto-positron',
        center: {
          lat: predictions[0]?.lat || 0,
          lon: predictions[0]?.lon || 0
        },
        zoom: 5
      },
      margin: { r: 80, t: 50, l: 80, b: 30 },
      height: 600,
      showlegend: true,
      legend: {
        x: 0.5,
        y: 1.1,
        xanchor: 'center',
        orientation: 'h'
      },
      title: {
        text: `Earthquake Predictions for ${timestamp}`,
        font: { size: 16 }
      }
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    // Create new plot
    Plotly.newPlot(mapContainer.current, [magnitudeTrace, probabilityTrace], layout, config)
      .then(() => {
        plotRef.current = mapContainer.current;
      })
      .catch(err => console.error('Error plotting:', err));

  }, [data, mapStyle, threshold]);

  if (!data) {
    return (
      <Box sx={{ 
        height: 600,
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #ddd',
        borderRadius: 1
      }}>
        <Typography variant="h6" color="text.secondary">
          Select date and time to view earthquake predictions
        </Typography>
      </Box>
    );
  }

  if (!data.predictions || data.predictions.length === 0) {
    return (
      <Box sx={{ 
        height: 600,
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #ddd',
        borderRadius: 1
      }}>
        <Typography variant="h6" color="text.secondary">
          No predictions found for the selected time
        </Typography>
      </Box>
    );
  }

  return (
    <div 
      ref={mapContainer} 
      style={{ 
        width: '100%', 
        height: 600,
        border: '1px solid #ddd',
        borderRadius: 4
      }} 
    />
  );
};

export default PredictionMap;