import { api } from './apiClient';
import { mockService } from './mockService';
import { Product, PaginatedResponse, ProductFormData } from '@/types';

// Check if we're in offline mode
const isOfflineMode = import.meta.env.VITE_OFFLINE_MODE === 'true';
console.log('Product service - offline mode:', isOfflineMode);
console.log('Environment VITE_OFFLINE_MODE:', import.meta.env.VITE_OFFLINE_MODE);

export const productService = {
  async getProducts(page: number = 1, limit: number = 10): Promise<PaginatedResponse<Product>> {
    if (isOfflineMode) {
      return mockService.getProducts(page, limit);
    }
    return api.get<PaginatedResponse<Product>>(`/products?page=${page}&limit=${limit}`);
  },

  async getProduct(id: string): Promise<Product> {
    if (isOfflineMode) {
      return mockService.getProduct(id);
    }
    return api.get<Product>(`/products/${id}`);
  },

  async createProduct(data: ProductFormData): Promise<Product> {
    if (isOfflineMode) {
      return mockService.createProduct(data);
    }
    return api.post<Product>('/products', data);
  },

  async updateProduct(id: string, data: Partial<ProductFormData>): Promise<Product> {
    if (isOfflineMode) {
      return mockService.updateProduct(id, data);
    }
    return api.put<Product>(`/products/${id}`, data);
  },

  async deleteProduct(id: string): Promise<void> {
    if (isOfflineMode) {
      return mockService.deleteProduct(id);
    }
    return api.delete(`/products/${id}`);
  },

  async searchProducts(query: string, page: number = 1, limit: number = 10): Promise<PaginatedResponse<Product>> {
    if (isOfflineMode) {
      // Simple client-side search for mock data
      const allProducts = await mockService.getProducts(1, 1000);
      const filteredProducts = allProducts.items.filter(product =>
        product.name.toLowerCase().includes(query.toLowerCase()) ||
        product.description?.toLowerCase().includes(query.toLowerCase()) ||
        product.category?.toLowerCase().includes(query.toLowerCase()) ||
        product.tags?.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
      );

      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const items = filteredProducts.slice(startIndex, endIndex);

      return {
        items,
        total: filteredProducts.length,
        page,
        per_page: limit,
        pages: Math.ceil(filteredProducts.length / limit),
        has_prev: page > 1,
        has_next: endIndex < filteredProducts.length,
      };
    }
    return api.get<PaginatedResponse<Product>>(`/products/search?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
  },
};