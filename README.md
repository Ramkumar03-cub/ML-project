# DiaProfile.AI — Diabetes Patient Phenotyping & Risk Stratification Web Platform

A machine learning web application for **Diabetes Patient Profiling**, moving beyond traditional binary Type 2 diabetes classification by stratifying patients into four validated physiological sub-phenotypes.

---

## 🌟 Key Features

1. **Four Validated Clinical Archetypes (Lancet / Scandinavian Phenotypes)**:
   - **SIRD (Severe Insulin-Resistant Diabetes)**: High BMI, hyperinsulinemia, accelerated diabetic kidney disease and NAFLD risk.
   - **SIDD (Severe Insulin-Deficient Diabetes)**: Lean/normal BMI, early onset, severe hyperglycemia, high risk of early diabetic retinopathy and DKA.
   - **MOD (Mild Obesity-Related Diabetes)**: Obesity-driven onset, preserved beta-cell function, highly responsive to weight loss and incretin therapies.
   - **MARD (Mild Age-Related Diabetes)**: Geriatric onset (>65), mild metabolic derangements, lower microvascular complication speed.

2. **Interactive Patient Assessment & Profiling Tool**:
   - 8 Biomarker inputs (Age, BMI, Fasting Glucose, HbA1c, Fasting Insulin, Systolic BP, Diastolic BP, Weekly Physical Activity).
   - Real-time calculated **HOMA-IR** (Homeostatic Model Assessment of Insulin Resistance) preview.
   - 1-Click Clinical Presets to test all 4 archetypes instantly.
   - Two-way binding between range sliders and numerical inputs with dynamic classification badges (e.g., Obese Class I, Impaired Fasting, Prediabetic, etc.).

3. **Multi-Dimensional Results & Visual Analytics**:
   - **Profile Affinity Meter**: Softmin distance breakdown across all 4 archetypes.
   - **Composite Clinical Severity Gauge**: Circular animated risk score (0-100) reflecting multi-organ vulnerability.
   - **Biomarker Multi-Axis Radar Chart (Chart.js)**: Compares the patient's lab values against cluster centroid norms and healthy baselines.
   - **2D Cohort Landscape (PCA Scatter Map)**: Plots the patient's coordinates as a prominent crosshair marker inside the 1,200 patient cohort space.
   - **Precision Clinical & Lifestyle Action Plan**: Tailored pharmacotherapy recommendations (SGLT2i, GLP-1 RA, Insulin), medical nutrition therapy, exercise prescriptions, and screening intervals.
   - **Clinical Summary Export**: One-click print / PDF export formatted for patient records.

---

## 🚀 How to Run the Website

### Prerequisites
- Python 3.10+ (Current environment: Python 3.13)
- Required packages: `fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `numpy`, `pydantic`

### Installation
```bash
pip install -r requirements.txt
```

### Start the Server
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 📂 Project Architecture

```
d:\ML project\
├── app.py                 # FastAPI application serving REST endpoints and static files
├── ml_engine.py           # Machine learning engine (KMeans, StandardScaler, PCA, HOMA-IR)
├── requirements.txt       # Python dependencies
├── static\
│   ├── index.html         # Modern HTML5 UI with glassmorphic layout
│   ├── style.css          # Vanilla CSS design system (Dark/Light mode, glowing accents)
│   └── app.js             # Two-way data binding, Chart.js integrations & live API calls
└── README.md              # Project documentation
```
