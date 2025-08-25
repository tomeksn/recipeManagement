import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4,
  Brightness7,
} from '@mui/icons-material';

import { User } from '@/types/auth';
import { useTheme as useCustomTheme } from '@/providers/ThemeProvider';
import { Sidebar } from './Sidebar';
import { UserMenu } from './UserMenu';

const DRAWER_WIDTH = 280;

interface AppLayoutProps {
  children: React.ReactNode;
  user: User | null;
}

export function AppLayout({ children, user }: AppLayoutProps) {
  const theme = useTheme();
  const { mode, toggleColorMode } = useCustomTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position='fixed'
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          zIndex: theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color='inherit'
            aria-label='open drawer'
            edge='start'
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography
            variant='h6'
            noWrap
            component='div'
            sx={{ flexGrow: 1, fontWeight: 600 }}
          >
            Recipe Management
          </Typography>

          {/* Theme toggle */}
          <IconButton
            sx={{ ml: 1 }}
            onClick={toggleColorMode}
            color='inherit'
            aria-label='toggle theme'
          >
            {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          {/* User menu */}
          <UserMenu user={user} />
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component='nav'
        sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant='temporary'
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          <Sidebar onItemClick={() => setMobileOpen(false)} />
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant='permanent'
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
          open
        >
          <Sidebar />
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component='main'
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar /> {/* Spacer for fixed AppBar */}
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}