import React from 'react';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';

export function Toast({ message, type = 'error', onClose }) {
  if (!message) return null;

  const isError = type === 'error';
  const bgColor = isError ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)';
  const borderColor = isError ? 'rgba(239, 68, 68, 0.35)' : 'rgba(16, 185, 129, 0.35)';
  const textColor = isError ? '#fca5a5' : '#86efac';

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '12px 18px',
        borderRadius: 'var(--radius-md)',
        background: bgColor,
        border: `1px solid ${borderColor}`,
        backdropFilter: 'blur(12px)',
        color: textColor,
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
        animation: 'fadeIn 0.2s ease-out',
        maxWidth: '400px',
      }}
    >
      {isError ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
      <span style={{ fontSize: '0.875rem', fontWeight: 500, flex: 1 }}>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer', display: 'flex' }}
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
