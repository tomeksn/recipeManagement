import React, { useState } from 'react';
import {
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Typography,
  Divider,
  ListItemIcon,
} from '@mui/material';
import {
  AccountCircle,
  Settings,
  Logout,
  Person,
} from '@mui/icons-material';

import { User } from '@/types/auth';
import { useAuth } from '@/hooks/useAuth';

interface UserMenuProps {
  user: User | null;
}

export function UserMenu({ user }: UserMenuProps) {
  const { logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    logout();
  };

  if (!user) {
    return (
      <IconButton color='inherit'>
        <AccountCircle />
      </IconButton>
    );
  }

  const getInitials = (name: string | undefined) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Box>
      <IconButton
        onClick={handleClick}
        size='small'
        sx={{ ml: 2 }}
        aria-controls={open ? 'user-menu' : undefined}
        aria-haspopup='true'
        aria-expanded={open ? 'true' : undefined}
      >
        <Avatar
          src={user.avatar}
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.main',
            fontSize: '0.875rem',
            fontWeight: 600,
          }}
        >
          {!user.avatar && getInitials(user.name)}
        </Avatar>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        id='user-menu'
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 3,
          sx: {
            mt: 1.5,
            minWidth: 200,
            '& .MuiAvatar-root': {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* User info */}
        <Box sx={{ px: 2, py: 1.5 }}>
          <Typography variant='subtitle2' sx={{ fontWeight: 600 }}>
            {user.name || 'Unknown User'}
          </Typography>
          <Typography variant='body2' color='text.secondary'>
            {user.email || 'No email'}
          </Typography>
          {user.role && (
            <Typography
              variant='caption'
              sx={{
                px: 1,
                py: 0.25,
                mt: 0.5,
                borderRadius: 1,
                bgcolor: 'primary.main',
                color: 'white',
                fontWeight: 500,
                display: 'inline-block',
                textTransform: 'capitalize',
              }}
            >
              {user.role}
            </Typography>
          )}
        </Box>

        <Divider />

        {/* Menu items */}
        <MenuItem onClick={handleClose}>
          <ListItemIcon>
            <Person fontSize='small' />
          </ListItemIcon>
          Profile
        </MenuItem>

        <MenuItem onClick={handleClose}>
          <ListItemIcon>
            <Settings fontSize='small' />
          </ListItemIcon>
          Settings
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize='small' />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
}