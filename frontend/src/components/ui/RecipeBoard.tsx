import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Avatar,
  useTheme,
} from '@mui/material';
import {
  DragDropContext,
  Droppable,
  Draggable,
  DropResult,
} from 'react-beautiful-dnd';
import {
  MoreVert,
  Add,
  Edit,
  Delete,
  DragIndicator,
  Scale,
} from '@mui/icons-material';

import { RecipeIngredient, Product } from '@/types';

interface IngredientCardProps {
  ingredient: RecipeIngredient;
  index: number;
  onEdit?: (ingredient: RecipeIngredient) => void;
  onDelete?: (ingredient: RecipeIngredient) => void;
  onExpand?: (ingredient: RecipeIngredient) => void;
}

function IngredientCard({ 
  ingredient, 
  index, 
  onEdit, 
  onDelete, 
  onExpand 
}: IngredientCardProps) {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMenuAction = (action: string) => {
    handleMenuClose();
    
    switch (action) {
      case 'edit':
        onEdit?.(ingredient);
        break;
      case 'delete':
        onDelete?.(ingredient);
        break;
      case 'expand':
        onExpand?.(ingredient);
        break;
    }
  };

  return (
    <Draggable draggableId={ingredient.id || `ingredient-${index}`} index={index}>
      {(provided, snapshot) => (
        <Paper
          ref={provided.innerRef}
          {...provided.draggableProps}
          sx={{
            p: 2,
            mb: 1,
            cursor: 'pointer',
            backgroundColor: snapshot.isDragging ? 'action.hover' : 'background.paper',
            transform: snapshot.isDragging ? 'rotate(3deg)' : 'none',
            boxShadow: snapshot.isDragging ? theme.shadows[8] : theme.shadows[1],
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              boxShadow: theme.shadows[4],
              '& .drag-handle': {
                opacity: 1,
              },
            },
            border: ingredient.expanded ? `2px solid ${theme.palette.primary.main}` : 'none',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
            {/* Drag Handle */}
            <Box
              className="drag-handle"
              {...provided.dragHandleProps}
              sx={{
                opacity: 0,
                transition: 'opacity 0.2s',
                color: 'text.secondary',
                cursor: 'grab',
                mt: 0.5,
                '&:active': {
                  cursor: 'grabbing',
                },
              }}
            >
              <DragIndicator fontSize="small" />
            </Box>

            {/* Product Avatar */}
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: 'primary.main',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {ingredient.product?.name?.charAt(0) || '?'}
            </Avatar>

            {/* Content */}
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 600,
                  lineHeight: 1.2,
                  mb: 0.5,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {ingredient.product?.name || `Product ${ingredient.product_id}`}
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Chip
                  label={`${ingredient.quantity} ${ingredient.unit}`}
                  size="small"
                  color="primary"
                  sx={{ fontWeight: 600, fontSize: '0.75rem' }}
                />
                
                {ingredient.product?.type && (
                  <Chip
                    label={ingredient.product.type}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', textTransform: 'capitalize' }}
                  />
                )}

                {ingredient.expanded && (
                  <Chip
                    label="Expanded"
                    size="small"
                    color="secondary"
                    sx={{ fontSize: '0.7rem' }}
                  />
                )}
              </Box>

              {ingredient.product?.description && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {ingredient.product.description}
                </Typography>
              )}

              {/* Sub-ingredients preview */}
              {ingredient.sub_ingredients && ingredient.sub_ingredients.length > 0 && (
                <Box sx={{ mt: 1, pl: 2, borderLeft: 2, borderColor: 'primary.main' }}>
                  <Typography variant="caption" color="primary.main" sx={{ fontWeight: 600 }}>
                    {ingredient.sub_ingredients.length} sub-ingredients
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Actions */}
            <IconButton
              size="small"
              onClick={handleMenuClick}
              aria-label="ingredient actions"
            >
              <MoreVert fontSize="small" />
            </IconButton>
          </Box>

          {/* Context Menu */}
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => handleMenuAction('edit')}>
              <ListItemIcon>
                <Edit fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="Edit" />
            </MenuItem>

            {ingredient.product?.type === 'semi-product' && (
              <MenuItem onClick={() => handleMenuAction('expand')}>
                <ListItemIcon>
                  <Scale fontSize="small" />
                </ListItemIcon>
                <ListItemText primary={ingredient.expanded ? 'Collapse' : 'Expand Recipe'} />
              </MenuItem>
            )}

            <MenuItem 
              onClick={() => handleMenuAction('delete')}
              sx={{ color: 'error.main' }}
            >
              <ListItemIcon>
                <Delete fontSize="small" sx={{ color: 'error.main' }} />
              </ListItemIcon>
              <ListItemText primary="Remove" />
            </MenuItem>
          </Menu>
        </Paper>
      )}
    </Draggable>
  );
}

interface RecipeBoardColumnProps {
  title: string;
  ingredients: RecipeIngredient[];
  droppableId: string;
  onAddIngredient?: () => void;
  onEditIngredient?: (ingredient: RecipeIngredient) => void;
  onDeleteIngredient?: (ingredient: RecipeIngredient) => void;
  onExpandIngredient?: (ingredient: RecipeIngredient) => void;
}

function RecipeBoardColumn({
  title,
  ingredients,
  droppableId,
  onAddIngredient,
  onEditIngredient,
  onDeleteIngredient,
  onExpandIngredient,
}: RecipeBoardColumnProps) {
  const theme = useTheme();

  return (
    <Paper
      sx={{
        width: 300,
        minHeight: 400,
        p: 2,
        bgcolor: 'grey.50',
        border: 1,
        borderColor: 'grey.200',
        borderRadius: 2,
      }}
    >
      {/* Column Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 2,
          pb: 1,
          borderBottom: 1,
          borderColor: 'grey.200',
        }}
      >
        <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
          {title}
        </Typography>
        
        <Chip
          label={ingredients.length}
          size="small"
          color="primary"
          sx={{ fontWeight: 600 }}
        />
      </Box>

      {/* Droppable Area */}
      <Droppable droppableId={droppableId}>
        {(provided, snapshot) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{
              minHeight: 200,
              p: 1,
              borderRadius: 1,
              backgroundColor: snapshot.isDraggingOver 
                ? 'primary.light' 
                : 'transparent',
              border: snapshot.isDraggingOver 
                ? `2px dashed ${theme.palette.primary.main}` 
                : '2px dashed transparent',
              transition: 'all 0.2s ease',
            }}
          >
            {ingredients.map((ingredient, index) => (
              <IngredientCard
                key={ingredient.id || `ingredient-${index}`}
                ingredient={ingredient}
                index={index}
                onEdit={onEditIngredient}
                onDelete={onDeleteIngredient}
                onExpand={onExpandIngredient}
              />
            ))}
            {provided.placeholder}

            {/* Add Ingredient Button */}
            {onAddIngredient && (
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Add />}
                onClick={onAddIngredient}
                sx={{
                  mt: 1,
                  py: 1.5,
                  borderStyle: 'dashed',
                  color: 'text.secondary',
                  borderColor: 'grey.300',
                  '&:hover': {
                    borderStyle: 'solid',
                    borderColor: 'primary.main',
                    color: 'primary.main',
                  },
                }}
              >
                Add Ingredient
              </Button>
            )}
          </Box>
        )}
      </Droppable>
    </Paper>
  );
}

interface RecipeBoardProps {
  ingredients: RecipeIngredient[];
  onDragEnd: (result: DropResult) => void;
  onAddIngredient?: () => void;
  onEditIngredient?: (ingredient: RecipeIngredient) => void;
  onDeleteIngredient?: (ingredient: RecipeIngredient) => void;
  onExpandIngredient?: (ingredient: RecipeIngredient) => void;
}

export function RecipeBoard({
  ingredients,
  onDragEnd,
  onAddIngredient,
  onEditIngredient,
  onDeleteIngredient,
  onExpandIngredient,
}: RecipeBoardProps) {
  // Group ingredients by type for different columns
  const groupedIngredients = {
    all: ingredients,
    standard: ingredients.filter(ing => ing.product?.type === 'standard'),
    'semi-product': ingredients.filter(ing => ing.product?.type === 'semi-product'),
    kit: ingredients.filter(ing => ing.product?.type === 'kit'),
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Box
        sx={{
          display: 'flex',
          gap: 3,
          overflowX: 'auto',
          pb: 2,
          minHeight: 500,
        }}
      >
        {/* All Ingredients Column */}
        <RecipeBoardColumn
          title="All Ingredients"
          ingredients={groupedIngredients.all}
          droppableId="all-ingredients"
          onAddIngredient={onAddIngredient}
          onEditIngredient={onEditIngredient}
          onDeleteIngredient={onDeleteIngredient}
          onExpandIngredient={onExpandIngredient}
        />

        {/* Standard Products Column */}
        <RecipeBoardColumn
          title="Standard Products"
          ingredients={groupedIngredients.standard}
          droppableId="standard-ingredients"
          onEditIngredient={onEditIngredient}
          onDeleteIngredient={onDeleteIngredient}
          onExpandIngredient={onExpandIngredient}
        />

        {/* Semi-Products Column */}
        <RecipeBoardColumn
          title="Semi-Products"
          ingredients={groupedIngredients['semi-product']}
          droppableId="semi-product-ingredients"
          onEditIngredient={onEditIngredient}
          onDeleteIngredient={onDeleteIngredient}
          onExpandIngredient={onExpandIngredient}
        />

        {/* Kit Products Column */}
        <RecipeBoardColumn
          title="Kit Products"
          ingredients={groupedIngredients.kit}
          droppableId="kit-ingredients"
          onEditIngredient={onEditIngredient}
          onDeleteIngredient={onDeleteIngredient}
          onExpandIngredient={onExpandIngredient}
        />
      </Box>
    </DragDropContext>
  );
}