// API client types
export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  headers?: Record<string, string>;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  params?: Record<string, unknown>;
  data?: unknown;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ApiError {
  message: string;
  status_code: number;
  timestamp?: string;
  service?: string;
  request_id?: string;
  details?: Record<string, unknown>;
}

// Query keys for React Query
export const QueryKeys = {
  // Products
  products: ['products'] as const,
  product: (id: string) => ['products', id] as const,
  productSearch: (query: string) => ['products', 'search', query] as const,
  
  // Recipes
  recipes: ['recipes'] as const,
  recipe: (id: string) => ['recipes', id] as const,
  recipeByProduct: (productId: string) => ['recipes', 'product', productId] as const,
  recipeHierarchy: (productId: string) => ['recipes', 'hierarchy', productId] as const,
  
  // Calculations
  calculations: ['calculations'] as const,
  calculationHistory: ['calculations', 'history'] as const,
  
  // Health
  health: ['health'] as const,
  serviceHealth: ['health', 'services'] as const,
} as const;

// Cache configuration
export interface CacheConfig {
  staleTime: number;
  cacheTime: number;
  refetchOnWindowFocus: boolean;
  refetchOnMount: boolean;
  retry: number | ((failureCount: number, error: unknown) => boolean);
}