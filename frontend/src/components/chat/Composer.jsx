import React, { useState, useRef } from 'react';
import { Send, Image as ImageIcon, X, Loader2 } from 'lucide-react';
import { uploadImageApi } from '../../api/uploads';

export function Composer({ onSend, disabled }) {
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (disabled || isUploading) return;
    if (!text.trim() && !selectedFile) return;

    let uploadedImageId = null;

    if (selectedFile) {
      try {
        setIsUploading(true);
        const uploadRes = await uploadImageApi(selectedFile);
        uploadedImageId = uploadRes.image_id;
      } catch (err) {
        alert(`Image upload failed: ${err.message}`);
        setIsUploading(false);
        return;
      }
    }

    const messageText = text;
    setText('');
    handleRemoveImage();
    setIsUploading(false);

    onSend(messageText, uploadedImageId);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div
      style={{
        maxWidth: '850px',
        margin: '0 auto',
        padding: '0 16px 20px 16px',
        width: '100%',
      }}
    >
      {/* Image Preview Thumbnail */}
      {imagePreview && (
        <div
          style={{
            position: 'relative',
            display: 'inline-block',
            marginBottom: '10px',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
          }}
        >
          <img
            src={imagePreview}
            alt="Meal preview"
            style={{ width: '80px', height: '80px', objectFit: 'cover', display: 'block' }}
          />
          <button
            type="button"
            onClick={handleRemoveImage}
            style={{
              position: 'absolute',
              top: '4px',
              right: '4px',
              background: 'rgba(0, 0, 0, 0.7)',
              border: 'none',
              borderRadius: '50%',
              color: '#fff',
              cursor: 'pointer',
              padding: '2px',
              display: 'flex',
            }}
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Input container */}
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 12px',
          borderRadius: 'var(--radius-lg)',
          background: 'rgba(18, 27, 49, 0.75)',
          backdropFilter: 'blur(16px)',
          border: '1px solid var(--border-glass)',
          boxShadow: 'var(--shadow-glass)',
        }}
      >
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/png,image/jpeg,image/webp"
          style={{ display: 'none' }}
        />

        {/* Attach photo button */}
        <button
          type="button"
          // onClick={() => fileInputRef.current?.click()}
          title="Attach meal photo"
          style={{
            background: selectedFile ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
            border: selectedFile ? '1px solid var(--accent-emerald)' : '1px solid var(--border-glass)',
            borderRadius: '50%',
            width: '38px',
            height: '38px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: selectedFile ? 'var(--accent-emerald)' : 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'all 0.2s',
            flexShrink: 0,
          }}
        >
          <ImageIcon size={18} />
        </button>

        {/* Text input */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Log food, attach a meal photo, or ask about your calories..."
          disabled={disabled || isUploading}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#fff',
            fontSize: '0.95rem',
            padding: '8px 4px',
            fontFamily: 'inherit',
          }}
        />

        {/* Send button */}
        <button
          type="submit"
          disabled={disabled || isUploading || (!text.trim() && !selectedFile)}
          style={{
            background:
              text.trim() || selectedFile
                ? 'linear-gradient(135deg, #10b981, #06b6d4)'
                : 'rgba(255, 255, 255, 0.05)',
            border: 'none',
            borderRadius: '50%',
            width: '38px',
            height: '38px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: text.trim() || selectedFile ? '#fff' : 'var(--text-subtle)',
            cursor: text.trim() || selectedFile ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
            boxShadow:
              text.trim() || selectedFile ? '0 2px 10px rgba(16, 185, 129, 0.35)' : 'none',
            flexShrink: 0,
          }}
        >
          {isUploading ? (
            <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <Send size={18} />
          )}
        </button>
      </form>
    </div>
  );
}
