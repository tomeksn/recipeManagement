import { apiClient } from './apiClient';
import { mockService } from './mockService';

export interface CalculationRequest {
  recipe_id: string;
  target_quantity: number;
  target_unit: 'piece' | 'gram';
}

export interface BatchCalculationRequest {
  calculations: CalculationRequest[];
}

export interface CalculatedIngredient {
  product_id: string;
  product_name: string;
  original_quantity: number;
  calculated_quantity: number;
  unit: 'piece' | 'gram';
  ingredient_type: 'standard' | 'semi-product' | 'kit';
}

export interface CalculationResult {
  recipe_id: string;
  recipe_name: string;
  original_yield: {
    quantity: number;
    unit: 'piece' | 'gram';
  };
  target_yield: {
    quantity: number;
    unit: 'piece' | 'gram';
  };
  scale_factor: number;
  ingredients: CalculatedIngredient[];
  hierarchical_ingredients?: CalculatedIngredient[];
  total_weight_grams?: number;
  total_pieces?: number;
  calculation_time_ms: number;
}

export interface BatchCalculationResult {
  calculations: CalculationResult[];
  total_calculation_time_ms: number;
}

export interface CalculationHistory {
  id: string;
  recipe_id: string;
  recipe_name: string;
  target_quantity: number;
  target_unit: 'piece' | 'gram';
  scale_factor: number;
  created_at: string;
  result: CalculationResult;
}

export interface CalculationCache {
  cache_key: string;
  recipe_id: string;
  target_quantity: number;
  target_unit: 'piece' | 'gram';
  cached_at: string;
  result: CalculationResult;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = import.meta.env.VITE_OFFLINE_MODE === 'true';

class CalculatorService {
  private baseURL = API_BASE;

  /**
   * Calculate ingredients for a single recipe with target quantity
   */
  async calculateRecipe(request: CalculationRequest): Promise<CalculationResult> {
    if (USE_MOCK) {
      return this.mockCalculateRecipe(request);
    }

    try {
      const response = await apiClient.post(`${this.baseURL}/calculate`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to calculate recipe:', error);
      // Fallback to mock service
      return this.mockCalculateRecipe(request);
    }
  }

  /**
   * Calculate multiple recipes in batch
   */
  async calculateBatch(request: BatchCalculationRequest): Promise<BatchCalculationResult> {
    if (USE_MOCK) {
      return this.mockCalculateBatch(request);
    }

    try {
      const response = await apiClient.post(`${this.baseURL}/calculate/batch`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to calculate batch:', error);
      // Fallback to mock service
      return this.mockCalculateBatch(request);
    }
  }

  /**
   * Get calculation history for a user
   */
  async getCalculationHistory(limit: number = 50): Promise<CalculationHistory[]> {
    if (USE_MOCK) {
      return this.mockGetCalculationHistory(limit);
    }

    try {
      const response = await apiClient.get(`${this.baseURL}/history?limit=${limit}`);
      return response.data.items || [];
    } catch (error) {
      console.error('Failed to get calculation history:', error);
      return this.mockGetCalculationHistory(limit);
    }
  }

  /**
   * Clear calculation cache
   */
  async clearCalculationCache(): Promise<void> {
    if (USE_MOCK) {
      localStorage.removeItem('calculator_cache');
      return;
    }

    try {
      await apiClient.delete(`${this.baseURL}/cache`);
    } catch (error) {
      console.error('Failed to clear calculation cache:', error);
      localStorage.removeItem('calculator_cache');
    }
  }

  /**
   * Get calculator service health status
   */
  async getHealthStatus() {
    if (USE_MOCK) {
      return { status: 'healthy', service: 'mock' };
    }

    try {
      const response = await apiClient.get(`${this.baseURL}/health`);
      return response.data;
    } catch (error) {
      console.error('Calculator service health check failed:', error);
      return { status: 'unhealthy', error: error.message };
    }
  }

  // Mock implementations for development
  private async mockCalculateRecipe(request: CalculationRequest): Promise<CalculationResult> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));

    // Get recipe from mock service
    const recipe = await mockService.getRecipe(request.recipe_id);
    if (!recipe) {
      throw new Error('Recipe not found');
    }

    const scaleFactor = request.target_quantity / recipe.yield_quantity;

    const calculatedIngredients: CalculatedIngredient[] = recipe.ingredients.map(ingredient => ({
      product_id: ingredient.product_id,
      product_name: ingredient.product?.name || 'Unknown product',
      original_quantity: ingredient.quantity,
      calculated_quantity: ingredient.quantity * scaleFactor,
      unit: ingredient.unit,
      ingredient_type: ingredient.product?.type || 'standard'
    }));

    const result: CalculationResult = {
      recipe_id: recipe.id,
      recipe_name: recipe.product?.name || 'Unknown recipe',
      original_yield: {
        quantity: recipe.yield_quantity,
        unit: recipe.yield_unit
      },
      target_yield: {
        quantity: request.target_quantity,
        unit: request.target_unit
      },
      scale_factor: scaleFactor,
      ingredients: calculatedIngredients,
      total_weight_grams: calculatedIngredients
        .filter(ing => ing.unit === 'gram')
        .reduce((sum, ing) => sum + ing.calculated_quantity, 0),
      total_pieces: calculatedIngredients
        .filter(ing => ing.unit === 'piece')
        .reduce((sum, ing) => sum + ing.calculated_quantity, 0),
      calculation_time_ms: 150
    };

    // Save to local storage as cache
    this.saveToLocalCache(request, result);

    return result;
  }

  private async mockCalculateBatch(request: BatchCalculationRequest): Promise<BatchCalculationResult> {
    const start = Date.now();
    
    const calculations = await Promise.all(
      request.calculations.map(calc => this.mockCalculateRecipe(calc))
    );

    return {
      calculations,
      total_calculation_time_ms: Date.now() - start
    };
  }

  private mockGetCalculationHistory(limit: number): CalculationHistory[] {
    const history = JSON.parse(localStorage.getItem('calculation_history') || '[]');
    return history.slice(0, limit);
  }

  private saveToLocalCache(request: CalculationRequest, result: CalculationResult) {
    // Save to calculation history
    const history = JSON.parse(localStorage.getItem('calculation_history') || '[]');
    const historyItem: CalculationHistory = {
      id: `calc-${Date.now()}`,
      recipe_id: request.recipe_id,
      recipe_name: result.recipe_name,
      target_quantity: request.target_quantity,
      target_unit: request.target_unit,
      scale_factor: result.scale_factor,
      created_at: new Date().toISOString(),
      result
    };

    history.unshift(historyItem);
    history.splice(20); // Keep only last 20 calculations
    localStorage.setItem('calculation_history', JSON.stringify(history));
  }

  /**
   * Export calculation results to different formats
   */
  exportCalculation(result: CalculationResult, format: 'csv' | 'json' | 'txt') {
    const filename = `recipe-calculation-${result.recipe_id}-${Date.now()}.${format}`;
    
    switch (format) {
      case 'csv':
        this.exportToCSV(result, filename);
        break;
      case 'json':
        this.exportToJSON(result, filename);
        break;
      case 'txt':
        this.exportToTXT(result, filename);
        break;
    }
  }

  private exportToCSV(result: CalculationResult, filename: string) {
    const header = 'Product Name,Original Quantity,Calculated Quantity,Unit,Type\n';
    const rows = result.ingredients.map(ing => 
      `"${ing.product_name}",${ing.original_quantity},${ing.calculated_quantity.toFixed(2)},${ing.unit},${ing.ingredient_type}`
    ).join('\n');
    
    const csv = header + rows;
    this.downloadFile(csv, filename, 'text/csv');
  }

  private exportToJSON(result: CalculationResult, filename: string) {
    const json = JSON.stringify(result, null, 2);
    this.downloadFile(json, filename, 'application/json');
  }

  private exportToTXT(result: CalculationResult, filename: string) {
    let txt = `Recipe Calculation Report\n`;
    txt += `========================\n\n`;
    txt += `Recipe: ${result.recipe_name}\n`;
    txt += `Scale Factor: ${result.scale_factor.toFixed(3)}\n`;
    txt += `Original Yield: ${result.original_yield.quantity} ${result.original_yield.unit}\n`;
    txt += `Target Yield: ${result.target_yield.quantity} ${result.target_yield.unit}\n\n`;
    txt += `Ingredients:\n`;
    txt += `-----------\n`;
    
    result.ingredients.forEach((ing, index) => {
      txt += `${index + 1}. ${ing.product_name}\n`;
      txt += `   Original: ${ing.original_quantity} ${ing.unit}\n`;
      txt += `   Calculated: ${ing.calculated_quantity.toFixed(2)} ${ing.unit}\n`;
      txt += `   Type: ${ing.ingredient_type}\n\n`;
    });

    if (result.total_weight_grams) {
      txt += `Total Weight: ${result.total_weight_grams.toFixed(2)}g\n`;
    }
    if (result.total_pieces) {
      txt += `Total Pieces: ${result.total_pieces}\n`;
    }

    this.downloadFile(txt, filename, 'text/plain');
  }

  private downloadFile(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }
}

export const calculatorService = new CalculatorService();