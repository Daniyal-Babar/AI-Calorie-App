import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Loader } from './Loader';
import './ProtectedRoute.css';

export function ProtectedRoute({ children, fallback }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="protected-route-loader-wrapper">
        <Loader size={36} text="Authenticating NutriAgent..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return children;
}