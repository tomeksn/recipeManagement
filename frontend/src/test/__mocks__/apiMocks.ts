import { vi } from 'vitest';
import type { Product, PaginatedResponse } from '@/types';

// Mock data
export const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Test Product 1',
    symbol: 'TEST001',
    type: 'standard',
    unit: 'gram',
    description: 'Test product description',
    category: 'Test Category',
    tags: ['test', 'mock'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Test Product 2',
    symbol: 'TEST002',
    type: 'semi-product',
    unit: 'piece',
    description: 'Another test product',
    category: 'Test Category',
    tags: ['test', 'mock'],
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
];

export const mockPaginatedResponse: PaginatedResponse<Product> = {
  items: mockProducts,
  total: 2,
  page: 1,
  per_page: 10,
  pages: 1,
  has_prev: false,
  has_next: false,
};

// Mock API functions
export const mockProductService = {
  getProducts: vi.fn(() => Promise.resolve(mockPaginatedResponse)),
  getProduct: vi.fn((id: string) => 
    Promise.resolve(mockProducts.find(p => p.id === id) || mockProducts[0])
  ),
  createProduct: vi.fn((data: any) => 
    Promise.resolve({ ...data, id: '3', created_at: new Date().toISOString(), updated_at: new Date().toISOString() })
  ),
  updateProduct: vi.fn((id: string, data: any) => 
    Promise.resolve({ ...mockProducts.find(p => p.id === id), ...data, updated_at: new Date().toISOString() })
  ),
  deleteProduct: vi.fn(() => Promise.resolve()),
  searchProducts: vi.fn(() => Promise.resolve(mockPaginatedResponse)),
};

// Reset all mocks
export const resetApiMocks = () => {
  Object.values(mockProductService).forEach(mock => {
    if (vi.isMockFunction(mock)) {
      mock.mockReset();
    }
  });
};