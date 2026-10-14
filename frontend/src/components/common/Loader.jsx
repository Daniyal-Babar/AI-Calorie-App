import React from 'react';
import './Loader.css';

export function Loader({ size = 24, text = 'Loading...' }) {
  return (
    <div className="loader-container">
      <div
        className="loader-spinner"
        style={{
          width: size,
          height: size,
        }}
      />
      {text && <span className="loader-text">{text}</span>}
    </div>
  );
}