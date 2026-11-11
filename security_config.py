"""
Security Configuration Module for MAPIMS Health Assessment System
Production-ready security settings and utilities
"""

import os
import hashlib
import secrets
import re
from functools import wraps
from flask import request, jsonify, session
from datetime import datetime, timedelta
import bleach

class SecurityConfig:
    """Security configuration and utilities"""
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://connect.facebook.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com; "
            "frame-src https://www.facebook.com;"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(self), camera=()'
    }
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', '100'))
    
    # Session Security
    # Only use secure cookies in production or when explicitly set
    # In development (HTTP), secure cookies won't work
    _is_production = os.environ.get('FLASK_ENV') == 'production'
    _secure_setting = os.environ.get('SESSION_COOKIE_SECURE', '').lower()
    if _secure_setting:
        SESSION_COOKIE_SECURE = _secure_setting == 'true'
    else:
        # Default: secure only in production
        SESSION_COOKIE_SECURE = _is_production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Password Security
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBER = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Input Validation
    MAX_INPUT_LENGTH = {
        'name': 100,
        'email': 255,
        'phone': 20,
        'symptoms': 2000,
        'medical_history': 2000,
        'family_history': 2000,
        'lifestyle': 2000
    }
    
    # Allowed HTML tags for sanitization (if needed)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def validate_secret_key():
        """Validate that SECRET_KEY is set and secure"""
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError(
                "SECRET_KEY environment variable is required for production. "
                "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if secret_key == 'mapims-professional-healthcare-secret-key-2025':
            raise ValueError("SECRET_KEY must be changed from default value for production")
        return secret_key
    
    @staticmethod
    def generate_secret_key():
        """Generate a secure random secret key"""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 with salt (for production, use bcrypt)"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets security requirements"""
        errors = []
        
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters")
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_NUMBER and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return errors
    
    @staticmethod
    def sanitize_input(text, max_length=None):
        """Sanitize user input to prevent XSS attacks"""
        if not text:
            return ''
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Truncate if max_length specified
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        # Strip HTML tags and escape special characters
        text = bleach.clean(text, tags=SecurityConfig.ALLOWED_TAGS, 
                           attributes=SecurityConfig.ALLOWED_ATTRIBUTES, strip=True)
        
        return text.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            return False
        # Remove common separators
        phone_clean = re.sub(r'[\s\-+()]', '', phone)
        # Check if it's numeric and reasonable length (7-15 digits)
        return phone_clean.isdigit() and 7 <= len(phone_clean) <= 15
    
    @staticmethod
    def validate_age(age):
        """Validate age is reasonable"""
        try:
            age_int = int(age)
            return 1 <= age_int <= 120
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_numeric_range(value, min_val, max_val):
        """Validate numeric value is within range"""
        try:
            num = float(value)
            return min_val <= num <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_safe_string(text, max_length=1000):
        """Check if string is safe (no suspicious patterns)"""
        if not text:
            return True  # Empty strings are safe
        
        if len(text) > max_length:
            return False
        
        # Only check for obvious SQL injection attempts, not normal text
        # Be less strict to avoid false positives
        dangerous_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\s+.*\b(FROM|INTO|SET|WHERE)\b)',  # SQL commands with keywords
            r'(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+\s*(--|#|/\*))',  # SQL injection with comments
            r'(;\s*(DROP|DELETE|TRUNCATE)\s+)',  # Command chaining
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True


class RateLimiter:
    """Simple in-memory rate limiter (for production, use Redis)"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = timedelta(minutes=5)
        self.last_cleanup = datetime.now()
    
    def is_allowed(self, identifier, limit_per_minute, limit_per_hour):
        """Check if request is within rate limits"""
        now = datetime.now()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup(now)
            self.last_cleanup = now
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        request_times = self.requests[identifier]
        
        # Remove requests older than 1 hour
        cutoff_hour = now - timedelta(hours=1)
        request_times[:] = [t for t in request_times if t > cutoff_hour]
        
        # Check hourly limit
        if len(request_times) >= limit_per_hour:
            return False
        
        # Check per-minute limit
        cutoff_minute = now - timedelta(minutes=1)
        recent_requests = [t for t in request_times if t > cutoff_minute]
        
        if len(recent_requests) >= limit_per_minute:
            return False
        
        # Record this request
        request_times.append(now)
        return True
    
    def _cleanup(self, now):
        """Remove old entries"""
        cutoff = now - timedelta(hours=2)
        identifiers_to_remove = []
        
        for identifier, request_times in self.requests.items():
            request_times[:] = [t for t in request_times if t > cutoff]
            if not request_times:
                identifiers_to_remove.append(identifier)
        
        for identifier in identifiers_to_remove:
            del self.requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit_per_minute=None, limit_per_hour=None):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SecurityConfig.RATE_LIMIT_ENABLED:
                return f(*args, **kwargs)
            
            # Get client identifier
            identifier = request.remote_addr
            if 'X-Forwarded-For' in request.headers:
                identifier = request.headers['X-Forwarded-For'].split(',')[0].strip()
            
            # Use default limits if not specified
            limit_min = limit_per_minute or SecurityConfig.RATE_LIMIT_PER_MINUTE
            limit_hour = limit_per_hour or SecurityConfig.RATE_LIMIT_PER_HOUR
            
            if not rate_limiter.is_allowed(identifier, limit_min, limit_hour):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def validate_assessment_input(data):
    """Validate assessment form input - ensures all fields needed for ML analysis are provided"""
    errors = []
    
    # Required fields for basic information
    required_fields = ['name', 'age', 'gender', 'weight', 'height', 'phone']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} is required")
    
    # Validate name
    if data.get('name'):
        name = SecurityConfig.sanitize_input(data['name'], SecurityConfig.MAX_INPUT_LENGTH['name'])
        if len(name) < 2:
            errors.append("Name must be at least 2 characters")
        elif len(name) > SecurityConfig.MAX_INPUT_LENGTH['name']:
            errors.append(f"Name must be less than {SecurityConfig.MAX_INPUT_LENGTH['name']} characters")
        # Only check for dangerous patterns, not normal text
        if not SecurityConfig.is_safe_string(name, SecurityConfig.MAX_INPUT_LENGTH['name']):
            errors.append("Name contains invalid characters")
    
    # Validate age
    if data.get('age'):
        if not SecurityConfig.validate_age(data['age']):
            errors.append("Age must be between 1 and 120")
    
    # Validate gender
    if data.get('gender'):
        if data['gender'] not in ['male', 'female', 'other']:
            errors.append("Invalid gender selection")
    
    # Validate weight
    if data.get('weight'):
        if not SecurityConfig.validate_numeric_range(data['weight'], 1, 500):
            errors.append("Weight must be between 1 and 500 kg")
    
    # Validate height
    if data.get('height'):
        if not SecurityConfig.validate_numeric_range(data['height'], 50, 300):
            errors.append("Height must be between 50 and 300 cm")
    
    # Validate phone
    if data.get('phone'):
        phone = str(data['phone']).strip()
        if not phone:
            errors.append("Phone number is required")
        elif not SecurityConfig.validate_phone(phone):
            errors.append("Invalid phone number format. Please enter a valid phone number (7-15 digits)")
    
    # Validate email (optional)
    if data.get('email'):
        if not SecurityConfig.validate_email(data['email']):
            errors.append("Invalid email format")
    
    # ========== ML ANALYSIS REQUIRED FIELDS ==========
    # Medical conditions - at least one must be answered for ML analysis
    medical_condition_fields = [
        'condition_diabetes', 'condition_hypertension', 'condition_heart_disease',
        'condition_thyroid', 'condition_asthma', 'condition_kidney'
    ]
    has_medical_answer = False
    for field in medical_condition_fields:
        value = data.get(field)
        if value and str(value).strip() and str(value).strip().lower() in ['yes', 'no', 'not_sure']:
            has_medical_answer = True
            break
    
    if not has_medical_answer:
        errors.append("Please answer at least one medical condition question (required for accurate health analysis)")
    
    # Family history - at least one must be answered for ML analysis
    family_history_fields = ['family_diabetes', 'family_heart_disease']
    has_family_answer = False
    for field in family_history_fields:
        value = data.get(field)
        if value and str(value).strip() and str(value).strip().lower() in ['yes', 'no', 'not_sure']:
            has_family_answer = True
            break
    
    if not has_family_answer:
        errors.append("Please answer at least one family history question (required for accurate health analysis)")
    
    # Lifestyle fields - all optional, only filled fields will be included in ML analysis
    # No validation required - if fields are empty, they won't be included in analysis
    
    # Symptoms - if not provided, set empty string (ML can work without it, but prefer it)
    # We'll allow empty symptoms but encourage providing them
    if not data.get('symptoms'):
        data['symptoms'] = ''  # Set default empty string for ML analysis
    
    # Sanitize text fields
    text_fields = ['symptoms', 'medical_history', 'family_history', 'lifestyle', 'other_conditions', 'lifestyle_other']
    for field in text_fields:
        if data.get(field):
            max_len = SecurityConfig.MAX_INPUT_LENGTH.get(field, 2000)
            data[field] = SecurityConfig.sanitize_input(data[field], max_len)
        elif field == 'symptoms':
            # Ensure symptoms exists as empty string for ML analysis
            data[field] = ''
    
    return errors

