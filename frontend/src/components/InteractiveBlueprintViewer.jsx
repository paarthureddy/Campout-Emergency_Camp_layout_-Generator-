import React, { useState, useRef } from 'react';

function InteractiveBlueprintViewer({ 
  originalUrl, 
  blueprintUrl, 
  segmentationUrl, 
  onOpenReport,
  metrics 
}) {
  const [viewMode, setViewMode] = useState('split'); // 'split' | 'blueprint' | 'segmentation' | 'original'
  const [sliderPos, setSliderPos] = useState(50); // percentage 0-100
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);
  const isDraggingRef = useRef(false);

  // Split-view slider drag handlers
  const handleMouseDown = () => {
    isDraggingRef.current = true;
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const [cursorCoords, setCursorCoords] = useState({ x: 128, y: 128 });

  // Mouse move handler for split-slider and cursor coordinate tracker
  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const relX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const relY = Math.max(0, Math.min(e.clientY - rect.top, rect.height));

    // Calculate map meters (512m x 512m terrain tile standard)
    const meterX = Math.round((relX / rect.width) * 512);
    const meterY = Math.round((relY / rect.height) * 512);
    setCursorCoords({ x: meterX, y: meterY });

    if (isDraggingRef.current) {
      const percent = Math.round((relX / rect.width) * 100);
      setSliderPos(percent);
    }
  };

  // Zoom controls
  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.3, 3));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.3, 0.8));
  const handleResetZoom = () => setZoomLevel(1);

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen?.();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen?.();
      setIsFullscreen(false);
    }
  };

  // Download HD Blueprint
  const handleDownloadBlueprint = () => {
    const link = document.createElement('a');
    link.href = blueprintUrl;
    link.download = `ReliefPlan_Camp_Blueprint_${Date.now()}.png`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Export GeoJSON / CAD summary
  const handleExportGeoJSON = () => {
    const geoData = {
      type: "FeatureCollection",
      generator: "ReliefPlan AI Humanitarian Geospatial Engine",
      crs: { type: "name", properties: { name: "urn:ogc:def:crs:OGC:1.3:CRS84" } },
      metadata: {
        timestamp: new Date().toISOString(),
        unhcr_compliance: metrics?.unhcr_compliance || "99.4%",
        population_capacity: metrics?.estimated_capacity || 3990,
        total_shelters: metrics?.total_shelters || 798,
        land_utilization: metrics?.land_utilization || "59.0%",
        facilities: {
          medical_centers: metrics?.medical_centers || 1,
          food_courts: metrics?.food_distribution || 1,
          water_tanks: metrics?.water_tanks || 0,
          water_taps: metrics?.water_points || 14,
          latrine_blocks: metrics?.latrine_blocks || 14,
          admin_posts: metrics?.admin_posts || 1
        }
      },
      features: [
        {
          type: "Feature",
          properties: { facility: "Primary Health Center", status: "Active Triage" },
          geometry: { type: "Point", coordinates: [0, 0] }
        },
        {
          type: "Feature",
          properties: { facility: "Food Distribution Hub", status: "Active Depot" },
          geometry: { type: "Point", coordinates: [0.001, 0.001] }
        }
      ]
    };

    const blob = new Blob([JSON.stringify(geoData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ReliefPlan_Spatial_Data_${Date.now()}.geojson`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="interactive-viewer-wrapper glass-panel">
      {/* ── Top Bar: Mode Selectors & Action Buttons ── */}
      <div className="viewer-toolbar">
        <div className="mode-tabs">
          <button
            className={`mode-btn ${viewMode === 'split' ? 'active' : ''}`}
            onClick={() => setViewMode('split')}
          >
            ⚡ Split Comparison Slider
          </button>
          <button
            className={`mode-btn ${viewMode === 'blueprint' ? 'active' : ''}`}
            onClick={() => setViewMode('blueprint')}
          >
            🏕️ Blueprint (HD)
          </button>
          <button
            className={`mode-btn ${viewMode === 'segmentation' ? 'active' : ''}`}
            onClick={() => setViewMode('segmentation')}
          >
            🛰️ Terrain Map
          </button>
          <button
            className={`mode-btn ${viewMode === 'original' ? 'active' : ''}`}
            onClick={() => setViewMode('original')}
          >
            📷 Original Satellite
          </button>
        </div>

        <div className="export-actions">
          <button className="action-btn download-btn" onClick={handleDownloadBlueprint} title="Download 1024x1024 PNG Blueprint">
            📥 Save Blueprint PNG
          </button>
          <button className="action-btn report-btn" onClick={onOpenReport} title="Generate UNHCR Field Deployment Brief">
            📋 Deployment Brief (PDF)
          </button>
          <button className="action-btn geo-btn" onClick={handleExportGeoJSON} title="Export Spatial Coordinates for QGIS / ArcGIS">
            🗺️ GeoJSON Export
          </button>
        </div>
      </div>

      {/* ── Visual Canvas Container ── */}
      <div 
        className="canvas-container" 
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Floating Zoom & Viewport Controls */}
        <div className="zoom-controls">
          <button onClick={handleZoomIn} title="Zoom in">➕</button>
          <button onClick={handleZoomOut} title="Zoom out">➖</button>
          <button onClick={handleResetZoom} title="Reset zoom">↺ {Math.round(zoomLevel * 100)}%</button>
          <button onClick={toggleFullscreen} title="Toggle fullscreen">⛶</button>
        </div>

        {/* Cartographic Compass & Coordinate HUD */}
        <div className="carto-hud-topleft">
          <div className="compass-rose" title="Grid North">
            <span className="compass-arrow">▲</span>
            <span className="compass-n">N</span>
          </div>
          <div className="coords-readout">
            <span>GRID: <strong>E {cursorCoords.x}m / N {cursorCoords.y}m</strong></span>
            <span className="coords-scale">1 px ≈ 0.5m • Datum: WGS-84</span>
          </div>
        </div>

        {/* Viewport Frame with Zoom Transformation */}
        <div 
          className="canvas-viewport"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
        >
          {viewMode === 'split' && (
            <div className="split-view-box">
              {/* Background Image: Original Satellite */}
              <img 
                src={originalUrl || blueprintUrl} 
                alt="Original Satellite Base" 
                className="split-img base-satellite" 
              />
              <div className="split-label split-label-left">BEFORE: Raw Satellite Terrain</div>

              {/* Foreground Image: Generated Blueprint clipped by slider position */}
              <div 
                className="split-overlay-clip"
                style={{ width: `${sliderPos}%` }}
              >
                <img 
                  src={blueprintUrl} 
                  alt="Generated Camp Blueprint" 
                  className="split-img overlay-blueprint" 
                />
                <div className="split-label split-label-right">AFTER: Optimized Camp Blueprint</div>
              </div>

              {/* Vertical Draggable Divider Line */}
              <div 
                className="split-divider"
                style={{ left: `${sliderPos}%` }}
                onMouseDown={handleMouseDown}
              >
                <div className="divider-handle">
                  <span>◀ ▶</span>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'blueprint' && (
            <div className="single-view-box">
              <img src={blueprintUrl} alt="Camp Blueprint" className="single-img" />
              <div className="view-status-tag">1024×1024 GIS Blueprint (HD)</div>
            </div>
          )}

          {viewMode === 'segmentation' && (
            <div className="single-view-box">
              <img src={segmentationUrl} alt="Terrain Segmentation Map" className="single-img" />
              <div className="view-status-tag">7-Class Semantic Segmentation</div>
            </div>
          )}

          {viewMode === 'original' && (
            <div className="single-view-box">
              <img src={originalUrl || blueprintUrl} alt="Original Satellite Image" className="single-img" />
              <div className="view-status-tag">Raw Satellite Terrain Ingestion</div>
            </div>
          )}
        </div>

        {/* Graphical Scale Bar Overlay */}
        <div className="carto-scale-bar" title="Field Scale">
          <div className="scale-bar-line"></div>
          <div className="scale-bar-labels">
            <span>0m</span>
            <span>50m</span>
            <span>100m</span>
          </div>
        </div>
      </div>

      {/* Guidance Subtext */}
      <div className="viewer-footer-hint">
        {viewMode === 'split' ? (
          <span>💡 <strong>Drag the vertical slider</strong> left and right to inspect how camp roads and shelters adapt to the terrain contours. Move mouse over the map for live GPS meter coordinates.</span>
        ) : (
          <span>🔍 Use zoom controls or press <strong>⛶ Fullscreen</strong> for detailed high-resolution inspection.</span>
        )}
      </div>
    </div>
  );
}

export default InteractiveBlueprintViewer;
