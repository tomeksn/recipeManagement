import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../test-utils';
import { SearchBar } from '@/components/ui/SearchBar';

describe('SearchBar', () => {
  const mockOnSearch = vi.fn();
  const mockOnClear = vi.fn();
  
  const defaultProps = {
    onSearch: mockOnSearch,
    onClear: mockOnClear,
    placeholder: 'Search products...',
  };

  beforeEach(() => {
    mockOnSearch.mockReset();
    mockOnClear.mockReset();
  });

  it('renders with placeholder text', () => {
    render(<SearchBar {...defaultProps} />);
    
    expect(screen.getByPlaceholderText('Search products...')).toBeInTheDocument();
  });

  it('calls onSearch when user types', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search products...');
    await user.type(searchInput, 'test query');
    
    // Should debounce the search calls
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith('test query');
    });
  });

  it('calls onSearch when search button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search products...');
    await user.type(searchInput, 'test query');
    
    const searchButton = screen.getByLabelText('search');
    await user.click(searchButton);
    
    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });

  it('calls onClear when clear button is clicked', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} value="existing search" />);
    
    const clearButton = screen.getByLabelText('clear');
    await user.click(clearButton);
    
    expect(mockOnClear).toHaveBeenCalled();
  });

  it('shows clear button only when there is text', () => {
    const { rerender } = render(<SearchBar {...defaultProps} value="" />);
    
    // Clear button should not be visible when empty
    expect(screen.queryByLabelText('clear')).not.toBeInTheDocument();
    
    // Rerender with text
    rerender(<SearchBar {...defaultProps} value="some text" />);
    
    // Clear button should be visible when there's text
    expect(screen.getByLabelText('clear')).toBeInTheDocument();
  });

  it('handles Enter key press', async () => {
    const user = userEvent.setup();
    render(<SearchBar {...defaultProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search products...');
    await user.type(searchInput, 'test query');
    await user.keyboard('{Enter}');
    
    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });

  it('displays loading state', () => {
    render(<SearchBar {...defaultProps} loading={true} />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    render(<SearchBar {...defaultProps} disabled={true} />);
    
    const searchInput = screen.getByPlaceholderText('Search products...');
    expect(searchInput).toBeDisabled();
  });

  it('applies custom className', () => {
    const customClassName = 'custom-search-bar';
    render(<SearchBar {...defaultProps} className={customClassName} />);
    
    const searchBar = screen.getByPlaceholderText('Search products...').closest('.MuiOutlinedInput-root');
    expect(searchBar).toHaveClass(customClassName);
  });

  it('supports controlled value', () => {
    const { rerender } = render(<SearchBar {...defaultProps} value="initial" />);
    
    const searchInput = screen.getByPlaceholderText('Search products...') as HTMLInputElement;
    expect(searchInput.value).toBe('initial');
    
    rerender(<SearchBar {...defaultProps} value="updated" />);
    expect(searchInput.value).toBe('updated');
  });
});