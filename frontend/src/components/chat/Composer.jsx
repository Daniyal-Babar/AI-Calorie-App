import React, { useState, useRef } from 'react';
import { Send, Image as ImageIcon, X, Loader2 } from 'lucide-react';
import { uploadImageApi } from '../../api/uploads';
import './Composer.css';

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

  const hasContent = text.trim() || selectedFile;

  return (
    <div className="composer-container">
      {/* Image Preview Thumbnail */}
      {imagePreview && (
        <div className="composer-preview-wrapper">
          <img src={imagePreview} alt="Meal preview" className="composer-preview-img" />
          <button
            type="button"
            onClick={handleRemoveImage}
            className="composer-preview-remove"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Input container */}
      <form onSubmit={handleSubmit} className="composer-form">
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
          onClick={() => fileInputRef.current?.click()}
          title="Attach meal photo"
          className={`composer-attach-btn ${selectedFile ? 'has-file' : 'no-file'}`}
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
          className="composer-input"
        />

        {/* Send button */}
        <button
          type="submit"
          disabled={disabled || isUploading || !hasContent}
          className={`composer-send-btn ${hasContent ? 'active' : 'inactive'}`}
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