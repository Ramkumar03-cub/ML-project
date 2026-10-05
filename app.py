from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os
from ml_engine import profiling_engine, PROFILE_METADATA

app = FastAPI(
    title="Diabetes Patient Profiling API",
    description="Precision Machine Learning for Diabetes Sub-Phenotyping and Risk Stratification",
    version="1.0.0"
)

# Patient Input Schema
class PatientAssessmentRequest(BaseModel):
    age: float = Field(..., ge=18, le=100, description="Age in years")
    bmi: float = Field(..., ge=15.0, le=60.0, description="Body Mass Index in kg/m²")
    fasting_glucose: float = Field(..., ge=60.0, le=450.0, description="Fasting Blood Glucose in mg/dL")
    hba1c: float = Field(..., ge=4.0, le=16.0, description="Glycated Hemoglobin in %")
    fasting_insulin: float = Field(..., ge=1.0, le=80.0, description="Fasting Serum Insulin in μU/mL")
    systolic_bp: float = Field(..., ge=80.0, le=220.0, description="Systolic Blood Pressure in mmHg")
    diastolic_bp: float = Field(..., ge=50.0, le=130.0, description="Diastolic Blood Pressure in mmHg")
    physical_activity_hours: float = Field(..., ge=0.0, le=14.0, description="Weekly moderate-to-vigorous exercise hours")

SAMPLE_PRESETS = [
    {
        "id": "sird_sample",
        "title": "Severe Insulin-Resistant (SIRD)",
        "subtitle": "High BMI • Severe Hyperinsulinemia • High Blood Pressure",
        "badge": "High Metabolic Risk",
        "badge_color": "#f43f5e",
        "data": {
            "age": 52.0,
            "bmi": 36.4,
            "fasting_glucose": 172.0,
            "hba1c": 8.6,
            "fasting_insulin": 34.5,
            "systolic_bp": 148.0,
            "diastolic_bp": 94.0,
            "physical_activity_hours": 1.0
        }
    },
    {
        "id": "sidd_sample",
        "title": "Severe Insulin-Deficient (SIDD)",
        "subtitle": "Lean/Normal Weight • Marked Hyperglycemia • Beta-cell Failure",
        "badge": "High Glycemic Instability",
        "badge_color": "#a855f7",
        "data": {
            "age": 39.0,
            "bmi": 22.8,
            "fasting_glucose": 228.0,
            "hba1c": 10.4,
            "fasting_insulin": 4.2,
            "systolic_bp": 122.0,
            "diastolic_bp": 78.0,
            "physical_activity_hours": 3.0
        }
    },
    {
        "id": "mod_sample",
        "title": "Mild Obesity-Related (MOD)",
        "subtitle": "Obesity • Younger Onset • Moderate Glycemic Deviation",
        "badge": "Lifestyle Responsive",
        "badge_color": "#0ea5e9",
        "data": {
            "age": 44.0,
            "bmi": 37.2,
            "fasting_glucose": 138.0,
            "hba1c": 7.1,
            "fasting_insulin": 17.0,
            "systolic_bp": 128.0,
            "diastolic_bp": 82.0,
            "physical_activity_hours": 1.5
        }
    },
    {
        "id": "mard_sample",
        "title": "Mild Age-Related (MARD)",
        "subtitle": "Older Age • Mild Glycemic Shift • Low Complication Speed",
        "badge": "Geriatric Low Risk",
        "badge_color": "#10b981",
        "data": {
            "age": 71.0,
            "bmi": 26.8,
            "fasting_glucose": 134.0,
            "hba1c": 6.8,
            "fasting_insulin": 10.5,
            "systolic_bp": 138.0,
            "diastolic_bp": 79.0,
            "physical_activity_hours": 2.5
        }
    }
]

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Diabetes Patient Profiling Engine"}

@app.get("/api/profiles")
def get_profiles():
    summary = profiling_engine.get_cohort_summary()
    return {
        "profiles": summary["profiles"],
        "total_patients": summary["total_patients"]
    }

@app.get("/api/cohort")
def get_cohort_data():
    return profiling_engine.get_cohort_summary()

@app.get("/api/presets")
def get_presets():
    return SAMPLE_PRESETS

class InterventionDeltas(BaseModel):
    bmi_delta: float = 0.0
    hba1c_delta: float = 0.0
    glucose_delta: float = 0.0
    bp_delta: float = 0.0
    exercise_delta: float = 0.0

class InterventionSimulationRequest(BaseModel):
    patient: PatientAssessmentRequest
    deltas: InterventionDeltas

@app.post("/api/assess")
def assess_patient_endpoint(patient: PatientAssessmentRequest):
    try:
        result = profiling_engine.assess_patient(patient.model_dump())
        return {
            "success": True,
            "assessment": result,
            "input_metrics": patient.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate")
def simulate_intervention_endpoint(req: InterventionSimulationRequest):
    try:
        result = profiling_engine.simulate_intervention(req.patient.model_dump(), req.deltas.model_dump())
        return {
            "success": True,
            "simulation": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-cohort")
def download_cohort_endpoint():
    from fastapi.responses import Response
    csv_data = profiling_engine.get_cohort_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=diabetes_phenotypes_cohort.csv"}
    )


# Mount static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Diabetes Profiling Frontend is loading..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
