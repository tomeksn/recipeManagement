import React from 'react';
import {
  Grid,
  Box,
  Typography,
  Skeleton,
  Alert,
  Button,
} from '@mui/material';
import { DragDropContext, Droppable, DropResult } from 'react-beautiful-dnd';
import { Add, Refresh } from '@mui/icons-material';

import { Product } from '@/types';
import { ProductCard } from './ProductCard';

interface ProductGridProps {
  products: Product[];
  loading?: boolean;
  error?: string | null;
  isDragEnabled?: boolean;
  onDragEnd?: (result: DropResult) => void;
  onProductEdit?: (product: Product) => void;
  onProductDelete?: (product: Product) => void;
  onProductDuplicate?: (product: Product) => void;
  onProductViewRecipe?: (product: Product) => void;
  onProductCalculate?: (product: Product) => void;
  onCreateNew?: () => void;
  onRetry?: () => void;
}

function ProductSkeleton() {
  return (
    <Grid item xs={12} sm={6} md={4} lg={3}>
      <Box sx={{ height: 280 }}>
        <Skeleton variant="rectangular" height="100%" sx={{ borderRadius: 2 }} />
      </Box>
    </Grid>
  );
}

function EmptyState({ onCreateNew }: { onCreateNew?: () => void }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        textAlign: 'center',
      }}
    >
      <Typography
        variant="h4"
        sx={{
          fontSize: '3rem',
          opacity: 0.3,
          mb: 2,
        }}
      >
        📦
      </Typography>
      
      <Typography variant="h6" gutterBottom>
        No products found
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        Start building your product catalog by creating your first product.
        You can add products individually or import them from a file.
      </Typography>
      
      {onCreateNew && (
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={onCreateNew}
          size="large"
        >
          Create First Product
        </Button>
      )}
    </Box>
  );
}

function ErrorState({ error, onRetry }: { error: string; onRetry?: () => void }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Alert 
        severity="error" 
        action={
          onRetry && (
            <Button
              color="inherit"
              size="small"
              startIcon={<Refresh />}
              onClick={onRetry}
            >
              Retry
            </Button>
          )
        }
      >
        {error}
      </Alert>
    </Box>
  );
}

export function ProductGrid({
  products,
  loading = false,
  error = null,
  isDragEnabled = false,
  onDragEnd,
  onProductEdit,
  onProductDelete,
  onProductDuplicate,
  onProductViewRecipe,
  onProductCalculate,
  onCreateNew,
  onRetry,
}: ProductGridProps) {
  // Loading state
  if (loading) {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: 12 }).map((_, index) => (
          <ProductSkeleton key={index} />
        ))}
      </Grid>
    );
  }

  // Error state
  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  // Empty state
  if (!products || products.length === 0) {
    return <EmptyState onCreateNew={onCreateNew} />;
  }

  // Render with drag and drop
  if (isDragEnabled && onDragEnd) {
    return (
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="products-grid" direction="horizontal">
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              style={{
                backgroundColor: snapshot.isDraggingOver ? 'rgba(25, 118, 210, 0.04)' : 'transparent',
                borderRadius: 8,
                transition: 'background-color 0.2s ease',
                padding: snapshot.isDraggingOver ? 16 : 0,
              }}
            >
              <Grid container spacing={3}>
                {products.map((product, index) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                    <ProductCard
                      product={product}
                      index={index}
                      isDraggable={true}
                      onEdit={onProductEdit}
                      onDelete={onProductDelete}
                      onDuplicate={onProductDuplicate}
                      onViewRecipe={onProductViewRecipe}
                      onCalculate={onProductCalculate}
                    />
                  </Grid>
                ))}
                {provided.placeholder}
              </Grid>
            </div>
          )}
        </Droppable>
      </DragDropContext>
    );
  }

  // Render without drag and drop
  return (
    <Grid container spacing={3}>
      {products.map((product) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
          <ProductCard
            product={product}
            isDraggable={false}
            onEdit={onProductEdit}
            onDelete={onProductDelete}
            onDuplicate={onProductDuplicate}
            onViewRecipe={onProductViewRecipe}
            onCalculate={onProductCalculate}
          />
        </Grid>
      ))}
    </Grid>
  );
}