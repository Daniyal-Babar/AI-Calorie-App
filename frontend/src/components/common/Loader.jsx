import React from 'react';

export function Loader({ size = 24, text = 'Loading...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', gap: '0.75rem' }}>
      <div
        style={{
          width: size,
          height: size,
          border: '3px solid rgba(255, 255, 255, 0.1)',
          borderTopColor: 'var(--accent-emerald)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }}
      />
      {text && <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{text}</span>}
    </div>
  );
}
