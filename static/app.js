/**
 * DiaProfile AI — Client Application Script
 * Precision Diabetes Phenotyping, Dynamic Charts & Real-Time Profiling
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global state
  let cohortData = null;
  let radarChartInstance = null;
  let pcaChartInstance = null;
  let currentPresetId = 'sird_sample';

  // DOM Elements
  const archetypesContainer = document.getElementById('archetypes-container');
  const presetsContainer = document.getElementById('presets-container');
  const form = document.getElementById('patient-assessment-form');
  const btnAssess = document.getElementById('btn-assess');
  const btnReset = document.getElementById('btn-reset');
  const btnPrint = document.getElementById('btn-print-report');
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const calcHomaPreview = document.getElementById('calc-homa-preview');

  // Input elements & sync
  const inputs = {
    age: { num: document.getElementById('input-age'), slider: document.getElementById('slider-age'), display: document.getElementById('age-display') },
    bmi: { num: document.getElementById('input-bmi'), slider: document.getElementById('slider-bmi'), display: document.getElementById('bmi-display') },
    glucose: { num: document.getElementById('input-glucose'), slider: document.getElementById('slider-glucose'), display: document.getElementById('glucose-display') },
    hba1c: { num: document.getElementById('input-hba1c'), slider: document.getElementById('slider-hba1c'), display: document.getElementById('hba1c-display') },
    insulin: { num: document.getElementById('input-insulin'), slider: document.getElementById('slider-insulin'), display: document.getElementById('insulin-display') },
    sysbp: { num: document.getElementById('input-sysbp'), slider: document.getElementById('slider-sysbp'), display: document.getElementById('sysbp-display') },
    diabp: { num: document.getElementById('input-diabp'), slider: document.getElementById('slider-diabp'), display: document.getElementById('diabp-display') },
    activity: { num: document.getElementById('input-activity'), slider: document.getElementById('slider-activity'), display: document.getElementById('activity-display') }
  };

  // Wire up two-way binding between sliders and inputs
  Object.keys(inputs).forEach(key => {
    const item = inputs[key];
    if (item.num && item.slider) {
      item.slider.addEventListener('input', (e) => {
        item.num.value = e.target.value;
        updateDynamicBadges();
      });
      item.num.addEventListener('input', (e) => {
        item.slider.value = e.target.value;
        updateDynamicBadges();
      });
    }
  });

  // Calculate dynamic badges and live HOMA-IR
  function updateDynamicBadges() {
    const age = parseFloat(inputs.age.num.value) || 0;
    const bmi = parseFloat(inputs.bmi.num.value) || 0;
    const glucose = parseFloat(inputs.glucose.num.value) || 0;
    const hba1c = parseFloat(inputs.hba1c.num.value) || 0;
    const insulin = parseFloat(inputs.insulin.num.value) || 0;
    const sys = parseFloat(inputs.sysbp.num.value) || 0;
    const dia = parseFloat(inputs.diabp.num.value) || 0;
    const act = parseFloat(inputs.activity.num.value) || 0;

    // Age
    inputs.age.display.textContent = `${age} yrs`;

    // BMI Category
    let bmiCat = 'Normal';
    let bmiClass = 'unit-tag';
    if (bmi < 18.5) { bmiCat = 'Underweight'; }
    else if (bmi < 25.0) { bmiCat = 'Normal'; }
    else if (bmi < 30.0) { bmiCat = 'Overweight'; bmiClass = 'unit-tag tag-amber'; }
    else if (bmi < 35.0) { bmiCat = 'Obese Class I'; bmiClass = 'unit-tag tag-amber'; }
    else if (bmi < 40.0) { bmiCat = 'Obese Class II'; bmiClass = 'unit-tag tag-rose'; }
    else { bmiCat = 'Obese Class III'; bmiClass = 'unit-tag tag-rose'; }
    inputs.bmi.display.textContent = `${bmi.toFixed(1)} kg/m² • ${bmiCat}`;
    inputs.bmi.display.className = bmiClass;

    // Fasting Glucose
    let glucCat = '';
    let glucClass = 'unit-tag';
    if (glucose < 100) { glucCat = 'Normoglycemic'; }
    else if (glucose < 126) { glucCat = 'Impaired Fasting'; glucClass = 'unit-tag tag-amber'; }
    else { glucCat = 'Diabetic Range'; glucClass = 'unit-tag tag-rose'; }
    inputs.glucose.display.textContent = `${Math.round(glucose)} mg/dL • ${glucCat}`;
    inputs.glucose.display.className = glucClass;

    // HbA1c
    let a1cClass = 'unit-tag';
    let a1cCat = 'Normal';
    if (hba1c < 5.7) { a1cCat = 'Normal'; }
    else if (hba1c < 6.5) { a1cCat = 'Prediabetes'; a1cClass = 'unit-tag tag-amber'; }
    else if (hba1c < 8.0) { a1cCat = 'Moderate Diabetes'; a1cClass = 'unit-tag tag-rose'; }
    else { a1cCat = 'Severe Glycemic Deviation'; a1cClass = 'unit-tag tag-rose'; }
    inputs.hba1c.display.textContent = `${hba1c.toFixed(1)}% • ${a1cCat}`;
    inputs.hba1c.display.className = a1cClass;

    // Insulin
    inputs.insulin.display.textContent = `${insulin.toFixed(1)} μU/mL`;

    // BP
    inputs.sysbp.display.textContent = `${Math.round(sys)} mmHg`;
    inputs.diabp.display.textContent = `${Math.round(dia)} mmHg`;

    // Exercise
    inputs.activity.display.textContent = `${act.toFixed(1)} hrs/wk`;

    // Live HOMA-IR calculation: (Glucose * Insulin) / 405
    if (glucose > 0 && insulin > 0) {
      const homa = (glucose * insulin) / 405.0;
      let homaText = '';
      if (homa < 1.9) homaText = 'Normal Insulin Sensitivity';
      else if (homa < 2.9) homaText = 'Early Insulin Resistance';
      else homaText = 'Significant Insulin Resistance';
      calcHomaPreview.textContent = `${homa.toFixed(2)} (${homaText})`;
    }
  }

  // Load Archetypes and populate Section 1
  async function loadArchetypes() {
    try {
      const res = await fetch('/api/profiles');
      const data = await res.json();
      const profiles = data.profiles;

      archetypesContainer.innerHTML = '';
      Object.keys(profiles).forEach(key => {
        const p = profiles[key];
        const card = document.createElement('div');
        card.className = 'archetype-card glass-panel';
        card.style.setProperty('--archetype-accent', p.color);
        card.style.setProperty('--archetype-bg', p.accent_bg);

        card.innerHTML = `
          <div>
            <div class="archetype-head">
              <div>
                <span class="archetype-code">${p.code}</span>
                <h3 class="archetype-name">${p.name}</h3>
              </div>
              <span class="archetype-badge" style="background:${p.accent_bg}; color:${p.color}; border:1px solid ${p.accent_border}">
                ${p.badge}
              </span>
            </div>
            <p class="archetype-summary">${p.short_summary}</p>
            <div class="archetype-stats-row">
              <div>
                <span class="stat-mini-label">Mean Age</span>
                <span class="stat-mini-val">${p.averages.age} yrs</span>
              </div>
              <div>
                <span class="stat-mini-label">Mean BMI</span>
                <span class="stat-mini-val">${p.averages.bmi}</span>
              </div>
              <div>
                <span class="stat-mini-label">Mean HbA1c</span>
                <span class="stat-mini-val">${p.averages.hba1c}%</span>
              </div>
            </div>
          </div>
          <div>
            <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.4rem; font-weight:700; text-transform:uppercase;">
              High Predilection Complications
            </div>
            <div class="archetype-complications">
              ${p.primary_complications.map(c => `<span class="comp-tag">${c}</span>`).join('')}
            </div>
          </div>
        `;
        archetypesContainer.appendChild(card);
      });
    } catch (err) {
      console.error('Error loading archetypes:', err);
    }
  }

  // Load Sample Presets
  async function loadPresets() {
    try {
      const res = await fetch('/api/presets');
      const presets = await res.json();

      presetsContainer.innerHTML = '';
      presets.forEach((preset, idx) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `preset-btn ${idx === 0 ? 'active' : ''}`;
        btn.id = `preset-${preset.id}`;
        btn.style.setProperty('--preset-border', preset.badge_color);
        btn.style.setProperty('--preset-bg', `${preset.badge_color}18`);

        btn.innerHTML = `
          <div>
            <span class="preset-title">${preset.title}</span>
            <span class="preset-subtitle">${preset.subtitle}</span>
          </div>
          <span style="font-size:0.7rem; font-weight:700; color:${preset.badge_color}; margin-top:0.4rem; display:block;">
            ${preset.badge}
          </span>
        `;

        btn.addEventListener('click', () => {
          document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentPresetId = preset.id;
          applyPresetData(preset.data);
        });

        presetsContainer.appendChild(btn);
      });
    } catch (err) {
      console.error('Error loading presets:', err);
    }
  }

  function applyPresetData(data) {
    inputs.age.num.value = data.age;
    inputs.age.slider.value = data.age;

    inputs.bmi.num.value = data.bmi;
    inputs.bmi.slider.value = data.bmi;

    inputs.glucose.num.value = data.fasting_glucose;
    inputs.glucose.slider.value = data.fasting_glucose;

    inputs.hba1c.num.value = data.hba1c;
    inputs.hba1c.slider.value = data.hba1c;

    inputs.insulin.num.value = data.fasting_insulin;
    inputs.insulin.slider.value = data.fasting_insulin;

    inputs.sysbp.num.value = data.systolic_bp;
    inputs.sysbp.slider.value = data.systolic_bp;

    inputs.diabp.num.value = data.diastolic_bp;
    inputs.diabp.slider.value = data.diastolic_bp;

    inputs.activity.num.value = data.physical_activity_hours;
    inputs.activity.slider.value = data.physical_activity_hours;

    updateDynamicBadges();
    // Trigger assessment automatically
    submitAssessment(false);
  }

  // Load Cohort Scatter Data (PCA)
  async function loadCohortData() {
    try {
      const res = await fetch('/api/cohort');
      cohortData = await res.json();
      if (document.getElementById('stat-cohort-size')) {
        document.getElementById('stat-cohort-size').textContent = cohortData.total_patients.toLocaleString();
      }
    } catch (err) {
      console.error('Error loading cohort data:', err);
    }
  }

  // Submit Assessment Form
  async function submitAssessment(scrollIntoView = true) {
    const payload = {
      age: parseFloat(inputs.age.num.value),
      bmi: parseFloat(inputs.bmi.num.value),
      fasting_glucose: parseFloat(inputs.glucose.num.value),
      hba1c: parseFloat(inputs.hba1c.num.value),
      fasting_insulin: parseFloat(inputs.insulin.num.value),
      systolic_bp: parseFloat(inputs.sysbp.num.value),
      diastolic_bp: parseFloat(inputs.diabp.num.value),
      physical_activity_hours: parseFloat(inputs.activity.num.value)
    };

    btnAssess.disabled = true;
    btnAssess.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Phenotyping...`;

    try {
      const res = await fetch('/api/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error('Assessment request failed with status ' + res.status);
      }

      const data = await res.json();
      renderAssessmentResults(data.assessment);

      if (scrollIntoView) {
        const resultsEl = document.getElementById('results-display-area');
        resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch (err) {
      alert('Error analyzing patient profile: ' + err.message);
    } finally {
      btnAssess.disabled = false;
      btnAssess.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Run Phenotyping Profile`;
    }
  }

  // Render assessment results & update charts
  function renderAssessmentResults(assessment) {
    const banner = document.getElementById('result-banner');
    banner.style.setProperty('--result-color', assessment.color);
    banner.style.setProperty('--result-bg', assessment.accent_bg);
    banner.style.setProperty('--result-border', assessment.accent_border);
    banner.style.setProperty('--result-risk-color', assessment.risk_color);

    // Profile Title & Badge
    document.getElementById('result-code-badge').textContent = assessment.cluster_code;
    document.getElementById('result-profile-name').textContent = assessment.cluster_name;
    document.getElementById('result-profile-badge').textContent = `${assessment.badge} • ${assessment.risk_level}`;

    // Risk Meter Circle Animation
    const riskScore = assessment.risk_score;
    document.getElementById('result-risk-score').textContent = riskScore;
    document.getElementById('result-risk-tier').textContent = `${assessment.risk_tier} (${riskScore}/100)`;
    
    // Circumference = 2 * PI * 42 ≈ 263.89
    const circleCircumference = 264;
    const offset = circleCircumference - (riskScore / 100) * circleCircumference;
    const circleBar = document.getElementById('risk-svg-bar');
    circleBar.style.strokeDashoffset = offset;
    circleBar.style.stroke = assessment.risk_color;

    // Affinity Bars
    const affinityContainer = document.getElementById('affinity-bars-container');
    affinityContainer.innerHTML = '';
    const affinities = assessment.profile_affinity;
    const colors = { SIRD: '#f43f5e', SIDD: '#a855f7', MOD: '#0ea5e9', MARD: '#10b981' };
    const fullNames = {
      SIRD: 'Severe Insulin-Resistant',
      SIDD: 'Severe Insulin-Deficient',
      MOD: 'Mild Obesity-Related',
      MARD: 'Mild Age-Related'
    };

    Object.keys(affinities).forEach(key => {
      const pct = affinities[key];
      const isAssigned = (key === assessment.cluster_code);
      const item = document.createElement('div');
      item.className = 'affinity-item';
      if (isAssigned) {
        item.style.borderColor = colors[key];
        item.style.background = `${colors[key]}14`;
      }
      item.innerHTML = `
        <div class="affinity-meta">
          <span style="color:${colors[key]}">${key} ${isAssigned ? '✓' : ''}</span>
          <span>${pct}%</span>
        </div>
        <div class="affinity-track">
          <div class="affinity-fill" style="width:${pct}%; background:${colors[key]}"></div>
        </div>
        <div style="font-size:0.68rem; color:var(--text-muted); margin-top:0.35rem;">
          ${fullNames[key]}
        </div>
      `;
      affinityContainer.appendChild(item);
    });

    // Update Recommendations
    document.getElementById('rec-pharma').textContent = assessment.recommendations.pharmacotherapy;
    document.getElementById('rec-diet').textContent = assessment.recommendations.dietary;
    document.getElementById('rec-exercise').textContent = assessment.recommendations.exercise;
    document.getElementById('rec-monitor').textContent = assessment.recommendations.monitoring;

    // Render Feature Drivers (Explainability)
    renderFeatureDrivers(assessment.feature_drivers);

    // Store current state for simulation
    lastAssessment = assessment;

    // Render Charts
    renderRadarChart(assessment);
    renderPcaChart(assessment, null);

    // Run Intervention Simulation
    runInterventionSimulation();
  }

  // Render Feature Drivers
  function renderFeatureDrivers(drivers) {
    const container = document.getElementById('feature-drivers-container');
    if (!container || !drivers) return;
    container.innerHTML = '';

    drivers.forEach(driver => {
      const item = document.createElement('div');
      item.className = `driver-item ${driver.is_primary_driver ? 'primary-driver' : ''}`;
      
      const zColor = driver.z_score > 0.8 ? '#f43f5e' : (driver.z_score < -0.8 ? '#a855f7' : '#38bdf8');
      const sign = driver.z_score > 0 ? '+' : '';

      item.innerHTML = `
        <div>
          <span class="driver-name">${driver.label}</span>
          <div class="driver-meta">
            <span>Value: <strong>${driver.patient_value}</strong></span>
            <span class="driver-zscore" style="color:${zColor}">${sign}${driver.z_score}σ (${driver.status})</span>
          </div>
        </div>
        <div class="driver-bar-track">
          <div class="driver-bar-fill" style="width:${driver.impact_pct}%; background:${zColor}"></div>
        </div>
      `;
      container.appendChild(item);
    });
  }


  // Biomarker Radar Chart
  function renderRadarChart(assessment) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    const radarData = assessment.radar_comparison;

    if (radarChartInstance) {
      radarChartInstance.destroy();
    }

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    const textColor = isDark ? '#94a3b8' : '#475569';

    radarChartInstance = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: radarData.labels,
        datasets: [
          {
            label: 'This Patient',
            data: radarData.patient_values,
            borderColor: assessment.color,
            backgroundColor: `${assessment.color}35`,
            borderWidth: 2.5,
            pointBackgroundColor: assessment.color,
            pointBorderColor: '#fff',
            pointHoverRadius: 6,
            pointRadius: 4
          },
          {
            label: `${assessment.cluster_code} Centroid`,
            data: radarData.cluster_values,
            borderColor: 'rgba(255, 255, 255, 0.5)',
            borderDash: [5, 5],
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            pointRadius: 2
          },
          {
            label: 'Healthy Normal Baseline',
            data: radarData.healthy_baseline,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.08)',
            borderWidth: 1.5,
            pointRadius: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: gridColor },
            grid: { color: gridColor },
            pointLabels: {
              color: textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 11, weight: '600' }
            },
            ticks: {
              display: false,
              stepSize: 20,
              min: 0,
              max: 100
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
              padding: 15
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.raw}% of max reference`
            }
          }
        }
      }
    });
  }

  // PCA Cohort Scatter Chart with Patient Position and Simulated Trajectory
  function renderPcaChart(assessment, projected = null) {
    if (!cohortData) return;
    const ctx = document.getElementById('pcaChart').getContext('2d');

    if (pcaChartInstance) {
      pcaChartInstance.destroy();
    }

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';
    const textColor = isDark ? '#94a3b8' : '#475569';

    // Separate cohort points into 4 datasets by cluster
    const clusterDatasets = [
      { id: 0, code: 'SIRD', color: '#f43f5e', name: 'Severe Insulin-Resistant (SIRD)' },
      { id: 1, code: 'SIDD', color: '#a855f7', name: 'Severe Insulin-Deficient (SIDD)' },
      { id: 2, code: 'MOD',  color: '#0ea5e9', name: 'Mild Obesity-Related (MOD)' },
      { id: 3, code: 'MARD', color: '#10b981', name: 'Mild Age-Related (MARD)' }
    ].map(archetype => {
      const points = cohortData.points
        .filter(pt => pt.cluster_id === archetype.id)
        .map(pt => ({ x: pt.x, y: pt.y, age: pt.age, bmi: pt.bmi, hba1c: pt.hba1c }));

      return {
        label: archetype.name,
        data: points,
        backgroundColor: `${archetype.color}75`,
        borderColor: archetype.color,
        borderWidth: 1,
        pointRadius: 4,
        pointHoverRadius: 6
      };
    });

    // Current patient dataset
    const patientDataset = {
      label: `Current Patient (${assessment.cluster_code})`,
      data: [{
        x: assessment.pca_coordinates.x,
        y: assessment.pca_coordinates.y
      }],
      backgroundColor: '#ffffff',
      borderColor: assessment.color,
      borderWidth: 3,
      pointRadius: 10,
      pointHoverRadius: 13,
      pointStyle: 'circle'
    };

    const datasets = [...clusterDatasets, patientDataset];

    // If projected simulation exists, add projected point and trajectory vector
    if (projected && projected.pca) {
      const projectedDataset = {
        label: `Projected Trajectory (${projected.cluster_code})`,
        data: [{
          x: projected.pca.x,
          y: projected.pca.y
        }],
        backgroundColor: '#10b981',
        borderColor: '#ffffff',
        borderWidth: 2,
        pointRadius: 9,
        pointHoverRadius: 12,
        pointStyle: 'triangle'
      };

      const trajectoryLineDataset = {
        label: 'Trajectory Path',
        data: [
          { x: assessment.pca_coordinates.x, y: assessment.pca_coordinates.y },
          { x: projected.pca.x, y: projected.pca.y }
        ],
        showLine: true,
        borderColor: '#10b981',
        borderDash: [6, 4],
        borderWidth: 2,
        fill: false,
        pointRadius: 0
      };

      datasets.push(projectedDataset, trajectoryLineDataset);
    }

    pcaChartInstance = new Chart(ctx, {
      type: 'scatter',
      data: { datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif" } },
            title: {
              display: true,
              text: `Principal Component 1 (${cohortData.explained_variance[0]}% variance)`,
              color: textColor,
              font: { size: 11 }
            }
          },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { family: "'Plus Jakarta Sans', sans-serif" } },
            title: {
              display: true,
              text: `Principal Component 2 (${cohortData.explained_variance[1]}% variance)`,
              color: textColor,
              font: { size: 11 }
            }
          }
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: textColor,
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 10 },
              boxWidth: 10,
              padding: 10
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                if (ctx.dataset.label.includes('Current Patient')) {
                  return `★ Current Patient: Assigned to ${assessment.cluster_code}`;
                }
                if (ctx.dataset.label.includes('Projected Trajectory')) {
                  return `▲ Projected Target: Shifted to ${projected.cluster_code}`;
                }
                const pt = ctx.raw;
                return `${ctx.dataset.label}: Age ${pt.age} | BMI ${pt.bmi} | A1c ${pt.hba1c}%`;
              }
            }
          }
        }
      }
    });
  }

  // Counterfactual Intervention Simulation
  let simDebounceTimer = null;
  async function runInterventionSimulation() {
    if (!lastAssessment) return;

    const bmiDelta = parseFloat(document.getElementById('sim-slider-bmi').value) || 0;
    const a1cDelta = parseFloat(document.getElementById('sim-slider-hba1c').value) || 0;
    const exerciseDelta = parseFloat(document.getElementById('sim-slider-exercise').value) || 0;
    const bpDelta = parseFloat(document.getElementById('sim-slider-bp').value) || 0;

    // Update slider label tags
    document.getElementById('sim-bmi-val').textContent = `${bmiDelta >= 0 ? '+' : ''}${bmiDelta.toFixed(1)} kg/m²`;
    document.getElementById('sim-hba1c-val').textContent = `${a1cDelta >= 0 ? '+' : ''}${a1cDelta.toFixed(1)}%`;
    document.getElementById('sim-exercise-val').textContent = `+${exerciseDelta.toFixed(1)} hrs/wk`;
    document.getElementById('sim-bp-val').textContent = `${bpDelta >= 0 ? '+' : ''}${Math.round(bpDelta)} mmHg`;

    const currentPatient = {
      age: parseFloat(inputs.age.num.value),
      bmi: parseFloat(inputs.bmi.num.value),
      fasting_glucose: parseFloat(inputs.glucose.num.value),
      hba1c: parseFloat(inputs.hba1c.num.value),
      fasting_insulin: parseFloat(inputs.insulin.num.value),
      systolic_bp: parseFloat(inputs.sysbp.num.value),
      diastolic_bp: parseFloat(inputs.diabp.num.value),
      physical_activity_hours: parseFloat(inputs.activity.num.value)
    };

    const payload = {
      patient: currentPatient,
      deltas: {
        bmi_delta: bmiDelta,
        hba1c_delta: a1cDelta,
        glucose_delta: a1cDelta * 22.0, // Clinical empirical correlation
        exercise_delta: exerciseDelta,
        bp_delta: bpDelta
      }
    };

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!data.success) return;

      const sim = data.simulation;
      document.getElementById('sim-current-risk').textContent = sim.baseline.risk_score;
      document.getElementById('sim-projected-risk').textContent = sim.projected.risk_score;
      
      const badgeEl = document.getElementById('sim-improvement-badge');
      if (sim.risk_delta < 0) {
        badgeEl.style.background = 'rgba(16, 185, 129, 0.15)';
        badgeEl.style.borderColor = 'rgba(16, 185, 129, 0.35)';
        badgeEl.style.color = '#10b981';
        document.getElementById('sim-reduction-text').textContent = `-${sim.percent_risk_reduction}% Severity Risk Reduction (Δ ${sim.risk_delta} pts)`;
      } else {
        badgeEl.style.background = 'rgba(244, 63, 94, 0.15)';
        badgeEl.style.borderColor = 'rgba(244, 63, 94, 0.35)';
        badgeEl.style.color = '#f43f5e';
        document.getElementById('sim-reduction-text').textContent = `Neutral / Baseline`;
      }

      // Transition text
      const transText = document.getElementById('sim-transition-text');
      if (sim.is_phenotype_transitioned) {
        transText.innerHTML = `<span style="color:#10b981">★ Transformed from ${sim.baseline.cluster_code} to ${sim.projected.cluster_name} (${sim.projected.cluster_code})</span>`;
      } else {
        transText.textContent = `Remains ${sim.baseline.cluster_name} with improved metabolic reserve`;
      }

      // Update PCA map with projected vector
      renderPcaChart(lastAssessment, sim.projected);

    } catch (err) {
      console.error('Error running simulation:', err);
    }
  }

  // Hook up simulator slider inputs
  ['sim-slider-bmi', 'sim-slider-hba1c', 'sim-slider-exercise', 'sim-slider-bp'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', () => {
        clearTimeout(simDebounceTimer);
        simDebounceTimer = setTimeout(runInterventionSimulation, 150);
      });
    }
  });

  // Reset simulation button
  const btnResetSim = document.getElementById('btn-reset-sim');
  if (btnResetSim) {
    btnResetSim.addEventListener('click', () => {
      document.getElementById('sim-slider-bmi').value = -3.0;
      document.getElementById('sim-slider-hba1c').value = -1.2;
      document.getElementById('sim-slider-exercise').value = 2.0;
      document.getElementById('sim-slider-bp').value = -15;
      runInterventionSimulation();
    });
  }

  // Theme Toggle
  themeToggleBtn.addEventListener('click', () => {
    const isCurrentDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const newTheme = isCurrentDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Refresh charts with updated axis styles
    if (radarChartInstance && pcaChartInstance) {
      submitAssessment(false);
    }
  });

  // Check saved theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  // Form submit handler
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    submitAssessment(true);
  });

  // Reset button handler
  btnReset.addEventListener('click', () => {
    const firstPresetBtn = document.querySelector('.preset-btn');
    if (firstPresetBtn) {
      firstPresetBtn.click();
    }
  });

  // Print clinical summary handler
  btnPrint.addEventListener('click', () => {
    window.print();
  });

  // Initialize App
  async function init() {
    updateDynamicBadges();
    await Promise.all([loadArchetypes(), loadPresets(), loadCohortData()]);
    // Automatically perform initial assessment with the default preset values
    await submitAssessment(false);
  }

  init();
});
