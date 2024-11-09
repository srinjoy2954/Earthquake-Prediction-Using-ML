import React from 'react';
import {
  Box,
  LinearProgress,
  Typography,
} from '@mui/material';
import { CheckCircle, Error, Pending } from '@mui/icons-material';

const StatusSection = ({ status }) => {
  const getStatusInfo = () => {
    switch (status) {
      case 'loading':
        return {
          message: 'Generating predictions...',
          icon: <Pending color="primary" />,
          color: 'primary.main'
        };
      case 'success':
        return {
          message: 'Prediction map generated successfully!',
          icon: <CheckCircle color="success" />,
          color: 'success.main'
        };
      case 'error':
        return {
          message: 'Error generating predictions',
          icon: <Error color="error" />,
          color: 'error.main'
        };
      default:
        return {
          message: 'Ready to generate predictions...',
          icon: <Pending color="info" />,
          color: 'info.main'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <Box sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {statusInfo.icon}
        <Typography color={statusInfo.color}>
          {statusInfo.message}
        </Typography>
      </Box>
      {status === 'loading' && (
        <LinearProgress sx={{ mt: 2 }} />
      )}
    </Box>
  );
};

export default StatusSection;