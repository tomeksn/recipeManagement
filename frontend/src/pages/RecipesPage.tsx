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
  Fab,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { Search, Add, Edit, Delete, Restaurant } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

import { recipeService } from '@/services/recipeService';
import { Recipe } from '@/types';
import { RecipeFormDialog, DeleteRecipeDialog } from '@/components/recipes';

export default function RecipesPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  
  // Dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['recipes', page, searchQuery],
    queryFn: () => searchQuery 
      ? recipeService.searchRecipes(searchQuery, page, 10)
      : recipeService.getRecipes(page, 10),
  });

  const getUnitLabel = (unit: 'piece' | 'gram') => {
    return unit === 'piece' ? 'szt' : 'g';
  };

  return (
    <>
      <Helmet>
        <title>Recipes - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant='h4' component='h1' gutterBottom sx={{ fontWeight: 600 }}>
              Receptury
            </Typography>
            <Typography variant='body1' color='text.secondary'>
              Twórz i zarządzaj recepturami z interaktywnym interfejsem
            </Typography>
          </Box>

          <Fab 
            color="primary" 
            aria-label="add recipe"
            onClick={() => setCreateDialogOpen(true)}
          >
            <Add />
          </Fab>
        </Box>

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Szukaj receptur..."
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
            Błąd podczas ładowania receptur
          </Alert>
        )}

        {data && (
          <>
            <Grid container spacing={3}>
              {data.items.map((recipe) => (
                <Grid item xs={12} md={6} lg={4} key={recipe.id}>
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
                    onClick={() => navigate(`/recipes/${recipe.id}`)}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Restaurant sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant='h6' component='h2'>
                          {recipe.product?.name || 'Nieznany produkt'}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ mb: 2 }}>
                        <Typography variant='body2' color='text.secondary'>
                          Wydajność: <strong>{recipe.yield_quantity} {getUnitLabel(recipe.yield_unit)}</strong>
                        </Typography>
                        <Typography variant='body2' color='text.secondary'>
                          Składników: <strong>{recipe.ingredients.length}</strong>
                        </Typography>
                        {recipe.version && (
                          <Typography variant='body2' color='text.secondary'>
                            Wersja: <strong>{recipe.version}</strong>
                          </Typography>
                        )}
                      </Box>

                      <Divider sx={{ my: 1 }} />
                      
                      <Typography variant='subtitle2' sx={{ mb: 1, fontWeight: 600 }}>
                        Składniki:
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {recipe.ingredients.slice(0, 3).map((ingredient) => (
                          <ListItem key={ingredient.id} sx={{ py: 0.5, px: 0 }}>
                            <ListItemText 
                              primary={ingredient.product?.name || 'Nieznany produkt'}
                              secondary={`${ingredient.quantity} ${getUnitLabel(ingredient.unit)}`}
                              primaryTypographyProps={{ variant: 'body2' }}
                              secondaryTypographyProps={{ variant: 'caption' }}
                            />
                          </ListItem>
                        ))}
                        {recipe.ingredients.length > 3 && (
                          <ListItem sx={{ py: 0, px: 0 }}>
                            <Typography variant='caption' color='text.secondary'>
                              ... i {recipe.ingredients.length - 3} więcej
                            </Typography>
                          </ListItem>
                        )}
                      </List>

                      {recipe.product?.category && (
                        <Box sx={{ mt: 2 }}>
                          <Chip 
                            label={recipe.product.category} 
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                      <Button 
                        size="small" 
                        startIcon={<Edit />}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedRecipe(recipe);
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
                          setSelectedRecipe(recipe);
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
                  {searchQuery ? 'Brak receptur pasujących do wyszukiwania' : 'Brak receptur'}
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ mt: 1 }}>
                  Rozpocznij od dodania swojej pierwszej receptury
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
      <RecipeFormDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        title="Create New Recipe"
      />

      <RecipeFormDialog
        open={editDialogOpen}
        onClose={() => {
          setEditDialogOpen(false);
          setSelectedRecipe(null);
        }}
        recipe={selectedRecipe}
        title="Edit Recipe"
      />

      <DeleteRecipeDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setSelectedRecipe(null);
        }}
        recipe={selectedRecipe}
      />
    </>
  );
}