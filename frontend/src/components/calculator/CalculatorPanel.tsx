import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
  Collapse,
  List,
  ListItem
} from '@mui/material';
import {
  Calculate,
  Download,
  History,
  Clear,
  ExpandMore,
  ExpandLess,
  GetApp,
  Description,
  Code,
  TextSnippet
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';

import { calculatorService, CalculationRequest, CalculationResult } from '@/services/calculatorService';
import { Recipe } from '@/types';

interface CalculatorPanelProps {
  recipe?: Recipe;
  onCalculationComplete?: (result: CalculationResult) => void;
  variant?: 'compact' | 'full';
  showHistory?: boolean;
}

export default function CalculatorPanel({
  recipe,
  onCalculationComplete,
  variant = 'full',
  showHistory = true
}: CalculatorPanelProps) {
  const [targetQuantity, setTargetQuantity] = useState<number>(1);
  const [targetUnit, setTargetUnit] = useState<'piece' | 'gram'>('piece');
  const [calculationResult, setCalculationResult] = useState<CalculationResult | null>(null);
  const [showIngredients, setShowIngredients] = useState(true);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<HTMLElement | null>(null);

  // Load calculation history
  const { data: calculationHistory } = useQuery({
    queryKey: ['calculationHistory'],
    queryFn: () => calculatorService.getCalculationHistory(10),
    enabled: showHistory
  });

  // Calculate mutation
  const calculateMutation = useMutation({
    mutationFn: (request: CalculationRequest) => calculatorService.calculateRecipe(request),
    onSuccess: (result) => {
      setCalculationResult(result);
      onCalculationComplete?.(result);
    }
  });

  // Initialize target unit based on recipe
  useEffect(() => {
    if (recipe && targetUnit !== recipe.yield_unit) {
      setTargetUnit(recipe.yield_unit);
      setTargetQuantity(recipe.yield_quantity);
    }
  }, [recipe]);

  const handleCalculate = () => {
    if (!recipe) return;

    const request: CalculationRequest = {
      recipe_id: recipe.id,
      target_quantity: targetQuantity,
      target_unit: targetUnit
    };

    calculateMutation.mutate(request);
  };

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportMenuAnchor(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportMenuAnchor(null);
  };

  const handleExport = (format: 'csv' | 'json' | 'txt') => {
    if (calculationResult) {
      calculatorService.exportCalculation(calculationResult, format);
    }
    handleExportClose();
  };

  const handleClearResult = () => {
    setCalculationResult(null);
  };

  const handleHistoryItemClick = (historyItem: any) => {
    setTargetQuantity(historyItem.target_quantity);
    setTargetUnit(historyItem.target_unit);
    setCalculationResult(historyItem.result);
  };

  const getUnitLabel = (unit: 'piece' | 'gram') => {
    return unit === 'piece' ? 'szt' : 'g';
  };

  if (!recipe && variant === 'compact') {
    return (
      <Paper sx={{ p: 2 }}>
        <Alert severity="info">
          Wybierz recepturę, aby skorzystać z kalkulatora
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: variant === 'compact' ? 2 : 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant={variant === 'compact' ? 'h6' : 'h5'} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Calculate />
          Kalkulator receptur
        </Typography>
        {calculationResult && (
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton
              size="small"
              onClick={handleExportClick}
              title="Eksportuj wyniki"
            >
              <Download />
            </IconButton>
            <IconButton
              size="small"
              onClick={handleClearResult}
              title="Wyczyść wyniki"
            >
              <Clear />
            </IconButton>
          </Box>
        )}
      </Box>

      {recipe && (
        <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Aktywna receptura:
          </Typography>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {recipe.product?.name || 'Nieznana receptura'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Bazowa wydajność: {recipe.yield_quantity} {getUnitLabel(recipe.yield_unit)}
          </Typography>
        </Box>
      )}

      {/* Calculator Inputs */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          label="Docelowa ilość"
          type="number"
          value={targetQuantity}
          onChange={(e) => setTargetQuantity(parseFloat(e.target.value) || 0)}
          inputProps={{ min: 0.001, step: 0.001 }}
          sx={{ flex: 1, minWidth: 120 }}
          disabled={!recipe}
        />

        <FormControl sx={{ flex: 1, minWidth: 100 }}>
          <InputLabel>Jednostka</InputLabel>
          <Select
            value={targetUnit}
            label="Jednostka"
            onChange={(e) => setTargetUnit(e.target.value as 'piece' | 'gram')}
            disabled={!recipe}
          >
            <MenuItem value="piece">Sztuki (szt)</MenuItem>
            <MenuItem value="gram">Gramy (g)</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="contained"
          startIcon={calculateMutation.isPending ? <CircularProgress size={16} /> : <Calculate />}
          onClick={handleCalculate}
          disabled={!recipe || targetQuantity <= 0 || calculateMutation.isPending}
          sx={{ minWidth: 120 }}
        >
          {calculateMutation.isPending ? 'Obliczam...' : 'Oblicz'}
        </Button>
      </Box>

      {/* Error Display */}
      {calculateMutation.error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {(calculateMutation.error as any)?.message || 'Błąd podczas obliczania'}
        </Alert>
      )}

      {/* Calculation Results */}
      {calculationResult && (
        <>
          <Divider sx={{ mb: 2 }} />
          
          {/* Result Summary */}
          <Box sx={{ mb: 2, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
              Wynik obliczeń
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 1 }}>
              <Chip 
                label={`Współczynnik: ${calculationResult.scale_factor.toFixed(3)}`}
                color="primary"
                size="small"
              />
              <Chip 
                label={`${calculationResult.ingredients.length} składników`}
                variant="outlined"
                size="small"
              />
              {calculationResult.total_weight_grams && (
                <Chip 
                  label={`Masa: ${calculationResult.total_weight_grams.toFixed(2)}g`}
                  variant="outlined"
                  size="small"
                />
              )}
              {calculationResult.total_pieces && (
                <Chip 
                  label={`Sztuk: ${calculationResult.total_pieces}`}
                  variant="outlined"
                  size="small"
                />
              )}
            </Box>

            <Typography variant="body2" color="text.secondary">
              Czas obliczeń: {calculationResult.calculation_time_ms}ms
            </Typography>
          </Box>

          {/* Ingredients Table Toggle */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Button
              onClick={() => setShowIngredients(!showIngredients)}
              startIcon={showIngredients ? <ExpandLess /> : <ExpandMore />}
              size="small"
            >
              Przeliczone składniki
            </Button>
          </Box>

          <Collapse in={showIngredients}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Składnik</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Oryginalna</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Przeliczona</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Jednostka</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Typ</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {calculationResult.ingredients.map((ingredient, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {ingredient.product_name}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="text.secondary">
                        {ingredient.original_quantity}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ fontWeight: 500, color: 'primary.main' }}>
                        {ingredient.calculated_quantity.toFixed(ingredient.unit === 'piece' ? 0 : 2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getUnitLabel(ingredient.unit)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={ingredient.ingredient_type}
                        size="small"
                        color={ingredient.ingredient_type === 'semi-product' ? 'secondary' : 'default'}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Collapse>
        </>
      )}

      {/* Calculation History */}
      {showHistory && calculationHistory && calculationHistory.length > 0 && variant === 'full' && (
        <>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History />
            Historia obliczeń
          </Typography>
          
          <List dense>
            {calculationHistory.slice(0, 5).map((item) => (
              <ListItem
                key={item.id}
                sx={{ 
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                  borderRadius: 1,
                  mb: 0.5
                }}
                onClick={() => handleHistoryItemClick(item)}
              >
                <Box sx={{ width: '100%' }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {item.recipe_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.target_quantity} {getUnitLabel(item.target_unit)} • 
                    współczynnik: {item.scale_factor.toFixed(3)} • 
                    {new Date(item.created_at).toLocaleDateString('pl-PL')}
                  </Typography>
                </Box>
              </ListItem>
            ))}
          </List>
        </>
      )}

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={handleExportClose}
      >
        <MenuItem onClick={() => handleExport('csv')}>
          <ListItemIcon>
            <Description fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eksport CSV</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleExport('json')}>
          <ListItemIcon>
            <Code fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eksport JSON</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleExport('txt')}>
          <ListItemIcon>
            <TextSnippet fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eksport TXT</ListItemText>
        </MenuItem>
      </Menu>
    </Paper>
  );
}