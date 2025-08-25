import React, { useState } from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import { DropResult } from 'react-beautiful-dnd';
import { Add, Save, Refresh } from '@mui/icons-material';

import { RecipeBoard } from './RecipeBoard';
import { RecipeIngredient, Product } from '@/types';

// Demo data
const demoProducts: Product[] = [
  {
    id: 'prod-1',
    name: 'Flour',
    type: 'standard',
    unit: 'gram',
    description: 'All-purpose wheat flour',
    category: 'Ingredients',
    tags: ['baking', 'grains'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-2',
    name: 'Sugar',
    type: 'standard',
    unit: 'gram',
    description: 'White granulated sugar',
    category: 'Ingredients',
    tags: ['baking', 'sweetener'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-3',
    name: 'Vanilla Extract',
    type: 'standard',
    unit: 'piece',
    description: 'Pure vanilla extract',
    category: 'Flavorings',
    tags: ['baking', 'flavoring'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-4',
    name: 'Cake Mix',
    type: 'semi-product',
    unit: 'gram',
    description: 'Pre-mixed cake ingredients',
    category: 'Semi-Products',
    tags: ['baking', 'mix'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const demoIngredients: RecipeIngredient[] = [
  {
    id: 'ing-1',
    product_id: 'prod-1',
    product: demoProducts[0],
    quantity: 500,
    unit: 'gram',
    order: 1,
  },
  {
    id: 'ing-2',
    product_id: 'prod-2',
    product: demoProducts[1],
    quantity: 200,
    unit: 'gram',
    order: 2,
  },
  {
    id: 'ing-3',
    product_id: 'prod-3',
    product: demoProducts[2],
    quantity: 2,
    unit: 'piece',
    order: 3,
  },
  {
    id: 'ing-4',
    product_id: 'prod-4',
    product: demoProducts[3],
    quantity: 300,
    unit: 'gram',
    order: 4,
    sub_ingredients: [
      {
        id: 'sub-1',
        product_id: 'prod-1',
        product: demoProducts[0],
        quantity: 200,
        unit: 'gram',
        order: 1,
        depth: 1,
      },
      {
        id: 'sub-2',
        product_id: 'prod-2',
        product: demoProducts[1],
        quantity: 100,
        unit: 'gram',
        order: 2,
        depth: 1,
      },
    ],
    expanded: false,
  },
];

export function RecipeBoardDemo() {
  const [ingredients, setIngredients] = useState<RecipeIngredient[]>(demoIngredients);

  const handleDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    // Find the dragged ingredient
    const draggedIngredient = ingredients.find(
      (ing) => ing.id === draggableId.replace('ingredient-', '')
    );

    if (!draggedIngredient) return;

    // Create new ingredients array with reordered items
    const newIngredients = Array.from(ingredients);
    const draggedIndex = newIngredients.findIndex((ing) => ing.id === draggedIngredient.id);
    
    // Remove from source
    newIngredients.splice(draggedIndex, 1);
    
    // Add to destination
    newIngredients.splice(destination.index, 0, draggedIngredient);
    
    // Update order numbers
    const updatedIngredients = newIngredients.map((ing, index) => ({
      ...ing,
      order: index + 1,
    }));

    setIngredients(updatedIngredients);
  };

  const handleAddIngredient = () => {
    const newIngredient: RecipeIngredient = {
      id: `ing-${Date.now()}`,
      product_id: 'new-product',
      product: {
        id: 'new-product',
        name: 'New Ingredient',
        type: 'standard',
        unit: 'gram',
        description: 'Click to edit',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      quantity: 100,
      unit: 'gram',
      order: ingredients.length + 1,
    };

    setIngredients([...ingredients, newIngredient]);
  };

  const handleEditIngredient = (ingredient: RecipeIngredient) => {
    console.log('Edit ingredient:', ingredient);
    // In real app, this would open an edit dialog
  };

  const handleDeleteIngredient = (ingredient: RecipeIngredient) => {
    setIngredients(ingredients.filter((ing) => ing.id !== ingredient.id));
  };

  const handleExpandIngredient = (ingredient: RecipeIngredient) => {
    setIngredients(
      ingredients.map((ing) =>
        ing.id === ingredient.id
          ? { ...ing, expanded: !ing.expanded }
          : ing
      )
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.paper' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Recipe Board Demo
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" startIcon={<Refresh />}>
              Reset Demo
            </Button>
            <Button variant="contained" startIcon={<Save />}>
              Save Recipe
            </Button>
          </Box>
        </Box>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          This demonstrates the Trello-like recipe board with drag-and-drop ingredient management.
          You can drag ingredients between columns, expand semi-products to view their sub-ingredients,
          and manage the recipe composition visually.
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Typography variant="h6">
            Total Ingredients: {ingredients.length}
          </Typography>
          <Typography variant="h6" color="primary">
            Standard: {ingredients.filter(i => i.product?.type === 'standard').length}
          </Typography>
          <Typography variant="h6" color="secondary">
            Semi-Products: {ingredients.filter(i => i.product?.type === 'semi-product').length}
          </Typography>
          <Typography variant="h6" color="success.main">
            Kits: {ingredients.filter(i => i.product?.type === 'kit').length}
          </Typography>
        </Box>
      </Paper>

      <RecipeBoard
        ingredients={ingredients}
        onDragEnd={handleDragEnd}
        onAddIngredient={handleAddIngredient}
        onEditIngredient={handleEditIngredient}
        onDeleteIngredient={handleDeleteIngredient}
        onExpandIngredient={handleExpandIngredient}
      />
    </Box>
  );
}