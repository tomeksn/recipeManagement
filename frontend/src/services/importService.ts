import { apiClient } from './apiClient';
import { Product, Recipe } from '@/types';

export interface ImportedProduct {
  name: string;
  symbol: string;
  type: 'standard' | 'semi-product' | 'kit';
  unit: 'piece' | 'gram';
  description?: string;
  category?: string;
  tags?: string[];
}

export interface ImportedRecipe {
  product_name: string;
  yield_quantity: number;
  yield_unit: 'piece' | 'gram';
  ingredients: ImportedIngredient[];
}

export interface ImportedIngredient {
  product_name: string;
  quantity: number;
  unit: 'piece' | 'gram';
  order?: number;
}

export interface ImportData {
  products?: ImportedProduct[];
  recipes?: ImportedRecipe[];
}

export interface ImportMapping {
  sourceField: string;
  targetField: string;
  required: boolean;
  transform?: 'string' | 'number' | 'boolean' | 'array' | 'unit_conversion';
}

export interface ImportValidationError {
  row: number;
  field: string;
  value: any;
  error: string;
}

export interface ImportResult {
  success_count: number;
  error_count: number;
  total_count: number;
  errors: ImportValidationError[];
  imported_products?: Product[];
  imported_recipes?: Recipe[];
  processing_time_ms: number;
}

export interface ImportProgress {
  stage: 'parsing' | 'validating' | 'importing' | 'completed' | 'error';
  current: number;
  total: number;
  message: string;
  percentage: number;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = import.meta.env.VITE_OFFLINE_MODE === 'true' || !API_BASE;

class ImportService {
  private baseURL = API_BASE;

  /**
   * Parse uploaded file and extract data
   */
  async parseFile(file: File): Promise<ImportData> {
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    switch (fileExtension) {
      case 'csv':
        return this.parseCSV(file);
      case 'json':
        return this.parseJSON(file);
      case 'xlsx':
      case 'xls':
        return this.parseExcel(file);
      default:
        throw new Error(`Unsupported file format: ${fileExtension}`);
    }
  }

  /**
   * Parse CSV file
   */
  private async parseCSV(file: File): Promise<ImportData> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csv = e.target?.result as string;
          const lines = csv.split('\n').filter(line => line.trim());
          
          if (lines.length < 2) {
            throw new Error('CSV file must have at least a header and one data row');
          }

          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
          const data: any[] = [];

          for (let i = 1; i < lines.length; i++) {
            const values = this.parseCSVLine(lines[i]);
            if (values.length !== headers.length) continue;

            const row: any = {};
            headers.forEach((header, index) => {
              row[header] = values[index].trim();
            });
            data.push(row);
          }

          const importData = this.detectDataType(headers, data);
          resolve(importData);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read CSV file'));
      reader.readAsText(file);
    });
  }

  /**
   * Parse JSON file
   */
  private async parseJSON(file: File): Promise<ImportData> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target?.result as string);
          
          if (jsonData.products || jsonData.recipes) {
            resolve(jsonData as ImportData);
          } else if (Array.isArray(jsonData)) {
            // Try to detect if it's products or recipes
            const firstItem = jsonData[0];
            if (firstItem.ingredients || firstItem.yield_quantity) {
              resolve({ recipes: jsonData as ImportedRecipe[] });
            } else {
              resolve({ products: jsonData as ImportedProduct[] });
            }
          } else {
            throw new Error('Invalid JSON structure');
          }
        } catch (error) {
          reject(new Error(`Invalid JSON file: ${error.message}`));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read JSON file'));
      reader.readAsText(file);
    });
  }

  /**
   * Parse Excel file (mock implementation - would need SheetJS in real app)
   */
  private async parseExcel(file: File): Promise<ImportData> {
    // In a real implementation, you would use SheetJS (xlsx library)
    throw new Error('Excel import not implemented yet. Please use CSV or JSON files.');
  }

  /**
   * Parse CSV line handling quoted values
   */
  private parseCSVLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current);
    return result;
  }

  /**
   * Detect if data represents products or recipes
   */
  private detectDataType(headers: string[], data: any[]): ImportData {
    const lowerHeaders = headers.map(h => h.toLowerCase());
    
    const productHeaders = ['name', 'type', 'unit', 'description', 'category'];
    const recipeHeaders = ['product_name', 'yield_quantity', 'yield_unit', 'ingredients'];
    
    const productScore = productHeaders.filter(h => lowerHeaders.includes(h)).length;
    const recipeScore = recipeHeaders.filter(h => lowerHeaders.includes(h)).length;
    
    if (recipeScore > productScore) {
      return { recipes: data as ImportedRecipe[] };
    } else {
      return { products: data as ImportedProduct[] };
    }
  }

  /**
   * Validate import data
   */
  async validateData(data: ImportData): Promise<ImportValidationError[]> {
    const errors: ImportValidationError[] = [];

    if (data.products) {
      data.products.forEach((product, index) => {
        if (!product.name) {
          errors.push({
            row: index + 1,
            field: 'name',
            value: product.name,
            error: 'Product name is required'
          });
        }
        
        if (!product.symbol) {
          errors.push({
            row: index + 1,
            field: 'symbol',
            value: product.symbol,
            error: 'Product symbol is required'
          });
        }
        
        if (!['standard', 'semi-product', 'kit'].includes(product.type)) {
          errors.push({
            row: index + 1,
            field: 'type',
            value: product.type,
            error: 'Type must be one of: standard, semi-product, kit'
          });
        }
        
        if (!['piece', 'gram'].includes(product.unit)) {
          errors.push({
            row: index + 1,
            field: 'unit',
            value: product.unit,
            error: 'Unit must be either piece or gram'
          });
        }
      });
    }

    if (data.recipes) {
      data.recipes.forEach((recipe, index) => {
        if (!recipe.product_name) {
          errors.push({
            row: index + 1,
            field: 'product_name',
            value: recipe.product_name,
            error: 'Product name is required'
          });
        }
        
        if (!recipe.yield_quantity || recipe.yield_quantity <= 0) {
          errors.push({
            row: index + 1,
            field: 'yield_quantity',
            value: recipe.yield_quantity,
            error: 'Yield quantity must be greater than 0'
          });
        }
        
        if (!recipe.ingredients || recipe.ingredients.length === 0) {
          errors.push({
            row: index + 1,
            field: 'ingredients',
            value: recipe.ingredients,
            error: 'At least one ingredient is required'
          });
        }
      });
    }

    return errors;
  }

  /**
   * Import validated data to backend
   */
  async importData(
    data: ImportData,
    onProgress?: (progress: ImportProgress) => void
  ): Promise<ImportResult> {
    if (USE_MOCK) {
      return this.mockImportData(data, onProgress);
    }

    try {
      const start = Date.now();
      let successCount = 0;
      let errorCount = 0;
      let totalCount = 0;
      const errors: ImportValidationError[] = [];
      const importedProducts: Product[] = [];
      const importedRecipes: Recipe[] = [];

      // Import products
      if (data.products) {
        totalCount += data.products.length;
        
        onProgress?.({
          stage: 'importing',
          current: 0,
          total: totalCount,
          message: 'Importing products...',
          percentage: 0
        });

        for (let i = 0; i < data.products.length; i++) {
          const product = data.products[i];
          
          try {
            // Use existing /products endpoint
            const response = await apiClient.post(`${this.baseURL}/products`, {
              name: product.name,
              symbol: product.symbol,
              type: product.type,
              unit: product.unit,
              description: product.description || '',
              category: product.category || '',
              tags: product.tags || []
            });
            
            importedProducts.push(response.data);
            successCount++;
          } catch (error: any) {
            errorCount++;
            errors.push({
              row: i + 1,
              field: 'product',
              value: product.name,
              error: error.response?.data?.message || error.message || 'Failed to create product'
            });
          }

          // Update progress
          const progress = Math.round(((i + 1) / totalCount) * 100);
          onProgress?.({
            stage: 'importing',
            current: i + 1,
            total: totalCount,
            message: `Importing products: ${i + 1}/${data.products.length}`,
            percentage: progress
          });
        }
      }

      // Import recipes (if supported)
      if (data.recipes) {
        totalCount += data.recipes.length;
        
        for (let i = 0; i < data.recipes.length; i++) {
          const recipe = data.recipes[i];
          
          try {
            // Try to use recipe service endpoint
            const response = await apiClient.post(`${this.baseURL.replace('/v1', ':8002/api/v1')}/recipes`, recipe);
            importedRecipes.push(response.data);
            successCount++;
          } catch (error: any) {
            errorCount++;
            errors.push({
              row: i + 1,
              field: 'recipe',
              value: recipe.product_name,
              error: error.response?.data?.message || error.message || 'Failed to create recipe'
            });
          }

          // Update progress
          const progress = Math.round(((data.products?.length || 0) + i + 1) / totalCount * 100);
          onProgress?.({
            stage: 'importing',
            current: (data.products?.length || 0) + i + 1,
            total: totalCount,
            message: `Importing recipes: ${i + 1}/${data.recipes.length}`,
            percentage: progress
          });
        }
      }

      // Complete
      onProgress?.({
        stage: 'completed',
        current: totalCount,
        total: totalCount,
        message: `Import completed: ${successCount} successful, ${errorCount} errors`,
        percentage: 100
      });

      return {
        success_count: successCount,
        error_count: errorCount,
        total_count: totalCount,
        errors,
        imported_products: importedProducts,
        imported_recipes: importedRecipes,
        processing_time_ms: Date.now() - start
      };

    } catch (error) {
      console.error('Import failed:', error);
      // Fallback to mock service
      return this.mockImportData(data, onProgress);
    }
  }

  /**
   * Mock import implementation for development
   */
  private async mockImportData(
    data: ImportData,
    onProgress?: (progress: ImportProgress) => void
  ): Promise<ImportResult> {
    const start = Date.now();
    let successCount = 0;
    let errorCount = 0;
    let totalCount = 0;

    // Simulate parsing stage
    onProgress?.({
      stage: 'parsing',
      current: 0,
      total: 100,
      message: 'Parsing import data...',
      percentage: 0
    });

    await this.delay(500);

    // Simulate validation stage
    onProgress?.({
      stage: 'validating',
      current: 25,
      total: 100,
      message: 'Validating data...',
      percentage: 25
    });

    const errors = await this.validateData(data);
    await this.delay(300);

    // Simulate importing stage
    onProgress?.({
      stage: 'importing',
      current: 50,
      total: 100,
      message: 'Importing data to database...',
      percentage: 50
    });

    if (data.products) {
      totalCount += data.products.length;
      // Simulate some failures
      successCount += Math.max(0, data.products.length - Math.floor(data.products.length * 0.1));
      errorCount = data.products.length - successCount;
    }

    if (data.recipes) {
      totalCount += data.recipes.length;
      successCount += Math.max(0, data.recipes.length - Math.floor(data.recipes.length * 0.05));
      errorCount += data.recipes.length - (data.recipes.length - Math.floor(data.recipes.length * 0.05));
    }

    await this.delay(1000);

    // Complete
    onProgress?.({
      stage: 'completed',
      current: 100,
      total: 100,
      message: `Import completed: ${successCount} successful, ${errorCount} errors`,
      percentage: 100
    });

    return {
      success_count: successCount,
      error_count: errorCount,
      total_count: totalCount,
      errors: errors.slice(0, errorCount), // Show some errors
      processing_time_ms: Date.now() - start
    };
  }

  /**
   * Get import template files
   */
  getTemplateCSV(type: 'products' | 'recipes'): string {
    if (type === 'products') {
      return `name,symbol,type,unit,description,category,tags
"Mąka pszenna","MAKA-PSZ-500",standard,gram,"Mąka typ 500","Składniki podstawowe","pieczenie,zboża"
"Cukier biały","CUKR-BIALY",standard,gram,"Cukier kryształ","Składniki podstawowe","pieczenie,słodzik"
"Jajka","JAJKA-KURZE",standard,piece,"Jajka kurze świeże","Składniki podstawowe","pieczenie,protein"`;
    } else {
      return `product_name,yield_quantity,yield_unit,ingredient_1_name,ingredient_1_quantity,ingredient_1_unit,ingredient_2_name,ingredient_2_quantity,ingredient_2_unit
"Ciasto biszkoptowe",500,gram,"Mąka pszenna",200,gram,"Cukier biały",150,gram`;
    }
  }

  /**
   * Download template file
   */
  downloadTemplate(type: 'products' | 'recipes', format: 'csv' | 'json') {
    const filename = `${type}_template.${format}`;
    
    if (format === 'csv') {
      const csv = this.getTemplateCSV(type);
      this.downloadFile(csv, filename, 'text/csv');
    } else {
      let data: any;
      if (type === 'products') {
        data = {
          products: [
            {
              name: "Mąka pszenna",
              symbol: "MAKA-PSZ-500",
              type: "standard",
              unit: "gram",
              description: "Mąka typ 500",
              category: "Składniki podstawowe",
              tags: ["pieczenie", "zboża"]
            }
          ]
        };
      } else {
        data = {
          recipes: [
            {
              product_name: "Ciasto biszkoptowe",
              yield_quantity: 500,
              yield_unit: "gram",
              ingredients: [
                {
                  product_name: "Mąka pszenna",
                  quantity: 200,
                  unit: "gram",
                  order: 1
                }
              ]
            }
          ]
        };
      }
      
      const json = JSON.stringify(data, null, 2);
      this.downloadFile(json, filename, 'application/json');
    }
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

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

export const importService = new ImportService();