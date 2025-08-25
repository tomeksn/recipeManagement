import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Paper,
  Typography,
  Chip,
  IconButton,
  InputAdornment,
  Popper,
  ClickAwayListener,
  useTheme,
  alpha,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Search,
  Clear,
  History,
  TrendingUp,
  FilterList,
  KeyboardArrowDown,
} from '@mui/icons-material';
import { debounce } from 'lodash';

import { Product, SearchResponse } from '@/types';
import { useProductSearch } from '@/hooks/useApi';

interface SearchBarProps {
  value?: string;
  placeholder?: string;
  onSearch?: (query: string) => void;
  onSelect?: (product: Product) => void;
  onFiltersToggle?: () => void;
  showFilters?: boolean;
  autoFocus?: boolean;
  size?: 'small' | 'medium';
  fullWidth?: boolean;
}

interface SearchSuggestion {
  id: string;
  text: string;
  type: 'product' | 'category' | 'tag' | 'recent' | 'popular';
  data?: Product;
  count?: number;
}

const getRecentSearches = (): string[] => {
  try {
    return JSON.parse(localStorage.getItem('recipe_recent_searches') || '[]');
  } catch {
    return [];
  }
};

const saveRecentSearch = (query: string) => {
  if (!query.trim()) return;
  
  const recent = getRecentSearches();
  const filtered = recent.filter(q => q !== query);
  const updated = [query, ...filtered].slice(0, 5);
  
  localStorage.setItem('recipe_recent_searches', JSON.stringify(updated));
};

const getPopularSearches = (): string[] => {
  // In real app, this would come from analytics
  return ['Flour', 'Sugar', 'Vanilla', 'Butter', 'Eggs'];
};

export function SearchBar({
  value = '',
  placeholder = 'Search products, recipes, or ingredients...',
  onSearch,
  onSelect,
  onFiltersToggle,
  showFilters = true,
  autoFocus = false,
  size = 'medium',
  fullWidth = true,
}: SearchBarProps) {
  const theme = useTheme();
  const [query, setQuery] = useState(value);
  const [focused, setFocused] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const anchorRef = useRef<HTMLDivElement>(null);
  
  // Search API
  const { data: searchResults, isLoading } = useProductSearch(query);

  // Debounced search
  const debouncedSearch = useCallback(
    debounce((searchQuery: string) => {
      onSearch?.(searchQuery);
    }, 300),
    [onSearch]
  );

  // Generate suggestions
  useEffect(() => {
    const newSuggestions: SearchSuggestion[] = [];

    if (!query.trim()) {
      // Show recent and popular searches when empty
      const recent = getRecentSearches();
      const popular = getPopularSearches();

      recent.forEach(search => {
        newSuggestions.push({
          id: `recent-${search}`,
          text: search,
          type: 'recent',
        });
      });

      if (recent.length > 0 && popular.length > 0) {
        newSuggestions.push({
          id: 'divider-1',
          text: '',
          type: 'recent',
        });
      }

      popular.forEach(search => {
        newSuggestions.push({
          id: `popular-${search}`,
          text: search,
          type: 'popular',
        });
      });
    } else {
      // Show search results and suggestions
      if (searchResults?.items) {
        searchResults.items.forEach(product => {
          newSuggestions.push({
            id: `product-${product.id}`,
            text: product.name,
            type: 'product',
            data: product,
          });
        });
      }

      // Add search suggestions from backend
      if (searchResults?.suggestions) {
        searchResults.suggestions.forEach(suggestion => {
          if (!newSuggestions.some(s => s.text.toLowerCase() === suggestion.toLowerCase())) {
            newSuggestions.push({
              id: `suggestion-${suggestion}`,
              text: suggestion,
              type: 'tag',
            });
          }
        });
      }

      // Add category suggestions (mock data)
      const categoryMatches = ['Ingredients', 'Semi-Products', 'Kits', 'Flavorings']
        .filter(cat => cat.toLowerCase().includes(query.toLowerCase()));
      
      categoryMatches.forEach(category => {
        newSuggestions.push({
          id: `category-${category}`,
          text: category,
          type: 'category',
        });
      });
    }

    setSuggestions(newSuggestions.slice(0, 10));
  }, [query, searchResults]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = event.target.value;
    setQuery(newQuery);
    debouncedSearch(newQuery);
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    if (suggestion.type === 'product' && suggestion.data) {
      onSelect?.(suggestion.data);
      setQuery('');
    } else {
      setQuery(suggestion.text);
      saveRecentSearch(suggestion.text);
      onSearch?.(suggestion.text);
    }
    setFocused(false);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      if (query.trim()) {
        saveRecentSearch(query.trim());
        onSearch?.(query.trim());
        setFocused(false);
      }
    } else if (event.key === 'Escape') {
      setFocused(false);
    }
  };

  const handleClear = () => {
    setQuery('');
    onSearch?.('');
    setFocused(false);
  };

  const getSuggestionIcon = (type: SearchSuggestion['type']) => {
    switch (type) {
      case 'product':
        return '📦';
      case 'category':
        return '🏷️';
      case 'tag':
        return '🔖';
      case 'recent':
        return <History fontSize="small" />;
      case 'popular':
        return <TrendingUp fontSize="small" />;
      default:
        return <Search fontSize="small" />;
    }
  };

  const getSuggestionLabel = (type: SearchSuggestion['type']) => {
    switch (type) {
      case 'product':
        return 'Product';
      case 'category':
        return 'Category';
      case 'tag':
        return 'Tag';
      case 'recent':
        return 'Recent';
      case 'popular':
        return 'Popular';
      default:
        return '';
    }
  };

  return (
    <ClickAwayListener onClickAway={() => setFocused(false)}>
      <Box ref={anchorRef} sx={{ position: 'relative', width: fullWidth ? '100%' : 'auto' }}>
        <TextField
          fullWidth={fullWidth}
          size={size}
          value={query}
          onChange={handleInputChange}
          onFocus={() => setFocused(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search 
                  sx={{ 
                    color: isLoading ? 'primary.main' : 'text.secondary',
                    animation: isLoading ? 'pulse 1s infinite' : 'none',
                  }} 
                />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {query && (
                    <IconButton
                      size="small"
                      onClick={handleClear}
                      aria-label="clear search"
                    >
                      <Clear fontSize="small" />
                    </IconButton>
                  )}
                  
                  {showFilters && (
                    <IconButton
                      size="small"
                      onClick={onFiltersToggle}
                      aria-label="toggle filters"
                      sx={{
                        color: 'text.secondary',
                        '&:hover': { color: 'primary.main' },
                      }}
                    >
                      <FilterList fontSize="small" />
                    </IconButton>
                  )}
                </Box>
              </InputAdornment>
            ),
            sx: {
              backgroundColor: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(8px)',
              '&:hover': {
                backgroundColor: theme.palette.background.paper,
              },
              '&.Mui-focused': {
                backgroundColor: theme.palette.background.paper,
                boxShadow: theme.shadows[8],
              },
            },
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
            },
          }}
        />

        {/* Search Suggestions Dropdown */}
        <Popper
          open={focused && suggestions.length > 0}
          anchorEl={anchorRef.current}
          placement="bottom-start"
          style={{ width: anchorRef.current?.offsetWidth, zIndex: theme.zIndex.modal }}
          modifiers={[
            {
              name: 'offset',
              options: {
                offset: [0, 8],
              },
            },
          ]}
        >
          <Paper
            elevation={8}
            sx={{
              maxHeight: 400,
              overflow: 'auto',
              border: 1,
              borderColor: 'divider',
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.background.paper, 0.95),
              backdropFilter: 'blur(12px)',
            }}
          >
            <List dense>
              {!query.trim() && suggestions.length > 0 && (
                <>
                  <ListItem sx={{ py: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                      {suggestions.some(s => s.type === 'recent') ? 'Recent Searches' : 'Popular Searches'}
                    </Typography>
                  </ListItem>
                  <Divider />
                </>
              )}

              {suggestions.map((suggestion, index) => {
                if (suggestion.text === '') {
                  return <Divider key={suggestion.id} sx={{ my: 1 }} />;
                }

                return (
                  <ListItem
                    key={suggestion.id}
                    button
                    onClick={() => handleSuggestionClick(suggestion)}
                    sx={{
                      py: 1,
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.08),
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      {getSuggestionIcon(suggestion.type)}
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2">
                            {suggestion.text}
                          </Typography>
                          
                          {suggestion.type !== 'recent' && suggestion.type !== 'popular' && (
                            <Chip
                              label={getSuggestionLabel(suggestion.type)}
                              size="small"
                              variant="outlined"
                              sx={{ 
                                fontSize: '0.7rem',
                                height: 20,
                                borderRadius: 1,
                              }}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        suggestion.data?.description && (
                          <Typography variant="caption" color="text.secondary">
                            {suggestion.data.description}
                          </Typography>
                        )
                      }
                    />

                    {suggestion.count && (
                      <Typography variant="caption" color="text.secondary">
                        {suggestion.count}
                      </Typography>
                    )}
                  </ListItem>
                );
              })}

              {query.trim() && suggestions.length === 0 && !isLoading && (
                <ListItem>
                  <ListItemText
                    primary={
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                        No results found for "{query}"
                      </Typography>
                    }
                  />
                </ListItem>
              )}

              {isLoading && (
                <ListItem>
                  <ListItemText
                    primary={
                      <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                        Searching...
                      </Typography>
                    }
                  />
                </ListItem>
              )}
            </List>
          </Paper>
        </Popper>

        {/* Pulse animation for loading indicator */}
        <style jsx>{`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
        `}</style>
      </Box>
    </ClickAwayListener>
  );
}