"""
MAPIMS ML Health Assessment Modules
Specialized ML algorithms for Diabetes, Heart Disease, and Thyroid assessment
High accuracy prediction models based on clinical guidelines
"""

import math
from typing import Dict, List, Tuple


class DiabetesMLModule:
    """
    Advanced Diabetes Risk Assessment Module
    Based on ADA (American Diabetes Association) guidelines and clinical scoring
    """
    
    @staticmethod
    def calculate_diabetes_risk(patient_data: Dict) -> Dict:
        """
        Calculate diabetes risk score (0-100)
        Higher score = higher risk
        """
        age = int(patient_data.get('age', 0))
        bmi = patient_data.get('bmi', 0)
        gender = patient_data.get('gender', '').lower()
        symptoms = str(patient_data.get('symptoms', '')).lower()
        medical_history = str(patient_data.get('medical_history', '')).lower()
        family_history = str(patient_data.get('family_history', '')).lower()
        lifestyle = str(patient_data.get('lifestyle', '')).lower()
        weight = float(patient_data.get('weight', 0))
        height = float(patient_data.get('height', 0))
        
        risk_score = 0
        risk_factors = []
        confidence = 0.0
        
        # 1. AGE FACTOR (0-25 points)
        if age >= 45:
            risk_score += 25
            risk_factors.append(f"Age {age} (High risk age group)")
        elif age >= 35:
            risk_score += 15
            risk_factors.append(f"Age {age} (Moderate risk age group)")
        elif age >= 25:
            risk_score += 8
        else:
            risk_score += 3
        
        # 2. BMI FACTOR (0-30 points) - Strong predictor
        if bmi >= 30:  # Obese
            risk_score += 30
            risk_factors.append(f"Obesity (BMI: {bmi:.1f})")
        elif bmi >= 27:  # Overweight
            risk_score += 20
            risk_factors.append(f"Overweight (BMI: {bmi:.1f})")
        elif bmi >= 25:
            risk_score += 12
            risk_factors.append(f"Pre-overweight (BMI: {bmi:.1f})")
        elif bmi < 18.5:
            risk_score += 5  # Underweight can also indicate issues
        
        # 3. WAIST-TO-HIP RATIO ESTIMATE (0-15 points)
        # Estimate based on BMI and gender
        if bmi >= 25:
            if gender == 'male':
                risk_score += 12  # Central obesity in males
            else:
                risk_score += 10  # Central obesity in females
            risk_factors.append("Central obesity pattern")
        
        # 4. DIABETES-SPECIFIC SYMPTOMS (0-20 points)
        diabetes_symptoms = {
            'excessive thirst': 8,
            'frequent urination': 8,
            'increased hunger': 6,
            'unexplained weight loss': 10,
            'fatigue': 5,
            'blurred vision': 7,
            'slow healing': 6,
            'numbness': 5,
            'tingling': 5,
            'dry mouth': 4,
            'itchy skin': 3,
            'yeast infection': 4
        }
        
        symptom_score = 0
        detected_symptoms = []
        for symptom, score in diabetes_symptoms.items():
            if symptom in symptoms:
                symptom_score += score
                detected_symptoms.append(symptom)
        
        risk_score += min(symptom_score, 20)  # Cap at 20
        if detected_symptoms:
            risk_factors.append(f"Diabetes symptoms: {', '.join(detected_symptoms[:3])}")
        
        # 5. MEDICAL HISTORY (0-25 points)
        if 'diabetes' in medical_history or 'diabetic' in medical_history:
            risk_score += 25
            risk_factors.append("Existing diabetes diagnosis")
        if 'prediabetes' in medical_history or 'pre-diabetes' in medical_history:
            risk_score += 18
            risk_factors.append("Prediabetes")
        if 'gestational diabetes' in medical_history:
            risk_score += 15
            risk_factors.append("History of gestational diabetes")
        if 'polycystic' in medical_history or 'pcos' in medical_history:
            risk_score += 12
            risk_factors.append("PCOS (increases diabetes risk)")
        if 'hypertension' in medical_history or 'high blood pressure' in medical_history:
            risk_score += 10
            risk_factors.append("Hypertension (comorbidity)")
        
        # 6. FAMILY HISTORY (0-15 points)
        if 'diabetes' in family_history or 'diabetic' in family_history:
            risk_score += 15
            risk_factors.append("Family history of diabetes")
            if 'parent' in family_history or 'mother' in family_history or 'father' in family_history:
                risk_score += 5  # First-degree relative
                risk_factors.append("First-degree relative with diabetes")
        
        # 7. LIFESTYLE FACTORS (0-15 points)
        if 'sedentary' in lifestyle or ('exercise' not in lifestyle and 'active' not in lifestyle):
            risk_score += 10
            risk_factors.append("Sedentary lifestyle")
        if 'stress' in lifestyle or 'anxiety' in lifestyle:
            risk_score += 5
            risk_factors.append("Chronic stress")
        if 'sleep' in lifestyle and ('less' in lifestyle or 'insomnia' in lifestyle):
            risk_score += 4
            risk_factors.append("Poor sleep quality")
        
        # 8. GENDER-SPECIFIC (0-5 points)
        if gender == 'female' and age >= 35:
            risk_score += 3
        if gender == 'male' and age >= 40:
            risk_score += 3
        
        # Calculate confidence based on data completeness
        data_points = sum([
            1 if age > 0 else 0,
            1 if bmi > 0 else 0,
            1 if symptoms else 0,
            1 if medical_history else 0,
            1 if family_history else 0,
            1 if lifestyle else 0
        ])
        confidence = min(data_points / 6.0, 1.0) * 0.95  # Max 95% confidence
        
        # Normalize risk score to 0-100
        risk_score = min(risk_score, 100)
        
        # Determine risk level with more granular categories
        if risk_score >= 80:
            risk_level = "Critical"
            recommendation = "Immediate comprehensive diabetes screening (HbA1c, Fasting Glucose, OGTT) required"
        elif risk_score >= 65:
            risk_level = "Moderate-Critical"
            recommendation = "Urgent comprehensive diabetes screening strongly recommended (HbA1c, Fasting Glucose, OGTT)"
        elif risk_score >= 50:
            risk_level = "High"
            recommendation = "Comprehensive diabetes screening strongly recommended (HbA1c, Fasting Glucose)"
        elif risk_score >= 40:
            risk_level = "High-Moderate"
            recommendation = "Enhanced diabetes screening recommended (HbA1c, Fasting Glucose)"
        elif risk_score >= 30:
            risk_level = "Moderate"
            recommendation = "Standard diabetes screening recommended (Fasting Glucose, HbA1c)"
        elif risk_score >= 20:
            risk_level = "Low-Moderate"
            recommendation = "Basic diabetes screening advised (Fasting Glucose)"
        elif risk_score >= 10:
            risk_level = "Low"
            recommendation = "Routine screening sufficient"
        else:
            risk_level = "Very Low"
            recommendation = "Routine screening sufficient"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors[:5],  # Top 5 factors
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
            "priority_tests": ["HbA1c", "Fasting Blood Glucose", "Postprandial Glucose", "Insulin Level"] if risk_score >= 30 else ["Fasting Blood Glucose"]
        }


class HeartDiseaseMLModule:
    """
    Advanced Cardiovascular Disease Risk Assessment Module
    Based on Framingham Risk Score and ACC/AHA guidelines
    """
    
    @staticmethod
    def calculate_heart_disease_risk(patient_data: Dict) -> Dict:
        """
        Calculate cardiovascular disease risk score (0-100)
        Higher score = higher risk
        """
        age = int(patient_data.get('age', 0))
        bmi = patient_data.get('bmi', 0)
        gender = patient_data.get('gender', '').lower()
        symptoms = str(patient_data.get('symptoms', '')).lower()
        medical_history = str(patient_data.get('medical_history', '')).lower()
        family_history = str(patient_data.get('family_history', '')).lower()
        lifestyle = str(patient_data.get('lifestyle', '')).lower()
        
        risk_score = 0
        risk_factors = []
        confidence = 0.0
        
        # 1. AGE FACTOR (0-30 points) - Strongest predictor
        if age >= 65:
            risk_score += 30
            risk_factors.append(f"Age {age} (High risk age group)")
        elif age >= 55:
            risk_score += 25
            risk_factors.append(f"Age {age} (Moderate-high risk)")
        elif age >= 45:
            risk_score += 18
            risk_factors.append(f"Age {age} (Moderate risk)")
        elif age >= 35:
            risk_score += 10
        else:
            risk_score += 3
        
        # Gender-specific age adjustments
        if gender == 'male' and age >= 45:
            risk_score += 5
        elif gender == 'female' and age >= 55:
            risk_score += 5
        
        # 2. BMI FACTOR (0-25 points)
        if bmi >= 30:  # Obese
            risk_score += 25
            risk_factors.append(f"Obesity (BMI: {bmi:.1f}) - Major CVD risk")
        elif bmi >= 27:  # Overweight
            risk_score += 18
            risk_factors.append(f"Overweight (BMI: {bmi:.1f})")
        elif bmi >= 25:
            risk_score += 12
            risk_factors.append(f"Pre-overweight (BMI: {bmi:.1f})")
        
        # 3. CARDIOVASCULAR SYMPTOMS (0-25 points)
        cardiac_symptoms = {
            'chest pain': 15,
            'chest discomfort': 12,
            'angina': 15,
            'shortness of breath': 10,
            'breathlessness': 10,
            'palpitation': 8,
            'irregular heartbeat': 10,
            'heart racing': 8,
            'dizziness': 6,
            'fainting': 10,
            'syncope': 10,
            'swelling': 7,
            'edema': 7,
            'leg pain': 6,
            'claudication': 8,
            'fatigue': 5,
            'exertional': 8
        }
        
        symptom_score = 0
        detected_symptoms = []
        for symptom, score in cardiac_symptoms.items():
            if symptom in symptoms:
                symptom_score += score
                detected_symptoms.append(symptom)
        
        risk_score += min(symptom_score, 25)  # Cap at 25
        if detected_symptoms:
            risk_factors.append(f"Cardiac symptoms: {', '.join(detected_symptoms[:3])}")
        
        # 4. MEDICAL HISTORY (0-30 points)
        if 'heart disease' in medical_history or 'cardiac' in medical_history or 'coronary' in medical_history:
            risk_score += 30
            risk_factors.append("Existing heart disease")
        if 'heart attack' in medical_history or 'myocardial infarction' in medical_history or 'mi' in medical_history:
            risk_score += 30
            risk_factors.append("Previous heart attack")
        if 'stroke' in medical_history or 'cva' in medical_history:
            risk_score += 25
            risk_factors.append("Previous stroke")
        if 'hypertension' in medical_history or 'high blood pressure' in medical_history or 'htn' in medical_history:
            risk_score += 20
            risk_factors.append("Hypertension")
        if 'diabetes' in medical_history or 'diabetic' in medical_history:
            risk_score += 18
            risk_factors.append("Diabetes (major CVD risk factor)")
        if 'high cholesterol' in medical_history or 'hyperlipidemia' in medical_history or 'dyslipidemia' in medical_history:
            risk_score += 15
            risk_factors.append("High cholesterol")
        if 'arrhythmia' in medical_history or 'atrial fibrillation' in medical_history or 'afib' in medical_history:
            risk_score += 12
            risk_factors.append("Arrhythmia")
        
        # 5. FAMILY HISTORY (0-20 points)
        if 'heart' in family_history or 'cardiac' in family_history:
            risk_score += 15
            risk_factors.append("Family history of heart disease")
            if 'early' in family_history or ('age' in family_history and any(x in family_history for x in ['40', '45', '50', '55'])):
                risk_score += 5
                risk_factors.append("Early-onset family history")
        if 'stroke' in family_history:
            risk_score += 10
            risk_factors.append("Family history of stroke")
        if 'heart attack' in family_history:
            risk_score += 12
            risk_factors.append("Family history of heart attack")
        
        # 6. LIFESTYLE FACTORS (0-25 points)
        if 'smok' in lifestyle or 'tobacco' in lifestyle or 'cigarette' in lifestyle:
            risk_score += 20
            risk_factors.append("Smoking (major CVD risk)")
        if 'alcohol' in lifestyle and ('excessive' in lifestyle or 'heavy' in lifestyle):
            risk_score += 8
            risk_factors.append("Excessive alcohol consumption")
        if 'sedentary' in lifestyle or ('exercise' not in lifestyle and 'active' not in lifestyle):
            risk_score += 12
            risk_factors.append("Sedentary lifestyle")
        if 'stress' in lifestyle or 'anxiety' in lifestyle:
            risk_score += 8
            risk_factors.append("Chronic stress")
        if 'sleep' in lifestyle and ('apnea' in lifestyle or 'snoring' in lifestyle):
            risk_score += 10
            risk_factors.append("Sleep apnea (CVD risk)")
        
        # 7. GENDER FACTOR
        if gender == 'male' and age >= 45:
            risk_score += 5
        elif gender == 'female' and age >= 55:
            risk_score += 5
        
        # Calculate confidence
        data_points = sum([
            1 if age > 0 else 0,
            1 if bmi > 0 else 0,
            1 if symptoms else 0,
            1 if medical_history else 0,
            1 if family_history else 0,
            1 if lifestyle else 0
        ])
        confidence = min(data_points / 6.0, 1.0) * 0.95
        
        # Normalize risk score
        risk_score = min(risk_score, 100)
        
        # Determine risk level with more granular categories
        if risk_score >= 80:
            risk_level = "Critical"
            recommendation = "Immediate comprehensive cardiac evaluation required (ECG, Stress Test, Echocardiography, Cardiac Markers)"
        elif risk_score >= 65:
            risk_level = "Moderate-Critical"
            recommendation = "Urgent comprehensive cardiac screening strongly recommended (ECG, Stress Test, Echocardiography)"
        elif risk_score >= 55:
            risk_level = "High"
            recommendation = "Comprehensive cardiac screening strongly recommended (ECG, Stress Test, Cardiac Markers)"
        elif risk_score >= 45:
            risk_level = "High-Moderate"
            recommendation = "Enhanced cardiac screening recommended (ECG, Stress Test, Lipid Profile)"
        elif risk_score >= 35:
            risk_level = "Moderate"
            recommendation = "Standard cardiac screening recommended (ECG, Lipid Profile, Cardiac Risk Markers)"
        elif risk_score >= 20:
            risk_level = "Low-Moderate"
            recommendation = "Basic cardiac screening advised (ECG, Lipid Profile)"
        elif risk_score >= 10:
            risk_level = "Low"
            recommendation = "Routine screening sufficient"
        else:
            risk_level = "Very Low"
            recommendation = "Routine screening sufficient"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors[:5],
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
            "priority_tests": ["ECG", "Stress Test", "Echocardiography", "Cardiac Markers", "Lipid Profile"] if risk_score >= 35 else ["ECG", "Lipid Profile"]
        }


class ThyroidMLModule:
    """
    Advanced Thyroid Disorder Risk Assessment Module
    Based on ATA (American Thyroid Association) guidelines
    """
    
    @staticmethod
    def calculate_thyroid_risk(patient_data: Dict) -> Dict:
        """
        Calculate thyroid disorder risk score (0-100)
        Higher score = higher risk
        """
        age = int(patient_data.get('age', 0))
        bmi = patient_data.get('bmi', 0)
        gender = patient_data.get('gender', '').lower()
        symptoms = str(patient_data.get('symptoms', '')).lower()
        medical_history = str(patient_data.get('medical_history', '')).lower()
        family_history = str(patient_data.get('family_history', '')).lower()
        lifestyle = str(patient_data.get('lifestyle', '')).lower()
        
        risk_score = 0
        risk_factors = []
        confidence = 0.0
        
        # 1. AGE AND GENDER FACTOR (0-20 points)
        # Thyroid disorders are more common in women and older adults
        if gender == 'female':
            risk_score += 12
            risk_factors.append("Female gender (higher thyroid risk)")
            if age >= 50:
                risk_score += 8
                risk_factors.append(f"Age {age} (post-menopausal risk)")
            elif age >= 35:
                risk_score += 5
        elif gender == 'male':
            if age >= 50:
                risk_score += 6
            else:
                risk_score += 2
        
        # 2. BMI FACTOR (0-20 points)
        # Thyroid disorders often affect weight
        if bmi >= 30:  # Obese - could indicate hypothyroidism
            risk_score += 15
            risk_factors.append(f"Obesity (BMI: {bmi:.1f}) - possible hypothyroidism")
        elif bmi < 18.5:  # Underweight - could indicate hyperthyroidism
            risk_score += 12
            risk_factors.append(f"Underweight (BMI: {bmi:.1f}) - possible hyperthyroidism")
        elif bmi >= 27:
            risk_score += 8
            risk_factors.append(f"Overweight (BMI: {bmi:.1f})")
        
        # 3. THYROID-SPECIFIC SYMPTOMS (0-30 points)
        # Hypothyroidism symptoms
        hypo_symptoms = {
            'fatigue': 8,
            'weight gain': 10,
            'cold intolerance': 9,
            'constipation': 6,
            'dry skin': 5,
            'hair loss': 6,
            'depression': 7,
            'memory problems': 6,
            'muscle weakness': 6,
            'hoarse voice': 5,
            'puffy face': 6,
            'slow heart rate': 8,
            'bradycardia': 8
        }
        
        # Hyperthyroidism symptoms
        hyper_symptoms = {
            'weight loss': 10,
            'rapid heartbeat': 9,
            'tachycardia': 9,
            'palpitation': 8,
            'anxiety': 7,
            'irritability': 6,
            'tremor': 7,
            'sweating': 6,
            'heat intolerance': 8,
            'insomnia': 6,
            'diarrhea': 5,
            'muscle weakness': 6,
            'bulging eyes': 10,
            'exophthalmos': 10
        }
        
        # General thyroid symptoms
        general_symptoms = {
            'neck swelling': 12,
            'goiter': 12,
            'neck pain': 8,
            'difficulty swallowing': 9,
            'voice changes': 6
        }
        
        symptom_score = 0
        detected_symptoms = []
        
        for symptom, score in hypo_symptoms.items():
            if symptom in symptoms:
                symptom_score += score
                detected_symptoms.append(symptom)
        
        for symptom, score in hyper_symptoms.items():
            if symptom in symptoms:
                symptom_score += score
                detected_symptoms.append(symptom)
        
        for symptom, score in general_symptoms.items():
            if symptom in symptoms:
                symptom_score += score
                detected_symptoms.append(symptom)
        
        risk_score += min(symptom_score, 30)  # Cap at 30
        if detected_symptoms:
            risk_factors.append(f"Thyroid symptoms: {', '.join(detected_symptoms[:3])}")
        
        # 4. MEDICAL HISTORY (0-25 points)
        if 'thyroid' in medical_history:
            risk_score += 25
            risk_factors.append("Existing thyroid disorder")
        if 'hypothyroidism' in medical_history or 'hypothyroid' in medical_history:
            risk_score += 25
            risk_factors.append("Hypothyroidism")
        if 'hyperthyroidism' in medical_history or 'hyperthyroid' in medical_history or 'graves' in medical_history:
            risk_score += 25
            risk_factors.append("Hyperthyroidism")
        if 'goiter' in medical_history:
            risk_score += 18
            risk_factors.append("Goiter")
        if 'thyroid nodule' in medical_history or 'nodule' in medical_history:
            risk_score += 15
            risk_factors.append("Thyroid nodule")
        if 'autoimmune' in medical_history or 'hashimoto' in medical_history:
            risk_score += 20
            risk_factors.append("Autoimmune condition (thyroid-related)")
        if 'radiation' in medical_history or 'radioactive' in medical_history:
            risk_score += 15
            risk_factors.append("Radiation exposure (thyroid risk)")
        if 'pregnancy' in medical_history and gender == 'female':
            risk_score += 8
            risk_factors.append("Pregnancy history (postpartum thyroiditis risk)")
        
        # 5. FAMILY HISTORY (0-15 points)
        if 'thyroid' in family_history:
            risk_score += 15
            risk_factors.append("Family history of thyroid disorder")
        if 'goiter' in family_history:
            risk_score += 10
            risk_factors.append("Family history of goiter")
        if 'autoimmune' in family_history:
            risk_score += 8
            risk_factors.append("Family history of autoimmune disease")
        
        # 6. LIFESTYLE FACTORS (0-10 points)
        if 'stress' in lifestyle or 'anxiety' in lifestyle:
            risk_score += 5
            risk_factors.append("Chronic stress (affects thyroid)")
        if 'iodine' in lifestyle and ('deficient' in lifestyle or 'low' in lifestyle):
            risk_score += 8
            risk_factors.append("Iodine deficiency")
        if 'sleep' in lifestyle and ('disorder' in lifestyle or 'apnea' in lifestyle):
            risk_score += 4
            risk_factors.append("Sleep disorders")
        
        # Calculate confidence
        data_points = sum([
            1 if age > 0 else 0,
            1 if bmi > 0 else 0,
            1 if symptoms else 0,
            1 if medical_history else 0,
            1 if family_history else 0,
            1 if lifestyle else 0
        ])
        confidence = min(data_points / 6.0, 1.0) * 0.95
        
        # Normalize risk score
        risk_score = min(risk_score, 100)
        
        # Determine risk level with more granular categories
        if risk_score >= 75:
            risk_level = "Critical"
            recommendation = "Immediate comprehensive thyroid evaluation required (TSH, T3, T4, Thyroid Antibodies, Thyroid Ultrasound)"
        elif risk_score >= 60:
            risk_level = "Moderate-Critical"
            recommendation = "Urgent comprehensive thyroid screening strongly recommended (TSH, T3, T4, Thyroid Antibodies)"
        elif risk_score >= 50:
            risk_level = "High"
            recommendation = "Comprehensive thyroid screening strongly recommended (TSH, T3, T4, Thyroid Antibodies)"
        elif risk_score >= 40:
            risk_level = "High-Moderate"
            recommendation = "Enhanced thyroid screening recommended (TSH, T3, T4)"
        elif risk_score >= 30:
            risk_level = "Moderate"
            recommendation = "Standard thyroid screening recommended (TSH, T3, T4)"
        elif risk_score >= 15:
            risk_level = "Low-Moderate"
            recommendation = "Basic thyroid screening advised (TSH)"
        elif risk_score >= 8:
            risk_level = "Low"
            recommendation = "Routine screening sufficient"
        else:
            risk_level = "Very Low"
            recommendation = "Routine screening sufficient"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors[:5],
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
            "priority_tests": ["TSH", "T3", "T4", "Free T3", "Free T4", "Thyroid Antibodies"] if risk_score >= 30 else ["TSH"]
        }


class MLHealthAnalyzer:
    """
    Main ML Health Analyzer combining all specialized modules
    """
    
    def __init__(self):
        self.diabetes_module = DiabetesMLModule()
        self.heart_module = HeartDiseaseMLModule()
        self.thyroid_module = ThyroidMLModule()
    
    def analyze_all_conditions(self, patient_data: Dict) -> Dict:
        """
        Run all ML modules and return comprehensive analysis
        """
        # Calculate BMI if not provided
        if 'bmi' not in patient_data:
            weight = float(patient_data.get('weight', 0))
            height = float(patient_data.get('height', 0))
            if weight > 0 and height > 0:
                patient_data['bmi'] = weight / ((height / 100) ** 2)
            else:
                patient_data['bmi'] = 0
        
        # Run all ML modules
        diabetes_analysis = self.diabetes_module.calculate_diabetes_risk(patient_data)
        heart_analysis = self.heart_module.calculate_heart_disease_risk(patient_data)
        thyroid_analysis = self.thyroid_module.calculate_thyroid_risk(patient_data)
        
        # Determine overall risk priority
        conditions = [
            ("diabetes", diabetes_analysis),
            ("heart_disease", heart_analysis),
            ("thyroid", thyroid_analysis)
        ]
        
        # Sort by risk score (highest first)
        conditions.sort(key=lambda x: x[1]['risk_score'], reverse=True)
        
        # Get top priority condition
        top_condition = conditions[0] if conditions else None
        
        return {
            "diabetes": diabetes_analysis,
            "heart_disease": heart_analysis,
            "thyroid": thyroid_analysis,
            "top_priority": {
                "condition": top_condition[0] if top_condition else None,
                "risk_level": top_condition[1]['risk_level'] if top_condition else "Low",
                "risk_score": top_condition[1]['risk_score'] if top_condition else 0
            },
            "overall_confidence": round(
                (diabetes_analysis['confidence'] + heart_analysis['confidence'] + thyroid_analysis['confidence']) / 3,
                2
            )
        }

