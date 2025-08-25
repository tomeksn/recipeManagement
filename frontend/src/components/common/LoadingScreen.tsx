import React from 'react';
import { Box, CircularProgress, Typography, useTheme } from '@mui/material';

interface LoadingScreenProps {
  message?: string;
  size?: number;
}

export function LoadingScreen({ 
  message = 'Loading...', 
  size = 48 
}: LoadingScreenProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
        color: 'white',
        gap: 3,
      }}
    >
      <CircularProgress
        size={size}
        thickness={4}
        sx={{
          color: 'white',
          '& .MuiCircularProgress-circle': {
            strokeLinecap: 'round',
          },
        }}
      />
      
      <Typography
        variant='h6'
        sx={{
          fontWeight: 500,
          opacity: 0.9,
          textAlign: 'center',
        }}
      >
        {message}
      </Typography>
    </Box>
  );
}