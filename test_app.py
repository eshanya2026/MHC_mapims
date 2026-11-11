#!/usr/bin/env python
"""Quick diagnostic test for MAPIMS app"""

import sys
import os

print("=" * 50)
print("MAPIMS Application Diagnostic Test")
print("=" * 50)

# Test 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")

# Test 2: Import Flask
print("\n2. Testing Flask import...")
try:
    from flask import Flask
    print("   ✓ Flask imported successfully")
except Exception as e:
    print(f"   ✗ Flask import failed: {e}")
    sys.exit(1)

# Test 3: Import app
print("\n3. Testing app.py import...")
try:
    import app
    print("   ✓ app.py imported successfully")
except Exception as e:
    print(f"   ✗ app.py import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check templates
print("\n4. Checking templates...")
template_files = [
    'templates/landing.html',
    'templates/assessment.html',
    'templates/analysis.html',
    'templates/packages.html',
    'templates/booking.html',
    'templates/confirmation.html',
    'templates/admin/login.html',
    'templates/admin/dashboard.html'
]

for template in template_files:
    if os.path.exists(template):
        print(f"   ✓ {template}")
    else:
        print(f"   ✗ {template} - MISSING")

# Test 5: Check static files
print("\n5. Checking static files...")
static_files = [
    'static/css/mapims.css',
    'static/js/assessment.js',
    'static/js/landing.js'
]

for static_file in static_files:
    if os.path.exists(static_file):
        print(f"   ✓ {static_file}")
    else:
        print(f"   ✗ {static_file} - MISSING")

# Test 6: Test Flask app creation
print("\n6. Testing Flask app creation...")
try:
    with app.app.app_context():
        print("   ✓ Flask app context created")
        print(f"   ✓ App name: {app.app.name}")
        print(f"   ✓ Debug mode: {app.app.debug}")
except Exception as e:
    print(f"   ✗ Flask app creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Test MongoDB connection
print("\n7. Testing MongoDB connection...")
try:
    # Try to ping MongoDB
    app.client.admin.command('ping')
    print("   ✓ MongoDB connection successful")
except Exception as e:
    print(f"   ⚠ MongoDB connection issue: {e}")
    print("   (This is OK if MongoDB is not accessible)")

# Test 8: Test OpenAI client
print("\n8. Testing OpenAI client...")
try:
    if hasattr(app, 'openai_client'):
        print("   ✓ OpenAI client initialized")
    else:
        print("   ⚠ OpenAI client not found")
except Exception as e:
    print(f"   ⚠ OpenAI client issue: {e}")

print("\n" + "=" * 50)
print("Diagnostic complete!")
print("=" * 50)
print("\nTo start the server, run:")
print("  python app.py")
print("\nThen open: http://localhost:5000")

