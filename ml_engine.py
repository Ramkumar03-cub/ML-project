import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pickle
import os

FEATURE_NAMES = [
    'age',
    'bmi',
    'fasting_glucose',
    'hba1c',
    'fasting_insulin',
    'systolic_bp',
    'diastolic_bp',
    'physical_activity_hours'
]

PROFILE_METADATA = {
    0: {
        'code': 'SIRD',
        'name': 'Severe Insulin-Resistant Diabetes',
        'badge': 'High Metabolic Risk',
        'color': '#f43f5e', # Rose Red
        'accent_bg': 'rgba(244, 63, 94, 0.12)',
        'accent_border': 'rgba(244, 63, 94, 0.35)',
        'short_summary': 'Characterized by severe insulin resistance, high BMI, hyperinsulinemia, and accelerated renal/hepatic risk.',
        'clinical_focus': 'Nephropathy & NAFLD protection, weight reduction, insulin sensitizers (Metformin, SGLT2i, GLP-1 RA).',
        'risk_level': 'High',
        'primary_complications': ['Diabetic Kidney Disease (DKD)', 'Non-Alcoholic Fatty Liver (NAFLD)', 'Coronary Artery Disease'],
        'recommendations': {
            'pharmacotherapy': 'Priority on SGLT2 inhibitors and GLP-1 receptor agonists with proven renal and cardio-protective outcomes. Metformin as first-line base.',
            'dietary': 'Very low glycemic load, Mediterranean-style nutrition, strict reduction of refined carbohydrates and saturated fats.',
            'exercise': 'Combined resistance training (3x/week) to upregulate GLUT-4 transporters and moderate aerobic conditioning (150+ min/week).',
            'monitoring': 'Quarterly HbA1c, urine albumin-to-creatinine ratio (uACR) every 6 months, liver ultrasound and lipid panel biannually.'
        }
    },
    1: {
        'code': 'SIDD',
        'name': 'Severe Insulin-Deficient Diabetes',
        'badge': 'High Glycemic Instability',
        'color': '#a855f7', # Purple
        'accent_bg': 'rgba(168, 85, 247, 0.12)',
        'accent_border': 'rgba(168, 85, 247, 0.35)',
        'short_summary': 'Characterized by beta-cell secretory failure, young/middle age, lean-to-normal BMI, marked hyperglycemia, and ketoacidosis vulnerability.',
        'clinical_focus': 'Exogenous insulin replacement, retinopathy screening, glycemic variability containment.',
        'risk_level': 'Critical / High Glycemic',
        'primary_complications': ['Early Retinopathy', 'Diabetic Peripheral Neuropathy', 'Diabetic Ketoacidosis (DKA)'],
        'recommendations': {
            'pharmacotherapy': 'Prompt initiation or escalation of basal-bolus or basal insulin regimen. Regular assessment of residual endogenous C-peptide.',
            'dietary': 'Consistent carbohydrate counting, adequate caloric density with lean proteins and healthy fats to preserve lean muscle mass.',
            'exercise': 'Regular moderate aerobic activity with pre-exercise glucose checks to prevent exercise-induced hypoglycemia or ketosis.',
            'monitoring': 'Continuous Glucose Monitoring (CGM) or minimum 4x/day fingerstick checks; annual dilated eye exam starting at baseline.'
        }
    },
    2: {
        'code': 'MOD',
        'name': 'Mild Obesity-Related Diabetes',
        'badge': 'Moderate Lifestyle-Responsive',
        'color': '#0ea5e9', # Sky Blue
        'accent_bg': 'rgba(14, 165, 233, 0.12)',
        'accent_border': 'rgba(14, 165, 233, 0.35)',
        'short_summary': 'Characterized by significant obesity and younger age of onset, but relatively preserved insulin sensitivity and moderate glycemic deviation.',
        'clinical_focus': 'Substantial weight loss (10-15%), metabolic improvement, incretin-based therapies.',
        'risk_level': 'Moderate',
        'primary_complications': ['Obstructive Sleep Apnea', 'Osteoarthritis', 'Progression to severe metabolic syndrome'],
        'recommendations': {
            'pharmacotherapy': 'GLP-1 receptor agonists / GIP dual co-agonists for appetite regulation and metabolic weight loss. Metformin as adjunct.',
            'dietary': 'Caloric restriction deficit (500-750 kcal/day), high fiber intake (>30g/day), whole-food plant-forward plate model.',
            'exercise': 'Graduated low-impact aerobic routines (brisk walking, swimming, cycling) building towards 200-300 min/week for weight maintenance.',
            'monitoring': 'HbA1c every 3-6 months, sleep apnea screening (STOP-Bang questionnaire), annual lipid and metabolic panel.'
        }
    },
    3: {
        'code': 'MARD',
        'name': 'Mild Age-Related Diabetes',
        'badge': 'Low-to-Moderate Geriatric Profile',
        'color': '#10b981', # Emerald Green
        'accent_bg': 'rgba(16, 185, 129, 0.12)',
        'accent_border': 'rgba(16, 185, 129, 0.35)',
        'short_summary': 'Characterized by older age onset, modest glycemic and metabolic derangements, and comparatively favorable microvascular outlook.',
        'clinical_focus': 'Avoidance of hypoglycemia, preserving functional autonomy, cardiovascular risk mitigation.',
        'risk_level': 'Low to Moderate',
        'primary_complications': ['Cardiovascular Atherosclerosis', 'Hypoglycemia vulnerability with sulfonylureas', 'Cognitive/fall risk'],
        'recommendations': {
            'pharmacotherapy': 'Mild antidiabetic agents with minimal hypoglycemia risk: Metformin, DPP-4 inhibitors. Avoid aggressive targets (HbA1c 7.0-7.8% acceptable based on frailty).',
            'dietary': 'Balanced nutrient-dense meals preventing sarcopenia; adequate high-quality protein (1.0-1.2g/kg/day) and hydration.',
            'exercise': 'Balance and mobility exercises (Tai Chi, light resistance, regular walking) to maintain muscle mass and prevent fall risks.',
            'monitoring': 'HbA1c twice yearly, annual cardiovascular review (BP, ECG, lipid profile), cognitive and foot examinations.'
        }
    }
}

class DiabetesProfilingEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=4, random_state=42, n_init=15)
        self.pca = PCA(n_components=2, random_state=42)
        self.cohort_df = None
        self.cohort_pca_df = None
        self._build_or_train_cohort()

    def _build_or_train_cohort(self):
        np.random.seed(42)
        n_per_cluster = 300
        
        # SIRD: High BMI, Very High Fasting Insulin, High BP, moderate-high glucose
        sird = {
            'age': np.clip(np.random.normal(54, 8, n_per_cluster), 35, 75),
            'bmi': np.clip(np.random.normal(35.5, 4.2, n_per_cluster), 29, 48),
            'fasting_glucose': np.clip(np.random.normal(168, 26, n_per_cluster), 125, 240),
            'hba1c': np.clip(np.random.normal(8.3, 0.9, n_per_cluster), 6.8, 11.2),
            'fasting_insulin': np.clip(np.random.normal(32, 6.5, n_per_cluster), 20, 55),
            'systolic_bp': np.clip(np.random.normal(146, 12, n_per_cluster), 120, 180),
            'diastolic_bp': np.clip(np.random.normal(92, 8, n_per_cluster), 75, 115),
            'physical_activity_hours': np.clip(np.random.normal(1.2, 0.8, n_per_cluster), 0, 4),
            'ground_truth': 0 # SIRD
        }
        
        # SIDD: Young/middle age, Normal/Lean BMI, Very High Fasting Glucose & HbA1c, Low Fasting Insulin
        sidd = {
            'age': np.clip(np.random.normal(42, 9, n_per_cluster), 22, 62),
            'bmi': np.clip(np.random.normal(23.2, 2.5, n_per_cluster), 18.5, 27.5),
            'fasting_glucose': np.clip(np.random.normal(215, 34, n_per_cluster), 150, 310),
            'hba1c': np.clip(np.random.normal(10.2, 1.3, n_per_cluster), 8.2, 13.5),
            'fasting_insulin': np.clip(np.random.normal(4.8, 1.8, n_per_cluster), 1.5, 9.0),
            'systolic_bp': np.clip(np.random.normal(124, 10, n_per_cluster), 105, 150),
            'diastolic_bp': np.clip(np.random.normal(78, 7, n_per_cluster), 65, 95),
            'physical_activity_hours': np.clip(np.random.normal(2.5, 1.2, n_per_cluster), 0.5, 6),
            'ground_truth': 1 # SIDD
        }

        # MOD: High BMI, Younger age, Mild/Moderate Glucose, Moderate Insulin
        mod = {
            'age': np.clip(np.random.normal(46, 8, n_per_cluster), 28, 64),
            'bmi': np.clip(np.random.normal(36.8, 4.0, n_per_cluster), 30, 49),
            'fasting_glucose': np.clip(np.random.normal(142, 18, n_per_cluster), 110, 185),
            'hba1c': np.clip(np.random.normal(7.2, 0.6, n_per_cluster), 6.4, 8.5),
            'fasting_insulin': np.clip(np.random.normal(16.5, 3.8, n_per_cluster), 10, 26),
            'systolic_bp': np.clip(np.random.normal(130, 9, n_per_cluster), 112, 155),
            'diastolic_bp': np.clip(np.random.normal(83, 7, n_per_cluster), 70, 100),
            'physical_activity_hours': np.clip(np.random.normal(1.8, 1.0, n_per_cluster), 0, 5),
            'ground_truth': 2 # MOD
        }

        # MARD: Older Age, Moderate BMI, Mild Glycemia, Normal Insulin
        mard = {
            'age': np.clip(np.random.normal(68, 6, n_per_cluster), 58, 86),
            'bmi': np.clip(np.random.normal(27.4, 3.0, n_per_cluster), 22, 33),
            'fasting_glucose': np.clip(np.random.normal(136, 16, n_per_cluster), 108, 175),
            'hba1c': np.clip(np.random.normal(6.9, 0.5, n_per_cluster), 6.2, 8.1),
            'fasting_insulin': np.clip(np.random.normal(11.2, 2.9, n_per_cluster), 6, 18),
            'systolic_bp': np.clip(np.random.normal(138, 11, n_per_cluster), 118, 168),
            'diastolic_bp': np.clip(np.random.normal(80, 7, n_per_cluster), 66, 96),
            'physical_activity_hours': np.clip(np.random.normal(2.2, 1.1, n_per_cluster), 0.5, 6),
            'ground_truth': 3 # MARD
        }

        dfs = [pd.DataFrame(group) for group in [sird, sidd, mod, mard]]
        raw_df = pd.concat(dfs, ignore_index=True)

        X = raw_df[FEATURE_NAMES]
        X_scaled = self.scaler.fit_transform(X)

        # Fit KMeans with fixed centers initialized near profile archetypes for consistent cluster indexing
        init_centers = []
        for i in range(4):
            subset = X_scaled[raw_df['ground_truth'] == i]
            init_centers.append(subset.mean(axis=0))
        init_centers = np.array(init_centers)

        self.kmeans = KMeans(n_clusters=4, init=init_centers, n_init=1, random_state=42)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        raw_df['assigned_cluster'] = cluster_labels

        # PCA transformation for 2D visualization
        pca_coords = self.pca.fit_transform(X_scaled)
        raw_df['pca_x'] = pca_coords[:, 0]
        raw_df['pca_y'] = pca_coords[:, 1]

        self.cohort_df = raw_df

    def get_cohort_summary(self):
        # Sample down to 350 points for fast, fluid web rendering
        sampled = self.cohort_df.sample(n=320, random_state=42).copy()
        
        cohort_points = []
        for _, row in sampled.iterrows():
            cluster_id = int(row['assigned_cluster'])
            meta = PROFILE_METADATA[cluster_id]
            cohort_points.append({
                'x': round(float(row['pca_x']), 2),
                'y': round(float(row['pca_y']), 2),
                'cluster_id': cluster_id,
                'cluster_code': meta['code'],
                'cluster_name': meta['name'],
                'color': meta['color'],
                'age': round(float(row['age']), 1),
                'bmi': round(float(row['bmi']), 1),
                'hba1c': round(float(row['hba1c']), 1),
                'fasting_glucose': round(float(row['fasting_glucose']), 1)
            })

        # Calculate cluster statistics
        stats = {}
        for c_id in range(4):
            subset = self.cohort_df[self.cohort_df['assigned_cluster'] == c_id]
            meta = PROFILE_METADATA[c_id]
            stats[c_id] = {
                'id': c_id,
                'code': meta['code'],
                'name': meta['name'],
                'badge': meta['badge'],
                'color': meta['color'],
                'accent_bg': meta['accent_bg'],
                'accent_border': meta['accent_border'],
                'count': int(len(subset)),
                'percentage': round((len(subset) / len(self.cohort_df)) * 100, 1),
                'short_summary': meta['short_summary'],
                'clinical_focus': meta['clinical_focus'],
                'risk_level': meta['risk_level'],
                'primary_complications': meta['primary_complications'],
                'recommendations': meta['recommendations'],
                'averages': {
                    'age': round(float(subset['age'].mean()), 1),
                    'bmi': round(float(subset['bmi'].mean()), 1),
                    'fasting_glucose': round(float(subset['fasting_glucose'].mean()), 1),
                    'hba1c': round(float(subset['hba1c'].mean()), 1),
                    'fasting_insulin': round(float(subset['fasting_insulin'].mean()), 1),
                    'systolic_bp': round(float(subset['systolic_bp'].mean()), 1),
                    'diastolic_bp': round(float(subset['diastolic_bp'].mean()), 1),
                    'physical_activity_hours': round(float(subset['physical_activity_hours'].mean()), 1)
                }
            }

        return {
            'points': cohort_points,
            'profiles': stats,
            'total_patients': len(self.cohort_df),
            'explained_variance': [round(float(v) * 100, 1) for v in self.pca.explained_variance_ratio_]
        }

    def assess_patient(self, patient_data):
        """
        Takes patient dictionary with keys:
        age, bmi, fasting_glucose, hba1c, fasting_insulin, systolic_bp, diastolic_bp, physical_activity_hours
        Returns assigned cluster, PCA position, similarity breakdown, risk index, radar data.
        """
        vals = {f: [float(patient_data[f])] for f in FEATURE_NAMES}
        input_df = pd.DataFrame(vals)
        
        arr_scaled = self.scaler.transform(input_df)
        cluster_id = int(self.kmeans.predict(arr_scaled)[0])
        pca_coords = self.pca.transform(arr_scaled)[0]
        
        # Calculate distances to all centroids to generate similarity percentages
        centroids = self.kmeans.cluster_centers_
        dists = np.linalg.norm(centroids - arr_scaled, axis=1)
        # Softmin similarity
        inv_dists = 1.0 / (dists + 1e-5)
        similarities = (inv_dists / np.sum(inv_dists)) * 100
        similarities = [round(float(s), 1) for s in similarities]

        meta = PROFILE_METADATA[cluster_id]

        # Calculate HOMA-IR (Homeostatic Model Assessment for Insulin Resistance)
        # HOMA-IR = (glucose in mg/dL * insulin in μU/mL) / 405
        homa_ir = round(float((patient_data['fasting_glucose'] * patient_data['fasting_insulin']) / 405.0), 2)

        # Composite Clinical Risk Score (0 - 100)
        # Weights: HbA1c (30%), Blood Pressure (25%), HOMA-IR/Insulin (25%), BMI (20%)
        # Base healthy baselines: HbA1c=5.4, SysBP=115, HOMA=1.0, BMI=22
        hba1c_score = min(100.0, max(0.0, (patient_data['hba1c'] - 5.4) / (12.0 - 5.4) * 100.0))
        bp_score = min(100.0, max(0.0, (patient_data['systolic_bp'] - 115) / (175 - 115) * 100.0))
        homa_score = min(100.0, max(0.0, (homa_ir - 1.0) / (8.0 - 1.0) * 100.0))
        bmi_score = min(100.0, max(0.0, (patient_data['bmi'] - 22.0) / (42.0 - 22.0) * 100.0))

        composite_risk = int(round(0.30 * hba1c_score + 0.25 * bp_score + 0.25 * homa_score + 0.20 * bmi_score))
        composite_risk = min(100, max(5, composite_risk))

        if composite_risk >= 75:
            risk_tier = 'Very High'
            risk_color = '#ef4444' # Red
        elif composite_risk >= 50:
            risk_tier = 'Elevated / High'
            risk_color = '#f97316' # Orange
        elif composite_risk >= 30:
            risk_tier = 'Moderate'
            risk_color = '#eab308' # Amber
        else:
            risk_tier = 'Mild / Controlled'
            risk_color = '#10b981' # Green

        # Normalization for Biomarker Radar Chart (0 to 100 scale relative to clinical reference ranges)
        radar_metrics = {
            'Glycemia (HbA1c)': min(100.0, round(float(patient_data['hba1c'] / 13.0) * 100, 1)),
            'Fasting Glucose': min(100.0, round(float(patient_data['fasting_glucose'] / 280.0) * 100, 1)),
            'Insulin Resistance': min(100.0, round(float(homa_ir / 9.0) * 100, 1)),
            'Adiposity (BMI)': min(100.0, round(float(patient_data['bmi'] / 46.0) * 100, 1)),
            'Systolic Pressure': min(100.0, round(float(patient_data['systolic_bp'] / 180.0) * 100, 1)),
            'Physical Inactivity': min(100.0, round(float(max(0, (5.0 - patient_data['physical_activity_hours']) / 5.0) * 100), 1))
        }

        # Cluster centroid averages for the radar comparison
        cluster_mean = self.cohort_df[self.cohort_df['assigned_cluster'] == cluster_id].mean()
        cluster_homa = float((cluster_mean['fasting_glucose'] * cluster_mean['fasting_insulin']) / 405.0)
        cluster_radar = {
            'Glycemia (HbA1c)': min(100.0, round(float(cluster_mean['hba1c'] / 13.0) * 100, 1)),
            'Fasting Glucose': min(100.0, round(float(cluster_mean['fasting_glucose'] / 280.0) * 100, 1)),
            'Insulin Resistance': min(100.0, round(float(cluster_homa / 9.0) * 100, 1)),
            'Adiposity (BMI)': min(100.0, round(float(cluster_mean['bmi'] / 46.0) * 100, 1)),
            'Systolic Pressure': min(100.0, round(float(cluster_mean['systolic_bp'] / 180.0) * 100, 1)),
            'Physical Inactivity': min(100.0, round(float(max(0, (5.0 - cluster_mean['physical_activity_hours']) / 5.0) * 100), 1))
        }

        # Benchmark healthy values
        healthy_radar = {
            'Glycemia (HbA1c)': round(float(5.2 / 13.0) * 100, 1),
            'Fasting Glucose': round(float(88.0 / 280.0) * 100, 1),
            'Insulin Resistance': round(float(1.0 / 9.0) * 100, 1),
            'Adiposity (BMI)': round(float(22.5 / 46.0) * 100, 1),
            'Systolic Pressure': round(float(115.0 / 180.0) * 100, 1),
            'Physical Inactivity': round(float(max(0, (5.0 - 4.0) / 5.0) * 100), 1)
        }

        # Feature Driver Breakdown (Explainability / Clinical Attribution)
        feature_drivers = self._calculate_feature_drivers(patient_data, cluster_id)

        return {
            'assigned_cluster': cluster_id,
            'cluster_code': meta['code'],
            'cluster_name': meta['name'],
            'badge': meta['badge'],
            'color': meta['color'],
            'accent_bg': meta['accent_bg'],
            'accent_border': meta['accent_border'],
            'short_summary': meta['short_summary'],
            'clinical_focus': meta['clinical_focus'],
            'recommendations': meta['recommendations'],
            'primary_complications': meta['primary_complications'],
            'pca_coordinates': {
                'x': round(float(pca_coords[0]), 2),
                'y': round(float(pca_coords[1]), 2)
            },
            'homa_ir': homa_ir,
            'risk_score': composite_risk,
            'risk_tier': risk_tier,
            'risk_color': risk_color,
            'profile_affinity': {
                'SIRD': similarities[0],
                'SIDD': similarities[1],
                'MOD': similarities[2],
                'MARD': similarities[3]
            },
            'feature_drivers': feature_drivers,
            'radar_comparison': {
                'labels': list(radar_metrics.keys()),
                'patient_values': list(radar_metrics.values()),
                'cluster_values': list(cluster_radar.values()),
                'healthy_baseline': list(healthy_radar.values())
            }
        }

    def _calculate_feature_drivers(self, patient_data, cluster_id):
        """
        Calculates normalized z-score deviations of patient features vs. overall cohort
        to identify the top driving clinical factors for this patient's profile.
        """
        labels_map = {
            'fasting_insulin': 'Fasting Insulin (Hyperinsulinemia)',
            'hba1c': 'Glycated Hemoglobin (HbA1c)',
            'bmi': 'Adiposity / Body Mass Index',
            'fasting_glucose': 'Fasting Blood Glucose',
            'systolic_bp': 'Systolic Arterial Pressure',
            'age': 'Age Factor',
            'diastolic_bp': 'Diastolic Arterial Pressure',
            'physical_activity_hours': 'Sedentary Lifestyle Level'
        }

        drivers = []
        for feat in FEATURE_NAMES:
            mean_val = float(self.cohort_df[feat].mean())
            std_val = float(self.cohort_df[feat].std()) + 1e-5
            val = float(patient_data[feat])
            
            # Directional impact: higher inactivity is worse
            if feat == 'physical_activity_hours':
                z = (mean_val - val) / std_val
            else:
                z = (val - mean_val) / std_val

            impact_pct = min(100, max(5, int(abs(z) * 35)))
            status = 'Elevated' if z > 0.5 else ('Low/Deficient' if z < -0.5 else 'Near Population Median')

            drivers.append({
                'feature': feat,
                'label': labels_map.get(feat, feat),
                'patient_value': round(val, 1),
                'z_score': round(z, 2),
                'status': status,
                'impact_pct': impact_pct,
                'is_primary_driver': abs(z) >= 0.8
            })

        # Sort by absolute z-score deviation
        drivers.sort(key=lambda d: abs(d['z_score']), reverse=True)
        return drivers

    def simulate_intervention(self, base_patient, deltas):
        """
        Simulates counterfactual interventions (e.g. lifestyle, medication)
        and computes trajectory towards phenotype improvement.
        deltas dict keys: bmi_delta, hba1c_delta, exercise_delta, bp_delta, glucose_delta
        """
        proj = dict(base_patient)
        
        # Apply deltas safely within clinical limits
        proj['bmi'] = max(18.5, min(55.0, proj['bmi'] + float(deltas.get('bmi_delta', 0.0))))
        proj['hba1c'] = max(4.8, min(14.0, proj['hba1c'] + float(deltas.get('hba1c_delta', 0.0))))
        proj['fasting_glucose'] = max(70.0, min(350.0, proj['fasting_glucose'] + float(deltas.get('glucose_delta', 0.0))))
        proj['systolic_bp'] = max(95.0, min(200.0, proj['systolic_bp'] + float(deltas.get('bp_delta', 0.0))))
        proj['physical_activity_hours'] = max(0.0, min(14.0, proj['physical_activity_hours'] + float(deltas.get('exercise_delta', 0.0))))
        
        # Correlated insulin sensitivity improvement with weight loss and exercise
        bmi_drop = float(deltas.get('bmi_delta', 0.0))
        if bmi_drop < 0:
            insulin_reduction = abs(bmi_drop) * 1.5
            proj['fasting_insulin'] = max(3.0, proj['fasting_insulin'] - insulin_reduction)

        # Baseline assessment
        baseline_res = self.assess_patient(base_patient)
        # Projected assessment
        projected_res = self.assess_patient(proj)

        risk_delta = projected_res['risk_score'] - baseline_res['risk_score']
        
        return {
            'baseline': {
                'cluster_code': baseline_res['cluster_code'],
                'cluster_name': baseline_res['cluster_name'],
                'risk_score': baseline_res['risk_score'],
                'risk_tier': baseline_res['risk_tier'],
                'risk_color': baseline_res['risk_color'],
                'pca': baseline_res['pca_coordinates']
            },
            'projected': {
                'cluster_code': projected_res['cluster_code'],
                'cluster_name': projected_res['cluster_name'],
                'risk_score': projected_res['risk_score'],
                'risk_tier': projected_res['risk_tier'],
                'risk_color': projected_res['risk_color'],
                'pca': projected_res['pca_coordinates'],
                'homa_ir': projected_res['homa_ir']
            },
            'risk_delta': risk_delta,
            'percent_risk_reduction': round((abs(risk_delta) / (baseline_res['risk_score'] + 1e-5)) * 100, 1) if risk_delta < 0 else 0.0,
            'is_phenotype_transitioned': baseline_res['cluster_code'] != projected_res['cluster_code'],
            'projected_inputs': proj
        }

    def get_cohort_csv(self):
        """Exports cohort records formatted as CSV string"""
        export_df = self.cohort_df.copy()
        export_df['cluster_code'] = export_df['assigned_cluster'].map(lambda cid: PROFILE_METADATA[cid]['code'])
        export_df['cluster_name'] = export_df['assigned_cluster'].map(lambda cid: PROFILE_METADATA[cid]['name'])
        return export_df.to_csv(index=False)

# Global engine instance
profiling_engine = DiabetesProfilingEngine()

