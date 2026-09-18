import React, { useRef, useState } from 'react';

function UploadSection({ onUpload }) {
  const fileInputRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState('deeplabv3');
  const [targetPopulation, setTargetPopulation] = useState(3500);
  const [campPhase, setCampPhase] = useState('planned'); // 'transit' | 'planned' | 'flood'

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0], selectedModel, { targetPopulation, campPhase });
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0], selectedModel, { targetPopulation, campPhase });
    }
  };

  return (
    <div className="upload-container">
      {/* ── Mission Brief Banner ── */}
      <div className="command-banner glass-panel">
        <div className="banner-badge">HUMANITARIAN COMMAND CENTER</div>
        <h2>Autonomous Disaster Relief Camp Planning</h2>
        <p className="banner-subtext">
          Upload overhead satellite imagery or select a disaster terrain to automatically segment land cover,
          model flood and environmental hazards, and synthesize an optimized UNHCR-compliant camp layout.
        </p>
      </div>

      <div className="upload-grid">
        {/* ── Left Column: Configuration & Scenario Planning ── */}
        <div className="scenario-panel glass-panel">
          <h3 className="panel-title">⚙️ Mission Planning Parameters</h3>
          
          {/* Target Population Input */}
          <div className="param-group">
            <div className="param-label-row">
              <label htmlFor="target-pop-input">Target Displaced Population:</label>
              <span className="param-badge">{targetPopulation.toLocaleString()} people</span>
            </div>
            <input 
              id="target-pop-input"
              type="range" 
              min="500" 
              max="10000" 
              step="250"
              value={targetPopulation}
              onChange={(e) => setTargetPopulation(Number(e.target.value))}
              className="slider-input"
            />
            <div className="slider-ticks">
              <span>500</span>
              <span>2,500</span>
              <span>5,000</span>
              <span>10,000+</span>
            </div>
            <p className="param-hint">Est. shelter requirement: ~{Math.ceil(targetPopulation / 5)} family tents</p>
          </div>

          {/* Emergency Phase Preset */}
          <div className="param-group">
            <label className="param-label">Emergency Settlement Phase:</label>
            <div className="preset-radio-grid">
              {[
                { id: 'transit', label: '🚨 Rapid Transit Camp', desc: 'Phase 1: High density, immediate water & medical triage priority' },
                { id: 'planned', label: '🏕️ Planned Settlement', desc: 'Phase 2: UNHCR standard, full schools & community hubs' },
                { id: 'flood', label: '🌊 Flood / Epidemic Relief', desc: 'Extended 25m water buffer, strict sanitation isolation' },
              ].map((p) => (
                <div 
                  key={p.id} 
                  className={`preset-card ${campPhase === p.id ? 'active' : ''}`}
                  onClick={() => setCampPhase(p.id)}
                >
                  <div className="preset-header">{p.label}</div>
                  <div className="preset-desc">{p.desc}</div>
                </div>
              ))}
            </div>
          </div>

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
        </div>

        {/* ── Right Column: Ingestion Zone & Benchmark Datasets ── */}
        <div 
          className="upload-zone glass-panel"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <div className="upload-icon" onClick={() => fileInputRef.current.click()} style={{ cursor: 'pointer' }}>
            🛰️
          </div>
          <h3>Ingest Disaster Site Imagery</h3>
          <p className="glow-text" style={{ marginTop: '0.3rem', marginBottom: '1.2rem', fontSize: '0.9rem' }}>
            Drag & drop raw satellite/drone PNG or JPG or browse local files
          </p>
          
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept="image/*"
          />
          
          <button className="btn-primary" onClick={(e) => { e.stopPropagation(); fileInputRef.current.click(); }}>
            📂 Select Satellite Image to Plan
          </button>

          {/* ── Benchmark Satellite Test Sites ── */}
          <div className="benchmark-section" onClick={(e) => e.stopPropagation()}>
            <p className="benchmark-title">
              ⚡ Quick-Test Benchmark Disaster Sites:
            </p>
            <div className="benchmark-cards">
              {[
                { id: 'sample_open_land.png', label: '🌾 Open Arable Plain', desc: 'LoveDA Rural #0 • 90% buildable ground' },
                { id: 'sample_river_basin.png', label: '🌊 River Basin & Wetland', desc: 'LoveDA Wetland #1 • 24% water hazard zone' },
                { id: 'sample_farmland.png', label: '🚜 Agricultural Valley', desc: 'LoveDA Rural #10 • Curved contour perimeter' },
              ].map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  className="benchmark-btn"
                  onClick={async () => {
                    try {
                      const res = await fetch(`http://localhost:8000/static/samples/${sample.id}`);
                      const blob = await res.blob();
                      const file = new File([blob], sample.id, { type: 'image/png' });
                      onUpload(file, selectedModel, { targetPopulation, campPhase });
                    } catch (err) {
                      console.error('Failed to load benchmark:', err);
                    }
                  }}
                >
                  <span className="benchmark-btn-title">{sample.label}</span>
                  <span className="benchmark-btn-sub">{sample.desc}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadSection;
