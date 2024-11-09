import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
} from '@mui/material';

const MapOptions = ({ mapStyle, onMapStyleChange, threshold, onThresholdChange }) => {
  return (
    <Box sx={{ mt: 4 }}>
      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Map Style</InputLabel>
        <Select
          value={mapStyle}
          onChange={(e) => onMapStyleChange(e.target.value)}
          label="Map Style"
        >
          <MenuItem value="open-street-map">Open Street Map</MenuItem>
          <MenuItem value="carto-positron">Carto Positron</MenuItem>
          <MenuItem value="carto-darkmatter">Carto Dark Matter</MenuItem>
          <MenuItem value="stamen-terrain">Stamen Terrain</MenuItem>
        </Select>
      </FormControl>

      <Box>
        <Typography gutterBottom>
          Prediction Threshold: {threshold.toFixed(2)}
        </Typography>
        <Slider
          value={threshold}
          onChange={(e, value) => onThresholdChange(value)}
          min={0}
          max={1}
          step={0.05}
          marks
          valueLabelDisplay="auto"
        />
      </Box>
    </Box>
  );
};

export default MapOptions;