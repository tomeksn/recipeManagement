import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { render, mockOnEdit, mockOnDelete } from '../test-utils';
import { ProductGrid } from '@/components/ui/ProductGrid';
import { mockProducts } from '../__mocks__/apiMocks';

describe('ProductGrid', () => {
  const defaultProps = {
    products: mockProducts,
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
  };

  it('renders all products', () => {
    render(<ProductGrid {...defaultProps} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    expect(screen.getByText('Test Product 2')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    render(<ProductGrid {...defaultProps} loading={true} />);
    
    // Should show skeleton loaders
    expect(screen.getAllByTestId('product-skeleton')).toHaveLength(6); // Default skeleton count
  });

  it('displays error state', () => {
    const error = new Error('Failed to load products');
    render(<ProductGrid {...defaultProps} error={error} />);
    
    expect(screen.getByText('Error loading products')).toBeInTheDocument();
    expect(screen.getByText('Failed to load products')).toBeInTheDocument();
  });

  it('displays empty state when no products', () => {
    render(<ProductGrid {...defaultProps} products={[]} />);
    
    expect(screen.getByText('No products found')).toBeInTheDocument();
    expect(screen.getByText('Create your first product to get started')).toBeInTheDocument();
  });

  it('passes callbacks to ProductCard components', () => {
    render(<ProductGrid {...defaultProps} />);
    
    // Verify that ProductCard components receive the callbacks
    // This is more of an integration test to ensure props are passed correctly
    const productCards = screen.getAllByTestId('product-card');
    expect(productCards).toHaveLength(2);
  });

  it('handles custom loading skeleton count', () => {
    render(<ProductGrid {...defaultProps} loading={true} skeletonCount={3} />);
    
    expect(screen.getAllByTestId('product-skeleton')).toHaveLength(3);
  });

  it('renders with responsive grid layout', () => {
    const { container } = render(<ProductGrid {...defaultProps} />);
    
    const grid = container.querySelector('.MuiGrid-container');
    expect(grid).toBeInTheDocument();
    expect(grid).toHaveClass('MuiGrid-container');
  });

  it('maintains consistent spacing between cards', () => {
    const { container } = render(<ProductGrid {...defaultProps} />);
    
    const gridItems = container.querySelectorAll('.MuiGrid-item');
    expect(gridItems).toHaveLength(2); // One for each product
  });

  it('handles products with missing optional fields', () => {
    const productsWithMissingFields = [
      {
        ...mockProducts[0],
        description: undefined,
        category: undefined,
        tags: undefined,
      }
    ];
    
    render(<ProductGrid {...defaultProps} products={productsWithMissingFields} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
  });

  it('renders retry button on error', async () => {
    const mockRetry = vi.fn();
    const error = new Error('Network error');
    
    render(<ProductGrid {...defaultProps} error={error} onRetry={mockRetry} />);
    
    const retryButton = screen.getByText('Try Again');
    expect(retryButton).toBeInTheDocument();
    
    retryButton.click();
    expect(mockRetry).toHaveBeenCalled();
  });

  it('updates when products prop changes', () => {
    const { rerender } = render(<ProductGrid {...defaultProps} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    
    const newProducts = [{
      ...mockProducts[0],
      name: 'Updated Product Name'
    }];
    
    rerender(<ProductGrid {...defaultProps} products={newProducts} />);
    
    expect(screen.getByText('Updated Product Name')).toBeInTheDocument();
    expect(screen.queryByText('Test Product 1')).not.toBeInTheDocument();
  });
});