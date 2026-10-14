import React, { useState, useEffect } from 'react';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Chat } from './pages/Chat';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function AppContent() {
  // Initialize state from sessionStorage, defaulting to 'login'
  const [authView, setAuthView] = useState(() => {
    return sessionStorage.getItem('nutriagent_auth_view') || 'login';
  });

  // Whenever authView changes, save it to sessionStorage
  const handleSwitchView = (view) => {
    setAuthView(view);
    sessionStorage.setItem('nutriagent_auth_view', view);
  };

  return (
    <ProtectedRoute
      fallback={
        authView === 'login' ? (
          <Login onSwitchToRegister={() => handleSwitchView('register')} />
        ) : (
          <Register onSwitchToLogin={() => handleSwitchView('login')} />
        )
      }
    >
      <Chat />
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}