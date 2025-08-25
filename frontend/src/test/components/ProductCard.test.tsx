import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { render, mockOnEdit, mockOnDelete } from '../test-utils';
import { ProductCard } from '@/components/ui/ProductCard';
import { mockProducts } from '../__mocks__/apiMocks';

describe('ProductCard', () => {
  const defaultProps = {
    product: mockProducts[0],
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
  };

  it('renders product information correctly', () => {
    render(<ProductCard {...defaultProps} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    expect(screen.getByText('TEST001')).toBeInTheDocument();
    expect(screen.getByText('Test product description')).toBeInTheDocument();
    expect(screen.getByText('Test Category')).toBeInTheDocument();
  });

  it('displays product type badge', () => {
    render(<ProductCard {...defaultProps} />);
    
    expect(screen.getByText('standard')).toBeInTheDocument();
  });

  it('displays product unit', () => {
    render(<ProductCard {...defaultProps} />);
    
    expect(screen.getByText('gram')).toBeInTheDocument();
  });

  it('displays tags', () => {
    render(<ProductCard {...defaultProps} />);
    
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('mock')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', async () => {
    render(<ProductCard {...defaultProps} />);
    
    // Find and click the more options button
    const moreButton = screen.getByLabelText('more options');
    fireEvent.click(moreButton);
    
    // Wait for menu to appear and click edit
    await waitFor(() => {
      const editButton = screen.getByText('Edit');
      fireEvent.click(editButton);
    });
    
    expect(mockOnEdit).toHaveBeenCalledWith(mockProducts[0]);
  });

  it('calls onDelete when delete button is clicked', async () => {
    render(<ProductCard {...defaultProps} />);
    
    // Find and click the more options button
    const moreButton = screen.getByLabelText('more options');
    fireEvent.click(moreButton);
    
    // Wait for menu to appear and click delete
    await waitFor(() => {
      const deleteButton = screen.getByText('Delete');
      fireEvent.click(deleteButton);
    });
    
    expect(mockOnDelete).toHaveBeenCalledWith(mockProducts[0]);
  });

  it('renders without optional props', () => {
    const minimalProps = {
      product: mockProducts[0],
    };
    
    render(<ProductCard {...minimalProps} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
  });

  it('handles missing description gracefully', () => {
    const productWithoutDescription = {
      ...mockProducts[0],
      description: undefined,
    };
    
    render(<ProductCard product={productWithoutDescription} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    // Description should not be rendered if missing
    expect(screen.queryByText('Test product description')).not.toBeInTheDocument();
  });

  it('handles empty tags array', () => {
    const productWithoutTags = {
      ...mockProducts[0],
      tags: [],
    };
    
    render(<ProductCard product={productWithoutTags} />);
    
    expect(screen.getByText('Test Product 1')).toBeInTheDocument();
    expect(screen.queryByText('test')).not.toBeInTheDocument();
  });

  it('applies hover effect on mouse enter', () => {
    const { container } = render(<ProductCard {...defaultProps} />);
    
    const card = container.firstChild as HTMLElement;
    fireEvent.mouseEnter(card);
    
    // Check if hover styles are applied (this might need adjustment based on actual implementation)
    expect(card).toHaveStyle('cursor: pointer');
  });
});