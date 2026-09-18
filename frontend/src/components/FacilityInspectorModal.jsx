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
    title: 'Food Distribution Hub & Logistics Depot',
    icon: '🍞',
    color: '#f59e0b',
    unhcrStandard: '1 Distribution Point per 5,000 people (Sphere Standards)',
    placementRationale: 'Located alongside the main arterial road with a dedicated vehicle offloading apron to allow heavy WFP supply trucks to deliver grain and provisions without clogging residential footpaths.',
    staffing: [
      '1 Logistics / Supply Depot Manager',
      '6 Inventory & Ration Verification Clerks',
      'Security personnel for crowd control & orderly queue separation',
      'Biometric / Ration Card Verification Officers'
    ],
    operationalSpecs: {
      'Ration Schedule': '15-day or 30-day family food basket cycles',
      'Storage Capacity': '50 Metric Tons grain, pulses, vegetable oil, high-energy biscuits',
      'Queuing Apron': 'Separate lanes for vulnerable individuals, pregnant women, and elderly',
      'Nutritional Triage': 'Attached Supplementary Feeding unit for acute malnutrition screening'
    }
  },
  community: {
    title: 'Community Center & Child-Safe School Tent',
    icon: '🏫',
    color: '#ec4899',
    unhcrStandard: '1 Child-Friendly Space per residential sector (approx 1,000–1,500 children)',
    placementRationale: 'Built within the quiet, central core of the residential clusters, safely isolated from heavy traffic corridors and flood zones to provide children with education and psychosocial stability.',
    staffing: [
      '4–6 Emergency Primary School Teachers',
      '2 Child Protection & Psychosocial Counselors',
      'Community Elder / Camp Committee Liaison',
      'Recreation & Early Childhood Play Coordinators'
    ],
    operationalSpecs: {
      'Daily Shifts': 'Morning (Primary Grades), Afternoon (Adolescents & Vocational Skills)',
      'Amenities': 'Weatherproof tarpaulins, blackboards, learning kits, sports balls',
      'Protection Feature': 'Designated perimeter fencing to prevent unauthorized entry',
      'Night-time Use': 'Camp coordination meetings and adult literacy workshops'
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
