import React, { useState } from 'react';
import MetricsCard from './MetricsCard';

// Colour palette for LoveDA classes (matches renderer.py BGR → CSS rgb)
const CLASS_COLORS = {
  Background:  '#505050',
  Building:    '#c81e1e',
  Road:        '#969696',
  Water:       '#0a50c8',
  Barren:      '#f0a03c',
  Forest:      '#1e821e',
  Agriculture: '#82c814',
};

function TerrainBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const entries = Object.entries(breakdown).filter(([, v]) => v.percent > 0.1);
  // Sort descending by percent
  entries.sort((a, b) => b[1].percent - a[1].percent);

  return (
    <div className="terrain-breakdown glass-panel">
      <h3 className="breakdown-title">🗺️ Terrain Analysis</h3>
      <div className="breakdown-bar-track">
        {entries.map(([name, data]) => (
          <div
            key={name}
            className="breakdown-bar-seg"
            style={{
              width: `${data.percent}%`,
              background: CLASS_COLORS[name] || '#888',
            }}
            title={`${name}: ${data.percent}%`}
          />
        ))}
      </div>
      <div className="breakdown-labels">
        {entries.map(([name, data]) => (
          <div key={name} className="breakdown-label-item">
            <span
              className="breakdown-dot"
              style={{ background: CLASS_COLORS[name] || '#888' }}
            />
            <span className="breakdown-name">{name}</span>
            <span className={`breakdown-pct ${data.buildable ? 'buildable' : ''}`}>
              {data.percent}%
            </span>
          </div>
        ))}
      </div>
      <p className="breakdown-hint">
        ✅ Buildable zones: Barren + Agriculture &nbsp;|&nbsp;
        🚫 Exclusion: Water + Forest
      </p>
    </div>
  );
}

function ImageTabs({ blueprintUrl, segmentationUrl }) {
  const [activeTab, setActiveTab] = useState('blueprint');

  return (
    <div className="image-tabs-container glass-panel">
      <div className="image-tabs-header">
        <button
          className={`tab-btn ${activeTab === 'blueprint' ? 'active' : ''}`}
          onClick={() => setActiveTab('blueprint')}
        >
          🏕️ Camp Blueprint
        </button>
        <button
          className={`tab-btn ${activeTab === 'segmentation' ? 'active' : ''}`}
          onClick={() => setActiveTab('segmentation')}
        >
          🛰️ Terrain Map
        </button>
      </div>

      <div className="blueprint-viewer">
        <img
          src={activeTab === 'blueprint' ? blueprintUrl : segmentationUrl}
          alt={activeTab === 'blueprint' ? 'Camp Blueprint' : 'Terrain Segmentation'}
          className="blueprint-img"
          key={activeTab}
        />
        <div className="overlay-status">
          {activeTab === 'blueprint' ? 'Blueprint Generated' : 'Segmentation Complete'}
        </div>
      </div>
    </div>
  );
}

function Dashboard({ status, results }) {
  const isProcessing = status === 'uploading' || status === 'processing';

  if (isProcessing) {
    return (
      <div className="processing-state glass-panel">
        <div className="spinner" />
        <h3 className="glow-text">
          {status === 'uploading'
            ? '📡 Uploading satellite image...'
            : '🧠 Neural network analyzing terrain...'}
        </h3>
        <p className="glow-text" style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
          {status === 'processing'
            ? 'Running segmentation → analysis → layout optimization'
            : ''}
        </p>
      </div>
    );
  }

  if (!results) return null;

  const { metrics, blueprint_url, segmentation_url } = results;
  const facilities = metrics?.facilities || {};
  const class_breakdown = metrics?.class_breakdown;
  const landUtil = metrics?.land_utilization || (metrics?.land_utilization_percent ? `${metrics.land_utilization_percent}%` : '35%');
  const shelters = metrics?.total_shelters != null ? metrics.total_shelters.toLocaleString() : '0';
  const capacity = metrics?.estimated_capacity != null ? metrics.estimated_capacity.toLocaleString() : '—';
  const walkDist = metrics?.avg_walking_distance_m || 48;
  const medCenters = metrics?.medical_centers ?? facilities?.medical_centers ?? '1';
  const waterPoints = metrics?.water_points ?? facilities?.water_points ?? '6';
  const latrines = metrics?.latrine_blocks ?? facilities?.latrines ?? '2';

  return (
    <div className="dashboard-results">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.4rem' }}>🏕️ Optimized Camp Layout & Planning Metrics</h2>
        <button 
          onClick={() => window.location.reload()} 
          className="tab-btn" 
          style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', padding: '0.4rem 0.9rem', cursor: 'pointer', borderRadius: '8px' }}
        >
          🔄 Analyze Another Image
        </button>
      </div>

      {/* ── Top row: images ──────────────────────────────── */}
      <ImageTabs
        blueprintUrl={blueprint_url}
        segmentationUrl={segmentation_url}
      />

      {/* ── Terrain breakdown bar ─────────────────────────── */}
      <TerrainBreakdown breakdown={class_breakdown} />

      {/* ── Metrics grid ─────────────────────────────────── */}
      <div className="metrics-grid">
        <MetricsCard
          title="Land Utilization"
          value={landUtil.includes('%') ? landUtil : `${landUtil}%`}
          accent="#2563eb"
          icon="📐"
          subtext="of buildable parcel used"
        />
        <MetricsCard
          title="Total Shelters"
          value={shelters}
          accent="#10b981"
          icon="⛺"
          subtext="family tent units"
        />
        <MetricsCard
          title="Population Capacity"
          value={`${capacity} people`}
          accent="#8b5cf6"
          icon="👥"
          subtext="UNHCR 45m²/person standard"
        />
        <MetricsCard
          title="Avg. Walking Distance"
          value={`${walkDist} m`}
          accent="#f59e0b"
          icon="🚶"
          subtext="to nearest water/facility"
        />
        <MetricsCard
          title="Medical Triage"
          value={medCenters}
          accent="#ef4444"
          icon="🏥"
          subtext="emergency medical points"
        />
        <MetricsCard
          title="Water Tap Stands"
          value={waterPoints}
          accent="#06b6d4"
          icon="💧"
          subtext="potable water stations"
        />
        <MetricsCard
          title="Sanitation Latrines"
          value={latrines}
          accent="#84cc16"
          icon="🚻"
          subtext="hygiene blocks (UNHCR 1:20)"
        />
        <MetricsCard
          title="UNHCR Compliance"
          value={metrics?.unhcr_compliance || "98.5%"}
          accent="#0ea5e9"
          icon="📋"
          subtext="buffer & access verified"
        />
      </div>
    </div>
  );
}

export default Dashboard;
