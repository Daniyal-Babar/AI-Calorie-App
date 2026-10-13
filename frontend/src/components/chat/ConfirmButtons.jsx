import React, { useState } from 'react';
import { AlertTriangle, Check, X, Loader2 } from 'lucide-react';

export function ConfirmButtons({ data, onConfirm }) {
  const [submitting, setSubmitting] = useState(false);
  const [resolved, setResolved] = useState(null);

  if (!data) return null;

  const { action_id, description, options = [] } = data;

  const handleAction = async (confirmed) => {
    try {
      setSubmitting(true);
      await onConfirm(action_id, confirmed);
      setResolved(confirmed ? 'confirmed' : 'cancelled');
    } catch (err) {
      console.error('Confirmation failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (resolved) {
    return (
      <div
        style={{
          marginTop: '10px',
          padding: '8px 12px',
          borderRadius: '8px',
          background: resolved === 'confirmed' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.05)',
          color: resolved === 'confirmed' ? 'var(--accent-emerald)' : 'var(--text-muted)',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        {resolved === 'confirmed' ? <Check size={16} /> : <X size={16} />}
        <span>Action {resolved === 'confirmed' ? 'confirmed' : 'cancelled'}.</span>
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: '12px',
        padding: '14px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(239, 68, 68, 0.08)',
        border: '1px solid rgba(239, 68, 68, 0.25)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fca5a5', marginBottom: '10px' }}>
        <AlertTriangle size={18} />
        <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>Confirmation Required</span>
      </div>

      {description && (
        <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '12px', lineHeight: 1.4 }}>
          {description}
        </p>
      )}

      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={() => handleAction(true)}
          disabled={submitting}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-sm)',
            border: 'none',
            background: 'var(--accent-rose)',
            color: '#fff',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: submitting ? 'not-allowed' : 'pointer',
            transition: 'opacity 0.2s',
            opacity: submitting ? 0.7 : 1,
          }}
        >
          {submitting ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={16} />}
          <span>Confirm</span>
        </button>

        <button
          onClick={() => handleAction(false)}
          disabled={submitting}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-glass)',
            background: 'rgba(255, 255, 255, 0.06)',
            color: '#cbd5e1',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: submitting ? 'not-allowed' : 'pointer',
          }}
        >
          <X size={16} />
          <span>Cancel</span>
        </button>
      </div>
    </div>
  );
}
