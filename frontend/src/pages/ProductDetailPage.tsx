import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  Breadcrumbs,
  Link,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  Home,
  Inventory,
  Receipt
} from '@mui/icons-material';

import { productService } from '@/services/productService';
import { Product } from '@/types';
import { ProductFormDialog, DeleteProductDialog } from '@/components/products';

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', id],
    queryFn: () => productService.getProduct(id!),
    enabled: !!id,
  });

  const getTypeColor = (type: Product['type']) => {
    switch (type) {
      case 'standard': return 'primary';
      case 'semi-product': return 'secondary';
      case 'kit': return 'success';
      default: return 'default';
    }
  };

  const getTypeLabel = (type: Product['type']) => {
    switch (type) {
      case 'standard': return 'Standardowy';
      case 'semi-product': return 'Półprodukt';
      case 'kit': return 'Zestaw';
      default: return type;
    }
  };

  const getUnitLabel = (unit: Product['unit']) => {
    return unit === 'piece' ? 'sztuki' : 'gramy';
  };

  const handleDeleteSuccess = () => {
    navigate('/products', { replace: true });
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !product) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error ? 'Failed to load product details' : 'Product not found'}
        </Alert>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/products')}
        >
          Back to Products
        </Button>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{product.name} - Recipe Management System</title>
      </Helmet>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link
            component="button"
            variant="body2"
            onClick={() => navigate('/')}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <Home fontSize="small" />
            Home
          </Link>
          <Link
            component="button"
            variant="body2"
            onClick={() => navigate('/products')}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <Inventory fontSize="small" />
            Products
          </Link>
          <Typography color="text.primary" variant="body2">
            {product.name}
          </Typography>
        </Breadcrumbs>

        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              {product.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={getTypeLabel(product.type)} 
                color={getTypeColor(product.type) as any}
                size="medium"
              />
              <Chip 
                label={`Jednostka: ${getUnitLabel(product.unit)}`}
                variant="outlined"
                size="medium"
              />
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={() => navigate('/products')} title="Back to products">
              <ArrowBack />
            </IconButton>
            <Button
              variant="outlined"
              startIcon={<Edit />}
              onClick={() => setEditDialogOpen(true)}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Delete
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Main Info */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Product Information
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Description
                  </Typography>
                  <Typography variant="body1">
                    {product.description || 'No description provided'}
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Category
                  </Typography>
                  <Typography variant="body1">
                    {product.category || 'Uncategorized'}
                  </Typography>
                </Box>

                {product.tags && product.tags.length > 0 && (
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Tags
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {product.tags.map((tag) => (
                        <Chip 
                          key={tag}
                          label={tag} 
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Recipes Section */}
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Recipes
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Receipt />}
                    onClick={() => navigate(`/recipes/new?product=${product.id}`)}
                  >
                    Create Recipe
                  </Button>
                </Box>
                <Divider sx={{ mb: 2 }} />

                <Alert severity="info">
                  Recipe management will be implemented in the next phase. 
                  For now, you can create and manage products.
                </Alert>
              </CardContent>
            </Card>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <List dense>
                <ListItem>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Receipt />}
                    onClick={() => navigate(`/recipes/new?product=${product.id}`)}
                  >
                    Create Recipe
                  </Button>
                </ListItem>
                <ListItem>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Edit />}
                    onClick={() => setEditDialogOpen(true)}
                  >
                    Edit Product
                  </Button>
                </ListItem>
              </List>
            </Paper>

            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Product Details
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="ID"
                    secondary={product.id}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Created"
                    secondary={new Date(product.created_at).toLocaleDateString()}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Last Updated"
                    secondary={new Date(product.updated_at).toLocaleDateString()}
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Dialogs */}
      <ProductFormDialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        product={product}
        title="Edit Product"
      />

      <DeleteProductDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        product={product}
      />
    </>
  );
}