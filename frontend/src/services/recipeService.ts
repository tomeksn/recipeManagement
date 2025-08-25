import { api } from './apiClient';
import { mockService } from './mockService';
import { Recipe, PaginatedResponse, RecipeFormData } from '@/types';

// Check if we're in offline mode
const isOfflineMode = import.meta.env.VITE_OFFLINE_MODE === 'true';

export const recipeService = {
  async getRecipes(page: number = 1, limit: number = 10): Promise<PaginatedResponse<Recipe>> {
    if (isOfflineMode) {
      return mockService.getRecipes(page, limit);
    }
    return api.get<PaginatedResponse<Recipe>>(`/recipes?page=${page}&limit=${limit}`);
  },

  async getRecipe(id: string): Promise<Recipe> {
    if (isOfflineMode) {
      return mockService.getRecipe(id);
    }
    return api.get<Recipe>(`/recipes/${id}`);
  },

  async getRecipeByProductId(productId: string): Promise<Recipe | null> {
    if (isOfflineMode) {
      return mockService.getRecipeByProductId(productId);
    }
    try {
      return api.get<Recipe>(`/recipes/by-product/${productId}`);
    } catch (error: any) {
      if (error?.status_code === 404) {
        return null;
      }
      throw error;
    }
  },

  async createRecipe(data: RecipeFormData): Promise<Recipe> {
    if (isOfflineMode) {
      return mockService.createRecipe(data);
    }
    return api.post<Recipe>('/recipes', data);
  },

  async updateRecipe(id: string, data: Partial<RecipeFormData>): Promise<Recipe> {
    if (isOfflineMode) {
      return mockService.updateRecipe(id, data);
    }
    return api.put<Recipe>(`/recipes/${id}`, data);
  },

  async deleteRecipe(id: string): Promise<void> {
    if (isOfflineMode) {
      return mockService.deleteRecipe(id);
    }
    return api.delete(`/recipes/${id}`);
  },

  async searchRecipes(query: string, page: number = 1, limit: number = 10): Promise<PaginatedResponse<Recipe>> {
    if (isOfflineMode) {
      // Simple client-side search for mock data
      const allRecipes = await mockService.getRecipes(1, 1000);
      const filteredRecipes = allRecipes.items.filter(recipe =>
        recipe.product?.name.toLowerCase().includes(query.toLowerCase()) ||
        recipe.product?.description?.toLowerCase().includes(query.toLowerCase()) ||
        recipe.product?.category?.toLowerCase().includes(query.toLowerCase()) ||
        recipe.ingredients.some(ing => 
          ing.product?.name.toLowerCase().includes(query.toLowerCase())
        )
      );

      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const items = filteredRecipes.slice(startIndex, endIndex);

      return {
        items,
        total: filteredRecipes.length,
        page,
        per_page: limit,
        pages: Math.ceil(filteredRecipes.length / limit),
        has_prev: page > 1,
        has_next: endIndex < filteredRecipes.length,
      };
    }
    return api.get<PaginatedResponse<Recipe>>(`/recipes/search?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
  },
};