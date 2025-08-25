// Mock service for offline development
import { User, LoginCredentials, TokenResponse } from '@/types/auth';
import { Product, Recipe, RecipeIngredient, PaginatedResponse } from '@/types';

// Mock data
const mockUser: User = {
  id: '1',
  name: 'Admin User',
  email: 'admin@example.com',
  role: 'admin',
  created_at: new Date().toISOString(),
  last_login: new Date().toISOString(),
};

const mockToken: TokenResponse = {
  access_token: 'mock_token_12345',
  refresh_token: 'mock_refresh_token_67890',
  token_type: 'Bearer',
  expires_in: 3600,
  user: mockUser,
};

// Mock products data
const mockProducts: Product[] = [
  {
    id: 'prod-1',
    name: 'Mąka pszenna',
    type: 'standard',
    unit: 'gram',
    description: 'Mąka pszenna typ 500',
    category: 'Składniki podstawowe',
    tags: ['pieczenie', 'zboża'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-2',
    name: 'Cukier biały',
    type: 'standard',
    unit: 'gram',
    description: 'Cukier kryształ biały',
    category: 'Składniki podstawowe',
    tags: ['pieczenie', 'słodzik'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-3',
    name: 'Jajka',
    type: 'standard',
    unit: 'piece',
    description: 'Jajka kurze świeże',
    category: 'Składniki podstawowe',
    tags: ['pieczenie', 'protein'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-4',
    name: 'Masło',
    type: 'standard',
    unit: 'gram',
    description: 'Masło 82% tłuszczu',
    category: 'Składniki podstawowe',
    tags: ['pieczenie', 'tłuszcz'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-5',
    name: 'Ciasto biszkoptowe',
    type: 'semi-product',
    unit: 'gram',
    description: 'Gotowe ciasto biszkoptowe',
    category: 'Półprodukty',
    tags: ['pieczenie', 'gotowy-mix'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 'prod-6',
    name: 'Tort czekoladowy',
    type: 'kit',
    unit: 'piece',
    description: 'Kompletny tort czekoladowy',
    category: 'Produkty gotowe',
    tags: ['deser', 'tort'],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

// Mock recipes data
const mockRecipes: Recipe[] = [
  {
    id: 'recipe-1',
    product_id: 'prod-5',
    product: mockProducts.find(p => p.id === 'prod-5'),
    yield_quantity: 500,
    yield_unit: 'gram',
    ingredients: [
      {
        id: 'ing-1',
        product_id: 'prod-1',
        product: mockProducts.find(p => p.id === 'prod-1'),
        quantity: 200,
        unit: 'gram',
        order: 1,
      },
      {
        id: 'ing-2',
        product_id: 'prod-2',
        product: mockProducts.find(p => p.id === 'prod-2'),
        quantity: 150,
        unit: 'gram',
        order: 2,
      },
      {
        id: 'ing-3',
        product_id: 'prod-3',
        product: mockProducts.find(p => p.id === 'prod-3'),
        quantity: 3,
        unit: 'piece',
        order: 3,
      },
      {
        id: 'ing-4',
        product_id: 'prod-4',
        product: mockProducts.find(p => p.id === 'prod-4'),
        quantity: 100,
        unit: 'gram',
        order: 4,
      },
    ],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    version: 1,
  },
  {
    id: 'recipe-2',
    product_id: 'prod-6',
    product: mockProducts.find(p => p.id === 'prod-6'),
    yield_quantity: 1,
    yield_unit: 'piece',
    ingredients: [
      {
        id: 'ing-5',
        product_id: 'prod-5',
        product: mockProducts.find(p => p.id === 'prod-5'),
        quantity: 500,
        unit: 'gram',
        order: 1,
      },
    ],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    version: 1,
  },
];

export const mockService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Accept any credentials for demo
    if (credentials.email && credentials.password) {
      localStorage.setItem('auth_token', mockToken.access_token);
      localStorage.setItem('user', JSON.stringify(mockUser));
      return mockToken;
    }
    
    throw new Error('Invalid credentials');
  },

  async getCurrentUser(): Promise<User> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return mockUser;
  },

  async logout(): Promise<void> {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  // Products API
  async getProducts(page: number = 1, limit: number = 10): Promise<PaginatedResponse<Product>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const items = mockProducts.slice(startIndex, endIndex);
    
    return {
      items,
      total: mockProducts.length,
      page,
      per_page: limit,
      pages: Math.ceil(mockProducts.length / limit),
      has_prev: page > 1,
      has_next: endIndex < mockProducts.length,
    };
  },

  async getProduct(id: string): Promise<Product> {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const product = mockProducts.find(p => p.id === id);
    if (!product) {
      throw new Error('Product not found');
    }
    return product;
  },

  async createProduct(data: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newProduct: Product = {
      ...data,
      id: `prod-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    
    mockProducts.push(newProduct);
    return newProduct;
  },

  async updateProduct(id: string, data: Partial<Product>): Promise<Product> {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    const index = mockProducts.findIndex(p => p.id === id);
    if (index === -1) {
      throw new Error('Product not found');
    }
    
    mockProducts[index] = {
      ...mockProducts[index],
      ...data,
      updated_at: new Date().toISOString(),
    };
    
    return mockProducts[index];
  },

  async deleteProduct(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const index = mockProducts.findIndex(p => p.id === id);
    if (index === -1) {
      throw new Error('Product not found');
    }
    
    mockProducts.splice(index, 1);
  },

  // Recipes API
  async getRecipes(page: number = 1, limit: number = 10): Promise<PaginatedResponse<Recipe>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const items = mockRecipes.slice(startIndex, endIndex);
    
    return {
      items,
      total: mockRecipes.length,
      page,
      per_page: limit,
      pages: Math.ceil(mockRecipes.length / limit),
      has_prev: page > 1,
      has_next: endIndex < mockRecipes.length,
    };
  },

  async getRecipe(id: string): Promise<Recipe> {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const recipe = mockRecipes.find(r => r.id === id);
    if (!recipe) {
      throw new Error('Recipe not found');
    }
    return recipe;
  },

  async getRecipeByProductId(productId: string): Promise<Recipe | null> {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const recipe = mockRecipes.find(r => r.product_id === productId);
    return recipe || null;
  },

  async createRecipe(data: Omit<Recipe, 'id' | 'created_at' | 'updated_at' | 'version'>): Promise<Recipe> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newRecipe: Recipe = {
      ...data,
      id: `recipe-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: 1,
    };
    
    mockRecipes.push(newRecipe);
    return newRecipe;
  },

  async updateRecipe(id: string, data: Partial<Recipe>): Promise<Recipe> {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    const index = mockRecipes.findIndex(r => r.id === id);
    if (index === -1) {
      throw new Error('Recipe not found');
    }
    
    mockRecipes[index] = {
      ...mockRecipes[index],
      ...data,
      updated_at: new Date().toISOString(),
      version: (mockRecipes[index].version || 1) + 1,
    };
    
    return mockRecipes[index];
  },

  async deleteRecipe(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const index = mockRecipes.findIndex(r => r.id === id);
    if (index === -1) {
      throw new Error('Recipe not found');
    }
    
    mockRecipes.splice(index, 1);
  },
};