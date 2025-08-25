import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';

import { 
  Product, 
  Recipe, 
  Calculation, 
  PaginatedResponse,
  SearchResponse,
  QueryKeys 
} from '@/types';
import { apiClient } from '@/services/apiClient';

// Products
export function useProducts(params?: { 
  page?: number; 
  limit?: number; 
  type?: string; 
  category?: string; 
}) {
  return useQuery({
    queryKey: [...QueryKeys.products, params],
    queryFn: () => apiClient.get<PaginatedResponse<Product>>('/products', { params }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useProduct(id: string) {
  return useQuery({
    queryKey: QueryKeys.product(id),
    queryFn: () => apiClient.get<Product>(`/products/${id}`),
    enabled: !!id,
  });
}

export function useProductSearch(query: string) {
  return useQuery({
    queryKey: QueryKeys.productSearch(query),
    queryFn: () => apiClient.get<SearchResponse<Product>>('/products/search', {
      params: { q: query }
    }),
    enabled: query.length > 2,
    staleTime: 2 * 60 * 1000, // 2 minutes for search
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<Product>) => apiClient.post<Product>('/products', data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.products });
      toast.success(`Product "${data.name}" created successfully!`);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to create product');
    },
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Product> }) => 
      apiClient.put<Product>(`/products/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.products });
      queryClient.invalidateQueries({ queryKey: QueryKeys.product(variables.id) });
      toast.success(`Product "${data.name}" updated successfully!`);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to update product');
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/products/${id}`),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.products });
      queryClient.removeQueries({ queryKey: QueryKeys.product(id) });
      toast.success('Product deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to delete product');
    },
  });
}

// Recipes
export function useRecipes(params?: { 
  page?: number; 
  limit?: number; 
  product_id?: string; 
}) {
  return useQuery({
    queryKey: [...QueryKeys.recipes, params],
    queryFn: () => apiClient.get<PaginatedResponse<Recipe>>('/recipes', { params }),
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecipe(id: string) {
  return useQuery({
    queryKey: QueryKeys.recipe(id),
    queryFn: () => apiClient.get<Recipe>(`/recipes/${id}`),
    enabled: !!id,
  });
}

export function useRecipeByProduct(productId: string) {
  return useQuery({
    queryKey: QueryKeys.recipeByProduct(productId),
    queryFn: () => apiClient.get<Recipe>(`/recipes/product/${productId}`),
    enabled: !!productId,
  });
}

export function useRecipeHierarchy(productId: string, options?: {
  target_quantity?: number;
  max_depth?: number;
}) {
  return useQuery({
    queryKey: [...QueryKeys.recipeHierarchy(productId), options],
    queryFn: () => apiClient.get<Recipe>(`/recipes/product/${productId}/hierarchy`, {
      params: options
    }),
    enabled: !!productId,
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Partial<Recipe>) => apiClient.post<Recipe>('/recipes', data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.recipes });
      if (data.product_id) {
        queryClient.invalidateQueries({ 
          queryKey: QueryKeys.recipeByProduct(data.product_id) 
        });
      }
      toast.success('Recipe created successfully!');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to create recipe');
    },
  });
}

export function useUpdateRecipe() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Recipe> }) => 
      apiClient.put<Recipe>(`/recipes/${id}`, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.recipes });
      queryClient.invalidateQueries({ queryKey: QueryKeys.recipe(variables.id) });
      if (data.product_id) {
        queryClient.invalidateQueries({ 
          queryKey: QueryKeys.recipeByProduct(data.product_id) 
        });
      }
      toast.success('Recipe updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to update recipe');
    },
  });
}

export function useDeleteRecipe() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/recipes/${id}`),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.recipes });
      queryClient.removeQueries({ queryKey: QueryKeys.recipe(id) });
      toast.success('Recipe deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Failed to delete recipe');
    },
  });
}

// Calculations
export function useCalculateRecipe() {
  return useMutation({
    mutationFn: (data: {
      product_id: string;
      target_quantity: number;
      target_unit: 'piece' | 'gram';
      include_hierarchy?: boolean;
      max_depth?: number;
      precision?: number;
    }) => apiClient.post<Calculation>('/calculations/calculate', data),
    onError: (error: any) => {
      toast.error(error?.response?.data?.message || 'Calculation failed');
    },
  });
}

export function useCalculationHistory(params?: { 
  product_id?: string; 
  limit?: number; 
  offset?: number; 
}) {
  return useQuery({
    queryKey: [...QueryKeys.calculationHistory, params],
    queryFn: () => apiClient.get<PaginatedResponse<Calculation>>('/calculations/history', { 
      params 
    }),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

// Health
export function useHealth() {
  return useQuery({
    queryKey: QueryKeys.health,
    queryFn: () => apiClient.get('/health'),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // 1 minute
  });
}

export function useServiceHealth() {
  return useQuery({
    queryKey: QueryKeys.serviceHealth,
    queryFn: () => apiClient.get('/health/services'),
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  });
}