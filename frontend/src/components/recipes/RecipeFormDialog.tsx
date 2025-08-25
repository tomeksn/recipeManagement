import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Autocomplete,
  IconButton,
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Divider,
  Chip
} from '@mui/material';
import { 
  Close as CloseIcon, 
  Add as AddIcon, 
  Delete as DeleteIcon,
  DragIndicator as DragIcon
} from '@mui/icons-material';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';

import { productService } from '@/services/productService';
import { recipeService } from '@/services/recipeService';
import { Recipe, RecipeFormData, Product, RecipeIngredient } from '@/types';

interface RecipeFormDialogProps {
  open: boolean;
  onClose: () => void;
  recipe?: Recipe | null;
  preselectedProductId?: string;
  title?: string;
}

interface IngredientFormData {
  product_id: string;
  product?: Product;
  quantity: number;
  unit: 'piece' | 'gram';
  order: number;
}

export default function RecipeFormDialog({
  open,
  onClose,
  recipe,
  preselectedProductId,
  title
}: RecipeFormDialogProps) {
  const queryClient = useQueryClient();
  const isEditing = !!recipe;

  // Form state
  const [formData, setFormData] = useState<RecipeFormData>({
    product_id: preselectedProductId || '',
    yield_quantity: 1,
    yield_unit: 'piece',
    ingredients: []
  });

  const [ingredients, setIngredients] = useState<IngredientFormData[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Load products for dropdowns
  const { data: productsData } = useQuery({
    queryKey: ['products', 1, ''],
    queryFn: () => productService.getProducts(1, 100),
  });

  const products = productsData?.items || [];

  // Initialize form data when recipe changes
  useEffect(() => {
    if (recipe) {
      setFormData({
        product_id: recipe.product_id,
        yield_quantity: recipe.yield_quantity,
        yield_unit: recipe.yield_unit,
        ingredients: recipe.ingredients.map(ing => ({
          product_id: ing.product_id,
          quantity: ing.quantity,
          unit: ing.unit,
          order: ing.order
        }))
      });

      setIngredients(recipe.ingredients.map(ing => ({
        product_id: ing.product_id,
        product: ing.product,
        quantity: ing.quantity,
        unit: ing.unit,
        order: ing.order
      })));
    } else {
      const initialData = {
        product_id: preselectedProductId || '',
        yield_quantity: 1,
        yield_unit: 'piece' as const,
        ingredients: []
      };
      setFormData(initialData);
      setIngredients([]);
    }
    setErrors({});
  }, [recipe, preselectedProductId, open]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: recipeService.createRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      onClose();
    },
    onError: (error: any) => {
      setErrors({ submit: error.message || 'Failed to create recipe' });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<RecipeFormData> }) =>
      recipeService.updateRecipe(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      queryClient.invalidateQueries({ queryKey: ['recipe', recipe?.id] });
      onClose();
    },
    onError: (error: any) => {
      setErrors({ submit: error.message || 'Failed to update recipe' });
    }
  });

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.product_id) {
      newErrors.product_id = 'Product is required';
    }

    if (formData.yield_quantity <= 0) {
      newErrors.yield_quantity = 'Yield quantity must be greater than 0';
    }

    if (ingredients.length === 0) {
      newErrors.ingredients = 'At least one ingredient is required';
    }

    // Validate ingredients
    ingredients.forEach((ingredient, index) => {
      if (!ingredient.product_id) {
        newErrors[`ingredient_${index}_product`] = 'Product is required';
      }
      if (ingredient.quantity <= 0) {
        newErrors[`ingredient_${index}_quantity`] = 'Quantity must be greater than 0';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const submitData: RecipeFormData = {
      ...formData,
      ingredients: ingredients.map((ing, index) => ({
        product_id: ing.product_id,
        quantity: ing.quantity,
        unit: ing.unit,
        order: index + 1
      }))
    };

    if (isEditing && recipe) {
      updateMutation.mutate({ id: recipe.id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleInputChange = (field: keyof RecipeFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleAddIngredient = () => {
    const newIngredient: IngredientFormData = {
      product_id: '',
      quantity: 1,
      unit: 'piece',
      order: ingredients.length + 1
    };
    setIngredients(prev => [...prev, newIngredient]);
  };

  const handleIngredientChange = (index: number, field: keyof IngredientFormData, value: any) => {
    setIngredients(prev => {
      const updated = [...prev];
      if (field === 'product_id') {
        const product = products.find(p => p.id === value);
        updated[index] = { ...updated[index], [field]: value, product };
      } else {
        updated[index] = { ...updated[index], [field]: value };
      }
      return updated;
    });

    // Clear errors for this ingredient field
    const errorKey = `ingredient_${index}_${field === 'product_id' ? 'product' : field}`;
    if (errors[errorKey]) {
      setErrors(prev => ({ ...prev, [errorKey]: '' }));
    }
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  const selectedProduct = products.find(p => p.id === formData.product_id);

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh', maxHeight: '90vh' }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Typography variant="h6">
          {title || (isEditing ? 'Edit Recipe' : 'Create New Recipe')}
        </Typography>
        <Button
          onClick={onClose}
          size="small"
          sx={{ minWidth: 'auto', p: 1 }}
        >
          <CloseIcon />
        </Button>
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent dividers sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {errors.submit && (
            <Alert severity="error">
              {errors.submit}
            </Alert>
          )}

          {/* Basic Recipe Info */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recipe Information
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* Product Selection */}
              <FormControl fullWidth>
                <Autocomplete
                  options={products}
                  getOptionLabel={(option) => option.name}
                  value={selectedProduct || null}
                  onChange={(_, newValue) => handleInputChange('product_id', newValue?.id || '')}
                  disabled={!!preselectedProductId}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Product"
                      error={!!errors.product_id}
                      helperText={errors.product_id}
                      required
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props}>
                      <Box>
                        <Typography variant="body2">{option.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {option.category} • {option.unit === 'piece' ? 'pieces' : 'grams'}
                        </Typography>
                      </Box>
                    </li>
                  )}
                />
              </FormControl>

              {/* Yield Settings */}
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="Yield Quantity"
                  type="number"
                  value={formData.yield_quantity}
                  onChange={(e) => handleInputChange('yield_quantity', parseFloat(e.target.value) || 0)}
                  error={!!errors.yield_quantity}
                  helperText={errors.yield_quantity}
                  required
                  inputProps={{ min: 0.001, step: 0.001 }}
                  sx={{ flex: 1 }}
                />

                <FormControl sx={{ flex: 1 }}>
                  <InputLabel>Yield Unit</InputLabel>
                  <Select
                    value={formData.yield_unit}
                    label="Yield Unit"
                    onChange={(e) => handleInputChange('yield_unit', e.target.value)}
                  >
                    <MenuItem value="piece">Pieces (szt)</MenuItem>
                    <MenuItem value="gram">Grams (g)</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </Paper>

          {/* Ingredients Section */}
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Ingredients
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddIngredient}
              >
                Add Ingredient
              </Button>
            </Box>

            {errors.ingredients && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errors.ingredients}
              </Alert>
            )}

            {ingredients.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell width="40px"></TableCell>
                    <TableCell>Product</TableCell>
                    <TableCell width="120px">Quantity</TableCell>
                    <TableCell width="100px">Unit</TableCell>
                    <TableCell width="60px">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {ingredients.map((ingredient, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <DragIcon color="disabled" />
                      </TableCell>
                      <TableCell>
                        <Autocomplete
                          options={products}
                          getOptionLabel={(option) => option.name}
                          value={ingredient.product || null}
                          onChange={(_, newValue) => handleIngredientChange(index, 'product_id', newValue?.id || '')}
                          renderInput={(params) => (
                            <TextField
                              {...params}
                              error={!!errors[`ingredient_${index}_product`]}
                              helperText={errors[`ingredient_${index}_product`]}
                              size="small"
                              placeholder="Select product..."
                            />
                          )}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={ingredient.quantity}
                          onChange={(e) => handleIngredientChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                          error={!!errors[`ingredient_${index}_quantity`]}
                          size="small"
                          inputProps={{ min: 0.001, step: 0.001 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Select
                          value={ingredient.unit}
                          onChange={(e) => handleIngredientChange(index, 'unit', e.target.value)}
                          size="small"
                        >
                          <MenuItem value="piece">szt</MenuItem>
                          <MenuItem value="gram">g</MenuItem>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={() => handleRemoveIngredient(index)}
                          color="error"
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                <Typography variant="body2">
                  No ingredients added yet. Click "Add Ingredient" to get started.
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Recipe Summary */}
          {selectedProduct && ingredients.length > 0 && (
            <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" gutterBottom>
                Recipe Summary
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
                <Chip 
                  label={`Product: ${selectedProduct.name}`}
                  color="primary"
                />
                <Chip 
                  label={`Yield: ${formData.yield_quantity} ${formData.yield_unit === 'piece' ? 'pieces' : 'grams'}`}
                  variant="outlined"
                />
                <Chip 
                  label={`${ingredients.length} ingredient${ingredients.length !== 1 ? 's' : ''}`}
                  variant="outlined"
                />
              </Box>
            </Paper>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button 
            onClick={onClose} 
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading || ingredients.length === 0}
            startIcon={isLoading && <CircularProgress size={16} />}
          >
            {isLoading ? 'Saving...' : (isEditing ? 'Update Recipe' : 'Create Recipe')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}