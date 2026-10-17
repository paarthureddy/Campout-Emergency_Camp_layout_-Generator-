import React, { useState, useEffect } from 'react';

const PIPELINE_STAGES = [
  { step: 1, label: 'Satellite Ingestion & Normalization', desc: 'Decoding multispectral channels and calibrating resolution' },
  { step: 2, label: 'Neural Semantic Terrain Segmentation', desc: 'Running DeepLabV3+ across 7 LoveDA land-cover classes' },
  { step: 3, label: 'Hazard & Hydrological Setback Modeling', desc: 'Extracting buildable contours and dilating water buffers' },
  { step: 4, label: 'UNHCR Constraint-Based Spatial Optimization', desc: 'Aligning arterial roads, shelters, and essential facility ratios' },
  { step: 5, label: 'Cartographic GIS Blueprint Synthesis', desc: 'Rendering 1024x1024 vector blueprint and cartographic HUD' }
];

function MissionProcessingState({ status, onBack }) {
  const [activeStage, setActiveStage] = useState(1);

  useEffect(() => {
    // Automatically cycle through simulation stages to give real command center feedback
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev < 5 ? prev + 1 : prev));
    }, 600);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="mission-processing-card glass-panel">
      {onBack && (
        <div style={{ marginBottom: '1rem' }}>
          <button 
            onClick={onBack}
            style={{
              background: 'none',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              padding: '0.4rem 0.8rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            ← Cancel & Back
          </button>
        </div>
      )}
      <div className="processing-header">
        <div className="pulse-radar">
          <div className="radar-sweep"></div>
        </div>
        <div>
          <h3 className="glow-text">🛰️ AI SPATIAL PLANNING ENGINE ACTIVE</h3>
          <p className="sub-text">
            {status === 'uploading' 
              ? 'Receiving remote sensing satellite feed...' 
              : 'Executing autonomous terrain segmentation & camp layout optimization...'}
          </p>
        </div>
      </div>

      <div className="stages-timeline">
        {PIPELINE_STAGES.map((s) => {
          const isDone = s.step < activeStage;
          const isCurrent = s.step === activeStage;

          return (
            <div 
              key={s.step} 
              className={`stage-row ${isDone ? 'done' : ''} ${isCurrent ? 'current' : ''}`}
            >
              <div className="stage-indicator">
                {isDone ? '✓' : isCurrent ? '●' : '○'}
              </div>
              <div className="stage-info">
                <div className="stage-title">
                  <span>Stage {s.step}: {s.label}</span>
                  {isCurrent && <span className="running-pill">COMPUTING</span>}
                  {isDone && <span className="done-pill">RESOLVED</span>}
                </div>
                <div className="stage-desc">{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="processing-footer">
        <span className="live-metric">⚡ Hardware: NVIDIA RTX 4060 GPU Acceleration</span>
        <span className="live-metric">📏 Standard: UNHCR Emergency Handbook 2026</span>
      </div>
    </div>
  );
}

export default MissionProcessingState;
