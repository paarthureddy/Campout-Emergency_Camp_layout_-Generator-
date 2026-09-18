import React, { useState } from 'react';

function LogisticsCalculator({ baseCapacity, targetPopulation }) {
  const [simPopulation, setSimPopulation] = useState(
    targetPopulation || baseCapacity || 3990
  );
  const [isExpanded, setIsExpanded] = useState(true);

  // Sphere Minimum Standards Formulas:
  // Water: 15 Litres / person / day
  const waterDailyLiters = simPopulation * 15;
  // Food: 2,100 kcal / person / day (~0.45 kg cereal/pulse/oil rations per person)
  const foodDailyTons = ((simPopulation * 0.45) / 1000).toFixed(2);
  const foodWeeklyTons = ((simPopulation * 0.45 * 7) / 1000).toFixed(1);
  // Shelter: 5 people per family tent
  const familyTents = Math.ceil(simPopulation / 5);
  // Latrines: 1 per 20 people
  const latrinesNeeded = Math.ceil(simPopulation / 20);
  // Health: 1 Interagency Emergency Health Kit (IEHK) per 1,000 people for 3 months
  const iehkKits = Math.max(1, Math.ceil(simPopulation / 1000));
  // Solid waste: 1 x 500L skip per 100 people
  const wasteSkips = Math.ceil(simPopulation / 100);
  // Clean power: ~30W per person for camp lights, medical cold chain & phones
  const microgridKw = ((simPopulation * 30) / 1000).toFixed(1);
  // Convoys: 10-ton standard transport trucks required weekly
  const supplyTrucksWeekly = Math.max(1, Math.ceil((simPopulation * 0.45 * 7) / 10000));

  // Capacity comparison
  const capacityDiff = (baseCapacity || 3990) - simPopulation;
  const isSurplus = capacityDiff >= 0;

  const handleExportCSV = () => {
    const rows = [
      ['Resource Category', 'Sphere Planning Standard', 'Daily Requirement', 'Weekly Requirement'],
      ['Potable Water', '15 Litres / person / day', `${waterDailyLiters.toLocaleString()} Litres`, `${(waterDailyLiters * 7).toLocaleString()} Litres`],
      ['Nutritional Rations', '2,100 kcal / person / day', `${foodDailyTons} Metric Tons`, `${foodWeeklyTons} Metric Tons`],
      ['Family Shelter Units', '3.5 m² covered / person (5/tent)', `${familyTents} Tents`, `${familyTents} Tents`],
      ['Sanitation Latrines', '1 stance per 20 persons', `${latrinesNeeded} Stances`, `${latrinesNeeded} Stances`],
      ['Emergency Health Kits', '1 IEHK per 1,000 persons', `${iehkKits} IEHK Kits`, `${iehkKits} IEHK Kits`],
      ['Communal Waste Skips', '1 x 500L skip per 100 persons', `${wasteSkips} Skips`, `${wasteSkips} Skips`],
      ['Clean Solar Power', '30W / person microgrid', `${microgridKw} kW Peak`, `${microgridKw} kW Peak`],
      ['Logistics Convoys', '10-ton cargo trucks', `${(supplyTrucksWeekly / 7).toFixed(1)} Trucks/day`, `${supplyTrucksWeekly} Trucks/week`]
    ];

    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `ReliefPlan_Logistics_Manifest_${simPopulation}pax.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="logistics-calculator-panel glass-panel">
      <div className="calc-header-bar" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="calc-title-group">
          <span className="calc-icon">📦</span>
          <div>
            <h3 className="calc-title">Sphere Project: Humanitarian Logistics & Supply Manifest</h3>
            <p className="calc-subtitle">
              Calculates daily consumables, cold chain, and life-saving materials under international humanitarian minimums
            </p>
          </div>
        </div>
        <div className="calc-header-actions" onClick={(e) => e.stopPropagation()}>
          <button className="calc-btn export-csv-btn" onClick={handleExportCSV}>
            📊 Export Supply Manifest (CSV)
          </button>
          <button className="calc-btn toggle-btn" onClick={() => setIsExpanded(!isExpanded)}>
            {isExpanded ? '▲ Collapse' : '▼ Expand'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="calc-body">
          {/* Interactive Simulation Controls */}
          <div className="calc-controls-box">
            <div className="sim-slider-row">
              <label htmlFor="sim-pop-range" className="sim-label">
                Simulated Displaced Population Demand:
                <strong className="sim-val">{simPopulation.toLocaleString()} persons</strong>
              </label>
              <input
                id="sim-pop-range"
                type="range"
                min="500"
                max="12000"
                step="100"
                value={simPopulation}
                onChange={(e) => setSimPopulation(Number(e.target.value))}
                className="slider-input"
              />
            </div>

            {/* Site Capacity Comparison Alert */}
            <div className={`site-compat-badge ${isSurplus ? 'compat-surplus' : 'compat-deficit'}`}>
              {isSurplus ? (
                <span>
                  ✅ <strong>Safe Land Capacity:</strong> Current site accommodates {(baseCapacity || 3990).toLocaleString()} people. You have a safety margin of +{capacityDiff.toLocaleString()} persons.
                </span>
              ) : (
                <span>
                  ⚠️ <strong>Overflow Alert:</strong> Target demand exceeds site layout capacity ({(baseCapacity || 3990).toLocaleString()} people) by {Math.abs(capacityDiff).toLocaleString()} persons. Consider satellite parcel expansion.
                </span>
              )}
            </div>
          </div>

          {/* Supply Manifest Resource Grid */}
          <div className="logistics-grid">
            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon blue">💧</span>
                <h4>Potable Water Supply</h4>
              </div>
              <div className="log-main-val">{waterDailyLiters.toLocaleString()} L<span className="log-unit">/day</span></div>
              <p className="log-rule">Sphere min: 15 L / person / day (drinking, cooking, hygiene)</p>
              <div className="log-secondary">Weekly: {(waterDailyLiters * 7).toLocaleString()} Litres</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon yellow">🍞</span>
                <h4>Nutritional Food Rations</h4>
              </div>
              <div className="log-main-val">{foodDailyTons} <span className="log-unit">tons/day</span></div>
              <p className="log-rule">Sphere min: 2,100 kcal / person / day dry rations</p>
              <div className="log-secondary">Weekly supply: {foodWeeklyTons} metric tons</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon green">⛺</span>
                <h4>UNHCR Family Shelter Kits</h4>
              </div>
              <div className="log-main-val">{familyTents.toLocaleString()} <span className="log-unit">tents</span></div>
              <p className="log-rule">3.5 m² covered living space / person (avg. 5 per tent)</p>
              <div className="log-secondary">Includes tarpaulin, ground sheet, frame</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon red">🩺</span>
                <h4>Emergency Health Kits (IEHK)</h4>
              </div>
              <div className="log-main-val">{iehkKits} <span className="log-unit">kits</span></div>
              <p className="log-rule">1 Interagency Kit per 1,000 population for 3 months</p>
              <div className="log-secondary">WHO standardized medical & trauma supply</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon lime">🚻</span>
                <h4>Sanitation Latrine Stances</h4>
              </div>
              <div className="log-main-val">{latrinesNeeded.toLocaleString()} <span className="log-unit">stances</span></div>
              <p className="log-rule">UNHCR standard: 1 stance per 20 persons max</p>
              <div className="log-secondary">Separated gender facilities with handwash</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon purple">⚡</span>
                <h4>Clean Solar Microgrid</h4>
              </div>
              <div className="log-main-val">{microgridKw} <span className="log-unit">kW peak</span></div>
              <p className="log-rule">30W / person for clinic cold chain & perimeter lights</p>
              <div className="log-secondary">Battery storage: {(microgridKw * 4).toFixed(1)} kWh</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon orange">🗑️</span>
                <h4>Communal Waste Skips</h4>
              </div>
              <div className="log-main-val">{wasteSkips} <span className="log-unit">skips (500L)</span></div>
              <p className="log-rule">1 communal refuse container per 100 persons</p>
              <div className="log-secondary">Daily collection schedule required</div>
            </div>

            <div className="logistics-card">
              <div className="log-card-header">
                <span className="log-badge-icon teal">🚚</span>
                <h4>Logistics Supply Convoys</h4>
              </div>
              <div className="log-main-val">{supplyTrucksWeekly} <span className="log-unit">trucks/wk</span></div>
              <p className="log-rule">Standard 10-metric-ton humanitarian cargo vehicles</p>
              <div className="log-secondary">Direct access via primary arterial road</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LogisticsCalculator;
