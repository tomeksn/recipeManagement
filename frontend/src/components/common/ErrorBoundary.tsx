import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Alert,
  AlertTitle,
  Stack,
} from '@mui/material';
import { Refresh, BugReport } from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });

    // Log error to monitoring service
    if (import.meta.env.PROD) {
      // TODO: Send to error reporting service
      console.error('Production error:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
      });
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
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
            <BugReport
              sx={{
                fontSize: 64,
                color: 'error.main',
                opacity: 0.8,
              }}
            />

            <Typography variant='h4' component='h1' gutterBottom>
              Oops! Something went wrong
            </Typography>

            <Typography variant='body1' color='text.secondary' sx={{ maxWidth: 500 }}>
              We're sorry, but an unexpected error occurred. This has been logged and we'll look into it.
            </Typography>

            {this.state.error && (
              <Alert severity='error' sx={{ width: '100%', textAlign: 'left' }}>
                <AlertTitle>Error Details</AlertTitle>
                {this.state.error.message}
              </Alert>
            )}

            <Stack direction='row' spacing={2}>
              <Button
                variant='contained'
                startIcon={<Refresh />}
                onClick={this.handleReload}
              >
                Reload Page
              </Button>
              
              <Button
                variant='outlined'
                onClick={this.handleReset}
              >
                Try Again
              </Button>
            </Stack>

            {import.meta.env.DEV && this.state.error && (
              <Box
                sx={{
                  mt: 4,
                  p: 2,
                  backgroundColor: 'grey.100',
                  borderRadius: 1,
                  textAlign: 'left',
                  width: '100%',
                  maxHeight: 300,
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                }}
              >
                <Typography variant='body2' sx={{ fontWeight: 600, mb: 1 }}>
                  Error Stack (Development Only):
                </Typography>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                  {this.state.error.stack}
                </pre>
                {this.state.errorInfo && (
                  <>
                    <Typography variant='body2' sx={{ fontWeight: 600, mt: 2, mb: 1 }}>
                      Component Stack:
                    </Typography>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </>
                )}
              </Box>
            )}
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}