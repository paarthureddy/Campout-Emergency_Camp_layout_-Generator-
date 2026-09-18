import React from 'react';

const FACILITY_DETAILS = {
  medical: {
    title: 'Hospital & Emergency Medical Triage',
    icon: '🏥',
    color: '#ef4444',
    unhcrStandard: '1 Primary Health Clinic per 10,000 to 20,000 people',
    placementRationale: 'Positioned at the primary arterial junction for immediate ambulance and triage access from both outside roads and internal camp pathways.',
    staffing: [
      '2–4 Medical Doctors & Trauma Surgeons',
      '8–12 Registered Triage Nurses',
      '2 Emergency Transport Ambulances / Evacuation Vehicles',
      'Pharmaceutical Supply Depository & Cold Chain Vaccine Storage'
    ],
    operationalSpecs: {
      'Target Walking Radius': '< 300 meters from residential center',
      'Bed Capacity': '30–50 Inpatient / Isolation Beds',
      'Water Requirement': '40–60 Litres per patient per day',
      'Hygiene Standard': 'Dedicated hazardous medical waste incineration pit'
    }
  },
  food: {
    title: 'Food Court & Communal Nutrition Hub',
    icon: '🍽️',
    color: '#d946ef',
    unhcrStandard: '1 Central Food Court & Ration Hub per 5,000 people (Sphere Standards)',
    placementRationale: 'Positioned prominently along the main arterial corridor with high-visibility magenta marquee canopy for easy identification. Features separate queuing and sheltered dining pavilions to serve hot nutritional rations without obstructing camp transit.',
    staffing: [
      '1 Chief Nutrition & Food Operations Officer',
      '6 Kitchen Staff & Hot Meal Preparers',
      '4 Ration Verification & Biometric Clerks',
      'Hygiene Stewards ensuring clean dining tables & sanitation'
    ],
    operationalSpecs: {
      'Ration Capacity': 'Daily hot meal serving for up to 3,000 persons / 15-day family dry ration packs',
      'Visual Identity': 'Distinct Vibrant Magenta (#D946EF) marquee roof canopy (zero confusion with amber family tents)',
      'Queuing Apron': 'Dedicated shaded lines for mothers, children, elderly, and differently-abled persons',
      'Nutrition Screening': 'Integrated Mid-Upper Arm Circumference (MUAC) malnutrition screening post'
    }
  },
  water_tank: {
    title: 'Water Intake & Purification Reservoir Tank',
    icon: '🚰',
    color: '#0284c7',
    unhcrStandard: 'Raw water source intake, sediment filtration, and high-capacity chlorination reservoir',
    placementRationale: 'Strategically positioned immediately adjacent to natural surface water bodies (outside the 20m flood buffer) to draw, purify, and pressurize potable water into the residential block pipelines.',
    staffing: [
      '1 Lead Environmental / WASH Plant Operator',
      '2 Water Quality Technicians (Hourly Turbidity & Free Residual Chlorine Testing)',
      'Submersible Pump & Solar Generator Technicians',
      'Pipeline Pressure & Valve Stewards'
    ],
    operationalSpecs: {
      'Purification Stage': 'Coagulation, sand flocculation, 5-micron sediment filter, and inline chlorination (>0.5 mg/L residual)',
      'Reservoir Capacity': '45,000–90,000 Litre elevated bladder & corrugated steel reservoir',
      'Distribution System': 'Gravity-fed / solar-pumped pressurized manifold directly feeding residential block tap stands',
      'Intake Setback': 'Built on stable, non-flooding high ground 10–25m from riverbank contour'
    }
  },
  water: {
    title: 'Potable Water Tap Stands & Storage Bladders',
    icon: '💧',
    color: '#06b6d4',
    unhcrStandard: '1 Tap per 80–100 persons; max 150m walking distance; min 20L / person / day',
    placementRationale: 'Distributed systematically along all secondary walkway intersections to ensure no family has to walk further than 50–100m carrying heavy 20-litre jerrycans.',
    staffing: [
      '1 Water, Sanitation & Hygiene (WASH) Engineer',
      'Daily Water Monitors checking residual chlorine levels (>0.5 mg/L)',
      'Pump Maintenance Mechanics & Tap Stand Stewards'
    ],
    operationalSpecs: {
      'Storage Volume': 'Collapsible bladder tanks (10,000L to 30,000L capacity)',
      'Water Quality': 'Turbidity < 5 NTU, E. coli 0 CFU / 100mL',
      'Drainage Soakaway': 'Gravel soakaway pit beneath every tap stand to prevent standing water',
      'Average Walk Distance': 'Current site metric: 38.5 meters'
    }
  },
  latrines: {
    title: 'Sanitation Latrines & Hygiene Blocks',
    icon: '🚻',
    color: '#84cc16',
    unhcrStandard: '1 Latrine per 20 persons; located 30–50m from shelters; >30m from water sources',
    placementRationale: 'Arranged along the outer edges of each parcel downwind of residential zones, at a strict downstream gradient away from water pipes and storage bladders to prevent cholera contamination.',
    staffing: [
      'Sanitation Maintenance Crew (daily lime dusting & disinfection)',
      'Community Hygiene Promoters (handwashing with soap awareness)',
      'Night-time security / solar lighting monitors'
    ],
    operationalSpecs: {
      'Gender Segregation': 'Separate, marked blocks with privacy screens and inside locks',
      'Ventilation': 'VIP (Ventilated Improved Pit) latrines with fly screens',
      'Handwashing Station': 'Water tap + soap dispenser attached to every latrine entrance',
      'Groundwater Safety': 'Pit base is minimum 1.5m above seasonal high water table'
    }
  },
  admin: {
    title: 'Camp Intake Gate & Security Admin Post',
    icon: '🛡️',
    color: '#14b8a6',
    unhcrStandard: '1 Central Registration & Security checkpoint at primary access road ingress',
    placementRationale: 'Located right at the camp boundary nearest to external roads so displaced arrivals are immediately registered, triaged, and assigned shelter pods without entering the camp unverified.',
    staffing: [
      'UNHCR Registration & Protection Officers',
      'Local Emergency Management Authorities',
      'Camp Security & Traffic Ingress Marshals',
      'Vulnerability Profiling Specialists (identifying unaccompanied minors)'
    ],
    operationalSpecs: {
      'Intake Workflow': 'Arrival -> Biometric/Fingerprint Intake -> Medical Check -> NFIs Distribution (blankets, mats, jerrycans) -> Tent Assignment',
      'Communications': 'Satellite link / VHF radio base station for emergency dispatch',
      'Vehicle Gate': 'Boom barrier controlling aid convoy and emergency vehicle entry'
    }
  }
};

function FacilityInspectorModal({ facilityKey, onClose }) {
  if (!facilityKey || !FACILITY_DETAILS[facilityKey]) return null;

  const facility = FACILITY_DETAILS[facilityKey];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="inspector-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="inspector-header" style={{ borderBottomColor: facility.color }}>
          <div className="inspector-title-box">
            <span className="inspector-icon">{facility.icon}</span>
            <div>
              <h3>{facility.title}</h3>
              <span className="unhcr-badge">UNHCR STANDARD: {facility.unhcrStandard}</span>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="inspector-body">
          {/* Spatial Rationale */}
          <div className="inspector-section">
            <h4>📍 Spatial Placement Rationale on Terrain</h4>
            <p className="inspector-text">{facility.placementRationale}</p>
          </div>

          {/* Operational Specifications */}
          <div className="inspector-section">
            <h4>⚙️ Operational Specifications & Standards</h4>
            <div className="specs-grid">
              {Object.entries(facility.operationalSpecs).map(([label, val]) => (
                <div key={label} className="spec-item">
                  <div className="spec-label">{label}</div>
                  <div className="spec-value">{val}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Staffing & Resources */}
          <div className="inspector-section">
            <h4>👥 Field Staffing & Equipment Allocation</h4>
            <ul className="staff-list">
              {facility.staffing.map((item, idx) => (
                <li key={idx}>✅ {item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="inspector-footer">
          <button className="btn-primary" onClick={onClose} style={{ background: facility.color }}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}

export default FacilityInspectorModal;
