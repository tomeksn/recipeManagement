import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Checkbox,
  Link,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff, Login } from '@mui/icons-material';
import { useForm } from 'react-hook-form';

import { LoginCredentials } from '@/types/auth';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();

  const onSubmit = async (data: LoginCredentials) => {
    await login(data);
  };

  return (
    <>
      <Helmet>
        <title>Login - Recipe Management System</title>
      </Helmet>

      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #0079bf 0%, #005a8b 100%)',
          py: 3,
        }}
      >
        <Container maxWidth='sm'>
          <Paper
            elevation={24}
            sx={{
              p: 4,
              borderRadius: 3,
              textAlign: 'center',
            }}
          >
            {/* Logo */}
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #0079bf 0%, #005a8b 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '2rem',
                mx: 'auto',
                mb: 3,
              }}
            >
              R
            </Box>

            <Typography variant='h4' component='h1' gutterBottom sx={{ fontWeight: 600 }}>
              Welcome Back
            </Typography>
            
            <Typography variant='body1' color='text.secondary' sx={{ mb: 4 }}>
              Sign in to your Recipe Management account
            </Typography>

            {error && (
              <Alert severity='error' sx={{ mb: 3, textAlign: 'left' }}>
                {error}
              </Alert>
            )}

            <Box component='form' onSubmit={handleSubmit(onSubmit)} sx={{ textAlign: 'left' }}>
              <TextField
                fullWidth
                label='Email Address'
                type='email'
                margin='normal'
                autoComplete='email'
                autoFocus
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
                error={!!errors.email}
                helperText={errors.email?.message}
              />

              <TextField
                fullWidth
                label='Password'
                type={showPassword ? 'text' : 'password'}
                margin='normal'
                autoComplete='current-password'
                {...register('password', {
                  required: 'Password is required',
                  minLength: {
                    value: 6,
                    message: 'Password must be at least 6 characters',
                  },
                })}
                error={!!errors.password}
                helperText={errors.password?.message}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position='end'>
                      <IconButton
                        aria-label='toggle password visibility'
                        onClick={() => setShowPassword(!showPassword)}
                        edge='end'
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <FormControlLabel
                control={
                  <Checkbox
                    {...register('remember_me')}
                    color='primary'
                  />
                }
                label='Remember me'
                sx={{ mt: 1, mb: 2 }}
              />

              <Button
                type='submit'
                fullWidth
                variant='contained'
                size='large'
                disabled={isLoading}
                startIcon={<Login />}
                sx={{ mt: 2, mb: 3, py: 1.5 }}
              >
                {isLoading ? 'Signing In...' : 'Sign In'}
              </Button>

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Link href='#' color='primary' sx={{ textDecoration: 'none' }}>
                  Forgot your password?
                </Link>
              </Box>

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant='body2' color='text.secondary'>
                  Don't have an account?{' '}
                  <Link href='#' color='primary' sx={{ textDecoration: 'none' }}>
                    Contact your administrator
                  </Link>
                </Typography>
              </Box>
            </Box>
          </Paper>

          {/* Demo credentials for development */}
          {import.meta.env.DEV && (
            <Paper sx={{ mt: 2, p: 2, bgcolor: 'info.light', color: 'info.contrastText' }}>
              <Typography variant='caption' sx={{ fontWeight: 600 }}>
                Demo Credentials (Development Only):
              </Typography>
              <br />
              <Typography variant='caption'>
                Email: admin@recipemanagement.com | Password: admin123
              </Typography>
            </Paper>
          )}
        </Container>
      </Box>
    </>
  );
}