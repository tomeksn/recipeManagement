import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Container,
  Typography,
  Button,
  Stack,
} from '@mui/material';
import { Home, ArrowBack, Search } from '@mui/icons-material';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <>
      <Helmet>
        <title>Page Not Found - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='md'>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            textAlign: 'center',
            gap: 3,
          }}
        >
          <Typography
            variant='h1'
            sx={{
              fontSize: '8rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #0079bf 0%, #005a8b 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1,
            }}
          >
            404
          </Typography>

          <Typography variant='h4' component='h1' gutterBottom sx={{ fontWeight: 600 }}>
            Page Not Found
          </Typography>

          <Typography
            variant='body1'
            color='text.secondary'
            sx={{ maxWidth: 500, mb: 2 }}
          >
            Sorry, we couldn't find the page you're looking for. The page might have been
            moved, deleted, or you might have entered the wrong URL.
          </Typography>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <Button
              variant='contained'
              startIcon={<Home />}
              onClick={() => navigate('/')}
              size='large'
            >
              Go Home
            </Button>
            
            <Button
              variant='outlined'
              startIcon={<ArrowBack />}
              onClick={() => navigate(-1)}
              size='large'
            >
              Go Back
            </Button>
            
            <Button
              variant='outlined'
              startIcon={<Search />}
              onClick={() => navigate('/products')}
              size='large'
            >
              Browse Products
            </Button>
          </Stack>

          <Box sx={{ mt: 4, opacity: 0.7 }}>
            <Typography variant='caption' color='text.secondary'>
              Error 404 - The requested page could not be found
            </Typography>
          </Box>
        </Box>
      </Container>
    </>
  );
}