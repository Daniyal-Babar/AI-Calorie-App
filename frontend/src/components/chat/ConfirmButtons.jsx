import React, { useState } from 'react';
import { AlertTriangle, Check, X, Loader2 } from 'lucide-react';
import './ConfirmButtons.css';

export function ConfirmButtons({ data, onConfirm }) {
  const [submitting, setSubmitting] = useState(false);
  const [resolved, setResolved] = useState(null);

  if (!data) return null;

  const { action_id, description } = data;

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
      <div className={`confirm-resolved ${resolved}`}>
        {resolved === 'confirmed' ? <Check size={16} /> : <X size={16} />}
        <span>Action {resolved === 'confirmed' ? 'confirmed' : 'cancelled'}.</span>
      </div>
    );
  }

  return (
    <div className="confirm-card">
      <div className="confirm-header">
        <AlertTriangle size={18} />
        <span className="confirm-title">Confirmation Required</span>
      </div>

      {description && (
        <p className="confirm-description">
          {description}
        </p>
      )}

      <div className="confirm-actions">
        <button
          type="button"
          onClick={() => handleAction(true)}
          disabled={submitting}
          className="confirm-btn-primary"
        >
          {submitting ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={16} />}
          <span>Confirm</span>
        </button>

        <button
          type="button"
          onClick={() => handleAction(false)}
          disabled={submitting}
          className="confirm-btn-secondary"
        >
          <X size={16} />
          <span>Cancel</span>
        </button>
      </div>
    </div>
  );
}