import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  RadioGroup,
  Radio,
  Chip,
  Slider,
  TextField,
  Button,
  IconButton,
  Divider,
  Collapse,
  useTheme,
  alpha,
} from '@mui/material';
import {
  ExpandMore,
  FilterList,
  Clear,
  Tune,
  Category,
  Label,
  Scale,
  DateRange,
  Close,
} from '@mui/icons-material';

import { FilterState, Product } from '@/types';

interface FilterPanelProps {
  open?: boolean;
  onClose?: () => void;
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  orientation?: 'vertical' | 'horizontal';
  compact?: boolean;
  categories?: string[];
  tags?: string[];
}

interface FilterSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  expanded: boolean;
}

const productTypes: Array<{ value: Product['type']; label: string; color: string }> = [
  { value: 'standard', label: 'Standard Products', color: '#0079bf' },
  { value: 'semi-product', label: 'Semi-Products', color: '#838c91' },
  { value: 'kit', label: 'Kit Products', color: '#61bd4f' },
];

const units: Array<{ value: Product['unit']; label: string }> = [
  { value: 'piece', label: 'Pieces (pcs)' },
  { value: 'gram', label: 'Grams (g)' },
];

const defaultCategories = [
  'Ingredients',
  'Semi-Products',
  'Flavorings',
  'Preservatives',
  'Packaging',
  'Equipment',
];

const defaultTags = [
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
];

export function FilterPanel({
  open = true,
  onClose,
  filters,
  onFiltersChange,
  orientation = 'vertical',
  compact = false,
  categories = defaultCategories,
  tags = defaultTags,
}: FilterPanelProps) {
  const theme = useTheme();
  const [sections, setSections] = useState<FilterSection[]>([
    { id: 'type', title: 'Product Type', icon: <Category />, expanded: true },
    { id: 'unit', title: 'Unit', icon: <Scale />, expanded: false },
    { id: 'category', title: 'Category', icon: <Label />, expanded: false },
    { id: 'tags', title: 'Tags', icon: <Label />, expanded: false },
  ]);

  const toggleSection = (sectionId: string) => {
    setSections(sections.map(section =>
      section.id === sectionId
        ? { ...section, expanded: !section.expanded }
        : section
    ));
  };

  const handleTypeChange = (type: Product['type']) => {
    onFiltersChange({
      ...filters,
      type: filters.type === type ? undefined : type,
    });
  };

  const handleUnitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const unit = event.target.value as Product['unit'];
    onFiltersChange({
      ...filters,
      unit: filters.unit === unit ? undefined : unit,
    });
  };

  const handleCategoryChange = (category: string) => {
    onFiltersChange({
      ...filters,
      category: filters.category === category ? undefined : category,
    });
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter(t => t !== tag)
      : [...currentTags, tag];
    
    onFiltersChange({
      ...filters,
      tags: newTags.length > 0 ? newTags : undefined,
    });
  };

  const handleClearFilters = () => {
    onFiltersChange({
      search: filters.search, // Keep search query
      type: undefined,
      unit: undefined,
      category: undefined,
      tags: undefined,
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.type) count++;
    if (filters.unit) count++;
    if (filters.category) count++;
    if (filters.tags && filters.tags.length > 0) count += filters.tags.length;
    return count;
  };

  const renderTypeFilter = () => (
    <Box sx={{ p: 2 }}>
      <FormGroup>
        {productTypes.map((type) => (
          <FormControlLabel
            key={type.value}
            control={
              <Checkbox
                checked={filters.type === type.value}
                onChange={() => handleTypeChange(type.value)}
                sx={{
                  color: type.color,
                  '&.Mui-checked': {
                    color: type.color,
                  },
                }}
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2">{type.label}</Typography>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: type.color,
                  }}
                />
              </Box>
            }
          />
        ))}
      </FormGroup>
    </Box>
  );

  const renderUnitFilter = () => (
    <Box sx={{ p: 2 }}>
      <RadioGroup
        value={filters.unit || ''}
        onChange={handleUnitChange}
      >
        <FormControlLabel
          value=""
          control={<Radio size="small" />}
          label="All Units"
        />
        {units.map((unit) => (
          <FormControlLabel
            key={unit.value}
            value={unit.value}
            control={<Radio size="small" />}
            label={unit.label}
          />
        ))}
      </RadioGroup>
    </Box>
  );

  const renderCategoryFilter = () => (
    <Box sx={{ p: 2 }}>
      <FormGroup>
        {categories.map((category) => (
          <FormControlLabel
            key={category}
            control={
              <Checkbox
                checked={filters.category === category}
                onChange={() => handleCategoryChange(category)}
                size="small"
              />
            }
            label={
              <Typography variant="body2">{category}</Typography>
            }
          />
        ))}
      </FormGroup>
    </Box>
  );

  const renderTagsFilter = () => (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {tags.map((tag) => (
          <Chip
            key={tag}
            label={tag}
            size="small"
            variant={filters.tags?.includes(tag) ? 'filled' : 'outlined'}
            color={filters.tags?.includes(tag) ? 'primary' : 'default'}
            onClick={() => handleTagToggle(tag)}
            sx={{
              borderRadius: 2,
              '&:hover': {
                backgroundColor: filters.tags?.includes(tag)
                  ? alpha(theme.palette.primary.main, 0.8)
                  : alpha(theme.palette.primary.main, 0.1),
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );

  const renderFilterSection = (section: FilterSection) => {
    const content = {
      type: renderTypeFilter(),
      unit: renderUnitFilter(),
      category: renderCategoryFilter(),
      tags: renderTagsFilter(),
    }[section.id];

    if (compact) {
      return (
        <Collapse key={section.id} in={section.expanded}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              {section.title}
            </Typography>
            {content}
          </Box>
        </Collapse>
      );
    }

    return (
      <Accordion
        key={section.id}
        expanded={section.expanded}
        onChange={() => toggleSection(section.id)}
        elevation={0}
        sx={{
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
          '&:before': { display: 'none' },
          '&.Mui-expanded': {
            margin: 'auto',
          },
        }}
      >
        <AccordionSummary
          expandIcon={<ExpandMore />}
          sx={{
            backgroundColor: alpha(theme.palette.background.default, 0.5),
            borderRadius: 1,
            '&.Mui-expanded': {
              borderBottomLeftRadius: 0,
              borderBottomRightRadius: 0,
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {section.icon}
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {section.title}
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          {content}
        </AccordionDetails>
      </Accordion>
    );
  };

  const activeFiltersCount = getActiveFiltersCount();

  if (orientation === 'horizontal') {
    return (
      <Collapse in={open}>
        <Paper
          sx={{
            p: 2,
            mb: 2,
            backgroundColor: alpha(theme.palette.background.paper, 0.8),
            backdropFilter: 'blur(8px)',
            border: 1,
            borderColor: 'divider',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tune />
              <Typography variant="h6">Filters</Typography>
              {activeFiltersCount > 0 && (
                <Chip
                  label={activeFiltersCount}
                  size="small"
                  color="primary"
                  sx={{ fontWeight: 600 }}
                />
              )}
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              {activeFiltersCount > 0 && (
                <Button
                  size="small"
                  startIcon={<Clear />}
                  onClick={handleClearFilters}
                >
                  Clear All
                </Button>
              )}
              
              {onClose && (
                <IconButton size="small" onClick={onClose}>
                  <Close />
                </IconButton>
              )}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            {sections.filter(s => s.expanded).map(renderFilterSection)}
          </Box>
        </Paper>
      </Collapse>
    );
  }

  return (
    <Collapse in={open}>
      <Paper
        sx={{
          width: compact ? '100%' : 280,
          backgroundColor: alpha(theme.palette.background.paper, 0.8),
          backdropFilter: 'blur(8px)',
          border: 1,
          borderColor: 'divider',
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList />
              <Typography variant="h6">Filters</Typography>
              {activeFiltersCount > 0 && (
                <Chip
                  label={activeFiltersCount}
                  size="small"
                  color="primary"
                  sx={{ fontWeight: 600 }}
                />
              )}
            </Box>
            
            {onClose && (
              <IconButton size="small" onClick={onClose}>
                <Close />
              </IconButton>
            )}
          </Box>

          {activeFiltersCount > 0 && (
            <Button
              size="small"
              startIcon={<Clear />}
              onClick={handleClearFilters}
              sx={{ mt: 1 }}
              fullWidth
            >
              Clear All Filters
            </Button>
          )}
        </Box>

        {/* Filter Sections */}
        <Box sx={{ p: compact ? 1 : 0 }}>
          {sections.map(renderFilterSection)}
        </Box>
      </Paper>
    </Collapse>
  );
}