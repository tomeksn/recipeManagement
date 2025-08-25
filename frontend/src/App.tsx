import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { CssBaseline, Box } from '@mui/material';

import { useAuth } from './hooks/useAuth';
import { AppLayout } from './components/layout/AppLayout';
import { LoadingScreen } from './components/common/LoadingScreen';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// Lazy load pages for better performance
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const ProductsPage = React.lazy(() => import('./pages/ProductsPage'));
const ProductDetailPage = React.lazy(() => import('./pages/ProductDetailPage'));
const RecipesPage = React.lazy(() => import('./pages/RecipesPage'));
const RecipeDetailPage = React.lazy(() => import('./pages/RecipeDetailPage'));
const CalculatorPage = React.lazy(() => import('./pages/CalculatorPage'));
const ImportPage = React.lazy(() => import('./pages/ImportPage'));
const LoginPage = React.lazy(() => import('./pages/LoginPage'));
const NotFoundPage = React.lazy(() => import('./pages/NotFoundPage'));

function App() {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Show loading screen while checking authentication
  if (isLoading) {
    return <LoadingScreen />;
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <CssBaseline />
        <Helmet>
          <title>Login - Recipe Management System</title>
        </Helmet>
        <React.Suspense fallback={<LoadingScreen />}>
          <LoginPage />
        </React.Suspense>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <CssBaseline />
      <Helmet>
        <title>Recipe Management System</title>
        <meta name='description' content='Modern recipe management system for production companies and laboratories' />
      </Helmet>
      
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <AppLayout user={user}>
          <React.Suspense fallback={<LoadingScreen />}>
            <Routes>
              {/* Dashboard */}
              <Route path='/' element={<DashboardPage />} />
              <Route path='/dashboard' element={<Navigate to='/' replace />} />
              
              {/* Products */}
              <Route path='/products' element={<ProductsPage />} />
              <Route path='/products/:id' element={<ProductDetailPage />} />
              
              {/* Recipes */}
              <Route path='/recipes' element={<RecipesPage />} />
              <Route path='/recipes/:id' element={<RecipeDetailPage />} />
              
              {/* Calculator */}
              <Route path='/calculator' element={<CalculatorPage />} />
              <Route path='/calculate' element={<Navigate to='/calculator' replace />} />
              
              {/* Import */}
              <Route path='/import' element={<ImportPage />} />
              
              {/* Catch all - 404 */}
              <Route path='*' element={<NotFoundPage />} />
            </Routes>
          </React.Suspense>
        </AppLayout>
      </Box>
    </ErrorBoundary>
  );
}

export default App;