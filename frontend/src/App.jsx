import React, { useState } from 'react';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Chat } from './pages/Chat';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

function AppContent() {
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'

  return (
    <ProtectedRoute
      fallback={
        authView === 'login' ? (
          <Login onSwitchToRegister={() => setAuthView('register')} />
        ) : (
          <Register onSwitchToLogin={() => setAuthView('login')} />
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
