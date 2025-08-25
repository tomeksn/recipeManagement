import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Fade,
  useTheme,
  useMediaQuery,
  Fab,
  Backdrop,
} from '@mui/material';
import {
  FilterList,
  Close,
} from '@mui/icons-material';

import { SearchBar } from './SearchBar';
import { FilterPanel } from './FilterPanel';
import { SearchResults } from './SearchResults';
import { Product, FilterState, SearchResponse } from '@/types';
import { useProductSearch } from '@/hooks/useApi';

interface SearchInterfaceProps {
  onProductSelect?: (product: Product) => void;
  onProductEdit?: (product: Product) => void;
  onProductDelete?: (product: Product) => void;
  onProductDuplicate?: (product: Product) => void;
  onProductViewRecipe?: (product: Product) => void;
  onProductCalculate?: (product: Product) => void;
  initialQuery?: string;
  showHeader?: boolean;
  fullHeight?: boolean;
  categories?: string[];
  tags?: string[];
}

export function SearchInterface({
  onProductSelect,
  onProductEdit,
  onProductDelete,
  onProductDuplicate,
  onProductViewRecipe,
  onProductCalculate,
  initialQuery = '',
  showHeader = true,
  fullHeight = false,
  categories,
  tags,
}: SearchInterfaceProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [filters, setFilters] = useState<FilterState>({
    search: initialQuery,
    type: undefined,
    unit: undefined,
    category: undefined,
    tags: undefined,
  });
  
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState(initialQuery);

  // Search API
  const { 
    data: searchResults, 
    isLoading, 
    error, 
    refetch 
  } = useProductSearch(searchQuery);

  // Update search query when filters change
  useEffect(() => {
    if (filters.search !== searchQuery) {
      setSearchQuery(filters.search);
    }
  }, [filters.search]);

  const handleSearch = (query: string) => {
    setFilters(prev => ({ ...prev, search: query }));
  };

  const handleFiltersToggle = () => {
    setShowFilters(!showFilters);
  };

  const handleFiltersChange = (newFilters: FilterState) => {
    setFilters(newFilters);
  };

  const handleRetry = () => {
    refetch();
  };

  return (
    <Box
      sx={{
        minHeight: fullHeight ? '100vh' : 'auto',
        backgroundColor: 'background.default',
        backgroundImage: `linear-gradient(135deg, 
          ${theme.palette.background.default} 0%, 
          ${theme.palette.background.paper} 100%)`,
      }}
    >
      <Container maxWidth="xl" sx={{ py: showHeader ? 3 : 1 }}>
        {/* Header */}
        {showHeader && (
          <Fade in timeout={800}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                mb: 3,
                textAlign: 'center',
                backgroundColor: 'transparent',
                backgroundImage: `linear-gradient(135deg, 
                  ${theme.palette.primary.main}15, 
                  ${theme.palette.secondary.main}10)`,
                borderRadius: 3,
              }}
            >
              <Typography
                variant="h3"
                component="h1"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  background: `linear-gradient(45deg, 
                    ${theme.palette.primary.main}, 
                    ${theme.palette.secondary.main})`,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Recipe Management
              </Typography>
              
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ maxWidth: 600, mx: 'auto' }}
              >
                Search and manage your product catalog with intelligent filtering 
                and hierarchical recipe organization
              </Typography>
            </Paper>
          </Fade>
        )}

        {/* Search Bar */}
        <Fade in timeout={600} style={{ transitionDelay: '200ms' }}>
          <Box sx={{ mb: 3 }}>
            <SearchBar
              value={filters.search}
              onSearch={handleSearch}
              onSelect={onProductSelect}
              onFiltersToggle={handleFiltersToggle}
              showFilters={!isMobile}
              autoFocus={!showHeader}
              size={showHeader ? 'medium' : 'small'}
            />
          </Box>
        </Fade>

        {/* Main Content */}
        <Grid container spacing={3}>
          {/* Filter Panel - Desktop */}
          {!isMobile && (
            <Grid item xs={12} md={3}>
              <Fade in timeout={600} style={{ transitionDelay: '400ms' }}>
                <Box sx={{ position: 'sticky', top: 20 }}>
                  <FilterPanel
                    open={showFilters}
                    filters={filters}
                    onFiltersChange={handleFiltersChange}
                    categories={categories}
                    tags={tags}
                  />
                </Box>
              </Fade>
            </Grid>
          )}

          {/* Search Results */}
          <Grid item xs={12} md={!isMobile && showFilters ? 9 : 12}>
            <Fade in timeout={600} style={{ transitionDelay: '600ms' }}>
              <Box>
                <SearchResults
                  searchResults={searchResults}
                  loading={isLoading}
                  error={error?.message || null}
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  onProductSelect={onProductSelect}
                  onProductEdit={onProductEdit}
                  onProductDelete={onProductDelete}
                  onProductDuplicate={onProductDuplicate}
                  onProductViewRecipe={onProductViewRecipe}
                  onProductCalculate={onProductCalculate}
                  onRetry={handleRetry}
                />
              </Box>
            </Fade>
          </Grid>
        </Grid>

        {/* Mobile Filter Panel */}
        {isMobile && (
          <>
            {/* Filter FAB */}
            <Fab
              color="primary"
              aria-label="filters"
              onClick={handleFiltersToggle}
              sx={{
                position: 'fixed',
                bottom: 16,
                right: 16,
                zIndex: theme.zIndex.speedDial,
              }}
            >
              {showFilters ? <Close /> : <FilterList />}
            </Fab>

            {/* Filter Backdrop */}
            <Backdrop
              open={showFilters}
              onClick={handleFiltersToggle}
              sx={{
                zIndex: theme.zIndex.drawer,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
              }}
            >
              <Box
                onClick={(e) => e.stopPropagation()}
                sx={{
                  width: '90vw',
                  maxWidth: 400,
                  maxHeight: '80vh',
                  overflow: 'auto',
                }}
              >
                <FilterPanel
                  open={showFilters}
                  onClose={handleFiltersToggle}
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  orientation="vertical"
                  compact={true}
                  categories={categories}
                  tags={tags}
                />
              </Box>
            </Backdrop>
          </>
        )}
      </Container>
    </Box>
  );
}