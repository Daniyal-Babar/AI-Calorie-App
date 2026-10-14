import React from 'react';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';
import './Toast.css';

export function Toast({ message, type = 'error', onClose }) {
  if (!message) return null;

  const isError = type === 'error';
  const typeClass = isError ? 'error' : 'success';

  return (
    <div className={`toast-container ${typeClass}`}>
      {isError ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}
      <span className="toast-message">{message}</span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="toast-close-btn"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}