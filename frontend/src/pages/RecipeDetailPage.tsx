import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Breadcrumbs,
  Link,
  Button,
  Chip,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Divider,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  TextField,
  InputAdornment,
  Fab
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  Restaurant,
  Calculate,
  NavigateNext,
  Scale,
  Inventory,
  Add,
  Remove
} from '@mui/icons-material';

import { recipeService } from '@/services/recipeService';
import { Recipe } from '@/types';
import { RecipeFormDialog, DeleteRecipeDialog } from '@/components/recipes';

export default function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Calculator state
  const [calculatorOpen, setCalculatorOpen] = useState(false);
  const [targetQuantity, setTargetQuantity] = useState<number>(1);
  const [calculatedIngredients, setCalculatedIngredients] = useState<any[]>([]);

  const { data: recipe, isLoading, error } = useQuery({
    queryKey: ['recipe', id],
    queryFn: () => recipeService.getRecipe(id!),
    enabled: !!id
  });

  const getUnitLabel = (unit: 'piece' | 'gram') => {
    return unit === 'piece' ? 'szt' : 'g';
  };

  const handleCalculateIngredients = () => {
    if (!recipe) return;

    // Calculate scaling factor based on yield unit
    const scaleFactor = recipe.yield_unit === 'piece' 
      ? targetQuantity / recipe.yield_quantity
      : targetQuantity / recipe.yield_quantity;

    const calculated = recipe.ingredients.map(ingredient => ({
      ...ingredient,
      calculatedQuantity: ingredient.quantity * scaleFactor
    }));

    setCalculatedIngredients(calculated);
  };

  const getTotalIngredientWeight = () => {
    if (!recipe) return 0;
    return recipe.ingredients
      .filter(ing => ing.unit === 'gram')
      .reduce((total, ing) => total + ing.quantity, 0);
  };

  if (isLoading) {
    return (
      <Container maxWidth='xl' sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !recipe) {
    return (
      <Container maxWidth='xl' sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error?.message || 'Nie znaleziono receptury'}
        </Alert>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/recipes')}
        >
          Powrót do listy receptur
        </Button>
      </Container>
    );
  }

  return (
    <>
      <Helmet>
        <title>{recipe.product?.name || 'Recipe Details'} - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs 
          separator={<NavigateNext fontSize="small" />} 
          sx={{ mb: 3 }}
          aria-label="breadcrumb"
        >
          <Link
            color="inherit"
            href="/recipes"
            onClick={(e) => {
              e.preventDefault();
              navigate('/recipes');
            }}
            sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
          >
            <Restaurant sx={{ mr: 0.5 }} fontSize="inherit" />
            Receptury
          </Link>
          <Typography color="text.primary">
            {recipe.product?.name || 'Nieznana receptura'}
          </Typography>
        </Breadcrumbs>

        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Restaurant sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant='h4' component='h1' sx={{ fontWeight: 600 }}>
                {recipe.product?.name || 'Nieznany produkt'}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
              <Chip 
                icon={<Scale />}
                label={`Wydajność: ${recipe.yield_quantity} ${getUnitLabel(recipe.yield_unit)}`}
                color="primary"
                variant="outlined"
              />
              <Chip 
                icon={<Inventory />}
                label={`${recipe.ingredients.length} składnik${recipe.ingredients.length !== 1 ? 'ów' : ''}`}
                variant="outlined"
              />
              {recipe.version && (
                <Chip 
                  label={`Wersja ${recipe.version}`}
                  size="small"
                  variant="outlined"
                />
              )}
              {recipe.product?.category && (
                <Chip 
                  label={recipe.product.category}
                  size="small"
                />
              )}
            </Box>

            {recipe.product?.description && (
              <Typography variant='body1' color='text.secondary' sx={{ mb: 2 }}>
                {recipe.product.description}
              </Typography>
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Edit />}
              onClick={() => setEditDialogOpen(true)}
            >
              Edytuj
            </Button>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={() => setDeleteDialogOpen(true)}
            >
              Usuń
            </Button>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {/* Ingredients Table */}
          <Grid item xs={12} lg={calculatorOpen ? 8 : 12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Inventory />
                Składniki receptury
              </Typography>
              
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Lp.</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Produkt</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Ilość</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Jednostka</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Typ</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recipe.ingredients.map((ingredient, index) => (
                    <TableRow key={ingredient.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {ingredient.product?.name || 'Nieznany produkt'}
                          </Typography>
                          {ingredient.product?.description && (
                            <Typography variant="caption" color="text.secondary">
                              {ingredient.product.description}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {ingredient.quantity}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={getUnitLabel(ingredient.unit)}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={ingredient.product?.type || 'standard'}
                          size="small"
                          color={ingredient.product?.type === 'semi-product' ? 'secondary' : 'default'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Summary */}
              <Divider sx={{ my: 3 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Całkowita masa składników (g): <strong>{getTotalIngredientWeight()}g</strong>
                  </Typography>
                  <Typography variant="subtitle2" color="text.secondary">
                    Składników piece: <strong>{recipe.ingredients.filter(ing => ing.unit === 'piece').length}</strong>
                  </Typography>
                </Box>
                <Fab
                  color="primary"
                  size="medium"
                  onClick={() => setCalculatorOpen(!calculatorOpen)}
                  sx={{ ml: 2 }}
                >
                  <Calculate />
                </Fab>
              </Box>
            </Paper>
          </Grid>

          {/* Calculator Panel */}
          {calculatorOpen && (
            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 3, position: 'sticky', top: 20 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Calculate />
                    Kalkulator
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => setCalculatorOpen(false)}
                  >
                    <Remove />
                  </IconButton>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <TextField
                    label={`Docelowa ilość (${getUnitLabel(recipe.yield_unit)})`}
                    type="number"
                    value={targetQuantity}
                    onChange={(e) => setTargetQuantity(parseFloat(e.target.value) || 0)}
                    fullWidth
                    inputProps={{ min: 0.001, step: 0.001 }}
                    sx={{ mb: 2 }}
                  />

                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleCalculateIngredients}
                    disabled={targetQuantity <= 0}
                    startIcon={<Calculate />}
                  >
                    Oblicz składniki
                  </Button>
                </Box>

                {calculatedIngredients.length > 0 && (
                  <>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                      Przeliczone składniki:
                    </Typography>
                    
                    <List dense>
                      {calculatedIngredients.map((ingredient) => (
                        <ListItem key={ingredient.id} sx={{ px: 0 }}>
                          <ListItemText
                            primary={ingredient.product?.name || 'Nieznany produkt'}
                            secondary={
                              <Box component="span" sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>
                                  {ingredient.calculatedQuantity.toFixed(ingredient.unit === 'piece' ? 0 : 2)} {getUnitLabel(ingredient.unit)}
                                </span>
                                <span style={{ color: '#666' }}>
                                  (było: {ingredient.quantity} {getUnitLabel(ingredient.unit)})
                                </span>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>

                    <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
                      <Typography variant="body2" color="primary.main">
                        <strong>Współczynnik przeliczenia: {(targetQuantity / recipe.yield_quantity).toFixed(3)}</strong>
                      </Typography>
                    </Box>
                  </>
                )}
              </Paper>
            </Grid>
          )}
        </Grid>

        {/* Additional Recipe Info */}
        <Box sx={{ mt: 3 }}>
          <Grid container spacing={3}>
            {recipe.product?.tags && recipe.product.tags.length > 0 && (
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Tagi produktu
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {recipe.product.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" />
                    ))}
                  </Box>
                </Paper>
              </Grid>
            )}

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Informacje o recepturze
                </Typography>
                <List dense>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText 
                      primary="Data utworzenia" 
                      secondary={new Date(recipe.created_at).toLocaleDateString('pl-PL')}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText 
                      primary="Ostatnia modyfikacja" 
                      secondary={new Date(recipe.updated_at).toLocaleDateString('pl-PL')}
                    />
                  </ListItem>
                  {recipe.version && (
                    <ListItem sx={{ px: 0 }}>
                      <ListItemText 
                        primary="Wersja" 
                        secondary={recipe.version}
                      />
                    </ListItem>
                  )}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Container>

      {/* Dialogs */}
      <RecipeFormDialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        recipe={recipe}
        title="Edytuj recepturę"
      />

      <DeleteRecipeDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        recipe={recipe}
      />
    </>
  );
}