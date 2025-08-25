import React, { useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Search,
  FilterList,
  Clear,
  TrendingUp,
  AccessTime,
  Visibility,
} from '@mui/icons-material';

import { Product, SearchResponse, FilterState } from '@/types';
import { ProductGrid } from './ProductGrid';

interface SearchResultsProps {
  searchResults?: SearchResponse<Product>;
  loading?: boolean;
  error?: string | null;
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onProductSelect?: (product: Product) => void;
  onProductEdit?: (product: Product) => void;
  onProductDelete?: (product: Product) => void;
  onProductDuplicate?: (product: Product) => void;
  onProductViewRecipe?: (product: Product) => void;
  onProductCalculate?: (product: Product) => void;
  onRetry?: () => void;
  showSuggestions?: boolean;
}

export function SearchResults({
  searchResults,
  loading = false,
  error = null,
  filters,
  onFiltersChange,
  onProductSelect,
  onProductEdit,
  onProductDelete,
  onProductDuplicate,
  onProductViewRecipe,
  onProductCalculate,
  onRetry,
  showSuggestions = true,
}: SearchResultsProps) {
  const theme = useTheme();

  // Filter and sort results based on current filters
  const filteredResults = useMemo(() => {
    if (!searchResults?.items) return [];

    let filtered = searchResults.items;

    // Apply type filter
    if (filters.type) {
      filtered = filtered.filter(product => product.type === filters.type);
    }

    // Apply unit filter
    if (filters.unit) {
      filtered = filtered.filter(product => product.unit === filters.unit);
    }

    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter(product => product.category === filters.category);
    }

    // Apply tags filter
    if (filters.tags && filters.tags.length > 0) {
      filtered = filtered.filter(product =>
        product.tags?.some(tag => filters.tags!.includes(tag))
      );
    }

    return filtered;
  }, [searchResults?.items, filters]);

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.type) count++;
    if (filters.unit) count++;
    if (filters.category) count++;
    if (filters.tags && filters.tags.length > 0) count += filters.tags.length;
    return count;
  };

  const handleClearFilters = () => {
    onFiltersChange({
      search: filters.search,
      type: undefined,
      unit: undefined,
      category: undefined,
      tags: undefined,
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    onFiltersChange({
      ...filters,
      search: suggestion,
    });
  };

  const activeFiltersCount = getActiveFiltersCount();
  const hasResults = filteredResults.length > 0;
  const hasQuery = filters.search.trim().length > 0;

  // Loading state
  if (loading) {
    return (
      <Box>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Search sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Searching...</Typography>
          </Box>
          <LinearProgress />
        </Paper>
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert 
        severity="error" 
        action={
          onRetry && (
            <Button color="inherit" size="small" onClick={onRetry}>
              Retry
            </Button>
          )
        }
        sx={{ mb: 2 }}
      >
        {error}
      </Alert>
    );
  }

  // No query state
  if (!hasQuery) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Search sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Start typing to search
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Search for products, recipes, or ingredients
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Search Header */}
      <Paper 
        sx={{ 
          p: 2, 
          mb: 2,
          backgroundColor: alpha(theme.palette.background.paper, 0.8),
          backdropFilter: 'blur(8px)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Search sx={{ color: 'primary.main' }} />
            <Typography variant="h6">
              Search Results
            </Typography>
            
            {searchResults && (
              <Chip
                label={`${filteredResults.length} of ${searchResults.items.length}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            )}
          </Box>

          {searchResults?.search_time_ms && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <AccessTime fontSize="small" sx={{ color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {searchResults.search_time_ms}ms
              </Typography>
            </Box>
          )}
        </Box>

        <Typography variant="body2" color="text.secondary">
          Results for "<strong>{filters.search}</strong>"
          {activeFiltersCount > 0 && ` with ${activeFiltersCount} filter${activeFiltersCount > 1 ? 's' : ''}`}
        </Typography>

        {/* Active Filters */}
        {activeFiltersCount > 0 && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <FilterList fontSize="small" />
              <Typography variant="caption" sx={{ fontWeight: 600 }}>
                Active Filters:
              </Typography>
              <Button
                size="small"
                startIcon={<Clear />}
                onClick={handleClearFilters}
                sx={{ ml: 'auto' }}
              >
                Clear All
              </Button>
            </Box>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {filters.type && (
                <Chip
                  label={`Type: ${filters.type}`}
                  size="small"
                  onDelete={() => onFiltersChange({ ...filters, type: undefined })}
                  color="primary"
                />
              )}
              
              {filters.unit && (
                <Chip
                  label={`Unit: ${filters.unit}`}
                  size="small"
                  onDelete={() => onFiltersChange({ ...filters, unit: undefined })}
                  color="primary"
                />
              )}
              
              {filters.category && (
                <Chip
                  label={`Category: ${filters.category}`}
                  size="small"
                  onDelete={() => onFiltersChange({ ...filters, category: undefined })}
                  color="primary"
                />
              )}
              
              {filters.tags?.map((tag) => (
                <Chip
                  key={tag}
                  label={`Tag: ${tag}`}
                  size="small"
                  onDelete={() => onFiltersChange({
                    ...filters,
                    tags: filters.tags!.filter(t => t !== tag),
                  })}
                  color="primary"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Search Suggestions */}
      {showSuggestions && searchResults?.suggestions && searchResults.suggestions.length > 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <TrendingUp fontSize="small" />
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Did you mean:
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {searchResults.suggestions.map((suggestion) => (
              <Chip
                key={suggestion}
                label={suggestion}
                size="small"
                variant="outlined"
                onClick={() => handleSuggestionClick(suggestion)}
                sx={{
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    borderColor: 'primary.main',
                  },
                }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Results */}
      {hasResults ? (
        <ProductGrid
          products={filteredResults}
          loading={false}
          error={null}
          onProductEdit={onProductEdit}
          onProductDelete={onProductDelete}
          onProductDuplicate={onProductDuplicate}
          onProductViewRecipe={onProductViewRecipe}
          onProductCalculate={onProductCalculate}
        />
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Box sx={{ opacity: 0.6, mb: 2 }}>
            <Search sx={{ fontSize: 48, color: 'text.secondary' }} />
          </Box>
          
          <Typography variant="h6" gutterBottom>
            No results found
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {activeFiltersCount > 0 ? (
              <>
                No products match your search criteria. Try removing some filters or 
                adjusting your search terms.
              </>
            ) : (
              <>
                No products found for "<strong>{filters.search}</strong>". 
                Try different keywords or check your spelling.
              </>
            )}
          </Typography>

          {activeFiltersCount > 0 && (
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={handleClearFilters}
              sx={{ mr: 1 }}
            >
              Clear Filters
            </Button>
          )}

          {searchResults?.suggestions && searchResults.suggestions.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Try these suggestions:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                {searchResults.suggestions.slice(0, 3).map((suggestion) => (
                  <Chip
                    key={suggestion}
                    label={suggestion}
                    variant="outlined"
                    onClick={() => handleSuggestionClick(suggestion)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Pagination could go here */}
      {searchResults && searchResults.pages > 1 && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Showing page {searchResults.page} of {searchResults.pages} 
            ({searchResults.total} total results)
          </Typography>
        </Box>
      )}
    </Box>
  );
}