import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  Fab
} from '@mui/material';
import { Search, Add, Edit, Delete } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import { productService } from '@/services/productService';
import { Product } from '@/types';
import { ProductFormDialog, DeleteProductDialog } from '@/components/products';

export default function ProductsPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  
  // Dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['products', page, searchQuery],
    queryFn: () => searchQuery 
      ? productService.searchProducts(searchQuery, page, 10)
      : productService.getProducts(page, 10),
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
    return unit === 'piece' ? 'szt' : 'g';
  };

  return (
    <>
      <Helmet>
        <title>Products - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant='h4' component='h1' gutterBottom sx={{ fontWeight: 600 }}>
              Produkty
            </Typography>
            <Typography variant='body1' color='text.secondary'>
              Zarządzaj katalogiem produktów
            </Typography>
          </Box>

          <Fab 
            color="primary" 
            aria-label="add product"
            onClick={() => setCreateDialogOpen(true)}
          >
            <Add />
          </Fab>
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Szukaj produktów..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ maxWidth: 500 }}
          />
        </Box>

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Błąd podczas ładowania produktów
          </Alert>
        )}

        {data && (
          <>
            <Grid container spacing={3}>
              {data.items.map((product) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                  <Card 
                    elevation={2}
                    sx={{ 
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      cursor: 'pointer',
                      '&:hover': {
                        elevation: 6,
                        transform: 'translateY(-2px)',
                        transition: 'all 0.2s ease-in-out'
                      }
                    }}
                    onClick={() => navigate(`/products/${product.id}`)}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                        <Typography variant='h6' component='h2' noWrap>
                          {product.name}
                        </Typography>
                        <Chip 
                          label={getTypeLabel(product.type)} 
                          color={getTypeColor(product.type) as any}
                          size="small"
                        />
                      </Box>
                      
                      {product.description && (
                        <Typography 
                          variant='body2' 
                          color='text.secondary' 
                          sx={{ mb: 2, height: '40px', overflow: 'hidden' }}
                        >
                          {product.description}
                        </Typography>
                      )}

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant='body2' color='primary'>
                          Jednostka: {getUnitLabel(product.unit)}
                        </Typography>
                        {product.category && (
                          <Chip 
                            label={product.category} 
                            variant="outlined"
                            size="small"
                          />
                        )}
                      </Box>

                      {product.tags && product.tags.length > 0 && (
                        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {product.tags.slice(0, 3).map((tag) => (
                            <Chip 
                              key={tag}
                              label={tag} 
                              variant="outlined"
                              size="small"
                              sx={{ fontSize: '0.7rem', height: '20px' }}
                            />
                          ))}
                          {product.tags.length > 3 && (
                            <Chip 
                              label={`+${product.tags.length - 3}`}
                              variant="outlined"
                              size="small"
                              sx={{ fontSize: '0.7rem', height: '20px' }}
                            />
                          )}
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                      <Button 
                        size="small" 
                        startIcon={<Edit />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedProduct(product);
                          setEditDialogOpen(true);
                        }}
                      >
                        Edytuj
                      </Button>
                      <Button 
                        size="small" 
                        color="error"
                        startIcon={<Delete />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedProduct(product);
                          setDeleteDialogOpen(true);
                        }}
                      >
                        Usuń
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {data.items.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant='h6' color='text.secondary'>
                  {searchQuery ? 'Brak produktów pasujących do wyszukiwania' : 'Brak produktów'}
                </Typography>
              </Box>
            )}

            {data.pages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                <Button 
                  disabled={!data.has_prev} 
                  onClick={() => setPage(page - 1)}
                  sx={{ mr: 1 }}
                >
                  Poprzednia
                </Button>
                <Typography sx={{ px: 2, py: 1 }}>
                  Strona {data.page} z {data.pages}
                </Typography>
                <Button 
                  disabled={!data.has_next} 
                  onClick={() => setPage(page + 1)}
                  sx={{ ml: 1 }}
                >
                  Następna
                </Button>
              </Box>
            )}
          </>
        )}
      </Container>

      {/* Dialogs */}
      <ProductFormDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        title="Create New Product"
      />

      <ProductFormDialog
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false);
          setSelectedProduct(null);
        }}
        product={selectedProduct}
        title="Edit Product"
      />

      <DeleteProductDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setSelectedProduct(null);
        }}
        product={selectedProduct}
      />
    </>
  );
}