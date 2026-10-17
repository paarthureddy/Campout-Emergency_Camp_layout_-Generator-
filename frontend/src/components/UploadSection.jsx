import React, { useRef, useState } from 'react';

function UploadSection({ onUpload }) {
  const fileInputRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState('deeplabv3');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleSelectedFile = (file) => {
    if (!file) return;
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleSelectedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleStartGeneration = () => {
    if (selectedFile) {
      onUpload(selectedFile, selectedModel, { localPreviewUrl: previewUrl });
    }
  };

  const handleClearFile = (e) => {
    e.stopPropagation();
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="upload-container">
      {/* ── Mission Brief Banner ── */}
      <div className="command-banner glass-panel">
        <div className="banner-badge">HUMANITARIAN COMMAND CENTER</div>
        <h2>Autonomous Disaster Relief Camp Planning</h2>
        <p className="banner-subtext">
          Upload overhead satellite imagery or aerial drone photos to automatically segment land cover,
          model flood and environmental hazard buffers, and synthesize an optimized UNHCR-compliant camp layout.
        </p>
      </div>

      <div className="upload-grid">
        {/* ── Left Column: Configuration & Scenario Planning ── */}
        <div className="scenario-panel glass-panel">
          <h3 className="panel-title">⚙️ AI Model & Spatial Configuration</h3>
          
          {/* AI Segmentation Model */}
          <div className="param-group">
            <label htmlFor="model-select" className="param-label">Neural Vision Backbone:</label>
            <select 
              id="model-select"
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="select-dropdown"
            >
              <option value="deeplabv3">DeepLabV3+ with ASPP & Pre-trained Backbone (45% mIoU) — Recommended</option>
              <option value="unet">U-Net Encoder-Decoder (30% mIoU)</option>
            </select>
          </div>

          {/* UNHCR & Sphere Standards Architecture Box */}
          <div className="model-info-box" style={{ marginTop: '1.2rem', padding: '1.1rem', background: 'rgba(37, 99, 235, 0.05)', borderRadius: '12px', border: '1px solid rgba(37, 99, 235, 0.2)' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              🛡️ UNHCR & Sphere Compliance Rules
            </div>
            <ul style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, paddingLeft: '1.2rem', lineHeight: 1.7 }}>
              <li><strong>Terrain Sizing:</strong> Capacity derived dynamically from available buildable land (45m²/person standard)</li>
              <li><strong>Hydrological Buffer:</strong> 20m automated setback from detected rivers & water bodies</li>
              <li><strong>WASH Coverage:</strong> Potable water tap guaranteed in every residential cluster (&lt;50m walk)</li>
              <li><strong>Sanitation:</strong> Minimum 1 latrine block per 20 persons with privacy setbacks</li>
              <li><strong>Critical Facilities:</strong> Emergency medical triage & communal food distribution hubs</li>
            </ul>
          </div>
        </div>

        {/* ── Right Column: Ingestion Zone ── */}
        <div 
          className="upload-zone glass-panel"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{ minHeight: '380px' }}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept="image/*"
          />

          {!previewUrl ? (
            <div 
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', width: '100%' }}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                🛰️
              </div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: 'var(--text-main)' }}>
                Upload Disaster Site Satellite Imagery
              </h3>
              <p className="glow-text" style={{ marginTop: '0.2rem', marginBottom: '1.5rem', fontSize: '0.9rem', textAlign: 'center' }}>
                Drag & drop satellite or drone PNG, JPG or browse from your computer
              </p>
              
              <button 
                type="button" 
                className="btn-primary" 
                style={{ padding: '0.8rem 1.8rem', fontSize: '1rem', fontWeight: '600' }}
                onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
              >
                📂 Choose Satellite Image
              </button>
              
              <span style={{ marginTop: '1.2rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Recommended resolution: 256×256 to 2048×2048 px
              </span>
            </div>
          ) : (
            <div className="upload-preview-container" style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '1rem' }}>
                <span style={{ fontWeight: '600', fontSize: '0.95rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  ✅ Selected Image Ready
                </span>
                <button 
                  onClick={handleClearFile}
                  style={{ background: 'none', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '0.3rem 0.7rem', color: 'var(--danger)', cursor: 'pointer', fontSize: '0.85rem' }}
                >
                  ✕ Change Image
                </button>
              </div>

              <div style={{ width: '100%', maxHeight: '280px', borderRadius: '12px', overflow: 'hidden', border: '2px solid var(--primary)', background: '#0b0f19', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.2rem' }}>
                <img 
                  src={previewUrl} 
                  alt="Selected Disaster Terrain Preview" 
                  style={{ maxHeight: '280px', maxWidth: '100%', objectFit: 'contain' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', marginBottom: '1.2rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <span>📁 {selectedFile?.name || 'satellite_image.png'}</span>
                <span>{(selectedFile?.size / 1024).toFixed(1)} KB</span>
              </div>

              <button 
                type="button" 
                className="btn-primary"
                style={{ width: '100%', padding: '0.9rem', fontSize: '1.05rem', fontWeight: '700', letterSpacing: '0.02em', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                onClick={handleStartGeneration}
              >
                🚀 Generate Relief Camp Layout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadSection;
