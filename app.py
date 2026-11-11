from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g, send_file
import os
import random
from pymongo import MongoClient
from datetime import datetime, timedelta
from openai import OpenAI
import json
from bson import ObjectId
from functools import wraps
from ml_modules import MLHealthAnalyzer
from dotenv import load_dotenv
from security_config import (
    SecurityConfig, rate_limit, require_admin, validate_assessment_input,
    rate_limiter
)
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import io
from whatsapp_service import whatsapp_service

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Validate and set secret key
try:
    app.secret_key = SecurityConfig.validate_secret_key()
except ValueError as e:
    if os.environ.get('FLASK_ENV') == 'production':
        raise e
    else:
        # Development fallback with warning
        import warnings
        warnings.warn(f"Security Warning: {str(e)}")
        app.secret_key = os.environ.get('SECRET_KEY', 'mapims-professional-healthcare-secret-key-2025')

# Configure session security
app.config['SESSION_COOKIE_SECURE'] = SecurityConfig.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = SecurityConfig.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = SecurityConfig.SESSION_COOKIE_SAMESITE
app.config['PERMANENT_SESSION_LIFETIME'] = SecurityConfig.PERMANENT_SESSION_LIFETIME

# MongoDB connection - MUST be set via environment variable in production
MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("MONGODB_URI environment variable is required for production")
    else:
        # Development fallback (REMOVE IN PRODUCTION)
        MONGODB_URI = 'mongodb+srv://APDCH:Nani@apdch.zdewrol.mongodb.net/'
        import warnings
        warnings.warn("Using default MongoDB URI. Set MONGODB_URI environment variable for production.")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client['mapims_health']
patients_collection = db['patients']
bookings_collection = db['bookings']
admin_collection = db['admin_users']

# OpenAI API configuration - MUST be set via environment variable
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("OPENAI_API_KEY environment variable is required")
    else:
        # Development fallback - API key must be set via environment variable
        OPENAI_API_KEY = None
        import warnings
        warnings.warn("OPENAI_API_KEY not set. AI features will be disabled. Set OPENAI_API_KEY environment variable to enable AI features.")

# Initialize OpenAI client (handle version compatibility)
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception as e:
    import warnings
    warnings.warn(f"OpenAI client initialization failed: {str(e)}. AI features may be limited.")
    openai_client = None

# Security Middleware - Add security headers to all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Request logging and security checks
@app.before_request
def before_request():
    """Security checks before each request"""
    # Log suspicious requests
    if request.method == 'POST' and request.path.startswith('/api/'):
        # Check for suspicious patterns
        if request.is_json:
            data = request.get_json()
            if data:
                for key, value in data.items():
                    if isinstance(value, str) and not SecurityConfig.is_safe_string(value, 5000):
                        app.logger.warning(f"Suspicious input detected: {key} from {request.remote_addr}")
                        return jsonify({'success': False, 'error': 'Invalid input detected'}), 400

# MAPIMS Health Checkup Packages
PACKAGES = {
    'basic': {
        'id': 'basic',
        'price': 999,
        'name': 'Basic Health Check Up Package',
        'description': 'Complete Basic Health Check-up',
        'includes': [
            'Complete Blood Count',
            'Lipid Profile',
            'Fasting Sugar',
            'PPBS',
            'Urea',
            'Creatinine',
            'TSH',
            'Complete Urine Routine',
            'ECG',
            'X-Ray Chest PA View',
            'Ultrasound of the Whole Abdomen',
            'Clinical examination',
            'Medical summary and advice by a Consultant Physician',
            'Dietician Consultation'
        ],
        'duration': '2-3 hours'
    },
    'master': {
        'id': 'master',
        'price': 1999,
        'name': 'Master Health Check Up Package',
        'description': 'Complete Health Check-up for All',
        'includes': [
            'Blood Grouping',
            'Complete Blood Count',
            'Fasting Sugar',
            'PPBS',
            'Urea',
            'Creatinine',
            'TSH',
            'Uric Acid',
            'Lipid Profile',
            'Liver Function Test',
            'Complete Urine Routine',
            'ECG',
            'X-Ray Chest PA View',
            'Ultrasound of the Whole Abdomen',
            'Clinical examination',
            'Medical summary and advice by a Consultant Physician',
            'Dietician Consultation'
        ],
        'duration': '3-4 hours'
    },
    'cardiac': {
        'id': 'cardiac',
        'price': 2499,
        'name': 'Cardio Health Check Up Package',
        'description': 'Cardiac Check-up for All',
        'includes': [
            'Blood Grouping',
            'Complete Blood Count',
            'Fasting Sugar',
            'PPBS',
            'Urea',
            'Creatinine',
            'Uric Acid',
            'Lipid Profile',
            'Liver Function Test',
            'HbA1C',
            'Sr. Electrolytes',
            'Thyroid Function Test',
            'ECG',
            'X-Ray Chest',
            'USG Whole Abdomen',
            'ECHO',
            'Pulmonary Function Test',
            'Hearing Assessment (AUDIOGRAM)',
            'Clinical examination',
            'Medical summary and advice by a Consultant Physician',
            'Cardiologist Consultation',
            'Dietician Consultation'
        ],
        'duration': '4-5 hours'
    },
    'well_women': {
        'id': 'well_women',
        'price': 2999,
        'name': 'Well Women Checkup Executive Package',
        'description': 'Well Women Checkup Executive Package',
        'includes': [
            'Blood Grouping',
            'Complete Blood Count',
            'Fasting Sugar',
            'PPBS',
            'Urea',
            'Creatinine',
            'Lipid Profile',
            'Liver Function Test',
            'Complete Urine Routine',
            'HbA1C',
            'Sr. Electrolytes',
            'Serum Calcium',
            'Thyroid Function Test',
            'ECG',
            'X-Ray Chest',
            'USG Whole Abdomen & Pelvis',
            'USG Breast/Above 40yrs Mammogram',
            'ECHO',
            'Papsmear Investigation',
            'Hearing Assessment (AUDIOGRAM)',
            'Gynecologist & Cardiologist Consultant',
            'Eye Consultant',
            'Dietician Consultation'
        ],
        'duration': '5-6 hours'
    },
    'diabetic': {
        'id': 'diabetic',
        'price': 2499,
        'name': 'Diabetic Health Check Package',
        'description': 'Comprehensive Diabetic Health Check-up',
        'includes': [
            'Complete Blood Count',
            'Post Prandial Blood Sugar',
            'Fasting Blood Sugar',
            'TSH',
            'Liver Function Test',
            'ESR',
            'HbA1c',
            'Blood Urea',
            'Serum Creatinine',
            'Complete Urine Analysis',
            'Lipid Profile',
            'P/C RATIO',
            'ECG',
            'ECHO',
            'Chest X-ray',
            'USG abdomen',
            'Foot Examination with Doctor Consultation',
            'Ophthalmology Consultation & Fundus Examination Retinal Photograph',
            'Diabetologist Consultation',
            'Diet Counselling'
        ],
        'duration': '4-5 hours'
    },
    'premium_diabetic': {
        'id': 'premium_diabetic',
        'price': 4999,
        'name': 'Premium Diabetic Health Check Package',
        'description': 'Comprehensive Premium Diabetic Health Check-up',
        'includes': [
            'Complete Blood Count',
            'Post Prandial Blood Sugar',
            'Fasting Blood Sugar',
            'Lipid Profile',
            'Blood Urea',
            'Serum Creatinine',
            'Vitamin-D',
            'S Amylase',
            'ESR',
            'HbA1c',
            'Thyroid Profile',
            'Liver Function Test',
            'Serum Calcium',
            'Serum Electrolytes',
            'Complete Urine Analysis',
            'ECG',
            'ECHO',
            'Chest X-ray',
            'USG Abdomen',
            'Doppler foot for both (arteries)',
            'Foot Examination with Doctor Consultation',
            'Ophthalmology Consultation & Fundus Examination Retinal Photograph',
            'Diabetologist Consultation',
            'Cardiology Consultation',
            'Diet Counselling'
        ],
        'duration': '5-6 hours'
    }
}

# Add-on tests
ADDON_TESTS = {
    'vitamin_d': {'name': 'Vitamin D Test', 'price': 800},
    'vitamin_b12': {'name': 'Vitamin B12 Test', 'price': 600},
    'thyroid_complete': {'name': 'Complete Thyroid Profile', 'price': 900},
    'hba1c': {'name': 'HbA1c (Diabetes Test)', 'price': 700},
    'psa': {'name': 'PSA (Prostate)', 'price': 1000},
    'mammography': {'name': 'Mammography', 'price': 2500},
    'bone_density': {'name': 'Bone Density Test', 'price': 2000},
    'stress_test': {'name': 'Treadmill Stress Test', 'price': 3000}
}

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    if weight <= 0 or height <= 0:
        return None
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def transform_form_data_to_ml_format(data):
    """
    Transform structured form data into string format expected by ML modules.
    
    Converts:
    - condition_* fields and other_conditions -> medical_history string
    - family_* fields -> family_history string
    - lifestyle fields -> lifestyle string
    - symptoms field (if exists)
    """
    # Build medical_history from condition fields
    medical_history_parts = []
    condition_mapping = {
        'condition_diabetes': 'diabetes',
        'condition_hypertension': 'hypertension',
        'condition_heart_disease': 'heart disease',
        'condition_thyroid': 'thyroid',
        'condition_asthma': 'asthma',
        'condition_kidney': 'kidney disease'
    }
    
    for field_key, condition_name in condition_mapping.items():
        value = data.get(field_key, '').lower()
        if value == 'yes':
            medical_history_parts.append(condition_name)
        elif value == 'not_sure':
            medical_history_parts.append(f"possible {condition_name}")
    
    # Add other_conditions if provided
    other_conditions = data.get('other_conditions', '').strip()
    if other_conditions:
        medical_history_parts.append(other_conditions)
    
    medical_history = ', '.join(medical_history_parts) if medical_history_parts else ''
    
    # Build family_history from family fields
    family_history_parts = []
    family_mapping = {
        'family_diabetes': 'diabetes',
        'family_heart_disease': 'heart disease'
    }
    
    for field_key, condition_name in family_mapping.items():
        value = data.get(field_key, '').lower()
        if value == 'yes':
            family_history_parts.append(condition_name)
        elif value == 'not_sure':
            family_history_parts.append(f"possible {condition_name}")
    
    family_history = ', '.join(family_history_parts) if family_history_parts else ''
    
    # Build lifestyle string from lifestyle fields
    lifestyle_parts = []
    
    # Sleep hours - only include if filled
    sleep_hours = data.get('sleep_hours', '').strip()
    if sleep_hours:
        sleep_hours_lower = sleep_hours.lower()
        if sleep_hours_lower in ['less_than_5']:
            lifestyle_parts.append('less sleep')
        elif sleep_hours_lower in ['5_to_7', '7_to_9']:
            lifestyle_parts.append('adequate sleep')
        elif sleep_hours_lower in ['more_than_9']:
            lifestyle_parts.append('excessive sleep')
    
    # Exercise frequency - only include if filled
    exercise_frequency = data.get('exercise_frequency', '').strip().lower()
    if exercise_frequency:
        if exercise_frequency in ['almost_never']:
            lifestyle_parts.append('sedentary lifestyle')
            lifestyle_parts.append('no exercise')
        elif exercise_frequency in ['1_to_2_days']:
            lifestyle_parts.append('low exercise')
        elif exercise_frequency in ['3_to_5_days', 'daily']:
            lifestyle_parts.append('regular exercise')
            lifestyle_parts.append('active lifestyle')
    
    # Smoking status - only include if filled
    smoking_status = data.get('smoking_status', '').strip().lower()
    if smoking_status:
        if smoking_status in ['sometimes', 'daily']:
            lifestyle_parts.append('smoking')
            lifestyle_parts.append('tobacco use')
        elif smoking_status in ['stopped']:
            lifestyle_parts.append('former smoker')
        # 'never' is not added to lifestyle_parts as it indicates no smoking
    
    # Alcohol consumption - only include if filled
    alcohol_consumption = data.get('alcohol_consumption', '').strip().lower()
    if alcohol_consumption:
        if alcohol_consumption in ['regular']:
            lifestyle_parts.append('alcohol consumption')
        elif alcohol_consumption in ['occasional']:
            lifestyle_parts.append('occasional alcohol')
        # 'never' is not added to lifestyle_parts as it indicates no alcohol
    
    # Diet type
    diet_type = data.get('diet_type', '').strip().lower()
    if diet_type:
        lifestyle_parts.append(f"{diet_type} diet")
    
    # Lifestyle other
    lifestyle_other = data.get('lifestyle_other', '').strip()
    if lifestyle_other:
        lifestyle_parts.append(lifestyle_other)
    
    # Check for stress/anxiety keywords in lifestyle_other
    if lifestyle_other:
        lifestyle_lower = lifestyle_other.lower()
        if 'stress' in lifestyle_lower:
            lifestyle_parts.append('stress')
        if 'anxiety' in lifestyle_lower:
            lifestyle_parts.append('anxiety')
    
    lifestyle = ', '.join(lifestyle_parts) if lifestyle_parts else ''
    
    # Get symptoms (if provided, otherwise empty string)
    symptoms = data.get('symptoms', '').strip()
    
    # Create transformed data dict
    transformed_data = data.copy()
    transformed_data['symptoms'] = symptoms
    transformed_data['medical_history'] = medical_history
    transformed_data['family_history'] = family_history
    transformed_data['lifestyle'] = lifestyle
    
    return transformed_data

def analyze_health_with_ai(patient_data):
    """
    Advanced ML-powered health analysis system
    Uses specialized ML modules for Diabetes, Heart Disease, and Thyroid
    Combined with rule-based analysis for comprehensive assessment
    """
    bmi = calculate_bmi(patient_data.get('weight', 0), patient_data.get('height', 0))
    bmi_category = get_bmi_category(bmi) if bmi else 'Unknown'
    
    # Initialize ML Analyzer
    ml_analyzer = MLHealthAnalyzer()
    
    # Prepare patient data for ML modules
    ml_patient_data = {
        'age': int(patient_data.get('age', 0)),
        'gender': patient_data.get('gender', ''),
        'weight': float(patient_data.get('weight', 0)),
        'height': float(patient_data.get('height', 0)),
        'bmi': bmi,
        'symptoms': patient_data.get('symptoms', ''),
        'medical_history': patient_data.get('medical_history', ''),
        'family_history': patient_data.get('family_history', ''),
        'lifestyle': patient_data.get('lifestyle', '')
    }
    
    # Run ML analysis for specialized conditions
    ml_results = ml_analyzer.analyze_all_conditions(ml_patient_data)
    
    age = int(patient_data.get('age', 0))
    gender = patient_data.get('gender', '').lower()
    weight = float(patient_data.get('weight', 0))
    height = float(patient_data.get('height', 0))
    symptoms = str(patient_data.get('symptoms', '')).lower()
    medical_history = str(patient_data.get('medical_history', '')).lower()
    family_history = str(patient_data.get('family_history', '')).lower()
    lifestyle = str(patient_data.get('lifestyle', '')).lower()
    
    # Initialize scoring system
    total_score = 0
    priority_factors = []
    health_risks = {
        "cardiovascular": {"score": 0, "level": "Low", "explanation": ""},
        "metabolic": {"score": 0, "level": "Low", "explanation": ""},
        "respiratory": {"score": 0, "level": "Low", "explanation": ""},
        "other": {"score": 0, "level": "Low", "explanation": ""}
    }
    
    # ========== AGE-BASED SCORING (0-25 points) ==========
    if age < 18:
        total_score += 2
        priority_factors.append("Young Age")
    elif age < 25:
        total_score += 3
    elif age < 30:
        total_score += 5
    elif age < 35:
        total_score += 8
    elif age < 40:
        total_score += 12
        priority_factors.append("Age 35-40")
    elif age < 45:
        total_score += 18
        priority_factors.append("Age 40-45")
    elif age < 50:
        total_score += 22
        priority_factors.append("Age 45-50")
    elif age < 55:
        total_score += 28
        priority_factors.append("Age 50-55")
    elif age < 60:
        total_score += 35
        priority_factors.append("Age 55-60")
    else:
        total_score += 40
        priority_factors.append("Age 60+")
    
    # ========== BMI-BASED SCORING (0-20 points) ==========
    if bmi:
        if bmi < 18.5:  # Underweight
            total_score += 8
            health_risks["metabolic"]["score"] += 5
            health_risks["metabolic"]["level"] = "Moderate"
            health_risks["metabolic"]["explanation"] = "Underweight may indicate nutritional deficiencies"
            priority_factors.append("Underweight")
        elif bmi < 25:  # Normal
            total_score += 2
        elif bmi < 27:  # Overweight
            total_score += 10
            health_risks["cardiovascular"]["score"] += 8
            health_risks["metabolic"]["score"] += 8
            health_risks["cardiovascular"]["level"] = "Moderate"
            health_risks["metabolic"]["level"] = "Moderate"
            health_risks["cardiovascular"]["explanation"] = "Overweight increases cardiovascular risk"
            health_risks["metabolic"]["explanation"] = "Overweight may affect metabolic health"
            priority_factors.append("Overweight")
        elif bmi < 30:  # Overweight (higher)
            total_score += 15
            health_risks["cardiovascular"]["score"] += 12
            health_risks["metabolic"]["score"] += 12
            health_risks["cardiovascular"]["level"] = "Moderate-High"
            health_risks["metabolic"]["level"] = "Moderate-High"
            priority_factors.append("Overweight")
        else:  # Obese
            total_score += 20
            health_risks["cardiovascular"]["score"] += 18
            health_risks["metabolic"]["score"] += 18
            health_risks["cardiovascular"]["level"] = "High"
            health_risks["metabolic"]["level"] = "High"
            health_risks["cardiovascular"]["explanation"] = "Obesity significantly increases cardiovascular disease risk"
            health_risks["metabolic"]["explanation"] = "Obesity is a major risk factor for diabetes and metabolic disorders"
            priority_factors.append("Obesity")
    
    # ========== SYMPTOMS ANALYSIS (0-30 points) ==========
    symptom_keywords = {
        "cardiovascular": ["chest", "heart", "palpitation", "breath", "shortness", "dizziness", "fainting", "swelling", "leg pain"],
        "metabolic": ["thirst", "urination", "hunger", "fatigue", "blurred vision", "slow healing", "numbness", "tingling"],
        "respiratory": ["cough", "wheezing", "asthma", "breathing", "chest tightness", "phlegm"],
        "other": ["headache", "fever", "pain", "weakness", "nausea", "vomiting"]
    }
    
    symptom_score = 0
    detected_risks = []
    
    for risk_type, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in symptoms:
                symptom_score += 5
                health_risks[risk_type]["score"] += 8
                if risk_type not in detected_risks:
                    detected_risks.append(risk_type)
                    priority_factors.append(f"{risk_type.capitalize()} Symptoms")
                break
    
    # Add dynamic field-based scoring
    # Age > 45 cardiac health questions
    if patient_data.get('chest_pain'):
        symptom_score += 5
        health_risks["cardiovascular"]["score"] += 10
        health_risks["cardiovascular"]["level"] = "High"
        priority_factors.append("Chest Pain Reported")
    
    if patient_data.get('shortness_breath'):
        symptom_score += 5
        health_risks["cardiovascular"]["score"] += 8
        health_risks["respiratory"]["score"] += 8
        priority_factors.append("Shortness of Breath Reported")
    
    if patient_data.get('heart_palpitations'):
        symptom_score += 5
        health_risks["cardiovascular"]["score"] += 10
        health_risks["cardiovascular"]["level"] = "High"
        priority_factors.append("Heart Palpitations Reported")
    
    # Age > 45 diabetes screening questions
    if patient_data.get('frequent_thirst'):
        symptom_score += 5
        health_risks["metabolic"]["score"] += 10
        health_risks["metabolic"]["level"] = "High"
        priority_factors.append("Frequent Thirst (Diabetes Risk)")
    
    if patient_data.get('blurred_vision'):
        symptom_score += 5
        health_risks["metabolic"]["score"] += 8
        priority_factors.append("Blurred Vision (Diabetes Risk)")
    
    if patient_data.get('slow_healing'):
        symptom_score += 5
        health_risks["metabolic"]["score"] += 8
        priority_factors.append("Slow Healing (Diabetes Risk)")
    
    if patient_data.get('family_diabetes'):
        health_risks["metabolic"]["score"] += 12
        health_risks["metabolic"]["level"] = "High"
        priority_factors.append("Family History of Diabetes")
    
    # Female-specific health considerations
    if gender == 'female':
        if patient_data.get('pregnant') == 'yes':
            total_score += 15
            priority_factors.append("Pregnancy - Specialized Care Required")
        if patient_data.get('menstrual_regular') == 'irregular' or patient_data.get('menstrual_regular') == 'no':
            total_score += 5
            priority_factors.append("Irregular Menstrual Cycle")
        if patient_data.get('menopause_status') == 'stopped':
            total_score += 10
            health_risks["metabolic"]["score"] += 5
            priority_factors.append("Menopause - Hormonal Health Monitoring")
    
    total_score += min(symptom_score, 30)  # Cap at 30 points
    
    # Update risk levels based on scores
    for risk_type in health_risks:
        if health_risks[risk_type]["score"] >= 15:
            health_risks[risk_type]["level"] = "High"
        elif health_risks[risk_type]["score"] >= 8:
            health_risks[risk_type]["level"] = "Moderate"
        else:
            health_risks[risk_type]["level"] = "Low"
    
    # ========== MEDICAL HISTORY ANALYSIS (0-25 points) ==========
    critical_conditions = ["diabetes", "hypertension", "heart disease", "stroke", "kidney", "liver", "thyroid"]
    moderate_conditions = ["asthma", "arthritis", "cholesterol", "anemia", "migraine"]
    
    medical_score = 0
    for condition in critical_conditions:
        if condition in medical_history:
            medical_score += 12
            total_score += 12
            if "diabetes" in condition or "diabetic" in medical_history:
                health_risks["metabolic"]["score"] += 15
                health_risks["metabolic"]["level"] = "High"
                health_risks["metabolic"]["explanation"] = "Existing diabetes requires comprehensive monitoring"
                priority_factors.append("Diabetes")
            if "heart" in condition or "cardiac" in medical_history:
                health_risks["cardiovascular"]["score"] += 15
                health_risks["cardiovascular"]["level"] = "High"
                health_risks["cardiovascular"]["explanation"] = "Existing heart condition requires specialized cardiac care"
                priority_factors.append("Heart Condition")
            break
    
    for condition in moderate_conditions:
        if condition in medical_history:
            medical_score += 6
            total_score += 6
            priority_factors.append(condition.capitalize())
            break
    
    # ========== FAMILY HISTORY ANALYSIS (0-15 points) ==========
    family_conditions = ["diabetes", "heart", "hypertension", "stroke", "kidney", "liver"]
    family_score = 0
    for condition in family_conditions:
        if condition in family_history:
            family_score += 5
            total_score += 5
            if "diabetes" in condition:
                health_risks["metabolic"]["score"] += 8
                priority_factors.append("Family History: Diabetes")
            if "heart" in condition:
                health_risks["cardiovascular"]["score"] += 8
                priority_factors.append("Family History: Heart Disease")
            break
    
    # ========== LIFESTYLE ANALYSIS (0-10 points) ==========
    if "smok" in lifestyle or "tobacco" in lifestyle:
        total_score += 8
        health_risks["cardiovascular"]["score"] += 10
        health_risks["respiratory"]["score"] += 10
        health_risks["cardiovascular"]["level"] = "Moderate-High" if health_risks["cardiovascular"]["level"] == "Low" else "High"
        health_risks["respiratory"]["level"] = "Moderate-High"
        priority_factors.append("Smoking")
    
    if "alcohol" in lifestyle or "drink" in lifestyle:
        total_score += 5
        health_risks["other"]["score"] += 8
        health_risks["other"]["level"] = "Moderate"
        priority_factors.append("Alcohol Consumption")
    
    if "stress" in lifestyle or "anxiety" in lifestyle:
        total_score += 4
        health_risks["cardiovascular"]["score"] += 5
        priority_factors.append("Stress")
    
    if "exercise" not in lifestyle or "sedentary" in lifestyle:
        total_score += 6
        health_risks["cardiovascular"]["score"] += 6
        health_risks["metabolic"]["score"] += 6
        priority_factors.append("Low Physical Activity")
    
    if "sleep" in lifestyle and ("less" in lifestyle or "insomnia" in lifestyle or "4" in lifestyle or "5" in lifestyle):
        total_score += 4
        health_risks["other"]["score"] += 5
        priority_factors.append("Sleep Issues")
    
    # ========== GENDER-SPECIFIC CONSIDERATIONS ==========
    if gender == "female" and age >= 40:
        total_score += 5
        priority_factors.append("Women's Health Screening")
    if gender == "male" and age >= 45:
        total_score += 5
        priority_factors.append("Men's Health Screening")
    
    # ========== DETERMINE RISK SCORE ==========
    if total_score >= 70:
        risk_score = "Critical"
    elif total_score >= 50:
        risk_score = "High"
    elif total_score >= 30:
        risk_score = "Moderate"
    else:
        risk_score = "Low"
    
    # ========== ENHANCE WITH ML MODULE RESULTS ==========
    # Integrate ML module results for higher accuracy
    diabetes_ml = ml_results.get('diabetes', {})
    heart_ml = ml_results.get('heart_disease', {})
    thyroid_ml = ml_results.get('thyroid', {})
    
    # Update cardiovascular risk with ML results
    if heart_ml.get('risk_score', 0) >= 50:
        health_risks["cardiovascular"]["score"] += 15
        health_risks["cardiovascular"]["level"] = "High"
        health_risks["cardiovascular"]["explanation"] = f"ML Analysis: {heart_ml.get('recommendation', 'High cardiovascular risk detected')}"
        if heart_ml.get('risk_factors'):
            priority_factors.extend([f"Cardiac: {factor}" for factor in heart_ml['risk_factors'][:2]])
    elif heart_ml.get('risk_score', 0) >= 35:
        health_risks["cardiovascular"]["score"] += 10
        if health_risks["cardiovascular"]["level"] == "Low":
            health_risks["cardiovascular"]["level"] = "Moderate"
        health_risks["cardiovascular"]["explanation"] = f"ML Analysis: {heart_ml.get('recommendation', 'Moderate cardiovascular risk')}"
    
    # Update metabolic risk with ML results
    if diabetes_ml.get('risk_score', 0) >= 50:
        health_risks["metabolic"]["score"] += 15
        health_risks["metabolic"]["level"] = "High"
        health_risks["metabolic"]["explanation"] = f"ML Analysis: {diabetes_ml.get('recommendation', 'High diabetes risk detected')}"
        if diabetes_ml.get('risk_factors'):
            priority_factors.extend([f"Diabetes: {factor}" for factor in diabetes_ml['risk_factors'][:2]])
    elif diabetes_ml.get('risk_score', 0) >= 30:
        health_risks["metabolic"]["score"] += 10
        if health_risks["metabolic"]["level"] == "Low":
            health_risks["metabolic"]["level"] = "Moderate"
        health_risks["metabolic"]["explanation"] = f"ML Analysis: {diabetes_ml.get('recommendation', 'Moderate diabetes risk')}"
    
    # Add thyroid risk (new category)
    thyroid_risk_level = thyroid_ml.get('risk_level', 'Low')
    thyroid_risk_score = thyroid_ml.get('risk_score', 0)
    if thyroid_risk_score >= 50:
        health_risks["other"]["score"] += 15
        health_risks["other"]["level"] = "High"
        health_risks["other"]["explanation"] = f"ML Analysis: {thyroid_ml.get('recommendation', 'High thyroid risk detected')}"
        if thyroid_ml.get('risk_factors'):
            priority_factors.extend([f"Thyroid: {factor}" for factor in thyroid_ml['risk_factors'][:2]])
    elif thyroid_risk_score >= 30:
        health_risks["other"]["score"] += 10
        if health_risks["other"]["level"] == "Low":
            health_risks["other"]["level"] = "Moderate"
        health_risks["other"]["explanation"] = f"ML Analysis: {thyroid_ml.get('recommendation', 'Moderate thyroid risk')}"
    
    # ========== RECOMMEND PACKAGES BASED ON SCORE + ML RESULTS ==========
    # Use ML results to refine package recommendations
    diabetes_risk = diabetes_ml.get('risk_score', 0)
    heart_risk = heart_ml.get('risk_score', 0)
    thyroid_risk = thyroid_ml.get('risk_score', 0)
    
    # Adjust total score based on ML results
    ml_adjusted_score = total_score
    if diabetes_risk >= 50:
        ml_adjusted_score += 10
    if heart_risk >= 50:
        ml_adjusted_score += 10
    if thyroid_risk >= 50:
        ml_adjusted_score += 8
    
    # Determine PRIMARY recommended package based on ML analysis and risk factors
    primary_recommended_package = None
    recommended_packages = []
    
    # Gender-specific recommendations (well_women for females)
    if gender == "female" and age >= 35:
        # If very high diabetic risk, consider premium diabetic
        if diabetes_risk >= 70 or (diabetes_risk >= 50 and heart_risk >= 45):
            primary_recommended_package = "premium_diabetic"
            recommended_packages = ["premium_diabetic", "diabetic", "well_women"]
        # If high diabetic risk, consider diabetic package
        elif diabetes_risk >= 50 or "diabetes" in medical_history or "diabetic" in medical_history:
            primary_recommended_package = "diabetic"
            recommended_packages = ["diabetic", "premium_diabetic", "well_women"]
        # For women 35+, consider well_women package if high risk
        elif ml_adjusted_score >= 50 or heart_risk >= 40:
            primary_recommended_package = "well_women"
            recommended_packages = ["well_women", "master"]
        elif ml_adjusted_score >= 30:
            primary_recommended_package = "master"
            recommended_packages = ["master", "well_women"]
    
    # If not gender-specific, determine based on ML analysis
    if not primary_recommended_package:
        if ml_adjusted_score >= 70:  # Critical
            # Highest risk - recommend premium diabetic, cardiac, diabetic, or master
            if diabetes_risk >= 70 or (diabetes_risk >= 50 and heart_risk >= 50):
                primary_recommended_package = "premium_diabetic"
                recommended_packages = ["premium_diabetic", "diabetic", "cardiac"]
            elif diabetes_risk >= 50 and diabetes_risk >= heart_risk:
                primary_recommended_package = "diabetic"
                recommended_packages = ["diabetic", "premium_diabetic", "master"]
            elif heart_risk >= 50:
                primary_recommended_package = "cardiac"
                recommended_packages = ["cardiac", "master"]
            elif diabetes_risk >= 50 or "diabetes" in medical_history or "diabetic" in medical_history:
                primary_recommended_package = "diabetic"
                recommended_packages = ["diabetic", "premium_diabetic", "master"]
            else:
                primary_recommended_package = "master"
                recommended_packages = ["master", "cardiac"]
        elif ml_adjusted_score >= 50:  # High
            # Prioritize based on ML-detected conditions
            if diabetes_risk >= 65:
                primary_recommended_package = "premium_diabetic"
                recommended_packages = ["premium_diabetic", "diabetic", "master"]
            elif diabetes_risk >= 50 or "diabetes" in medical_history or "diabetic" in medical_history:
                primary_recommended_package = "diabetic"
                recommended_packages = ["diabetic", "premium_diabetic", "master"]
            elif heart_risk >= 50:
                primary_recommended_package = "cardiac"
                recommended_packages = ["cardiac", "master"]
            elif thyroid_risk >= 50:
                primary_recommended_package = "master"
                recommended_packages = ["master", "cardiac"]
            elif health_risks["metabolic"]["level"] == "High":
                primary_recommended_package = "diabetic"
                recommended_packages = ["diabetic", "master"]
            elif health_risks["cardiovascular"]["level"] in ["High", "Moderate-High"]:
                primary_recommended_package = "cardiac"
                recommended_packages = ["cardiac", "master"]
            else:
                primary_recommended_package = "master"
                recommended_packages = ["master", "cardiac"]
        elif ml_adjusted_score >= 30:  # Moderate
            # Check if any ML module detected moderate risk
            if diabetes_risk >= 35 or "diabetes" in medical_history or "diabetic" in medical_history:
                primary_recommended_package = "diabetic"
                recommended_packages = ["diabetic", "master"]
            elif heart_risk >= 35 or thyroid_risk >= 30:
                primary_recommended_package = "master"
                recommended_packages = ["master", "basic"]
            else:
                primary_recommended_package = "master"
                recommended_packages = ["master", "basic"]
        else:  # Low
            primary_recommended_package = "basic"
            recommended_packages = ["basic", "master"]
    
    # Ensure primary is always in recommended_packages list
    if primary_recommended_package not in recommended_packages:
        recommended_packages.insert(0, primary_recommended_package)
    
    # ========== GENERATE HEALTH RISK EXPLANATIONS ==========
    if not health_risks["cardiovascular"]["explanation"]:
        if health_risks["cardiovascular"]["level"] == "High":
            health_risks["cardiovascular"]["explanation"] = "High risk factors detected - comprehensive cardiac screening recommended"
        elif health_risks["cardiovascular"]["level"] == "Moderate":
            health_risks["cardiovascular"]["explanation"] = "Moderate cardiovascular risk factors present - standard screening advised"
        else:
            health_risks["cardiovascular"]["explanation"] = "Low cardiovascular risk - routine screening sufficient"
    
    if not health_risks["metabolic"]["explanation"]:
        if health_risks["metabolic"]["level"] == "High":
            health_risks["metabolic"]["explanation"] = "High metabolic risk - comprehensive diabetes and metabolic screening essential"
        elif health_risks["metabolic"]["level"] == "Moderate":
            health_risks["metabolic"]["explanation"] = "Moderate metabolic risk - standard metabolic screening recommended"
        else:
            health_risks["metabolic"]["explanation"] = "Low metabolic risk - basic screening adequate"
    
    if health_risks["respiratory"]["level"] == "Low":
        health_risks["respiratory"]["explanation"] = "No significant respiratory risks identified"
    elif health_risks["respiratory"]["level"] == "Moderate":
        health_risks["respiratory"]["explanation"] = "Some respiratory risk factors present - consider respiratory screening"
    else:
        health_risks["respiratory"]["explanation"] = "Respiratory risk factors detected - specialized screening recommended"
    
    if health_risks["other"]["level"] == "Low":
        health_risks["other"]["explanation"] = "Routine health monitoring advised"
    else:
        health_risks["other"]["explanation"] = "Additional health factors require attention"
    
    # ========== GENERATE REASONING ==========
    reasoning_parts = []
    if age >= 50:
        reasoning_parts.append(f"At {age} years, comprehensive health screening is essential for early detection")
    elif age >= 40:
        reasoning_parts.append(f"At {age} years, preventive health screening is recommended")
    
    if bmi and bmi >= 30:
        reasoning_parts.append("Your BMI indicates obesity, requiring detailed metabolic and cardiovascular assessment")
    elif bmi and bmi >= 25:
        reasoning_parts.append("Your BMI suggests being overweight, warranting thorough health screening")
    elif bmi and bmi < 18.5:
        reasoning_parts.append("Your BMI indicates being underweight, requiring comprehensive evaluation")
    
    if symptoms:
        reasoning_parts.append("Based on your reported symptoms, detailed health assessment is advisable")
    
    if medical_history:
        reasoning_parts.append("Given your medical history, comprehensive monitoring is essential")
    
    if family_history:
        reasoning_parts.append("Family history indicates need for preventive screening")
    
    if not reasoning_parts:
        reasoning_parts.append("A comprehensive health checkup is recommended for maintaining optimal health")
    
    # Enhance reasoning with ML insights
    ml_insights = []
    if diabetes_ml.get('risk_score', 0) >= 50:
        ml_insights.append(f"ML Analysis detected high diabetes risk ({diabetes_ml.get('risk_score', 0)}/100) with {diabetes_ml.get('confidence', 0)*100:.0f}% confidence.")
    if heart_ml.get('risk_score', 0) >= 50:
        ml_insights.append(f"ML Analysis detected high cardiovascular risk ({heart_ml.get('risk_score', 0)}/100) with {heart_ml.get('confidence', 0)*100:.0f}% confidence.")
    if thyroid_ml.get('risk_score', 0) >= 50:
        ml_insights.append(f"ML Analysis detected high thyroid risk ({thyroid_ml.get('risk_score', 0)}/100) with {thyroid_ml.get('confidence', 0)*100:.0f}% confidence.")
    
    if ml_insights:
        reasoning = " ".join(reasoning_parts) + " " + " ".join(ml_insights) + " MAPIMS recommends the appropriate health checkup package based on your individual risk profile and ML-powered analysis."
    else:
        reasoning = " ".join(reasoning_parts) + ". MAPIMS recommends the appropriate health checkup package based on your individual risk profile."
    
    # Remove duplicates from priority factors
    priority_factors = list(dict.fromkeys(priority_factors))
    
    return {
        "risk_score": risk_score,
        "recommended_packages": recommended_packages,
        "primary_recommended_package": primary_recommended_package,
        "health_risks": {
            "cardiovascular": f"{health_risks['cardiovascular']['level']} - {health_risks['cardiovascular']['explanation']}",
            "metabolic": f"{health_risks['metabolic']['level']} - {health_risks['metabolic']['explanation']}",
            "respiratory": f"{health_risks['respiratory']['level']} - {health_risks['respiratory']['explanation']}",
            "other": f"{health_risks['other']['level']} - {health_risks['other']['explanation']}"
        },
        "reasoning": reasoning,
        "priority_factors": priority_factors[:5],  # Top 5 factors
        "total_score": total_score,  # For debugging
        "ml_analysis": {
            "diabetes": {
                "risk_score": diabetes_ml.get('risk_score', 0),
                "risk_level": diabetes_ml.get('risk_level', 'Low'),
                "confidence": diabetes_ml.get('confidence', 0),
                "priority_tests": diabetes_ml.get('priority_tests', [])
            },
            "heart_disease": {
                "risk_score": heart_ml.get('risk_score', 0),
                "risk_level": heart_ml.get('risk_level', 'Low'),
                "confidence": heart_ml.get('confidence', 0),
                "priority_tests": heart_ml.get('priority_tests', [])
            },
            "thyroid": {
                "risk_score": thyroid_ml.get('risk_score', 0),
                "risk_level": thyroid_ml.get('risk_level', 'Low'),
                "confidence": thyroid_ml.get('confidence', 0),
                "priority_tests": thyroid_ml.get('priority_tests', [])
            },
            "overall_confidence": ml_results.get('overall_confidence', 0)
        }
    }, bmi, bmi_category

# ==================== ROUTES ====================

@app.route('/')
def landing():
    """MAPIMS Landing Page"""
    return render_template('landing.html')

@app.route('/assessment')
def assessment():
    """Health Assessment Form"""
    return render_template('assessment.html')

@app.route('/api/submit-assessment', methods=['POST'])
@rate_limit(limit_per_minute=10, limit_per_hour=50)
def submit_assessment():
    """Submit health assessment and get AI analysis"""
    try:
        data = request.json
        
        if not data:
            app.logger.warning("Assessment submission: No data received")
            return jsonify({
                'success': False,
                'error': 'No data received. Please fill in the form and try again.'
            }), 400
        
        # Log received data for debugging (without sensitive info)
        app.logger.info(f"Assessment submission: Name={data.get('name', 'N/A')[:10]}..., Age={data.get('age')}, Gender={data.get('gender')}")
        
        # Validate and sanitize input
        validation_errors = validate_assessment_input(data)
        if validation_errors:
            app.logger.warning(f"Assessment validation failed: {validation_errors}")
            return jsonify({
                'success': False,
                'error': 'Please correct the following errors',
                'details': validation_errors
            }), 400
        
        # Calculate BMI
        bmi = calculate_bmi(data.get('weight', 0), data.get('height', 0))
        bmi_category = get_bmi_category(bmi) if bmi else 'Unknown'
        
        # Get health analysis using advanced rule-based system
        try:
            # Transform structured form data to ML-expected format
            transformed_data = transform_form_data_to_ml_format(data)
            
            # Include dynamic fields in analysis data
            analysis_data = transformed_data.copy()
            # Add dynamic fields to analysis if they exist
            if 'chest_pain' in data:
                analysis_data['chest_pain'] = data.get('chest_pain')
            if 'shortness_breath' in data:
                analysis_data['shortness_breath'] = data.get('shortness_breath')
            if 'heart_palpitations' in data:
                analysis_data['heart_palpitations'] = data.get('heart_palpitations')
            if 'frequent_thirst' in data:
                analysis_data['frequent_thirst'] = data.get('frequent_thirst')
            if 'blurred_vision' in data:
                analysis_data['blurred_vision'] = data.get('blurred_vision')
            if 'slow_healing' in data:
                analysis_data['slow_healing'] = data.get('slow_healing')
            if 'family_diabetes' in data:
                analysis_data['family_diabetes'] = data.get('family_diabetes')
            if 'pregnant' in data:
                analysis_data['pregnant'] = data.get('pregnant')
            if 'menstrual_regular' in data:
                analysis_data['menstrual_regular'] = data.get('menstrual_regular')
            if 'menopause_status' in data:
                analysis_data['menopause_status'] = data.get('menopause_status')
            
            ai_analysis, bmi_calc, bmi_category = analyze_health_with_ai(analysis_data)
        except Exception as analysis_error:
            print(f"Health analysis error: {str(analysis_error)}")
            import traceback
            traceback.print_exc()
            # Use basic fallback analysis
            age = int(data.get('age', 0))
            symptoms_str = str(data.get('symptoms', '')).lower()
            history_str = str(data.get('medical_history', '')).lower()
            if 'diabetes' in history_str or 'diabetic' in history_str or 'sugar' in symptoms_str:
                if age >= 50:
                    risk_score = "Critical"
                    packages = ["premium_diabetic", "diabetic"]
                    primary_package = "premium_diabetic"
                else:
                    risk_score = "Moderate"
                    packages = ["diabetic", "premium_diabetic"]
                    primary_package = "diabetic"
            elif age >= 50:
                risk_score = "High"
                packages = ["master", "cardiac"]
                primary_package = "master"
            elif age >= 40:
                risk_score = "Moderate"
                packages = ["master", "basic"]
                primary_package = "master"
            else:
                risk_score = "Low"
                packages = ["basic", "master"]
                primary_package = "basic"
            
            ai_analysis = {
                "risk_score": risk_score,
                "recommended_packages": packages,
                "primary_recommended_package": primary_package,
                "health_risks": {
                    "cardiovascular": "Standard screening recommended based on your profile",
                    "metabolic": "Routine health monitoring advised",
                    "respiratory": "No significant risks identified",
                    "other": "Preventive health checkup recommended"
                },
                "reasoning": f"Based on your health profile (age {age}), MAPIMS recommends comprehensive health screening to ensure your wellbeing. Our professional healthcare approach ensures you receive the best care.",
                "priority_factors": ["Age", "BMI", "Health Profile"]
            }
            bmi_calc = bmi
        
        # Store in database
        patient_document = {
            'name': data.get('name', ''),
            'age': int(data.get('age', 0)),
            'gender': data.get('gender', ''),
            'weight': float(data.get('weight', 0)),
            'height': float(data.get('height', 0)),
            'bmi': bmi_calc,
            'bmi_category': bmi_category,
            'symptoms': data.get('symptoms', ''),
            'medical_history': data.get('medical_history', ''),
            'family_history': data.get('family_history', ''),
            'lifestyle': data.get('lifestyle', ''),
            'phone': data.get('phone', ''),
            'email': data.get('email', ''),
            'consent': data.get('consent', False),
            'ai_analysis': ai_analysis,
            'submitted_at': datetime.utcnow(),
            'ip_address': request.remote_addr,
            'status': 'assessment_completed'
        }
        
        # Add age > 45 specific fields if present
        if data.get('chest_pain') is not None or data.get('shortness_breath') is not None:
            patient_document['cardiac_health'] = {
                'chest_pain': data.get('chest_pain', False),
                'shortness_breath': data.get('shortness_breath', False),
                'heart_palpitations': data.get('heart_palpitations', False)
            }
            patient_document['diabetes_screening'] = {
                'frequent_thirst': data.get('frequent_thirst', False),
                'blurred_vision': data.get('blurred_vision', False),
                'slow_healing': data.get('slow_healing', False),
                'family_diabetes': data.get('family_diabetes', False)
            }
        
        # Add Women's Health fields if present
        if data.get('pregnant') is not None:
            patient_document['pregnant'] = data.get('pregnant')
            patient_document['menstrual_regular'] = data.get('menstrual_regular', '')
            patient_document['menopause_status'] = data.get('menopause_status', '')
        
        # Add pediatric fields if present
        if data.get('vaccination_up_to_date') is not None:
            patient_document['pediatric_health'] = {
                'vaccination_up_to_date': data.get('vaccination_up_to_date', False),
                'growth_concerns': data.get('growth_concerns', ''),
                'school_performance': data.get('school_performance', ''),
                'allergies': data.get('pediatric_allergies', ''),
                'sleep_patterns_normal': data.get('sleep_patterns_normal', False)
            }
        
        try:
            result = patients_collection.insert_one(patient_document)
            patient_id = str(result.inserted_id)
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            patient_id = None
        
        # Store in session
        session['patient_id'] = patient_id
        session['assessment_data'] = data
        session['ai_analysis'] = ai_analysis
        
        return jsonify({
            'success': True,
            'patient_id': patient_id,
            'ai_analysis': ai_analysis,
            'bmi': bmi_calc,
            'bmi_category': bmi_category
        })
    
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': f'Invalid input data: {str(ve)}'
        }), 400
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Submit assessment error: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/analysis')
def analysis():
    """AI Analysis Results Page"""
    if 'patient_id' not in session:
        return redirect(url_for('assessment'))
    ai_analysis = session.get('ai_analysis', {})
    return render_template('analysis.html', ai_analysis=ai_analysis)

@app.route('/api/get-analysis')
def get_analysis():
    """Get AI analysis data"""
    if 'ai_analysis' not in session:
        return jsonify({'success': False, 'error': 'No analysis found'}), 404
    return jsonify({'success': True, 'analysis': session.get('ai_analysis', {})})

@app.route('/packages')
def packages():
    """Package Recommendation Page"""
    if 'patient_id' not in session:
        return redirect(url_for('assessment'))
    
    ai_analysis = session.get('ai_analysis', {})
    recommended_packages = ai_analysis.get('recommended_packages', ['basic'])
    primary_recommended_package = ai_analysis.get('primary_recommended_package', 'basic')
    
    # Fallback: if primary not set, use first recommended package
    if not primary_recommended_package and recommended_packages:
        primary_recommended_package = recommended_packages[0]
    
    return render_template('packages.html', 
                         packages=PACKAGES,
                         recommended_packages=recommended_packages,
                         primary_recommended_package=primary_recommended_package,
                         addon_tests=ADDON_TESTS)

@app.route('/api/select-package', methods=['POST'])
def select_package():
    """Select package"""
    try:
        data = request.json
        session['selected_package'] = data.get('package_id')
        session['selected_addons'] = []  # Addons section removed
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/booking')
def booking():
    """Booking Page"""
    if 'selected_package' not in session:
        return redirect(url_for('packages'))
    
    package_id = session.get('selected_package')
    package = PACKAGES.get(package_id, PACKAGES['basic'])
    addons = session.get('selected_addons', [])
    
    return render_template('booking.html',
                         package=package,
                         addons=addons,
                         addon_tests=ADDON_TESTS)

@app.route('/api/create-booking', methods=['POST'])
def create_booking():
    """Create booking"""
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Invalid request format'}), 400
            
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400
        
        patient_id = session.get('patient_id')
        
        if not patient_id:
            return jsonify({'success': False, 'error': 'No patient data found. Please complete the assessment first.'}), 400
        
        # Validate required fields
        if not data.get('booking_date'):
            return jsonify({'success': False, 'error': 'Booking date is required'}), 400
        
        # Set default booking time to 8:00 AM if not provided
        booking_time = data.get('booking_time', '08:00')
        
        # Sample type defaults to hospital if not provided
        sample_type = data.get('sample_type', 'hospital')
        
        # Get patient data
        try:
            patient = patients_collection.find_one({'_id': ObjectId(patient_id)})
            if not patient:
                return jsonify({'success': False, 'error': 'Patient record not found'}), 404
        except Exception as e:
            app.logger.error(f"Error finding patient: {str(e)}")
            return jsonify({'success': False, 'error': 'Invalid patient ID'}), 400
        
        # Parse booking date
        try:
            booking_date = datetime.strptime(data.get('booking_date'), '%Y-%m-%d')
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Invalid booking date format'}), 400
        
        booking_document = {
            'patient_id': patient_id,
            'patient_name': patient.get('name', ''),
            'patient_phone': patient.get('phone', ''),
            'patient_email': patient.get('email', ''),
            'package_id': data.get('package_id'),
            'package_name': data.get('package_name'),
            'package_price': data.get('package_price', 0),
            'addons': data.get('addons', []),
            'total_price': data.get('total_price', 0),
            'booking_date': booking_date,
            'booking_time': booking_time,
            'sample_type': sample_type,
            'address': data.get('address', ''),
            'fasting_consent': data.get('fasting_consent', False),
            'payment_status': 'pending',
            'booking_status': 'confirmed',
            'created_at': datetime.utcnow(),
            'booking_reference': f"MAP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'whatsapp_message_status': 'pending',
            'whatsapp_message_sent_at': None
        }
        
        # Insert booking into database
        try:
            result = bookings_collection.insert_one(booking_document)
            booking_id = str(result.inserted_id)
            app.logger.info(f"Booking created: {booking_id} for patient {patient_id}")
        except Exception as e:
            app.logger.error(f"Database error creating booking: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to save booking to database'}), 500
        
        # Update patient status
        try:
            patients_collection.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': {'status': 'booking_completed', 'booking_id': booking_id}}
            )
        except Exception as e:
            app.logger.warning(f"Failed to update patient status: {str(e)}")
            # Don't fail the booking if patient update fails
        
        # Send WhatsApp confirmation message
        whatsapp_status = 'pending'
        whatsapp_sent_at = None
        patient_phone = patient.get('phone', '')
        
        if patient_phone:
            try:
                # Format booking date for message
                booking_date_str = booking_date.strftime('%d-%m-%Y') if isinstance(booking_date, datetime) else str(booking_date)
                
                success, message = whatsapp_service.send_booking_confirmation(
                    phone_number=patient_phone,
                    patient_name=patient.get('name', 'Patient'),
                    booking_reference=booking_document['booking_reference'],
                    booking_date=booking_date_str,
                    booking_time=booking_time,
                    package_name=data.get('package_name', 'Health Checkup Package'),
                    total_price=data.get('total_price', 0)
                )
                
                if success:
                    whatsapp_status = 'sent'
                    whatsapp_sent_at = datetime.utcnow()
                    app.logger.info(f"WhatsApp message sent successfully for booking {booking_id} to {patient_phone}")
                else:
                    whatsapp_status = 'failed'
                    app.logger.warning(f"WhatsApp message failed for booking {booking_id}: {message}")
                
                # Update booking with WhatsApp status
                try:
                    bookings_collection.update_one(
                        {'_id': ObjectId(booking_id)},
                        {'$set': {
                            'whatsapp_message_status': whatsapp_status,
                            'whatsapp_message_sent_at': whatsapp_sent_at
                        }}
                    )
                except Exception as e:
                    app.logger.error(f"Failed to update WhatsApp status in booking: {str(e)}")
                    
            except Exception as e:
                app.logger.error(f"Error sending WhatsApp message for booking {booking_id}: {str(e)}")
                whatsapp_status = 'failed'
                # Update booking with failed status
                try:
                    bookings_collection.update_one(
                        {'_id': ObjectId(booking_id)},
                        {'$set': {'whatsapp_message_status': 'failed'}}
                    )
                except Exception as update_error:
                    app.logger.error(f"Failed to update WhatsApp status after error: {str(update_error)}")
        else:
            app.logger.warning(f"No phone number found for patient {patient_id}, skipping WhatsApp message")
        
        # Store in session
        session['booking_id'] = booking_id
        session['booking_reference'] = booking_document['booking_reference']
        session['booking_package_name'] = booking_document.get('package_name', 'Health Checkup Package')
        session['booking_date'] = booking_date.strftime('%d-%m-%Y') if isinstance(booking_date, datetime) else str(booking_date)
        session['booking_time'] = booking_time
        session['booking_total_price'] = booking_document.get('total_price', 0)
        session['patient_name'] = patient.get('name', 'Valued Patient')
        session['patient_phone'] = patient.get('phone', '')
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'booking_reference': booking_document['booking_reference'],
            'whatsapp_status': whatsapp_status
        })
    
    except Exception as e:
        app.logger.error(f"Error creating booking: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/confirmation')
def confirmation():
    """Booking Confirmation Page"""
    if 'booking_id' not in session:
        return redirect(url_for('landing'))
    
    booking_reference = session.get('booking_reference', '')
    patient_name = session.get('patient_name', 'Valued Patient')
    package_name = session.get('booking_package_name', 'Executive Health Checkup Package')
    booking_date = session.get('booking_date', '')
    booking_time = session.get('booking_time', '08:00 AM')
    total_price = session.get('booking_total_price', 0)
    patient_phone = session.get('patient_phone', '')
    
    return render_template(
        'confirmation.html',
        booking_reference=booking_reference,
        patient_name=patient_name,
        package_name=package_name,
        booking_date=booking_date,
        booking_time=booking_time,
        total_price=total_price,
        patient_phone=patient_phone
    )

# ==================== ADMIN PANEL ====================

def admin_required(f):
    """Legacy decorator - use require_admin from security_config"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated') and not session.get('admin_logged_in'):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
def admin_login():
    """Admin Login Page"""
    return render_template('admin/login.html')

@app.route('/admin/authenticate', methods=['POST'])
@rate_limit(limit_per_minute=5, limit_per_hour=20)
def admin_authenticate():
    """Admin authentication with secure password verification"""
    data = request.json
    username = SecurityConfig.sanitize_input(data.get('username', ''), 50)
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    # Check for brute force attempts
    identifier = request.remote_addr
    if 'X-Forwarded-For' in request.headers:
        identifier = request.headers['X-Forwarded-For'].split(',')[0].strip()
    
    # Get admin user from database
    admin_user = admin_collection.find_one({'username': username})
    
    if admin_user:
        # Verify password hash
        if SecurityConfig.verify_password(password, admin_user.get('password_hash', '')):
            session['admin_authenticated'] = True
            session['admin_username'] = username
            session.permanent = True
            return jsonify({'success': True})
    
    # Log failed attempt
    app.logger.warning(f"Failed admin login attempt for username: {username} from {identifier}")
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin Dashboard"""
    # Get date filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build date filter
    date_filter = {}
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter['created_at'] = {'$gte': start_dt}
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'created_at' in date_filter:
                date_filter['created_at']['$lt'] = end_dt
            else:
                date_filter['created_at'] = {'$lt': end_dt}
        except ValueError:
            pass
    
    # Get statistics (use date_filter for consistency with the table)
    # Note: total_patients remains unfiltered as it represents all-time patient count
    # Bookings metrics use date_filter to match the filtered table below
    total_patients = patients_collection.count_documents({})
    total_bookings = bookings_collection.count_documents(date_filter if date_filter else {})
    confirmed_filter = date_filter.copy() if date_filter else {}
    confirmed_filter['booking_status'] = 'confirmed'
    confirmed_bookings = bookings_collection.count_documents(confirmed_filter)
    
    # Get recent bookings with pagination
    query = bookings_collection.find(date_filter).sort('created_at', -1)
    total_bookings_count = bookings_collection.count_documents(date_filter)
    skip = (page - 1) * per_page
    recent_bookings = list(query.skip(skip).limit(per_page))
    total_pages = (total_bookings_count + per_page - 1) // per_page
    
    # Get top packages
    pipeline = [
        {'$match': {'package_id': {'$ne': None, '$exists': True}}},
        {'$group': {'_id': '$package_id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    top_packages = list(bookings_collection.aggregate(pipeline))
    
    # Get top symptoms
    pipeline = [
        {'$match': {'$and': [
            {'symptoms': {'$ne': None}},
            {'symptoms': {'$ne': ''}},
            {'symptoms': {'$exists': True}}
        ]}},
        {'$group': {'_id': '$symptoms', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    top_symptoms = list(patients_collection.aggregate(pipeline))
    
    return render_template('admin/dashboard.html',
                         total_patients=total_patients,
                         total_bookings=total_bookings,
                         confirmed_bookings=confirmed_bookings,
                         recent_bookings=recent_bookings,
                         top_packages=top_packages,
                         top_symptoms=top_symptoms,
                         packages=PACKAGES,
                         start_date=start_date,
                         end_date=end_date,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_bookings_count=total_bookings_count)

@app.route('/admin/leads')
@admin_required
def admin_leads():
    """View all leads/patients"""
    # Get date filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build date filter
    date_filter = {}
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter['submitted_at'] = {'$gte': start_dt}
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'submitted_at' in date_filter:
                date_filter['submitted_at']['$lt'] = end_dt
            else:
                date_filter['submitted_at'] = {'$lt': end_dt}
        except ValueError:
            pass
    
    # Get patients with pagination
    query = patients_collection.find(date_filter).sort('submitted_at', -1)
    total_patients_count = patients_collection.count_documents(date_filter)
    skip = (page - 1) * per_page
    patients = list(query.skip(skip).limit(per_page))
    total_pages = (total_patients_count + per_page - 1) // per_page
    
    return render_template('admin/leads.html', 
                         patients=patients,
                         start_date=start_date,
                         end_date=end_date,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_patients_count=total_patients_count)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """View all bookings"""
    # Get date filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build date filter
    date_filter = {}
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter['created_at'] = {'$gte': start_dt}
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'created_at' in date_filter:
                date_filter['created_at']['$lt'] = end_dt
            else:
                date_filter['created_at'] = {'$lt': end_dt}
        except ValueError:
            pass
    
    # Get bookings with pagination
    query = bookings_collection.find(date_filter).sort('created_at', -1)
    total_bookings_count = bookings_collection.count_documents(date_filter)
    skip = (page - 1) * per_page
    bookings = list(query.skip(skip).limit(per_page))
    total_pages = (total_bookings_count + per_page - 1) // per_page
    
    return render_template('admin/bookings.html', 
                         bookings=bookings, 
                         packages=PACKAGES,
                         start_date=start_date,
                         end_date=end_date,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         total_bookings_count=total_bookings_count)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout - securely clears all session data"""
    session.clear()  # Clear all session data for security
    return redirect(url_for('admin_login'))

@app.route('/admin/export/leads')
@admin_required
def export_leads():
    """Export leads/patients to Excel"""
    # Get date filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    hide_headers = request.args.get('hide_headers', '0') == '1'
    columns_param = request.args.get('columns', '')
    
    # Parse selected columns
    selected_columns = columns_param.split(',') if columns_param else []
    
    # Define all available columns with their mappings
    all_columns = {
        'sno': {'header': 'S.No', 'index': 0},
        'name': {'header': 'Name', 'index': 1},
        'age': {'header': 'Age', 'index': 2},
        'gender': {'header': 'Gender', 'index': 3},
        'phone': {'header': 'Phone', 'index': 4},
        'email': {'header': 'Email', 'index': 5},
        'bmi': {'header': 'BMI', 'index': 6},
        'bmi_category': {'header': 'BMI Category', 'index': 7},
        'risk_score': {'header': 'Risk Score', 'index': 8},
        'submitted_date': {'header': 'Submitted Date', 'index': 9},
        'status': {'header': 'Status', 'index': 10}
    }
    
    # If no columns selected, use all columns
    if not selected_columns:
        selected_columns = list(all_columns.keys())
    
    # Filter to only valid columns
    selected_columns = [col for col in selected_columns if col in all_columns]
    
    # Sort columns by their original index to maintain order
    selected_columns = sorted(selected_columns, key=lambda x: all_columns[x]['index'])
    
    # Build date filter (same logic as admin_leads)
    date_filter = {}
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter['submitted_at'] = {'$gte': start_dt}
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'submitted_at' in date_filter:
                date_filter['submitted_at']['$lt'] = end_dt
            else:
                date_filter['submitted_at'] = {'$lt': end_dt}
        except ValueError:
            pass
    
    # Get all patients matching the filter (no pagination for export)
    patients = list(patients_collection.find(date_filter).sort('submitted_at', -1))
    
    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    
    # Define header style
    header_fill = PatternFill(start_color="E31837", end_color="E31837", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    # Determine starting row (2 if headers are hidden, 1 if shown)
    start_row = 2 if hide_headers else 1
    header_row = 1
    
    # Write headers
    for col_num, col_key in enumerate(selected_columns, 1):
        header = all_columns[col_key]['header']
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Hide the header row if requested
    if hide_headers:
        ws.row_dimensions[1].hidden = True
    
    # Write data
    for row_num, patient in enumerate(patients, start_row):
        for col_num, col_key in enumerate(selected_columns, 1):
            value = 'N/A'
            if col_key == 'sno':
                value = row_num - (start_row - 1)
            elif col_key == 'name':
                value = patient.get('name', 'N/A')
            elif col_key == 'age':
                value = patient.get('age', 'N/A')
            elif col_key == 'gender':
                value = patient.get('gender', 'N/A')
            elif col_key == 'phone':
                value = patient.get('phone', 'N/A')
            elif col_key == 'email':
                value = patient.get('email', 'N/A')
            elif col_key == 'bmi':
                value = patient.get('bmi', 'N/A')
            elif col_key == 'bmi_category':
                value = patient.get('bmi_category', 'N/A')
            elif col_key == 'risk_score':
                value = patient.get('ai_analysis', {}).get('risk_score', 'N/A') if patient.get('ai_analysis') else 'N/A'
            elif col_key == 'submitted_date':
                submitted_at = patient.get('submitted_at')
                value = submitted_at.strftime('%Y-%m-%d %H:%M') if submitted_at else 'N/A'
            elif col_key == 'status':
                value = patient.get('status', 'N/A')
            
            ws.cell(row=row_num, column=col_num, value=value)
    
    # Auto-adjust column widths
    for col_num in range(1, len(selected_columns) + 1):
        max_length = 0
        column_letter = ws.cell(row=start_row, column=col_num).column_letter
        for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            for cell in row:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    # Generate filename with date range
    filename = 'leads'
    if start_date and end_date:
        filename += f'_{start_date}_to_{end_date}'
    elif start_date:
        filename += f'_from_{start_date}'
    elif end_date:
        filename += f'_until_{end_date}'
    filename += '.xlsx'
    
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

@app.route('/admin/export/bookings')
@admin_required
def export_bookings():
    """Export bookings to Excel"""
    # Get date filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    hide_headers = request.args.get('hide_headers', '0') == '1'
    columns_param = request.args.get('columns', '')
    
    # Parse selected columns
    selected_columns = columns_param.split(',') if columns_param else []
    
    # Define all available columns with their mappings
    all_columns = {
        'sno': {'header': 'S.No', 'index': 0},
        'reference': {'header': 'Reference', 'index': 1},
        'patient_name': {'header': 'Patient Name', 'index': 2},
        'patient_phone': {'header': 'Patient Phone', 'index': 3},
        'package': {'header': 'Package', 'index': 4},
        'total_amount': {'header': 'Total Amount (₹)', 'index': 5},
        'booking_date': {'header': 'Booking Date', 'index': 6},
        'time': {'header': 'Time', 'index': 7},
        'sample_type': {'header': 'Sample Type', 'index': 8},
        'payment_status': {'header': 'Payment Status', 'index': 9},
        'booking_status': {'header': 'Booking Status', 'index': 10},
        'created_date': {'header': 'Created Date', 'index': 11}
    }
    
    # If no columns selected, use all columns
    if not selected_columns:
        selected_columns = list(all_columns.keys())
    
    # Filter to only valid columns
    selected_columns = [col for col in selected_columns if col in all_columns]
    
    # Sort columns by their original index to maintain order
    selected_columns = sorted(selected_columns, key=lambda x: all_columns[x]['index'])
    
    # Build date filter (same logic as admin_bookings)
    date_filter = {}
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            date_filter['created_at'] = {'$gte': start_dt}
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'created_at' in date_filter:
                date_filter['created_at']['$lt'] = end_dt
            else:
                date_filter['created_at'] = {'$lt': end_dt}
        except ValueError:
            pass
    
    # Get all bookings matching the filter (no pagination for export)
    bookings = list(bookings_collection.find(date_filter).sort('created_at', -1))
    
    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Bookings"
    
    # Define header style
    header_fill = PatternFill(start_color="E31837", end_color="E31837", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    # Determine starting row (2 if headers are hidden, 1 if shown)
    start_row = 2 if hide_headers else 1
    header_row = 1
    
    # Write headers
    for col_num, col_key in enumerate(selected_columns, 1):
        header = all_columns[col_key]['header']
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Hide the header row if requested
    if hide_headers:
        ws.row_dimensions[1].hidden = True
    
    # Write data
    for row_num, booking in enumerate(bookings, start_row):
        for col_num, col_key in enumerate(selected_columns, 1):
            value = 'N/A'
            if col_key == 'sno':
                value = row_num - (start_row - 1)
            elif col_key == 'reference':
                value = booking.get('booking_reference', 'N/A')
            elif col_key == 'patient_name':
                value = booking.get('patient_name', 'N/A')
            elif col_key == 'patient_phone':
                value = booking.get('patient_phone', 'N/A')
            elif col_key == 'package':
                value = booking.get('package_name', 'N/A')
            elif col_key == 'total_amount':
                value = booking.get('total_price', 0)
            elif col_key == 'booking_date':
                booking_date = booking.get('booking_date')
                value = booking_date.strftime('%Y-%m-%d') if booking_date else 'N/A'
            elif col_key == 'time':
                value = booking.get('booking_time', 'N/A')
            elif col_key == 'sample_type':
                value = booking.get('sample_type', 'N/A')
            elif col_key == 'payment_status':
                value = booking.get('payment_status', 'N/A')
            elif col_key == 'booking_status':
                value = booking.get('booking_status', 'N/A')
            elif col_key == 'created_date':
                created_at = booking.get('created_at')
                value = created_at.strftime('%Y-%m-%d %H:%M') if created_at else 'N/A'
            
            ws.cell(row=row_num, column=col_num, value=value)
    
    # Auto-adjust column widths
    for col_num in range(1, len(selected_columns) + 1):
        max_length = 0
        column_letter = ws.cell(row=start_row, column=col_num).column_letter
        for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            for cell in row:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    # Generate filename with date range
    filename = 'bookings'
    if start_date and end_date:
        filename += f'_{start_date}_to_{end_date}'
    elif start_date:
        filename += f'_from_{start_date}'
    elif end_date:
        filename += f'_until_{end_date}'
    filename += '.xlsx'
    
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

# ==================== API ENDPOINTS ====================

@app.route('/api/packages')
def api_packages():
    """Get all packages"""
    return jsonify(PACKAGES)

@app.route('/api/addons')
def api_addons():
    """Get all add-on tests"""
    return jsonify(ADDON_TESTS)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    # Treat as development unless explicitly set to production
    env = os.environ.get('FLASK_ENV', 'development').lower()
    debug = env == 'development'

    # Auto reload templates + auto restart server on file changes
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    )
