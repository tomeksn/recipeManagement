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
  Box
} from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { productService } from '@/services/productService';
import { Product } from '@/types';

interface DeleteProductDialogProps {
  open: boolean;
  onClose: () => void;
  product: Product | null;
}

export default function DeleteProductDialog({
  open,
  onClose,
  product
}: DeleteProductDialogProps) {
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: (id: string) => productService.deleteProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      onClose();
    }
  });

  const handleDelete = () => {
    if (product) {
      deleteMutation.mutate(product.id);
    }
  };

  if (!product) return null;

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
        Delete Product
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Are you sure you want to delete this product? This action cannot be undone.
        </Typography>

        <Box sx={{ 
          p: 2, 
          backgroundColor: 'grey.50', 
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'grey.200'
        }}>
          <Typography variant="subtitle2" color="text.secondary">
            Product to delete:
          </Typography>
          <Typography variant="h6">
            {product.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Type: {product.type} • Unit: {product.unit === 'piece' ? 'pieces' : 'grams'}
          </Typography>
        </Box>

        {deleteMutation.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {(deleteMutation.error as any)?.message || 'Failed to delete product'}
          </Alert>
        )}

        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Warning:</strong> If this product is used in any recipes, 
            those recipes may become invalid. Please check recipe dependencies 
            before deleting.
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
          {deleteMutation.isPending ? 'Deleting...' : 'Delete Product'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}