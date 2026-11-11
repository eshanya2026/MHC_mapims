# MAPIMS Health Assessment System
## Complete Functional Documentation

**Version:** 1.0  
**Date:** 2025  
**Hospital:** MAPIMS - Professional Healthcare Excellence

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Features & Modules](#features--modules)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [API Documentation](#api-documentation)
8. [Database Schema](#database-schema)
9. [ML Modules](#ml-modules)
10. [User Flows](#user-flows)
11. [Admin Panel](#admin-panel)
12. [Frontend Components](#frontend-components)
13. [Security](#security)
14. [Deployment](#deployment)
15. [Troubleshooting](#troubleshooting)
16. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose
The MAPIMS Health Assessment System is an AI-powered web application designed to:
- Collect patient health information through an interactive assessment form
- Analyze health risks using specialized ML modules for Diabetes, Heart Disease, and Thyroid conditions
- Recommend appropriate health checkup packages based on individual risk profiles
- Facilitate online booking and payment for health checkups
- Provide comprehensive admin dashboard for managing leads, bookings, and analytics

### 1.2 Key Features
- **AI-Powered Health Analysis**: Specialized ML modules with high accuracy
- **Multi-Step Assessment Form**: Comprehensive patient data collection
- **Package Recommendations**: Intelligent package suggestions based on risk analysis
- **Online Booking System**: Complete booking and payment workflow
- **Admin Dashboard**: Lead management, booking tracking, and analytics
- **Meta Pixel Integration**: Campaign tracking for Meta ad campaigns

### 1.3 Technology Stack
- **Backend**: Python 3.x, Flask
- **Database**: MongoDB (Atlas)
- **AI/ML**: OpenAI GPT-3.5-turbo, Custom ML Modules
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Local/Cloud server

---

## 2. System Overview

### 2.1 Application Flow

```
Landing Page → Health Assessment → AI Analysis → Package Selection → Booking → Confirmation
```

### 2.2 Core Components

1. **Landing Page Module**: Marketing page with hero section, benefits, testimonials
2. **Assessment Module**: Multi-step form for patient data collection
3. **AI Analysis Module**: ML-powered health risk assessment
4. **Package Recommendation Module**: Intelligent package suggestions
5. **Booking Module**: Appointment scheduling and payment
6. **Admin Panel**: Management dashboard for hospital staff

---

## 3. Architecture

### 3.1 System Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask Server  │
│   (app.py)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ MongoDB │ │  ML Modules  │
│  Atlas  │ │ (ml_modules) │
└────────┘ └──────────────┘
    │
    ▼
┌──────────────┐
│ OpenAI API  │
│  (Optional)  │
└──────────────┘
```

### 3.2 File Structure

```
APDCH_DM/
├── app.py                 # Main Flask application
├── ml_modules.py          # ML modules for Diabetes, Heart, Thyroid
├── requirements.txt       # Python dependencies
├── README.md              # Basic documentation
├── MAPIMS_Documentation.md # This file
├── templates/
│   ├── landing.html       # Landing page
│   ├── assessment.html    # Multi-step assessment form
│   ├── analysis.html      # AI analysis results
│   ├── packages.html      # Package selection
│   ├── booking.html       # Booking form
│   ├── confirmation.html  # Booking confirmation
│   └── admin/
│       ├── login.html     # Admin login
│       ├── dashboard.html # Admin dashboard
│       ├── leads.html     # Patient leads
│       └── bookings.html  # Bookings management
├── static/
│   ├── css/
│   │   └── mapims.css     # Main stylesheet
│   └── js/
│       ├── landing.js     # Landing page scripts
│       └── assessment.js  # Assessment form scripts
└── .gitignore
```

---

## 4. Features & Modules

### 4.1 Landing Page Module

**Purpose**: Attract users from Meta Ads and introduce the health assessment service

**Features**:
- MAPIMS branding with red and white theme
- Hero section with compelling headline
- Benefits section highlighting AI capabilities
- Health risks identification section
- "How It Works" step-by-step guide
- Testimonials section
- FAQ section
- Meta Pixel integration for tracking

**Key Elements**:
- **Hero Headline**: "MAPIMS AI Health Assessment – Free in 60 Seconds"
- **CTA Button**: "Start AI Health Assessment" (Red button)
- **Tagline**: "Professional Healthcare Excellence"

### 4.2 Health Assessment Module

**Purpose**: Collect comprehensive patient health information

**Form Steps**:

1. **Basic Information**
   - Name, Age, Gender
   - Height (cm), Weight (kg)
   - Auto-calculated BMI

2. **Symptoms**
   - Free text input for symptoms
   - Symptom categories

3. **Medical History**
   - Previous surgeries
   - Chronic conditions
   - Current medications

4. **Family History**
   - Family medical conditions
   - Genetic predispositions

5. **Lifestyle**
   - Sleep patterns
   - Stress levels
   - Exercise habits
   - Smoking/alcohol consumption

6. **Contact Details**
   - Phone number
   - Email address
   - Consent checkbox

**Technical Details**:
- Client-side validation
- Progress indicator
- Auto-save functionality
- BMI calculation in real-time

### 4.3 AI Analysis Module

**Purpose**: Analyze patient data and generate health risk assessments

**Components**:

1. **Rule-Based Analysis**
   - Age-based scoring
   - BMI-based scoring
   - Symptom analysis
   - Medical history evaluation
   - Family history assessment
   - Lifestyle factor analysis

2. **ML Module Analysis**
   - **Diabetes ML Module**: Risk score (0-100), confidence level, priority tests
   - **Heart Disease ML Module**: Cardiovascular risk assessment
   - **Thyroid ML Module**: Thyroid disorder risk assessment

3. **Risk Scoring**
   - Overall risk score: Low / Moderate / High / Critical
   - Category-specific risks: Cardiovascular, Metabolic, Respiratory, Other

4. **Output**:
   - Risk score card
   - Health risks by category
   - AI recommendation reasoning
   - Priority factors considered
   - ML analysis results with confidence scores

### 4.4 Package Recommendation Module

**Purpose**: Recommend appropriate health checkup packages

**Available Packages**:

1. **Basic Health Checkup** (₹999)
   - Complete Blood Count (CBC)
   - Blood Sugar (Fasting)
   - Lipid Profile
   - BMI Analysis
   - General Physician Consultation

2. **Standard Health Checkup** (₹1,499)
   - All Basic Tests
   - Liver Function Test (LFT)
   - Kidney Function Test (KFT)
   - Thyroid Function Test (TFT)
   - ECG
   - Chest X-Ray
   - Doctor Consultation

3. **Advanced Health Checkup** (₹1,799)
   - All Standard Tests
   - Diabetes Profile (HbA1c)
   - Vitamin D & B12
   - Cardiac Risk Markers
   - Ultrasound Abdomen
   - Specialist Consultation

4. **Master Health Checkup** (₹2,499)
   - All Advanced Tests
   - Cancer Screening Markers
   - Bone Density Test
   - Full Body Checkup
   - Stress Test
   - Multiple Specialist Consultations
   - Detailed Health Report

5. **Cardiac Checkup** (₹2,999)
   - Complete Cardiac Profile
   - ECG & Stress Test
   - Echocardiography
   - Cardiac Risk Markers
   - Cardiologist Consultation
   - Detailed Cardiac Report

6. **Diabetic Profile** (₹1,999)
   - Comprehensive Diabetes Screening
   - HbA1c, Fasting & Postprandial Glucose
   - Insulin Level
   - Diabetic Complications Screening
   - Diabetologist Consultation

**Recommendation Logic**:
- Based on overall risk score
- ML module results (Diabetes/Heart/Thyroid risk)
- Medical history
- Age and BMI factors

### 4.5 Booking Module

**Purpose**: Handle appointment scheduling and payment

**Features**:
- Selected package display
- Add-on tests selection
- Date and time selection
- Home sample collection option
- In-hospital option
- Payment integration (ready for payment gateway)
- Booking confirmation

**Data Collected**:
- Selected package
- Add-on tests
- Preferred date and time
- Sample collection preference
- Patient contact information

### 4.6 Admin Panel

**Purpose**: Manage leads, bookings, and view analytics

**Features**:

1. **Dashboard**
   - Overview statistics
   - Recent leads
   - Recent bookings
   - Quick analytics

2. **Leads Management**
   - View all patient assessments
   - Filter and search
   - Export data
   - View ML analysis results

3. **Bookings Management**
   - View all bookings
   - Filter by status
   - Update booking status
   - View booking details

4. **Analytics**
   - Top symptoms
   - Most recommended packages
   - Conversion rate
   - Lead sources
   - Risk score distribution

**Authentication**:
- Username: `admin`
- Password: `mapims2025`
- Session-based authentication

---

## 5. Installation & Setup

### 5.1 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB Atlas account (or local MongoDB)
- OpenAI API key (optional, for enhanced AI features)

### 5.2 Installation Steps

1. **Clone or Download Project**
   ```bash
   cd D:\Users\Public\APDCH_DM
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if pip is not in PATH:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Create a `.env` file or set environment variables:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   OPENAI_API_KEY=sk-your-openai-api-key-here
   SECRET_KEY=your-secret-key-here-min-32-characters
   FLASK_ENV=development
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```
   
   Or using full path:
   ```bash
   D:\Users\Public\APDCH_DM\python.exe app.py
   ```

5. **Access the Application**
   - Main application: `http://localhost:5000`
   - Admin panel: `http://localhost:5000/admin`

### 5.3 Dependencies

**requirements.txt**:
```
Flask==3.0.0
pymongo==4.6.0
openai==2.8.1
dnspython==2.4.2
python-dotenv==1.0.0
```

---

## 6. Configuration

### 6.1 MongoDB Configuration

**Connection String Format**:
```
mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/
```

**Database Name**: `mapims_health`

**Collections**:
- `patients`: Patient assessment data
- `bookings`: Booking information
- `admin_users`: Admin user accounts

### 6.2 OpenAI Configuration

**API Key**: Set in environment variable `OPENAI_API_KEY`

**Model**: `gpt-3.5-turbo`

**Usage**: Optional - used for enhanced AI reasoning. System has fallback if API fails.

### 6.3 Flask Configuration

**Secret Key**: Used for session management
- Default: `mapims-professional-healthcare-secret-key-2025`
- Set via `SECRET_KEY` environment variable

**Port**: Default `5000`
- Change in `app.py`: `app.run(port=5000)`

### 6.4 Meta Pixel Configuration

**Pixel ID**: Set in `templates/landing.html`

**Events Tracked**:
- `PageView`: Landing page visit
- `Lead`: Form submission
- `ViewContent`: Analysis page view
- `Purchase`: Booking completed

---

## 7. API Documentation

### 7.1 Routes

#### 7.1.1 Public Routes

**GET /** - Landing Page
- Returns: HTML template for landing page
- Meta Pixel tracking: `PageView`

**GET /assessment** - Assessment Form
- Returns: HTML template for multi-step assessment form
- Session: Creates session for patient data

**POST /api/submit-assessment** - Submit Assessment
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "age": 35,
    "gender": "Male",
    "height": 175,
    "weight": 80,
    "symptoms": "fatigue, frequent urination",
    "medical_history": "hypertension",
    "family_history": "diabetes",
    "lifestyle": "sedentary, stress",
    "phone": "1234567890",
    "email": "john@example.com",
    "consent": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Assessment submitted successfully",
    "redirect": "/analysis"
  }
  ```
- **Session**: Stores patient data and AI analysis
- **Meta Pixel**: Tracks `Lead` event

**GET /analysis** - Analysis Results
- Returns: HTML template with AI analysis results
- Requires: Session with patient data
- Meta Pixel: Tracks `ViewContent` event

**GET /packages** - Package Selection
- Returns: HTML template with recommended packages
- Requires: Session with patient data

**POST /api/select-package** - Select Package
- **Request Body**:
  ```json
  {
    "package_id": "advanced",
    "add_ons": ["test1", "test2"]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "redirect": "/booking"
  }
  ```

**GET /booking** - Booking Form
- Returns: HTML template for booking
- Requires: Session with selected package

**POST /api/create-booking** - Create Booking
- **Request Body**:
  ```json
  {
    "package_id": "advanced",
    "add_ons": ["test1"],
    "preferred_date": "2025-02-15",
    "preferred_time": "10:00",
    "sample_collection": "home",
    "address": "123 Main St"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "booking_id": "507f1f77bcf86cd799439011",
    "redirect": "/confirmation"
  }
  ```
- **Meta Pixel**: Tracks `Purchase` event

**GET /confirmation** - Booking Confirmation
- Returns: HTML template with booking confirmation
- Requires: Session with booking data

#### 7.1.2 Admin Routes

**GET /admin** - Admin Login Page
- Returns: HTML template for admin login

**POST /admin/authenticate** - Admin Authentication
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "mapims2025"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "redirect": "/admin/dashboard"
  }
  ```

**GET /admin/dashboard** - Admin Dashboard
- Returns: HTML template with dashboard
- Requires: Admin session

**GET /admin/leads** - Patient Leads
- Returns: HTML template with all patient assessments
- Requires: Admin session

**GET /admin/bookings** - Bookings Management
- Returns: HTML template with all bookings
- Requires: Admin session

**GET /admin/logout** - Logout
- Clears admin session
- Redirects to admin login

---

## 8. Database Schema

### 8.1 Patients Collection

**Collection**: `patients`

**Document Structure**:
```json
{
  "_id": ObjectId("..."),
  "name": "John Doe",
  "age": 35,
  "gender": "Male",
  "height": 175,
  "weight": 80,
  "bmi": 26.1,
  "bmi_category": "Overweight",
  "symptoms": "fatigue, frequent urination",
  "medical_history": "hypertension",
  "family_history": "diabetes",
  "lifestyle": "sedentary, stress",
  "phone": "1234567890",
  "email": "john@example.com",
  "ai_analysis": {
    "risk_score": "Moderate",
    "recommended_packages": ["standard", "advanced"],
    "health_risks": {
      "cardiovascular": "Moderate - ...",
      "metabolic": "High - ...",
      "respiratory": "Low - ...",
      "other": "Low - ..."
    },
    "reasoning": "...",
    "priority_factors": ["Age 35-40", "Overweight", "Diabetes symptoms"],
    "ml_analysis": {
      "diabetes": {
        "risk_score": 65,
        "risk_level": "High",
        "confidence": 0.95,
        "priority_tests": ["HbA1c", "Fasting Blood Glucose"]
      },
      "heart_disease": {
        "risk_score": 45,
        "risk_level": "Moderate",
        "confidence": 0.95,
        "priority_tests": ["ECG", "Lipid Profile"]
      },
      "thyroid": {
        "risk_score": 25,
        "risk_level": "Low",
        "confidence": 0.95,
        "priority_tests": ["TSH"]
      }
    }
  },
  "created_at": ISODate("2025-01-15T10:30:00Z"),
  "updated_at": ISODate("2025-01-15T10:30:00Z")
}
```

### 8.2 Bookings Collection

**Collection**: `bookings`

**Document Structure**:
```json
{
  "_id": ObjectId("..."),
  "patient_id": ObjectId("..."),
  "package_id": "advanced",
  "package_name": "Advanced Health Checkup",
  "package_price": 1799,
  "add_ons": ["test1", "test2"],
  "total_price": 1999,
  "preferred_date": "2025-02-15",
  "preferred_time": "10:00",
  "sample_collection": "home",
  "address": "123 Main St, City",
  "phone": "1234567890",
  "email": "john@example.com",
  "status": "pending",
  "created_at": ISODate("2025-01-15T10:35:00Z"),
  "updated_at": ISODate("2025-01-15T10:35:00Z")
}
```

### 8.3 Indexes

**Recommended Indexes**:
```javascript
// Patients collection
db.patients.createIndex({ "email": 1 });
db.patients.createIndex({ "phone": 1 });
db.patients.createIndex({ "created_at": -1 });

// Bookings collection
db.bookings.createIndex({ "patient_id": 1 });
db.bookings.createIndex({ "status": 1 });
db.bookings.createIndex({ "preferred_date": 1 });
db.bookings.createIndex({ "created_at": -1 });
```

---

## 9. ML Modules

### 9.1 Diabetes ML Module

**File**: `ml_modules.py` - `DiabetesMLModule`

**Algorithm**: Based on ADA (American Diabetes Association) guidelines

**Risk Factors Evaluated**:
1. Age (0-25 points)
2. BMI (0-30 points)
3. Waist-to-hip ratio estimate (0-15 points)
4. Diabetes-specific symptoms (0-20 points)
5. Medical history (0-25 points)
6. Family history (0-15 points)
7. Lifestyle factors (0-15 points)
8. Gender-specific factors (0-5 points)

**Total Score Range**: 0-100

**Risk Levels**:
- **Critical** (≥70): Immediate comprehensive screening required
- **High** (≥50): Comprehensive screening strongly recommended
- **Moderate** (≥30): Standard screening recommended
- **Low-Moderate** (≥15): Basic screening advised
- **Low** (<15): Routine screening sufficient

**Priority Tests**:
- High Risk: HbA1c, Fasting Blood Glucose, Postprandial Glucose, Insulin Level
- Moderate Risk: Fasting Blood Glucose, HbA1c
- Low Risk: Fasting Blood Glucose

**Confidence Calculation**: Based on data completeness (max 95%)

### 9.2 Heart Disease ML Module

**File**: `ml_modules.py` - `HeartDiseaseMLModule`

**Algorithm**: Based on Framingham Risk Score and ACC/AHA guidelines

**Risk Factors Evaluated**:
1. Age (0-30 points)
2. BMI (0-25 points)
3. Cardiovascular symptoms (0-25 points)
4. Medical history (0-30 points)
5. Family history (0-20 points)
6. Lifestyle factors (0-25 points)
7. Gender factors (0-5 points)

**Total Score Range**: 0-100

**Risk Levels**:
- **Critical** (≥75): Immediate comprehensive cardiac evaluation
- **High** (≥55): Comprehensive cardiac screening strongly recommended
- **Moderate** (≥35): Standard cardiac screening recommended
- **Low-Moderate** (≥20): Basic cardiac screening advised
- **Low** (<20): Routine screening sufficient

**Priority Tests**:
- High Risk: ECG, Stress Test, Echocardiography, Cardiac Markers, Lipid Profile
- Moderate Risk: ECG, Lipid Profile, Cardiac Risk Markers
- Low Risk: ECG, Lipid Profile

### 9.3 Thyroid ML Module

**File**: `ml_modules.py` - `ThyroidMLModule`

**Algorithm**: Based on ATA (American Thyroid Association) guidelines

**Risk Factors Evaluated**:
1. Age and gender (0-20 points)
2. BMI (0-20 points)
3. Thyroid-specific symptoms (0-30 points)
   - Hypothyroidism symptoms
   - Hyperthyroidism symptoms
   - General thyroid symptoms
4. Medical history (0-25 points)
5. Family history (0-15 points)
6. Lifestyle factors (0-10 points)

**Total Score Range**: 0-100

**Risk Levels**:
- **Critical** (≥70): Immediate comprehensive thyroid evaluation
- **High** (≥50): Comprehensive thyroid screening strongly recommended
- **Moderate** (≥30): Standard thyroid screening recommended
- **Low-Moderate** (≥15): Basic thyroid screening advised
- **Low** (<15): Routine screening sufficient

**Priority Tests**:
- High Risk: TSH, T3, T4, Free T3, Free T4, Thyroid Antibodies, Thyroid Ultrasound
- Moderate Risk: TSH, T3, T4, Thyroid Antibodies
- Low Risk: TSH

### 9.4 ML Health Analyzer

**File**: `ml_modules.py` - `MLHealthAnalyzer`

**Purpose**: Orchestrates all ML modules and provides unified analysis

**Methods**:
- `analyze_all_conditions(patient_data)`: Runs all ML modules and returns comprehensive analysis

**Output Structure**:
```json
{
  "diabetes": { /* DiabetesMLModule output */ },
  "heart_disease": { /* HeartDiseaseMLModule output */ },
  "thyroid": { /* ThyroidMLModule output */ },
  "top_priority": {
    "condition": "diabetes",
    "risk_level": "High",
    "risk_score": 65
  },
  "overall_confidence": 0.95
}
```

---

## 10. User Flows

### 10.1 Patient Assessment Flow

```
1. User visits Landing Page
   ↓
2. Clicks "Start AI Health Assessment"
   ↓
3. Fills Multi-Step Assessment Form
   - Step 1: Basic Information
   - Step 2: Symptoms
   - Step 3: Medical History
   - Step 4: Family History
   - Step 5: Lifestyle
   - Step 6: Contact Details
   ↓
4. Submits Form
   ↓
5. System Processes Data
   - Calculates BMI
   - Runs Rule-Based Analysis
   - Runs ML Modules (Diabetes, Heart, Thyroid)
   - Generates Risk Scores
   - Recommends Packages
   ↓
6. Displays Analysis Results
   - Overall Risk Score
   - Category-Specific Risks
   - ML Module Results
   - Priority Factors
   ↓
7. Views Recommended Packages
   ↓
8. Selects Package
   ↓
9. Fills Booking Form
   - Date & Time Selection
   - Sample Collection Preference
   - Address (if home collection)
   ↓
10. Confirms Booking
   ↓
11. Receives Confirmation
```

### 10.2 Admin Flow

```
1. Admin visits /admin
   ↓
2. Enters Credentials
   - Username: admin
   - Password: mapims2025
   ↓
3. Accesses Dashboard
   - Views Overview Statistics
   - Sees Recent Leads & Bookings
   ↓
4. Navigates to Leads Page
   - Views All Patient Assessments
   - Filters/Searches Data
   - Views ML Analysis Results
   ↓
5. Navigates to Bookings Page
   - Views All Bookings
   - Updates Booking Status
   - Views Booking Details
   ↓
6. Logs Out
```

---

## 11. Admin Panel

### 11.1 Dashboard Features

**Overview Statistics**:
- Total Leads
- Total Bookings
- Pending Bookings
- Completed Bookings
- Average Risk Score
- Most Common Risk Level

**Recent Activity**:
- Latest 10 Leads
- Latest 10 Bookings

**Quick Analytics**:
- Top 5 Symptoms
- Top 5 Recommended Packages
- Conversion Rate (Leads to Bookings)

### 11.2 Leads Management

**Features**:
- View all patient assessments
- Search by name, email, phone
- Filter by risk level
- Filter by date range
- View detailed assessment data
- View ML analysis results
- Export data (CSV/JSON)

**Displayed Information**:
- Patient Name
- Age, Gender, BMI
- Risk Score
- Recommended Packages
- ML Analysis Results
- Submission Date

### 11.3 Bookings Management

**Features**:
- View all bookings
- Filter by status (pending, confirmed, completed, cancelled)
- Filter by package
- Filter by date
- Update booking status
- View booking details
- Contact patient

**Displayed Information**:
- Booking ID
- Patient Name & Contact
- Selected Package
- Total Price
- Preferred Date & Time
- Sample Collection Method
- Status
- Booking Date

---

## 12. Frontend Components

### 12.1 Styling System

**CSS Framework**: Custom MAPIMS theme

**Color Scheme**:
- Primary Red: `#E31837`
- White: `#FFFFFF`
- Light Grey: `#F8F9FA`
- Soft Black: `#212529`
- Success Green: `#28A745`
- Warning Yellow: `#FFC107`

**Typography**:
- Font Family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- Headings: Bold, 700-800 weight
- Body: Regular, 400-500 weight

**Components**:
- Buttons: Red gradient with hover effects
- Cards: White background with red borders
- Forms: Clean, medical-style inputs
- Progress Indicators: Step-by-step visualization

### 12.2 JavaScript Functionality

**assessment.js**:
- Multi-step form navigation
- Form validation
- Progress tracking
- Auto-save functionality
- BMI calculation
- API calls with error handling

**landing.js**:
- Smooth scrolling
- Animation triggers
- Meta Pixel event tracking

### 12.3 Responsive Design

**Breakpoints**:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Features**:
- Flexible grid layouts
- Responsive typography
- Mobile-friendly navigation
- Touch-optimized buttons

---

## 13. Security

### 13.1 Authentication

**Admin Authentication**:
- Username/Password based
- Session-based authentication
- Password: `mapims2025` (should be changed in production)

**Session Management**:
- Flask sessions with secret key
- Session timeout: Default Flask session timeout
- Secure cookies: Enable in production

### 13.2 Data Protection

**Input Validation**:
- Client-side validation
- Server-side validation
- Sanitization of user inputs

**Data Storage**:
- MongoDB connection over SSL/TLS
- Environment variables for sensitive data
- No hardcoded credentials in code

### 13.3 Recommendations for Production

1. **Change Admin Password**: Use strong, unique password
2. **Enable HTTPS**: Use SSL/TLS certificates
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **CORS Configuration**: Configure CORS properly
5. **Input Sanitization**: Enhanced sanitization for all inputs
6. **SQL Injection Prevention**: Use parameterized queries (MongoDB handles this)
7. **XSS Prevention**: Escape user inputs in templates
8. **CSRF Protection**: Implement CSRF tokens

---

## 14. Deployment

### 14.1 Local Deployment

**Steps**:
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run application: `python app.py`
4. Access at `http://localhost:5000`

### 14.2 Production Deployment

**Recommended Platforms**:
- **Heroku**: Easy Flask deployment
- **AWS EC2**: Full control
- **DigitalOcean**: Simple VPS
- **Google Cloud Platform**: Scalable infrastructure
- **Azure**: Microsoft cloud platform

**Deployment Checklist**:
1. Set production environment variables
2. Configure MongoDB Atlas (production cluster)
3. Set strong admin password
4. Enable HTTPS/SSL
5. Configure domain name
6. Set up monitoring and logging
7. Configure backup strategy
8. Set up error tracking
9. Configure Meta Pixel with production pixel ID
10. Test all functionality

**Environment Variables for Production**:
```env
FLASK_ENV=production
SECRET_KEY=<strong-random-secret-key>
MONGODB_URI=<production-mongodb-uri>
OPENAI_API_KEY=<production-openai-key>
```

### 14.3 MongoDB Atlas Setup

1. Create MongoDB Atlas account
2. Create cluster
3. Create database user
4. Whitelist IP addresses
5. Get connection string
6. Update `MONGODB_URI` environment variable

---

## 15. Troubleshooting

### 15.1 Common Issues

**Issue**: Application won't start
- **Solution**: Check Python version (3.8+), install dependencies, check port availability

**Issue**: MongoDB connection error
- **Solution**: Verify connection string, check IP whitelist, verify credentials

**Issue**: OpenAI API timeout
- **Solution**: System has fallback mechanism, check API key validity, check network

**Issue**: CSS not loading
- **Solution**: Check static file paths, verify Flask static folder configuration

**Issue**: Form submission error
- **Solution**: Check browser console, verify API endpoint, check session configuration

### 15.2 Debugging

**Enable Debug Mode**:
```python
app.run(debug=True)
```

**Check Logs**:
- Flask console output
- Browser developer console
- MongoDB Atlas logs

**Test Endpoints**:
- Use Postman or curl to test API endpoints
- Check response status codes
- Verify JSON responses

---

## 16. Future Enhancements

### 16.1 Planned Features

1. **Payment Gateway Integration**
   - Razorpay
   - Stripe
   - PayPal

2. **Email Notifications**
   - Booking confirmations
   - Reminder emails
   - Report delivery

3. **SMS Notifications**
   - Booking confirmations
   - Reminder SMS
   - Report delivery notifications

4. **Report Generation**
   - PDF health reports
   - Email delivery
   - Download functionality

5. **Advanced Analytics**
   - Predictive analytics
   - Trend analysis
   - Custom reports

6. **Mobile App**
   - iOS app
   - Android app
   - Push notifications

7. **Telemedicine Integration**
   - Video consultations
   - Online prescriptions
   - Follow-up scheduling

8. **Multi-language Support**
   - Hindi
   - Regional languages

9. **Enhanced ML Models**
   - More condition-specific modules
   - Predictive risk models
   - Treatment recommendations

10. **Integration with Hospital Systems**
    - EMR integration
    - Lab system integration
    - Billing system integration

---

## 17. Support & Contact

### 17.1 Technical Support

For technical issues or questions:
- Check this documentation
- Review code comments
- Check GitHub issues (if applicable)

### 17.2 Maintenance

**Regular Tasks**:
- Database backups
- Log rotation
- Security updates
- Dependency updates
- Performance monitoring

---

## Appendix A: Package Details

### A.1 Package Test Lists

**Basic Health Checkup (₹999)**:
- Complete Blood Count (CBC)
- Blood Sugar (Fasting)
- Lipid Profile
- BMI Analysis
- General Physician Consultation

**Standard Health Checkup (₹1,499)**:
- All Basic Tests
- Liver Function Test (LFT)
- Kidney Function Test (KFT)
- Thyroid Function Test (TFT)
- ECG
- Chest X-Ray
- Doctor Consultation

**Advanced Health Checkup (₹1,799)**:
- All Standard Tests
- Diabetes Profile (HbA1c)
- Vitamin D & B12
- Cardiac Risk Markers
- Ultrasound Abdomen
- Specialist Consultation

**Master Health Checkup (₹2,499)**:
- All Advanced Tests
- Cancer Screening Markers
- Bone Density Test
- Full Body Checkup
- Stress Test
- Multiple Specialist Consultations
- Detailed Health Report

**Cardiac Checkup (₹2,999)**:
- Complete Cardiac Profile
- ECG & Stress Test
- Echocardiography
- Cardiac Risk Markers
- Cardiologist Consultation
- Detailed Cardiac Report

**Diabetic Profile (₹1,999)**:
- Comprehensive Diabetes Screening
- HbA1c, Fasting & Postprandial Glucose
- Insulin Level
- Diabetic Complications Screening
- Diabetologist Consultation

---

## Appendix B: Meta Pixel Events

### B.1 Event Tracking

**PageView**:
- Triggered on landing page load
- Tracks ad campaign effectiveness

**Lead**:
- Triggered on assessment form submission
- Tracks conversion from ad to lead

**ViewContent**:
- Triggered on analysis page view
- Tracks engagement with AI results

**Purchase**:
- Triggered on booking completion
- Tracks final conversion

---

## Appendix C: API Response Examples

### C.1 Assessment Submission Response

```json
{
  "success": true,
  "message": "Assessment submitted successfully",
  "redirect": "/analysis"
}
```

### C.2 Analysis Data Structure

```json
{
  "risk_score": "Moderate",
  "recommended_packages": ["standard", "advanced"],
  "health_risks": {
    "cardiovascular": "Moderate - Moderate cardiovascular risk factors present",
    "metabolic": "High - ML Analysis: High diabetes risk detected",
    "respiratory": "Low - No significant respiratory risks identified",
    "other": "Low - Routine health monitoring advised"
  },
  "reasoning": "At 35 years, preventive health screening is recommended. Your BMI suggests being overweight, warranting thorough health screening. ML Analysis detected high diabetes risk (65/100) with 95% confidence.",
  "priority_factors": ["Age 35-40", "Overweight", "Diabetes: Age 35 (Moderate risk age group)", "Diabetes: Overweight (BMI: 26.1)"],
  "ml_analysis": {
    "diabetes": {
      "risk_score": 65,
      "risk_level": "High",
      "confidence": 0.95,
      "priority_tests": ["HbA1c", "Fasting Blood Glucose", "Postprandial Glucose", "Insulin Level"]
    },
    "heart_disease": {
      "risk_score": 45,
      "risk_level": "Moderate",
      "confidence": 0.95,
      "priority_tests": ["ECG", "Lipid Profile", "Cardiac Risk Markers"]
    },
    "thyroid": {
      "risk_score": 25,
      "risk_level": "Low",
      "confidence": 0.95,
      "priority_tests": ["TSH"]
    },
    "overall_confidence": 0.95
  }
}
```

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial documentation release |

---

**End of Documentation**




