import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  Inventory,
  Restaurant,
  Calculate,
  CloudUpload,
  Analytics,
  Settings,
  Help,
} from '@mui/icons-material';

interface SidebarProps {
  onItemClick?: () => void;
}

const menuItems = [
  {
    text: 'Dashboard',
    icon: Dashboard,
    path: '/',
    description: 'Overview and quick actions',
  },
  {
    text: 'Products',
    icon: Inventory,
    path: '/products',
    description: 'Manage your product catalog',
  },
  {
    text: 'Recipes',
    icon: Restaurant,
    path: '/recipes',
    description: 'Create and edit recipes',
  },
  {
    text: 'Calculator',
    icon: Calculate,
    path: '/calculator',
    description: 'Scale recipes and calculate ingredients',
    badge: 'New',
  },
  {
    text: 'Import Data',
    icon: CloudUpload,
    path: '/import',
    description: 'Import products and recipes from files',
    badge: 'New',
  },
];

const secondaryItems = [
  {
    text: 'Analytics',
    icon: Analytics,
    path: '/analytics',
    description: 'Usage statistics and insights',
    disabled: true,
  },
  {
    text: 'Settings',
    icon: Settings,
    path: '/settings',
    description: 'Application preferences',
    disabled: true,
  },
  {
    text: 'Help',
    icon: Help,
    path: '/help',
    description: 'Documentation and support',
    disabled: true,
  },
];

export function Sidebar({ onItemClick }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigation = (path: string) => {
    navigate(path);
    onItemClick?.();
  };

  const isSelected = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Brand */}
      <Toolbar sx={{ px: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 1,
              background: 'linear-gradient(135deg, #0079bf 0%, #005a8b 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1.2rem',
            }}
          >
            R
          </Box>
          <Typography
            variant='h6'
            sx={{
              fontWeight: 600,
              background: 'linear-gradient(135deg, #0079bf 0%, #005a8b 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Recipe Mgmt
          </Typography>
        </Box>
      </Toolbar>

      <Divider />

      {/* Main Navigation */}
      <Box sx={{ flex: 1, px: 2, py: 1 }}>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.path}
              selected={isSelected(item.path)}
              onClick={() => handleNavigation(item.path)}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon>
                <item.icon />
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                secondary={item.description}
                primaryTypographyProps={{
                  fontWeight: isSelected(item.path) ? 600 : 500,
                  fontSize: '0.875rem',
                }}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  sx: {
                    color: isSelected(item.path) ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  },
                }}
              />
              {item.badge && (
                <Chip
                  label={item.badge}
                  size='small'
                  color='secondary'
                  sx={{
                    height: 20,
                    fontSize: '0.625rem',
                    fontWeight: 600,
                  }}
                />
              )}
            </ListItemButton>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        {/* Secondary Navigation */}
        <List>
          <Typography
            variant='overline'
            sx={{
              px: 2,
              py: 1,
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'text.secondary',
            }}
          >
            More
          </Typography>
          {secondaryItems.map((item) => (
            <ListItemButton
              key={item.path}
              selected={isSelected(item.path)}
              onClick={() => !item.disabled && handleNavigation(item.path)}
              disabled={item.disabled}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover:not(.Mui-disabled)': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon>
                <item.icon />
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                secondary={item.description}
                primaryTypographyProps={{
                  fontWeight: isSelected(item.path) ? 600 : 500,
                  fontSize: '0.875rem',
                }}
                secondaryTypographyProps={{
                  fontSize: '0.75rem',
                  sx: {
                    color: isSelected(item.path) ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  },
                }}
              />
            </ListItemButton>
          ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2 }}>
        <Typography
          variant='caption'
          sx={{
            color: 'text.secondary',
            textAlign: 'center',
            display: 'block',
          }}
        >
          Recipe Management v1.0.0
        </Typography>
      </Box>
    </Box>
  );
}