import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Flame, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import './Login&Register.css';

export function Register({ onSwitchToLogin }) {
  const { register } = useAuth();
  const [name, setName] = useState('');
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
      await register({ name: name || 'User', email, password });
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="glass-panel login-card fade-in">
        <div className="login-brand">
          <div className="brand-icon-wrapper">
            <Flame size={28} />
          </div>
          <h1 className="brand-title">Get Started</h1>
          <p className="brand-subtitle">Create your account to start tracking meals conversationally</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">Your Name</label>
            <div className="input-wrapper">
              <User size={16} color="var(--text-subtle)" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Smith"
                className="form-input"
              />
            </div>
          </div>

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
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="form-input"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="login-submit-btn"
          >
            {loading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : 'Create Account'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        <div className="login-footer">
          Already have an account?{' '}
          <button type="button" onClick={onSwitchToLogin} className="switch-auth-btn">
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}