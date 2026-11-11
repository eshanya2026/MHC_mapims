# MAPIMS Health Checkup Recommendation System

An AI-powered web application that collects patient details and recommends personalized health checkup packages based on age, weight, height, BMI, symptoms, and existing health conditions.

## Features

- **Patient Data Collection**: Collects comprehensive patient information including:
  - Personal details (name, age, gender)
  - Physical measurements (weight, height - calculates BMI automatically)
  - Contact information (phone, email)
  - Health information (symptoms, existing conditions)

- **AI-Powered Recommendations**: Intelligently suggests one of six health checkup packages:
  - **₹999** - Basic Health Check Up Package
  - **₹1,999** - Master Health Check Up Package
  - **₹2,499** - Cardio Health Check Up Package
  - **₹2,499** - Diabetic Health Check Package
  - **₹2,999** - Well Women Checkup Executive Package
  - **₹4,999** - Premium Diabetic Health Check Package

- **MongoDB Integration**: All patient data and recommendations are automatically stored in MongoDB for tracking and analysis

- **Modern Red & White Theme**: Beautiful, professional design optimized for Meta ad campaigns
- **Real-time Processing**: Instant AI-powered recommendations with smooth animations
- **Mobile-Friendly**: Fully responsive design for all devices

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or set environment variables:
```bash
export FLASK_ENV=production
export PORT=5000
python app.py
```

## How It Works

1. **User fills out the form** with their details
2. **OpenAI AI analyzes** the patient profile:
   - Age (older patients need more comprehensive screening)
   - BMI (calculated from weight and height)
   - Symptoms (if any reported)
   - Existing health conditions
   - Gender-specific considerations

3. **AI generates recommendation** using GPT-3.5 with:
   - Package name and price
   - Detailed description
   - List of included tests/services
   - AI-generated reasoning for the recommendation
   - Priority factors considered

4. **Data is stored** in MongoDB for:
   - Patient records
   - Recommendation tracking
   - Analytics and follow-up

## API Endpoints

### `GET /`
Main page with the patient form

### `POST /recommend`
Submit patient data and get recommendation

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 45,
  "weight": 75,
  "height": 175,
  "gender": "male",
  "phone": "+91 1234567890",
  "email": "john@example.com",
  "symptoms": "frequent headaches",
  "existing_conditions": "hypertension"
}
```

**Response:**
```json
{
  "success": true,
  "recommendation": {
    "package_id": "1799",
    "package_name": "Premium Health Checkup",
    "price": 1799,
    "description": "Advanced screening with detailed analysis",
    "includes": ["All Standard Tests", "Thyroid Function", ...],
    "bmi": 24.5,
    "reasoning": "AI-generated detailed explanation...",
    "priority_factors": ["Age", "BMI", "Symptoms"]
  },
  "patient_data": {...},
  "patient_id": "mongodb_document_id"
}
```

### `GET /packages`
Get all available health checkup packages

## Deployment for Meta Ads

1. **Deploy to a hosting service** (Heroku, AWS, DigitalOcean, etc.)
2. **Update the URL** in your Meta ad campaign
3. **Add tracking pixels** (optional):
   - Add Google Analytics or Facebook Pixel code to `templates/index.html`
   - Track conversions when recommendations are shown

## Customization

### Modify Package Details
Edit the `PACKAGES` dictionary in `app.py`

### Adjust AI Recommendation Prompt
Modify the `recommend_package_with_ai()` function in `app.py` to change the AI prompt and recommendation logic

### Update Styling
Edit `static/css/style.css` to match your brand colors

## Requirements

- Python 3.7+
- Flask 3.0.0+
- MongoDB Atlas account (connection string configured)
- OpenAI API key (configured in app.py)
- pymongo 4.6.0+
- openai 1.3.0+

## License

This project is created for MAPIMS (mapims.org)

## Support

For issues or questions, contact MAPIMS support.

