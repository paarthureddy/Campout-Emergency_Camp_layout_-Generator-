import React, { useRef, useState } from 'react';

function UploadSection({ onUpload }) {
  const fileInputRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState('unet');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0], selectedModel);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0], selectedModel);
    }
  };

  return (
    <div 
      className="upload-zone glass-panel"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      <div className="upload-icon" onClick={() => fileInputRef.current.click()} style={{ cursor: 'pointer' }}>🛰️</div>
      <h2>Upload Satellite Imagery</h2>
      <p className="glow-text" style={{ marginTop: '0.5rem', marginBottom: '1.5rem' }}>
        Drag & drop or click to select a disaster site image
      </p>
      
      <div style={{ marginBottom: '1.5rem' }} onClick={(e) => e.stopPropagation()}>
        <label htmlFor="model-select" style={{ marginRight: '1rem', fontWeight: 'bold' }}>AI Engine:</label>
        <select 
          id="model-select" 
          value={selectedModel} 
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{ padding: '0.5rem', borderRadius: '4px', background: '#333', color: 'white', border: '1px solid #555' }}
        >
          <option value="unet">U-Net (Baseline)</option>
          <option value="deeplabv3">DeepLabV3+ (Advanced)</option>
        </select>
      </div>
      
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        accept="image/*"
      />
      
      <button className="btn-primary" onClick={(e) => { e.stopPropagation(); fileInputRef.current.click(); }}>
        Generate Layout Blueprint
      </button>
    </div>
  );
}

export default UploadSection;
