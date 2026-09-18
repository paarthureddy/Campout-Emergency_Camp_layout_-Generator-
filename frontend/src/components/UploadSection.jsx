import React, { useRef, useState } from 'react';

function UploadSection({ onUpload }) {
  const fileInputRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState('deeplabv3');

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

      {/* ── Quick Test Sample Images ────────────────────────── */}
      <div style={{ marginTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem', width: '100%' }} onClick={(e) => e.stopPropagation()}>
        <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '0.8rem', fontWeight: 600 }}>
          ⚡ Or select a benchmark disaster site to test:
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {[
            { id: 'sample_open_land.png', label: '🌾 Open Rural Plain', desc: 'Continuous arable land' },
            { id: 'sample_river_basin.png', label: '🌊 River Basin (Water)', desc: 'Water exclusion zone' },
            { id: 'sample_farmland.png', label: '🚜 Agricultural Valley', desc: 'Complex field contours' },
          ].map((sample) => (
            <button
              key={sample.id}
              type="button"
              className="tab-btn"
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '0.6rem 1rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s',
              }}
              onClick={async () => {
                try {
                  const res = await fetch(`http://localhost:8000/static/samples/${sample.id}`);
                  const blob = await res.blob();
                  const file = new File([blob], sample.id, { type: 'image/png' });
                  onUpload(file, selectedModel);
                } catch (err) {
                  console.error('Failed to load sample:', err);
                }
              }}
            >
              <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{sample.label}</span>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{sample.desc}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default UploadSection;
