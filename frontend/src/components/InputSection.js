import React from 'react';
import {
  Box,
  Button,
  Stack,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import dayjs from 'dayjs';

const InputSection = ({ onPredict }) => {
  const [selectedDate, setSelectedDate] = React.useState(dayjs());
  const [selectedTime, setSelectedTime] = React.useState(dayjs());

  const handlePredict = () => {
    const dateTime = {
      date: selectedDate.format('YYYY/MM/DD'),
      time: selectedTime.format('HH:mm:ss'),
    };
    onPredict(dateTime);
  };

  return (
    <Stack spacing={3}>
      <DatePicker
        label="Select Date"
        value={selectedDate}
        onChange={setSelectedDate}
        slotProps={{
          textField: {
            fullWidth: true,
            size: "large"
          },
        }}
      />
      
      <TimePicker
        label="Select Time"
        value={selectedTime}
        onChange={setSelectedTime}
        slotProps={{
          textField: {
            fullWidth: true,
            size: "large"
          },
        }}
      />
      
      <Button
        variant="contained"
        size="large"
        onClick={handlePredict}
        sx={{ py: 1.5 }}
      >
        Generate Prediction Map
      </Button>
    </Stack>
  );
};

export default InputSection;