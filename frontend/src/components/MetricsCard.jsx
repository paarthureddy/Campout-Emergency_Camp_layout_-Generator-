import React from 'react';

function MetricsCard({ title, value, accent, icon, subtext }) {
  return (
    <div className="metric-card" style={{ borderLeft: `3px solid ${accent}` }}>
      <div className="metric-header">
        {icon && <span className="metric-icon">{icon}</span>}
        <h3>{title}</h3>
      </div>
      <div className="metric-value" style={{ color: accent }}>{value}</div>
      {subtext && <p className="metric-subtext">{subtext}</p>}
    </div>
  );
}

export default MetricsCard;
