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
  Chip,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Autocomplete
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { productService } from '@/services/productService';
import { Product, ProductFormData } from '@/types';

interface ProductFormDialogProps {
  open: boolean;
  onClose: () => void;
  product?: Product | null;
  title?: string;
}

export default function ProductFormDialog({
  open,
  onClose,
  product,
  title
}: ProductFormDialogProps) {
  const queryClient = useQueryClient();
  const isEditing = !!product;

  // Form state
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    type: 'standard',
    unit: 'piece',
    description: '',
    category: '',
    tags: []
  });

  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form data when product changes
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        type: product.type,
        unit: product.unit,
        description: product.description || '',
        category: product.category || '',
        tags: product.tags || []
      });
    } else {
      setFormData({
        name: '',
        type: 'standard',
        unit: 'piece',
        description: '',
        category: '',
        tags: []
      });
    }
    setErrors({});
    setTagInput('');
  }, [product, open]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: productService.createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      onClose();
    },
    onError: (error: any) => {
      setErrors({ submit: error.message || 'Failed to create product' });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ProductFormData> }) =>
      productService.updateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['product', product?.id] });
      onClose();
    },
    onError: (error: any) => {
      setErrors({ submit: error.message || 'Failed to update product' });
    }
  });

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    if (formData.category && formData.category.length > 50) {
      newErrors.category = 'Category must be less than 50 characters';
    }

    if (formData.description && formData.description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const submitData = {
      ...formData,
      description: formData.description || undefined,
      category: formData.category || undefined,
      tags: formData.tags.length > 0 ? formData.tags : undefined
    };

    if (isEditing && product) {
      updateMutation.mutate({ id: product.id, data: submitData });
    } else {
      createMutation.mutate(submitData);
    }
  };

  const handleInputChange = (field: keyof ProductFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !formData.tags.includes(trimmedTag) && formData.tags.length < 10) {
      handleInputChange('tags', [...formData.tags, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    handleInputChange('tags', formData.tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  // Common categories for autocomplete
  const commonCategories = [
    'Bakery', 'Dairy', 'Meat', 'Vegetables', 'Fruits', 'Spices', 'Ingredients',
    'Finished Products', 'Semi-Products', 'Raw Materials', 'Packaging'
  ];

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        pb: 1
      }}>
        <Typography variant="h6">
          {title || (isEditing ? 'Edit Product' : 'Create New Product')}
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
        <DialogContent dividers>
          {errors.submit && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.submit}
            </Alert>
          )}

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Name */}
            <TextField
              label="Product Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={!!errors.name}
              helperText={errors.name}
              required
              fullWidth
              autoFocus
            />

            {/* Type and Unit */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.type}
                  label="Type"
                  onChange={(e) => handleInputChange('type', e.target.value)}
                >
                  <MenuItem value="standard">Standard Product</MenuItem>
                  <MenuItem value="semi-product">Semi-Product</MenuItem>
                  <MenuItem value="kit">Kit/Set</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Unit</InputLabel>
                <Select
                  value={formData.unit}
                  label="Unit"
                  onChange={(e) => handleInputChange('unit', e.target.value)}
                >
                  <MenuItem value="piece">Pieces (szt)</MenuItem>
                  <MenuItem value="gram">Grams (g)</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Category */}
            <Autocomplete
              options={commonCategories}
              value={formData.category}
              onChange={(_, newValue) => handleInputChange('category', newValue || '')}
              onInputChange={(_, newInputValue) => handleInputChange('category', newInputValue)}
              freeSolo
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Category (Optional)"
                  error={!!errors.category}
                  helperText={errors.category}
                />
              )}
            />

            {/* Description */}
            <TextField
              label="Description (Optional)"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              error={!!errors.description}
              helperText={errors.description}
              multiline
              rows={3}
              fullWidth
            />

            {/* Tags */}
            <Box>
              <TextField
                label="Add Tags"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={handleTagKeyPress}
                placeholder="Type a tag and press Enter"
                fullWidth
                helperText={`${formData.tags.length}/10 tags`}
                InputProps={{
                  endAdornment: tagInput.trim() && (
                    <Button onClick={handleAddTag} size="small">
                      Add
                    </Button>
                  )
                }}
              />

              {formData.tags.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {formData.tags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => handleRemoveTag(tag)}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
            </Box>
          </Box>
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
            disabled={isLoading}
            startIcon={isLoading && <CircularProgress size={16} />}
          >
            {isLoading ? 'Saving...' : (isEditing ? 'Update Product' : 'Create Product')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}