import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  Autocomplete,
  TextField,
  Button,
  Tabs,
  Tab,
  Alert,
  Chip,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Calculate,
  Add,
  Delete,
  Clear,
  History,
  BatchPrediction,
  Restaurant,
  Speed,
  Assignment
} from '@mui/icons-material';

import { recipeService } from '@/services/recipeService';
import { calculatorService, CalculationRequest, BatchCalculationRequest } from '@/services/calculatorService';
import { CalculatorPanel } from '@/components/calculator';
import { Recipe } from '@/types';

interface BatchCalculationItem {
  id: string;
  recipe: Recipe;
  targetQuantity: number;
  targetUnit: 'piece' | 'gram';
}

export default function CalculatorPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [batchItems, setBatchItems] = useState<BatchCalculationItem[]>([]);
  const [batchResults, setBatchResults] = useState<any>(null);
  const [batchCalculationLoading, setBatchCalculationLoading] = useState(false);

  // Load recipes for selection
  const { data: recipesData, isLoading: recipesLoading } = useQuery({
    queryKey: ['recipes', 1, ''],
    queryFn: () => recipeService.getRecipes(1, 100),
  });

  // Load calculation history
  const { data: calculationHistory, refetch: refetchHistory } = useQuery({
    queryKey: ['calculationHistory'],
    queryFn: () => calculatorService.getCalculationHistory(20),
  });

  const recipes = recipesData?.items || [];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleRecipeSelect = (recipe: Recipe | null) => {
    setSelectedRecipe(recipe);
  };

  const handleAddToBatch = () => {
    if (!selectedRecipe) return;

    const newItem: BatchCalculationItem = {
      id: `batch-${Date.now()}`,
      recipe: selectedRecipe,
      targetQuantity: selectedRecipe.yield_quantity,
      targetUnit: selectedRecipe.yield_unit
    };

    setBatchItems(prev => [...prev, newItem]);
  };

  const handleRemoveFromBatch = (id: string) => {
    setBatchItems(prev => prev.filter(item => item.id !== id));
  };

  const handleBatchItemChange = (id: string, field: 'targetQuantity' | 'targetUnit', value: any) => {
    setBatchItems(prev => prev.map(item => 
      item.id === id ? { ...item, [field]: value } : item
    ));
  };

  const handleCalculateBatch = async () => {
    if (batchItems.length === 0) return;

    setBatchCalculationLoading(true);
    try {
      const request: BatchCalculationRequest = {
        calculations: batchItems.map(item => ({
          recipe_id: item.recipe.id,
          target_quantity: item.targetQuantity,
          target_unit: item.targetUnit
        }))
      };

      const result = await calculatorService.calculateBatch(request);
      setBatchResults(result);
      refetchHistory();
    } catch (error) {
      console.error('Batch calculation failed:', error);
    } finally {
      setBatchCalculationLoading(false);
    }
  };

  const handleClearBatch = () => {
    setBatchItems([]);
    setBatchResults(null);
  };

  const getUnitLabel = (unit: 'piece' | 'gram') => {
    return unit === 'piece' ? 'szt' : 'g';
  };

  const TabPanel = ({ children, value, index }: { children: React.ReactNode; value: number; index: number }) => (
    <Box role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </Box>
  );

  return (
    <>
      <Helmet>
        <title>Calculator - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Calculate sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant='h4' component='h1' sx={{ fontWeight: 600 }}>
              Kalkulator receptur
            </Typography>
          </Box>
          <Typography variant='body1' color='text.secondary'>
            Obliczaj składniki receptur dla różnych ilości oraz zarządzaj obliczeniami wsadowymi
          </Typography>
        </Box>

        {/* Recipe Selection */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Restaurant />
            Wybór receptury
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Autocomplete
                options={recipes}
                getOptionLabel={(option) => option.product?.name || 'Unknown recipe'}
                value={selectedRecipe}
                onChange={(_, newValue) => handleRecipeSelect(newValue)}
                loading={recipesLoading}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Wybierz recepturę do obliczeń"
                    placeholder="Wpisz nazwę receptury..."
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {recipesLoading ? <CircularProgress color="inherit" size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box>
                      <Typography variant="body2">{option.product?.name || 'Unknown recipe'}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Wydajność: {option.yield_quantity} {getUnitLabel(option.yield_unit)} • 
                        {option.ingredients.length} składników
                      </Typography>
                    </Box>
                  </li>
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={handleAddToBatch}
                disabled={!selectedRecipe}
                fullWidth
              >
                Dodaj do wsadu
              </Button>
            </Grid>
          </Grid>

          {selectedRecipe && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Wybrana receptura:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={selectedRecipe.product?.name || 'Unknown recipe'}
                  color="primary"
                />
                <Chip 
                  label={`${selectedRecipe.yield_quantity} ${getUnitLabel(selectedRecipe.yield_unit)}`}
                  variant="outlined"
                />
                <Chip 
                  label={`${selectedRecipe.ingredients.length} składników`}
                  variant="outlined"
                />
                {selectedRecipe.product?.category && (
                  <Chip 
                    label={selectedRecipe.product.category}
                    size="small"
                  />
                )}
              </Box>
            </Box>
          )}
        </Paper>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
          >
            <Tab 
              label="Pojedyncze obliczenie" 
              icon={<Calculate />} 
              iconPosition="start"
            />
            <Tab 
              label="Obliczenia wsadowe" 
              icon={<BatchPrediction />} 
              iconPosition="start"
            />
            <Tab 
              label="Historia obliczeń" 
              icon={<History />} 
              iconPosition="start"
            />
          </Tabs>

          {/* Single Calculation Tab */}
          <TabPanel value={activeTab} index={0}>
            <Box sx={{ p: 3 }}>
              <CalculatorPanel
                recipe={selectedRecipe}
                variant="full"
                showHistory={false}
                onCalculationComplete={() => refetchHistory()}
              />
            </Box>
          </TabPanel>

          {/* Batch Calculation Tab */}
          <TabPanel value={activeTab} index={1}>
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Obliczenia wsadowe ({batchItems.length} receptur)
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={batchCalculationLoading ? <CircularProgress size={16} /> : <Calculate />}
                    onClick={handleCalculateBatch}
                    disabled={batchItems.length === 0 || batchCalculationLoading}
                  >
                    {batchCalculationLoading ? 'Obliczam...' : 'Oblicz wsad'}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Clear />}
                    onClick={handleClearBatch}
                    disabled={batchItems.length === 0}
                  >
                    Wyczyść
                  </Button>
                </Box>
              </Box>

              {batchItems.length === 0 ? (
                <Alert severity="info">
                  Dodaj receptury do wsadu używając pola wyboru powyżej
                </Alert>
              ) : (
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Receptura</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Docelowa ilość</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Jednostka</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Bazowa wydajność</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Akcje</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {batchItems.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {item.recipe.product?.name || 'Unknown recipe'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {item.recipe.ingredients.length} składników
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            value={item.targetQuantity}
                            onChange={(e) => handleBatchItemChange(item.id, 'targetQuantity', parseFloat(e.target.value) || 0)}
                            size="small"
                            inputProps={{ min: 0.001, step: 0.001 }}
                            sx={{ width: 100 }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            select
                            value={item.targetUnit}
                            onChange={(e) => handleBatchItemChange(item.id, 'targetUnit', e.target.value)}
                            size="small"
                            sx={{ width: 80 }}
                          >
                            <option value="piece">szt</option>
                            <option value="gram">g</option>
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {item.recipe.yield_quantity} {getUnitLabel(item.recipe.yield_unit)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => handleRemoveFromBatch(item.id)}
                            color="error"
                          >
                            <Delete />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}

              {/* Batch Results */}
              {batchResults && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Wyniki obliczeń wsadowych
                  </Typography>
                  
                  <Box sx={{ mb: 2, p: 2, bgcolor: 'success.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="success.main">
                      <strong>
                        Obliczono {batchResults.calculations.length} receptur w czasie {batchResults.total_calculation_time_ms}ms
                      </strong>
                    </Typography>
                  </Box>

                  <Grid container spacing={2}>
                    {batchResults.calculations.map((result: any, index: number) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Card>
                          <CardHeader
                            title={result.recipe_name}
                            subheader={`Współczynnik: ${result.scale_factor.toFixed(3)}`}
                            action={
                              <Chip 
                                label={`${result.ingredients.length} składników`}
                                size="small"
                              />
                            }
                          />
                          <CardContent>
                            <Typography variant="body2" gutterBottom>
                              <strong>Wydajność:</strong> {result.original_yield.quantity} → {result.target_yield.quantity} {getUnitLabel(result.target_yield.unit)}
                            </Typography>
                            
                            {result.total_weight_grams && (
                              <Typography variant="body2">
                                <strong>Całkowita masa:</strong> {result.total_weight_grams.toFixed(2)}g
                              </Typography>
                            )}
                            
                            {result.total_pieces && (
                              <Typography variant="body2">
                                <strong>Całkowita liczba sztuk:</strong> {result.total_pieces}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </>
              )}
            </Box>
          </TabPanel>

          {/* History Tab */}
          <TabPanel value={activeTab} index={2}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assignment />
                Historia obliczeń
              </Typography>

              {!calculationHistory || calculationHistory.length === 0 ? (
                <Alert severity="info">
                  Brak historii obliczeń. Wykonaj pierwsze obliczenie, aby zobaczyć historię.
                </Alert>
              ) : (
                <List>
                  {calculationHistory.map((item) => (
                    <ListItem
                      key={item.id}
                      sx={{ 
                        border: 1,
                        borderColor: 'grey.200',
                        borderRadius: 1,
                        mb: 1,
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {item.recipe_name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(item.created_at).toLocaleDateString('pl-PL', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                            <Chip 
                              label={`${item.target_quantity} ${getUnitLabel(item.target_unit)}`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Chip 
                              label={`Współczynnik: ${item.scale_factor.toFixed(3)}`}
                              size="small"
                              variant="outlined"
                            />
                            <Chip 
                              label={`${item.result.ingredients.length} składników`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </TabPanel>
        </Paper>
      </Container>
    </>
  );
}