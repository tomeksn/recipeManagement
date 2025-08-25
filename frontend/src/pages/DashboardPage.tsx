import React from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Inventory,
  Restaurant,
  Calculate,
  Add,
  AccessTime,
} from '@mui/icons-material';

export default function DashboardPage() {
  return (
    <>
      <Helmet>
        <title>Dashboard - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant='h4' component='h1' gutterBottom sx={{ fontWeight: 600 }}>
            Dashboard
          </Typography>
          <Typography variant='body1' color='text.secondary'>
            Welcome back! Here's what's happening with your recipes.
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Inventory sx={{ color: 'primary.main', mr: 1 }} />
                  <Typography variant='h6' component='div'>
                    Products
                  </Typography>
                </Box>
                <Typography variant='h3' component='div' sx={{ fontWeight: 600 }}>
                  247
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  Total products in catalog
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Restaurant sx={{ color: 'success.main', mr: 1 }} />
                  <Typography variant='h6' component='div'>
                    Recipes
                  </Typography>
                </Box>
                <Typography variant='h3' component='div' sx={{ fontWeight: 600 }}>
                  89
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  Active recipes
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Calculate sx={{ color: 'warning.main', mr: 1 }} />
                  <Typography variant='h6' component='div'>
                    Calculations
                  </Typography>
                </Box>
                <Typography variant='h3' component='div' sx={{ fontWeight: 600 }}>
                  1,234
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  This month
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUp sx={{ color: 'info.main', mr: 1 }} />
                  <Typography variant='h6' component='div'>
                    Growth
                  </Typography>
                </Box>
                <Typography variant='h3' component='div' sx={{ fontWeight: 600 }}>
                  +15%
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  vs last month
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Quick Actions */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant='h6' gutterBottom sx={{ fontWeight: 600 }}>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant='contained'
                    fullWidth
                    startIcon={<Add />}
                    sx={{ py: 2 }}
                  >
                    Add Product
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant='outlined'
                    fullWidth
                    startIcon={<Restaurant />}
                    sx={{ py: 2 }}
                  >
                    Create Recipe
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant='outlined'
                    fullWidth
                    startIcon={<Calculate />}
                    sx={{ py: 2 }}
                  >
                    Calculate Recipe
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Button
                    variant='outlined'
                    fullWidth
                    sx={{ py: 2 }}
                  >
                    Import Data
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant='h6' gutterBottom sx={{ fontWeight: 600 }}>
                Recent Activity
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <AccessTime fontSize='small' />
                  </ListItemIcon>
                  <ListItemText
                    primary='Chocolate Chip Cookies recipe updated'
                    secondary='2 hours ago'
                  />
                  <Chip label='Recipe' size='small' color='primary' />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AccessTime fontSize='small' />
                  </ListItemIcon>
                  <ListItemText
                    primary='New product "Vanilla Extract" added'
                    secondary='4 hours ago'
                  />
                  <Chip label='Product' size='small' color='success' />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AccessTime fontSize='small' />
                  </ListItemIcon>
                  <ListItemText
                    primary='Calculation for 500 cookies completed'
                    secondary='6 hours ago'
                  />
                  <Chip label='Calculation' size='small' color='warning' />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AccessTime fontSize='small' />
                  </ListItemIcon>
                  <ListItemText
                    primary='Bread recipe ingredients optimized'
                    secondary='1 day ago'
                  />
                  <Chip label='Recipe' size='small' color='primary' />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}