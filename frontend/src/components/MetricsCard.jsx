import React from 'react';

function MetricsCard({ title, value, accent }) {
  return (
    <div className="metric-card glass-panel" style={{ borderLeftColor: accent }}>
      <h3>{title}</h3>
      <div className="value">{value}</div>
    </div>
  );
}

export default MetricsCard;
