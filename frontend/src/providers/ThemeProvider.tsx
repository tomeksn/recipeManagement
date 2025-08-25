import React, { createContext, useContext, useMemo, useState } from 'react';
import {
  ThemeProvider as MuiThemeProvider,
  createTheme,
  Theme,
} from '@mui/material/styles';
import { useMediaQuery } from '@mui/material';

// Trello-inspired color palette
const trelloColors = {
  primary: {
    main: '#0079bf', // Trello blue
    light: '#4d9cc7',
    dark: '#005a8b',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#838c91', // Trello gray
    light: '#a6b1b7',
    dark: '#5e6c75',
    contrastText: '#ffffff',
  },
  success: {
    main: '#61bd4f', // Trello green
    light: '#8acc6f',
    dark: '#519839',
    contrastText: '#ffffff',
  },
  warning: {
    main: '#f2d600', // Trello yellow
    light: '#f5e233',
    dark: '#d4bb00',
    contrastText: '#000000',
  },
  error: {
    main: '#eb5a46', // Trello red
    light: '#ef7b6b',
    dark: '#c44237',
    contrastText: '#ffffff',
  },
  info: {
    main: '#c377e0', // Trello purple
    light: '#cf92e6',
    dark: '#a05db5',
    contrastText: '#ffffff',
  },
};

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    ...trelloColors,
    background: {
      default: '#f5f6f8', // Light Trello background
      paper: '#ffffff',
    },
    text: {
      primary: '#172b4d',
      secondary: '#5e6c84',
    },
    divider: '#dfe1e6',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif',
    h1: {
      fontWeight: 600,
      fontSize: '2.5rem',
      lineHeight: 1.2,
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      lineHeight: 1.3,
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.125rem',
      lineHeight: 1.4,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 500,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
  shadows: [
    'none',
    '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
    '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
    '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
    '0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)',
    // Additional shadows...
    ...Array(19).fill('0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)'),
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          '&:hover': {
            boxShadow: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 8px rgba(0,0,0,0.16), 0 4px 8px rgba(0,0,0,0.23)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 16,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          color: '#172b4d',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #dfe1e6',
          backgroundColor: '#f5f6f8',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          '&.Mui-selected': {
            backgroundColor: '#e4f0f6',
            color: '#0079bf',
            '&:hover': {
              backgroundColor: '#d0e7f0',
            },
          },
        },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    ...trelloColors,
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b3b3b3',
    },
    divider: '#333333',
  },
  typography: lightTheme.typography,
  shape: lightTheme.shape,
  shadows: lightTheme.shadows,
  components: {
    ...lightTheme.components,
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          color: '#ffffff',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #333333',
          backgroundColor: '#1e1e1e',
        },
      },
    },
  },
});

interface ThemeContextValue {
  theme: Theme;
  mode: 'light' | 'dark';
  toggleColorMode: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState<'light' | 'dark'>(
    () => {
      const saved = localStorage.getItem('theme-mode');
      return (saved as 'light' | 'dark') || (prefersDarkMode ? 'dark' : 'light');
    }
  );

  const theme = useMemo(() => {
    return mode === 'dark' ? darkTheme : lightTheme;
  }, [mode]);

  const toggleColorMode = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('theme-mode', newMode);
  };

  const contextValue = useMemo(
    () => ({
      theme,
      mode,
      toggleColorMode,
    }),
    [theme, mode, toggleColorMode]
  );

  return (
    <ThemeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}