# Recipe Management Frontend

Modern React application with Trello-inspired UI for the Recipe Management System. Built with TypeScript, Material-UI, and Vite for optimal performance and developer experience.

## Features

- **Trello-like Interface**: Card-based UI with drag-and-drop functionality
- **TypeScript**: Full type safety and better developer experience
- **Material-UI**: Modern component library with custom theming
- **React Query**: Powerful data fetching and caching
- **React Router**: Client-side routing with lazy loading
- **Form Management**: React Hook Form with validation
- **Responsive Design**: Mobile-first approach with Material-UI breakpoints
- **Dark/Light Theme**: User-controlled theme switching
- **PWA Ready**: Progressive Web App capabilities
- **Accessibility**: WCAG compliant components

## Tech Stack

### Core
- **React 18** - User interface framework
- **TypeScript 5** - Type-safe JavaScript
- **Vite 4** - Build tool and development server
- **Material-UI 5** - Component library and theming

### State Management
- **React Query** - Server state management and caching
- **React Context** - Global client state
- **React Hook Form** - Form state and validation

### Routing & Navigation
- **React Router v6** - Client-side routing
- **React Helmet Async** - Document head management

### Development
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Vitest** - Unit testing
- **React Testing Library** - Component testing

## Quick Start

### Prerequisites
- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 3+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

### Development Server

The development server runs on `http://localhost:3000` with:
- Hot module replacement
- API proxy to backend (port 8000)
- TypeScript checking
- ESLint integration

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components
│   ├── layout/         # Layout components
│   └── ui/             # UI-specific components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API services
├── providers/          # React context providers
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── assets/             # Static assets
├── styles/             # Global styles
└── test/               # Test utilities
```

## Environment Variables

Create `.env` file in the root directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1

# Application Settings
VITE_APP_NAME=Recipe Management System
VITE_APP_VERSION=1.0.0

# Development Settings
VITE_ENABLE_DEVTOOLS=true
```

## API Integration

The frontend communicates with the API Gateway:

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `/api/v1` (served by same domain)

### Authentication
JWT-based authentication with automatic token management:

```typescript
// Login
const { login } = useAuth();
await login({ email, password });

// API calls automatically include Bearer token
const products = await api.get('/products');
```

### Data Fetching
React Query provides caching and synchronization:

```typescript
// Products
const { data: products, isLoading } = useProducts();
const { mutate: createProduct } = useCreateProduct();

// Recipes
const { data: recipe } = useRecipe(recipeId);
const { mutate: updateRecipe } = useUpdateRecipe();

// Calculations
const { mutate: calculate } = useCalculateRecipe();
```

## Component Development

### Naming Conventions
- **PascalCase** for components: `ProductCard.tsx`
- **camelCase** for functions and variables: `handleSubmit`
- **SCREAMING_SNAKE_CASE** for constants: `API_BASE_URL`

### Component Structure
```typescript
interface ComponentProps {
  // Props interface
}

export function Component({ prop }: ComponentProps) {
  // Component implementation
}
```

### Styling Approach
1. **Material-UI System** - Primary styling method
2. **CSS Modules** - Component-scoped styles when needed
3. **Global CSS** - Reset, utilities, and animations

### Example Component
```typescript
import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface ProductCardProps {
  product: Product;
  onClick?: (product: Product) => void;
}

export function ProductCard({ product, onClick }: ProductCardProps) {
  return (
    <Card 
      sx={{ 
        cursor: 'pointer',
        transition: 'transform 0.2s',
        '&:hover': { transform: 'translateY(-2px)' }
      }}
      onClick={() => onClick?.(product)}
    >
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {product.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {product.description}
        </Typography>
      </CardContent>
    </Card>
  );
}
```

## Testing Strategy

### Unit Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Component Testing
```typescript
import { render, screen } from '@testing-library/react';
import { ProductCard } from './ProductCard';

test('renders product information', () => {
  const product = { id: '1', name: 'Test Product', description: 'Test' };
  render(<ProductCard product={product} />);
  
  expect(screen.getByText('Test Product')).toBeInTheDocument();
});
```

### Integration Testing
- API mocking with MSW
- E2E testing with Playwright (separate package)

## Build & Deployment

### Development Build
```bash
npm run build:dev
```

### Production Build
```bash
npm run build
```

### Docker Build
```bash
# Development
docker build -f Dockerfile.dev -t recipe-frontend:dev .

# Production
docker build -t recipe-frontend:latest .
```

### Build Optimization
- Code splitting by routes and vendors
- Tree shaking for unused code
- Asset optimization and compression
- Service worker for caching

## Performance Optimization

### Code Splitting
```typescript
// Lazy load pages
const ProductsPage = React.lazy(() => import('./pages/ProductsPage'));

// Route-based splitting
<Route path="/products" element={<ProductsPage />} />
```

### Bundle Analysis
```bash
npm run build:analyze
```

### Performance Monitoring
- React DevTools Profiler
- Lighthouse audits
- Core Web Vitals tracking

## Theming & Customization

### Custom Theme
The application uses a Trello-inspired Material-UI theme:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#0079bf' }, // Trello blue
    secondary: { main: '#838c91' }, // Trello gray
    // ... more colors
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
    // ... typography settings
  }
});
```

### Dark Mode
User-controlled theme switching with system preference detection:

```typescript
const { mode, toggleColorMode } = useTheme();
```

## Accessibility

### Features
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management

### Testing
```bash
# Run accessibility tests
npm run test:a11y
```

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Polyfills
Automatic polyfill injection for unsupported features via Vite.

## Contributing

### Code Style
```bash
# Format code
npm run format

# Lint code
npm run lint:fix
```

### Git Hooks
Pre-commit hooks ensure code quality:
- ESLint checking
- Prettier formatting
- TypeScript compilation
- Test execution

### Component Guidelines
1. Use TypeScript interfaces for all props
2. Implement proper error boundaries
3. Follow Material-UI design system
4. Add proper ARIA attributes
5. Write unit tests for complex logic

## Troubleshooting

### Common Issues

**Build fails with TypeScript errors**
```bash
npm run type-check
```

**API calls fail in development**
- Check API Gateway is running on port 8000
- Verify VITE_API_URL environment variable

**Styling issues**
- Clear browser cache
- Check Material-UI theme configuration
- Verify CSS import order

**Hot reload not working**
```bash
# Set polling for file watching
export CHOKIDAR_USEPOLLING=true
npm run dev
```

### Debug Mode
```bash
# Enable React DevTools
VITE_ENABLE_DEVTOOLS=true npm run dev
```

## Production Considerations

### Security
- Content Security Policy headers
- XSS protection
- Secure cookie settings
- Input sanitization

### Performance
- CDN for static assets
- Image optimization
- Lazy loading
- Service worker caching

### Monitoring
- Error tracking with Sentry
- Analytics integration
- Performance monitoring
- User feedback collection