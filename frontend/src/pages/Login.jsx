import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Flame, Mail, Lock, ArrowRight, Loader2 } from 'lucide-react';
import './Login&Register.css';

export function Login({ onSwitchToRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;
    try {
      setLoading(true);
      setError(null);
      await login({ email, password });
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="glass-panel login-card fade-in">
        {/* Brand Icon */}
        <div className="login-brand">
          <div className="brand-icon-wrapper">
            <Flame size={28} />
          </div>
          <h1 className="brand-title">NutriAgent</h1>
          <p className="brand-subtitle">Autonomous AI Calorie & Diet Companion</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-wrapper">
              <Mail size={16} color="var(--text-subtle)" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="form-input"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock size={16} color="var(--text-subtle)" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="form-input"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`login-submit-btn ${loading ? 'loading' : ''}`}
          >
            {loading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : 'Sign In'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        <div className="login-footer">
          Don't have an account?{' '}
          <button type="button" onClick={onSwitchToRegister} className="switch-auth-btn">
            Create one
          </button>
        </div>
      </div>
    </div>
  );
}