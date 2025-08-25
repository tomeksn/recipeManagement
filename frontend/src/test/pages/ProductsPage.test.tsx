import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../test-utils';
import { ProductsPage } from '@/pages/ProductsPage';
import { mockProductService, resetApiMocks } from '../__mocks__/apiMocks';

// Mock the productService
vi.mock('@/services/productService', () => ({
  productService: mockProductService,
}));

describe('ProductsPage', () => {
  beforeEach(() => {
    resetApiMocks();
  });

  it('renders page title and search functionality', async () => {
    render(<ProductsPage />);
    
    expect(screen.getByText('Products')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search products...')).toBeInTheDocument();
  });

  it('loads and displays products on mount', async () => {
    render(<ProductsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      expect(screen.getByText('Test Product 2')).toBeInTheDocument();
    });
    
    expect(mockProductService.getProducts).toHaveBeenCalledWith(1, 12);
  });

  it('handles search functionality', async () => {
    const user = userEvent.setup();
    render(<ProductsPage />);
    
    const searchInput = screen.getByPlaceholderText('Search products...');
    await user.type(searchInput, 'test search');
    
    await waitFor(() => {
      expect(mockProductService.searchProducts).toHaveBeenCalledWith('test search', 1, 12);
    });
  });

  it('opens create product dialog when create button is clicked', async () => {
    const user = userEvent.setup();
    render(<ProductsPage />);
    
    const createButton = screen.getByText('Create Product');
    await user.click(createButton);
    
    expect(screen.getByText('Create Product')).toBeInTheDocument(); // Dialog title
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Create')).toBeInTheDocument();
  });

  it('handles pagination', async () => {
    const user = userEvent.setup();
    
    // Mock multiple pages
    mockProductService.getProducts.mockResolvedValueOnce({
      items: [],
      total: 50,
      page: 1,
      per_page: 12,
      pages: 5,
      has_prev: false,
      has_next: true,
    });
    
    render(<ProductsPage />);
    
    await waitFor(() => {
      const pagination = screen.getByRole('navigation');
      expect(pagination).toBeInTheDocument();
    });
    
    // Click next page (if pagination controls are rendered)
    const nextButton = screen.queryByLabelText('Go to next page');
    if (nextButton) {
      await user.click(nextButton);
      
      await waitFor(() => {
        expect(mockProductService.getProducts).toHaveBeenCalledWith(2, 12);
      });
    }
  });

  it('handles product editing', async () => {
    render(<ProductsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    });
    
    // Find and click edit button on first product card
    const moreButtons = screen.getAllByLabelText('more options');
    const user = userEvent.setup();
    await user.click(moreButtons[0]);
    
    await waitFor(() => {
      const editButton = screen.getByText('Edit');
      user.click(editButton);
    });
    
    // Dialog should open
    await waitFor(() => {
      expect(screen.getByText('Edit Product')).toBeInTheDocument();
    });
  });

  it('handles product deletion', async () => {
    render(<ProductsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    });
    
    // Find and click delete button on first product card
    const moreButtons = screen.getAllByLabelText('more options');
    const user = userEvent.setup();
    await user.click(moreButtons[0]);
    
    await waitFor(() => {
      const deleteButton = screen.getByText('Delete');
      user.click(deleteButton);
    });
    
    // Confirm deletion dialog should open
    await waitFor(() => {
      expect(screen.getByText('Delete Product')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to delete this product?')).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    render(<ProductsPage />);
    
    // Should show skeleton loaders while loading
    expect(screen.getAllByTestId('product-skeleton')).toHaveLength(6);
  });

  it('handles API errors gracefully', async () => {
    const error = new Error('Failed to fetch products');
    mockProductService.getProducts.mockRejectedValueOnce(error);
    
    render(<ProductsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Error loading products')).toBeInTheDocument();
    });
  });

  it('shows empty state when no products found', async () => {
    mockProductService.getProducts.mockResolvedValueOnce({
      items: [],
      total: 0,
      page: 1,
      per_page: 12,
      pages: 0,
      has_prev: false,
      has_next: false,
    });
    
    render(<ProductsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No products found')).toBeInTheDocument();
    });
  });

  it('clears search when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<ProductsPage />);
    
    // First perform a search
    const searchInput = screen.getByPlaceholderText('Search products...');
    await user.type(searchInput, 'test search');
    
    await waitFor(() => {
      expect(mockProductService.searchProducts).toHaveBeenCalled();
    });
    
    // Then clear the search
    const clearButton = screen.getByLabelText('clear');
    await user.click(clearButton);
    
    // Should reload all products
    await waitFor(() => {
      expect(mockProductService.getProducts).toHaveBeenCalledWith(1, 12);
    });
  });
});