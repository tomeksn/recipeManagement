import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Box,
  Avatar,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  MoreVert,
  Edit,
  Delete,
  FileCopy,
  Visibility,
  Restaurant,
  Calculate,
  DragIndicator,
} from '@mui/icons-material';
import { Draggable } from 'react-beautiful-dnd';
import { format } from 'date-fns';

import { Product } from '@/types';

interface ProductCardProps {
  product: Product;
  index?: number;
  isDraggable?: boolean;
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
  onDuplicate?: (product: Product) => void;
  onViewRecipe?: (product: Product) => void;
  onCalculate?: (product: Product) => void;
}

const getProductTypeColor = (type: Product['type']) => {
  switch (type) {
    case 'standard':
      return 'primary';
    case 'semi-product':
      return 'secondary';
    case 'kit':
      return 'success';
    default:
      return 'default';
  }
};

const getProductTypeIcon = (type: Product['type']) => {
  switch (type) {
    case 'standard':
      return '📦';
    case 'semi-product':
      return '🔧';
    case 'kit':
      return '📋';
    default:
      return '❓';
  }
};

function ProductCardContent({ 
  product, 
  onEdit, 
  onDelete, 
  onDuplicate, 
  onViewRecipe, 
  onCalculate 
}: Omit<ProductCardProps, 'index' | 'isDraggable'>) {
  const theme = useTheme();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCardClick = () => {
    navigate(`/products/${product.id}`);
  };

  const handleMenuAction = (action: string) => {
    handleMenuClose();
    
    switch (action) {
      case 'edit':
        onEdit?.(product);
        break;
      case 'delete':
        onDelete?.(product);
        break;
      case 'duplicate':
        onDuplicate?.(product);
        break;
      case 'recipe':
        onViewRecipe?.(product);
        break;
      case 'calculate':
        onCalculate?.(product);
        break;
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        position: 'relative',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[8],
          '& .drag-handle': {
            opacity: 1,
          },
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      }}
      onClick={handleCardClick}
    >
      {/* Drag Handle */}
      <Box
        className="drag-handle"
        sx={{
          position: 'absolute',
          top: 8,
          left: 8,
          opacity: 0,
          transition: 'opacity 0.2s',
          color: 'text.secondary',
          cursor: 'grab',
          '&:active': {
            cursor: 'grabbing',
          },
        }}
      >
        <DragIndicator fontSize="small" />
      </Box>

      <CardContent sx={{ flexGrow: 1, pt: 5 }}>
        {/* Product Header */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Avatar
            sx={{
              width: 40,
              height: 40,
              mr: 1.5,
              bgcolor: `${getProductTypeColor(product.type)}.main`,
              fontSize: '1.2rem',
            }}
          >
            {getProductTypeIcon(product.type)}
          </Avatar>
          
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography
              variant="h6"
              component="h3"
              sx={{
                fontWeight: 600,
                fontSize: '1rem',
                lineHeight: 1.3,
                mb: 0.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {product.name}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Chip
                label={product.type.replace('-', ' ')}
                size="small"
                color={getProductTypeColor(product.type)}
                sx={{ textTransform: 'capitalize', fontSize: '0.75rem' }}
              />
              <Chip
                label={product.unit}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            </Box>
          </Box>
        </Box>

        {/* Description */}
        {product.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              mb: 2,
              lineHeight: 1.4,
            }}
          >
            {product.description}
          </Typography>
        )}

        {/* Tags */}
        {product.tags && product.tags.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {product.tags.slice(0, 3).map((tag) => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                variant="outlined"
                sx={{ 
                  fontSize: '0.7rem',
                  height: 20,
                  borderRadius: 2,
                }}
              />
            ))}
            {product.tags.length > 3 && (
              <Chip
                label={`+${product.tags.length - 3}`}
                size="small"
                variant="outlined"
                sx={{ 
                  fontSize: '0.7rem',
                  height: 20,
                  borderRadius: 2,
                }}
              />
            )}
          </Box>
        )}

        {/* Category */}
        {product.category && (
          <Typography
            variant="caption"
            sx={{
              display: 'inline-block',
              px: 1,
              py: 0.25,
              bgcolor: 'action.hover',
              borderRadius: 1,
              fontWeight: 500,
              mb: 1,
            }}
          >
            {product.category}
          </Typography>
        )}
      </CardContent>

      <CardActions
        sx={{
          px: 2,
          py: 1,
          justifyContent: 'space-between',
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Updated {format(new Date(product.updated_at), 'MMM d')}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {/* Quick Actions */}
          <Tooltip title="View Recipe">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onViewRecipe?.(product);
              }}
              sx={{ mr: 0.5 }}
            >
              <Restaurant fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Calculate">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onCalculate?.(product);
              }}
              sx={{ mr: 0.5 }}
            >
              <Calculate fontSize="small" />
            </IconButton>
          </Tooltip>

          {/* Menu */}
          <IconButton
            size="small"
            onClick={handleMenuClick}
            aria-label="more actions"
          >
            <MoreVert fontSize="small" />
          </IconButton>
        </Box>
      </CardActions>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: { minWidth: 180 },
        }}
      >
        <MenuItem onClick={() => handleMenuAction('edit')}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Edit" />
        </MenuItem>

        <MenuItem onClick={() => handleMenuAction('duplicate')}>
          <ListItemIcon>
            <FileCopy fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Duplicate" />
        </MenuItem>

        <MenuItem onClick={() => handleMenuAction('recipe')}>
          <ListItemIcon>
            <Restaurant fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="View Recipe" />
        </MenuItem>

        <MenuItem onClick={() => handleMenuAction('calculate')}>
          <ListItemIcon>
            <Calculate fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Calculate" />
        </MenuItem>

        <MenuItem 
          onClick={() => handleMenuAction('delete')}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <Delete fontSize="small" sx={{ color: 'error.main' }} />
          </ListItemIcon>
          <ListItemText primary="Delete" />
        </MenuItem>
      </Menu>
    </Card>
  );
}

export function ProductCard(props: ProductCardProps) {
  const { isDraggable = false, index = 0, ...cardProps } = props;

  if (!isDraggable) {
    return <ProductCardContent {...cardProps} />;
  }

  return (
    <Draggable 
      draggableId={props.product.id} 
      index={index}
      isDragDisabled={!isDraggable}
    >
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={{
            ...provided.draggableProps.style,
            opacity: snapshot.isDragging ? 0.8 : 1,
            transform: snapshot.isDragging 
              ? `${provided.draggableProps.style?.transform} rotate(3deg)`
              : provided.draggableProps.style?.transform,
          }}
        >
          <ProductCardContent {...cardProps} />
        </div>
      )}
    </Draggable>
  );
}