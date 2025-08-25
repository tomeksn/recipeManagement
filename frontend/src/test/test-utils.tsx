import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';
import { vi, beforeEach } from 'vitest';

// Create a test theme (simplified version of the main theme)
const testTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Turn off retries for tests
        cacheTime: 0, // Disable cache for tests
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider theme={testTheme}>
          {children}
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Re-export everything
export { userEvent } from '@testing-library/user-event';

// Helper function to create a test query client
export const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
});

// Mock functions for common props
export const mockNavigate = vi.fn();
export const mockOnClose = vi.fn();
export const mockOnSubmit = vi.fn();
export const mockOnDelete = vi.fn();
export const mockOnEdit = vi.fn();

// Reset mocks before each test
beforeEach(() => {
  mockNavigate.mockReset();
  mockOnClose.mockReset();
  mockOnSubmit.mockReset();
  mockOnDelete.mockReset();
  mockOnEdit.mockReset();
});