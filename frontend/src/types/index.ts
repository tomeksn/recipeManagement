// Core entity types
export interface Product {
  id: string;
  name: string;
  type: 'standard' | 'kit' | 'semi-product';
  unit: 'piece' | 'gram';
  description?: string;
  category?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface Recipe {
  id: string;
  product_id: string;
  product?: Product;
  yield_quantity: number;
  yield_unit: 'piece' | 'gram';
  ingredients: RecipeIngredient[];
  created_at: string;
  updated_at: string;
  version?: number;
}

export interface RecipeIngredient {
  id?: string;
  product_id: string;
  product?: Product;
  quantity: number;
  unit: 'piece' | 'gram';
  order: number;
  sub_ingredients?: RecipeIngredient[];
  expanded?: boolean;
  depth?: number;
}

export interface Calculation {
  product_id: string;
  product_name?: string;
  target_quantity: number;
  target_unit: 'piece' | 'gram';
  scale_factor: number;
  original_yield: number;
  original_yield_unit: 'piece' | 'gram';
  ingredients: CalculatedIngredient[];
  calculation_metadata: {
    include_hierarchy: boolean;
    max_depth: number;
    precision: number;
    ingredient_count: number;
    algorithm_version: string;
  };
  cached: boolean;
  calculation_time_ms: number;
}

export interface CalculatedIngredient {
  product_id: string;
  product_name: string;
  original_quantity: number;
  calculated_quantity: number;
  unit: 'piece' | 'gram';
  order: number;
  sub_ingredients?: CalculatedIngredient[];
  expanded?: boolean;
  depth?: number;
}

// API response types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_prev: boolean;
  has_next: boolean;
}

export interface SearchResponse<T> extends PaginatedResponse<T> {
  query: string;
  search_time_ms: number;
  suggestions?: string[];
}

// Form types
export interface ProductFormData {
  name: string;
  type: 'standard' | 'kit' | 'semi-product';
  unit: 'piece' | 'gram';
  description?: string;
  category?: string;
  tags?: string[];
}

export interface RecipeFormData {
  product_id: string;
  yield_quantity: number;
  yield_unit: 'piece' | 'gram';
  ingredients: {
    product_id: string;
    quantity: number;
    unit: 'piece' | 'gram';
    order: number;
  }[];
}

export interface CalculationFormData {
  product_id: string;
  target_quantity: number;
  target_unit: 'piece' | 'gram';
  include_hierarchy?: boolean;
  max_depth?: number;
  precision?: number;
}

// UI state types
export interface ViewMode {
  type: 'card' | 'list' | 'table';
  density: 'compact' | 'comfortable' | 'spacious';
}

export interface FilterState {
  search: string;
  type?: Product['type'];
  unit?: Product['unit'];
  category?: string;
  tags?: string[];
}

export interface SortState {
  field: string;
  direction: 'asc' | 'desc';
}

// Theme types
export interface TrelloTheme {
  primary: string;
  secondary: string;
  background: {
    board: string;
    card: string;
    list: string;
  };
  colors: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
  shadows: {
    card: string;
    elevated: string;
  };
}

// Error types
export interface AppError {
  message: string;
  code?: string;
  field?: string;
  details?: Record<string, unknown>;
}

export interface ValidationError extends AppError {
  field: string;
  value?: unknown;
}

// Loading states
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  data: T | null;
  loading: LoadingState;
  error: AppError | null;
}

// Navigation types
export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ComponentType;
}

// Card types for Trello-like UI
export interface CardItem {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  tags?: string[];
  status?: 'active' | 'inactive' | 'draft';
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  assignee?: string;
  progress?: number;
}

export interface BoardColumn {
  id: string;
  title: string;
  items: CardItem[];
  color?: string;
  limit?: number;
}

export interface Board {
  id: string;
  title: string;
  description?: string;
  columns: BoardColumn[];
  background?: string;
}

// Export all types
export * from './api';
export * from './auth';