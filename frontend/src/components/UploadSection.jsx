import React, { useRef } from 'react';

function UploadSection({ onUpload }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div 
      className="upload-zone glass-panel"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current.click()}
    >
      <div className="upload-icon">🛰️</div>
      <h2>Upload Satellite Imagery</h2>
      <p className="glow-text" style={{ marginTop: '0.5rem', marginBottom: '2rem' }}>
        Drag & drop or click to select a disaster site image
      </p>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept="image/*"
      />
      
      <button className="btn-primary" onClick={(e) => { e.stopPropagation(); fileInputRef.current.click(); }}>
        Browse Files
      </button>
    </div>
  );
}

export default UploadSection;
