import React from 'react';
import { Box, Typography, Paper, Alert } from '@mui/material';
import { Info } from '@mui/icons-material';

import { SearchInterface } from './SearchInterface';
import { Product } from '@/types';

const demoCategories = [
  'Ingredients',
  'Semi-Products',
  'Flavorings',
  'Preservatives',
  'Packaging',
  'Equipment',
  'Raw Materials',
  'Additives',
];

const demoTags = [
  'baking',
  'sweetener',
  'flavoring',
  'organic',
  'gluten-free',
  'dairy-free',
  'vegan',
  'kosher',
  'halal',
  'premium',
  'imported',
  'local',
  'seasonal',
  'bulk',
  'specialty',
];

export function SearchDemo() {
  const handleProductSelect = (product: Product) => {
    console.log('Product selected:', product);
    // In real app, this would navigate to product details
  };

  const handleProductEdit = (product: Product) => {
    console.log('Edit product:', product);
    // In real app, this would open edit dialog
  };

  const handleProductDelete = (product: Product) => {
    console.log('Delete product:', product);
    // In real app, this would show confirmation dialog
  };

  const handleProductDuplicate = (product: Product) => {
    console.log('Duplicate product:', product);
    // In real app, this would create a copy
  };

  const handleProductViewRecipe = (product: Product) => {
    console.log('View recipe for product:', product);
    // In real app, this would navigate to recipe view
  };

  const handleProductCalculate = (product: Product) => {
    console.log('Calculate for product:', product);
    // In real app, this would open calculator
  };

  return (
    <Box>
      {/* Demo Info */}
      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'info.50', borderLeft: 4, borderColor: 'info.main' }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Info color="info" />
          <Box>
            <Typography variant="h6" color="info.main" gutterBottom>
              Search & Filter Demo
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This demonstrates the complete search interface with:
            </Typography>
            <ul style={{ margin: '8px 0', paddingLeft: '20px', color: 'rgba(0,0,0,0.6)' }}>
              <li>Real-time search with autocomplete and suggestions</li>
              <li>Advanced filtering by type, unit, category, and tags</li>
              <li>Search result highlighting and performance metrics</li>
              <li>Recent and popular search history</li>
              <li>Responsive design with mobile-friendly filters</li>
              <li>Drag-and-drop product cards with context actions</li>
            </ul>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try searching for terms like "flour", "sugar", or "vanilla". 
              Use the filter panel to narrow down results by product type or category.
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Search Interface */}
      <SearchInterface
        onProductSelect={handleProductSelect}
        onProductEdit={handleProductEdit}
        onProductDelete={handleProductDelete}
        onProductDuplicate={handleProductDuplicate}
        onProductViewRecipe={handleProductViewRecipe}
        onProductCalculate={handleProductCalculate}
        initialQuery=""
        showHeader={false}
        fullHeight={false}
        categories={demoCategories}
        tags={demoTags}
      />
    </Box>
  );
}