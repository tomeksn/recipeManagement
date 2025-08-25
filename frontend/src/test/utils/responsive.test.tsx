import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { useMediaQuery } from '@mui/material';
import { Box, Typography } from '@mui/material';

// Test component that uses responsive breakpoints
const ResponsiveTestComponent = () => {
  const theme = createTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));

  return (
    <ThemeProvider theme={theme}>
      <Box>
        {isMobile && <Typography data-testid="mobile-view">Mobile View</Typography>}
        {isTablet && <Typography data-testid="tablet-view">Tablet View</Typography>}
        {isDesktop && <Typography data-testid="desktop-view">Desktop View</Typography>}
        
        <Box
          sx={{
            display: { xs: 'block', sm: 'flex' },
            flexDirection: { sm: 'row', md: 'column' },
            gap: { xs: 1, sm: 2, md: 3 },
          }}
          data-testid="responsive-box"
        >
          <Typography>Responsive content</Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

describe('Responsive Design Tests', () => {
  let originalMatchMedia: typeof window.matchMedia;

  beforeEach(() => {
    // Store original matchMedia
    originalMatchMedia = window.matchMedia;
  });

  afterEach(() => {
    // Restore original matchMedia
    window.matchMedia = originalMatchMedia;
  });

  const mockMatchMedia = (width: number) => {
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    // Mock specific breakpoint queries
    window.matchMedia = vi.fn().mockImplementation((query) => {
      const breakpoints = {
        '(max-width: 599.95px)': width < 600, // xs
        '(min-width: 600px) and (max-width: 1199.95px)': width >= 600 && width < 1200, // sm-lg
        '(min-width: 1200px)': width >= 1200, // lg+
      };
      
      return {
        matches: breakpoints[query] || false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      };
    });
  };

  it('renders mobile view on small screens', () => {
    mockMatchMedia(375); // Mobile width
    
    render(<ResponsiveTestComponent />);
    
    expect(screen.getByTestId('mobile-view')).toBeInTheDocument();
    expect(screen.queryByTestId('tablet-view')).not.toBeInTheDocument();
    expect(screen.queryByTestId('desktop-view')).not.toBeInTheDocument();
  });

  it('renders tablet view on medium screens', () => {
    mockMatchMedia(768); // Tablet width
    
    render(<ResponsiveTestComponent />);
    
    expect(screen.getByTestId('tablet-view')).toBeInTheDocument();
    expect(screen.queryByTestId('mobile-view')).not.toBeInTheDocument();
    expect(screen.queryByTestId('desktop-view')).not.toBeInTheDocument();
  });

  it('renders desktop view on large screens', () => {
    mockMatchMedia(1440); // Desktop width
    
    render(<ResponsiveTestComponent />);
    
    expect(screen.getByTestId('desktop-view')).toBeInTheDocument();
    expect(screen.queryByTestId('mobile-view')).not.toBeInTheDocument();
    expect(screen.queryByTestId('tablet-view')).not.toBeInTheDocument();
  });

  it('applies responsive styles correctly', () => {
    mockMatchMedia(375); // Mobile width
    
    const { container } = render(<ResponsiveTestComponent />);
    const responsiveBox = container.querySelector('[data-testid="responsive-box"]');
    
    expect(responsiveBox).toBeInTheDocument();
    // Note: In a real test, you might want to check computed styles
    // This is a simplified version due to jsdom limitations
  });
});