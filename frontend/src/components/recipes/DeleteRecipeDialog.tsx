import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Box,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { Warning as WarningIcon, Restaurant as RestaurantIcon } from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { recipeService } from '@/services/recipeService';
import { Recipe } from '@/types';

interface DeleteRecipeDialogProps {
  open: boolean;
  onClose: () => void;
  recipe: Recipe | null;
}

export default function DeleteRecipeDialog({
  open,
  onClose,
  recipe
}: DeleteRecipeDialogProps) {
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: (id: string) => recipeService.deleteRecipe(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      onClose();
    }
  });

  const handleDelete = () => {
    if (recipe) {
      deleteMutation.mutate(recipe.id);
    }
  };

  if (!recipe) return null;

  const getUnitLabel = (unit: 'piece' | 'gram') => {
    return unit === 'piece' ? 'pieces' : 'grams';
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        color: 'error.main' 
      }}>
        <WarningIcon />
        Delete Recipe
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Are you sure you want to delete this recipe? This action cannot be undone.
        </Typography>

        <Box sx={{ 
          p: 2, 
          backgroundColor: 'grey.50', 
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'grey.200',
          mb: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <RestaurantIcon color="primary" />
            <Typography variant="subtitle2" color="text.secondary">
              Recipe to delete:
            </Typography>
          </Box>
          
          <Typography variant="h6">
            {recipe.product?.name || 'Unknown Product'}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Yield: {recipe.yield_quantity} {getUnitLabel(recipe.yield_unit)}
            {recipe.version && ` • Version ${recipe.version}`}
          </Typography>

          {recipe.ingredients && recipe.ingredients.length > 0 && (
            <>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Ingredients ({recipe.ingredients.length}):
              </Typography>
              <List dense sx={{ py: 0 }}>
                {recipe.ingredients.slice(0, 3).map((ingredient) => (
                  <ListItem key={ingredient.id} sx={{ py: 0, px: 0 }}>
                    <ListItemText 
                      primary={ingredient.product?.name || 'Unknown product'}
                      secondary={`${ingredient.quantity} ${getUnitLabel(ingredient.unit)}`}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                ))}
                {recipe.ingredients.length > 3 && (
                  <ListItem sx={{ py: 0, px: 0 }}>
                    <ListItemText>
                      <Typography variant="caption" color="text.secondary">
                        ... and {recipe.ingredients.length - 3} more ingredients
                      </Typography>
                    </ListItemText>
                  </ListItem>
                )}
              </List>
            </>
          )}
        </Box>

        {deleteMutation.error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {(deleteMutation.error as any)?.message || 'Failed to delete recipe'}
          </Alert>
        )}

        <Alert severity="warning">
          <Typography variant="body2">
            <strong>Warning:</strong> Deleting this recipe will permanently remove 
            all ingredient information and calculations. This may affect related 
            production planning and cost calculations.
          </Typography>
        </Alert>
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button 
          onClick={onClose} 
          disabled={deleteMutation.isPending}
        >
          Cancel
        </Button>
        <Button
          onClick={handleDelete}
          variant="contained"
          color="error"
          disabled={deleteMutation.isPending}
          startIcon={deleteMutation.isPending && <CircularProgress size={16} />}
        >
          {deleteMutation.isPending ? 'Deleting...' : 'Delete Recipe'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}