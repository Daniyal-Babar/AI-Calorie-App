import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Loader } from './Loader';

export function ProtectedRoute({ children, fallback }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Loader size={36} text="Authenticating NutriAgent..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return children;
}
