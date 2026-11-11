"""
WhatsApp Service Module
Handles sending WhatsApp messages for booking confirmations
Uses S3 InfoSystem WhatsApp API
"""
import os
import requests
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending WhatsApp messages via S3 InfoSystem API"""
    
    def __init__(self):
        """Initialize WhatsApp service with configuration from environment variables"""
        self.enabled = os.environ.get('WHATSAPP_ENABLED', 'true').lower() == 'true'
        self.test_mode = os.environ.get('WHATSAPP_TEST_MODE', 'false').lower() == 'true'
        
        # S3 InfoSystem WhatsApp API Configuration
        # Base URL should be the template API endpoint
        default_base_url = 'https://wa.s3infosystem.in/api/sendtemplate.php'
        self.base_url = os.environ.get('WA_BASE_URL', default_base_url)
        self.license_number = os.environ.get('WA_LICENSE_NUMBER', '')
        self.api_key = os.environ.get('WA_API_KEY', '')
        self.contact = os.environ.get('WA_CONTACT', '')
        self.template = os.environ.get('WA_TEMPLATE', '')
        self.tag = os.environ.get('wa_TAG', os.environ.get('WA_TAG', 'Whatsapp'))
        # 7th template parameter (hospital/clinic name)
        self.hospital_name = os.environ.get('WA_HOSPITAL_NAME', 'Adhiparasakthi Hospitals')
        
        # Validate configuration
        if self.enabled:
            # Auto-enable test mode in development if credentials are missing
            is_production = os.environ.get('FLASK_ENV', 'development').lower() == 'production'
            # Template is required for template API
            credentials_missing = not all([self.license_number, self.api_key, self.contact, self.template])
            
            # Auto-enable test mode in development if credentials are missing
            if credentials_missing and not is_production and not self.test_mode:
                logger.info("WhatsApp API credentials not configured. Auto-enabling TEST MODE for development.")
                logger.info("Messages will be simulated (not actually sent). Set WHATSAPP_TEST_MODE=false to disable.")
                self.test_mode = True
            
            # Test mode allows sending without real credentials (for development/testing)
            if self.test_mode:
                logger.info("WhatsApp service running in TEST MODE - messages will be simulated (not actually sent)")
                self.enabled = True  # Keep enabled for test mode
            elif credentials_missing:
                logger.warning("WhatsApp API not fully configured. WhatsApp messages will be disabled.")
                logger.warning("Required: WA_LICENSE_NUMBER, WA_API_KEY, WA_CONTACT, WA_TEMPLATE")
                logger.warning("Optional: WA_BASE_URL (defaults to sendtemplate.php), wa_TAG")
                logger.warning("Or set WHATSAPP_TEST_MODE=true to simulate messages for testing")
                self.enabled = False
            else:
                logger.info(f"WhatsApp service configured: {self.base_url}")
                if self.template:
                    logger.info(f"Using template: {self.template}")
                else:
                    logger.warning("WA_TEMPLATE not set - template messages require a template name")
    
    def send_booking_confirmation(
        self, 
        phone_number: str, 
        patient_name: str, 
        booking_reference: str,
        booking_date: str,
        booking_time: str,
        package_name: str,
        total_price: float
    ) -> Tuple[bool, str]:
        """
        Send booking confirmation WhatsApp message
        
        Args:
            phone_number: Patient's phone number (with country code, e.g., +91XXXXXXXXXX)
            patient_name: Patient's name
            booking_reference: Booking reference ID
            booking_date: Booking date (formatted string)
            booking_time: Booking time
            package_name: Package name
            total_price: Total price
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            return False, "WhatsApp service is disabled"
        
        if not phone_number:
            return False, "Phone number is required"
        
        # Format phone number (remove + and spaces for API)
        phone_number = self._format_phone_number(phone_number)
        
        # Test mode: Simulate sending without actual API call
        if self.test_mode:
            logger.info(f"[TEST MODE] Simulating WhatsApp message to {phone_number}")
            logger.info(f"[TEST MODE] Template: {self.template}")
            logger.info(f"[TEST MODE] Patient: {patient_name}, Reference: {booking_reference}")
            return True, "Message sent successfully (TEST MODE - not actually sent)"
        
        # Send message via S3 InfoSystem Template API
        try:
            return self._send_via_template_api(
                phone_number, patient_name, booking_reference, 
                booking_date, booking_time, package_name, total_price
            )
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False, f"Error sending WhatsApp message: {str(e)}"
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for API (remove + and spaces)"""
        phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
        
        # If phone doesn't start with country code, assume it's Indian number and add 91
        if not phone.startswith('91') and len(phone) == 10:
            phone = '91' + phone
        elif phone.startswith('91') and len(phone) == 12:
            pass  # Already has country code
        elif len(phone) == 11 and phone.startswith('0'):
            # Remove leading 0 and add 91
            phone = '91' + phone[1:]
        
        return phone
    
    def _send_via_template_api(
        self, 
        phone_number: str, 
        patient_name: str,
        booking_reference: str,
        booking_date: str,
        booking_time: str,
        package_name: str,
        total_price: float
    ) -> Tuple[bool, str]:
        """Send WhatsApp message via S3 InfoSystem Template API (GET method)"""
        try:
            if not self.template:
                return False, "Template name (WA_TEMPLATE) is required for template messages"
            
            # Prepare template parameters (comma-separated values)
            # IMPORTANT: Your template expects 7 parameters in this exact order:
            # 1. Patient Name
            # 2. Booking Reference
            # 3. Booking Date
            # 4. Booking Time
            # 5. Package Name
            # 6. Total Price
            # 7. Hospital/Clinic Name
            template_params = [
                str(patient_name).strip(),           # Template variable {{1}} - Patient Name
                str(booking_reference).strip(),      # Template variable {{2}} - Booking Reference
                str(booking_date).strip(),           # Template variable {{3}} - Booking Date
                str(booking_time).strip(),           # Template variable {{4}} - Booking Time
                str(package_name).strip(),           # Template variable {{5}} - Package Name
                str(int(total_price)),               # Template variable {{6}} - Total Price (integer, no currency symbol)
                str(self.hospital_name).strip()      # Template variable {{7}} - Hospital/Clinic Name
            ]
            # Join with commas - don't URL encode the Param field, keep commas as-is
            param_string = ','.join(template_params)
            
            # Prepare query parameters for GET request
            # According to API docs: Contact is the recipient phone number (format: 91XXXXXXXXXX)
            params = {
                'LicenseNumber': str(self.license_number),
                'APIKey': str(self.api_key),
                'Contact': phone_number,  # Recipient phone number (format: 91XXXXXXXXXX, no + sign)
                'Template': str(self.template),
                'Param': param_string  # Comma-separated template variables
            }
            
            # Note: Param should NOT be URL encoded - commas must remain as commas
            # requests.get will handle URL encoding, but we need to preserve commas in Param
            
            # Optional parameters (if needed)
            # params['Fileurl'] = ''  # If template requires file
            # params['URLParam'] = ''  # If template has URL button
            # params['HeadURL'] = ''  # If template has header image
            # params['HeadParam'] = ''  # Header parameters
            # params['Name'] = ''  # Name parameter
            # params['PDFName'] = ''  # PDF name if sending PDF
            
            # Send GET request to the API
            # requests.get will handle URL encoding properly, including commas in Param
            logger.info("=" * 80)
            logger.info("WHATSAPP API REQUEST DETAILS:")
            logger.info("=" * 80)
            logger.info(f"Base URL: {self.base_url}")
            logger.info(f"Recipient Phone: {phone_number}")
            logger.info(f"Template: {self.template}")
            logger.info("")
            logger.info("Parameters being sent:")
            logger.info(f"  LicenseNumber = {self.license_number}")
            logger.info(f"  APIKey = {self.api_key}")
            logger.info(f"  Contact = {phone_number}")
            logger.info(f"  Template = {self.template}")
            logger.info(f"  Param = {param_string}")
            logger.info("")
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=15
            )
            
            # Log the actual URL that was called (for Postman testing)
            logger.info("=" * 80)
            logger.info("FULL API URL (Copy this to Postman):")
            logger.info("=" * 80)
            logger.info(response.url)
            logger.info("=" * 80)
            
            # Log the response for debugging
            logger.info(f"WhatsApp API Response Status: {response.status_code}")
            logger.info(f"WhatsApp API Response Headers: {dict(response.headers)}")
            logger.info(f"WhatsApp API Response Text: {response.text}")
            logger.info(f"WhatsApp API Response URL: {response.url}")
            
            # Check if request was successful
            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Try to parse JSON response
                try:
                    import json
                    response_json = json.loads(response_text)
                    
                    # Check for ApiResponse field (common in this API)
                    if 'ApiResponse' in response_json:
                        api_response = str(response_json['ApiResponse']).lower()
                        
                        # Check for error indicators
                        error_keywords = ['invalid', 'error', 'failed', 'fail', 'denied', 'unauthorized']
                        if any(keyword in api_response for keyword in error_keywords):
                            error_msg = response_json['ApiResponse']
                            logger.error(f"WhatsApp API error: {error_msg}")
                            return False, f"API error: {error_msg}"
                        
                        # Check for success indicators
                        success_keywords = ['success', 'sent', 'delivered', 'queued']
                        if any(keyword in api_response for keyword in success_keywords):
                            logger.info(f"WhatsApp message sent successfully to {phone_number}")
                            return True, "Message sent successfully"
                        
                        # If no clear indicator, check the response text
                        if 'success' in api_response or 'sent' in api_response:
                            logger.info(f"WhatsApp message sent successfully to {phone_number}")
                            return True, "Message sent successfully"
                        else:
                            # Unknown response format - treat as error if it contains error-like words
                            if any(keyword in api_response for keyword in ['invalid', 'error']):
                                error_msg = response_json['ApiResponse']
                                logger.error(f"WhatsApp API error: {error_msg}")
                                return False, f"API error: {error_msg}"
                            else:
                                # Unknown response - log and treat as success (might be a new format)
                                logger.warning(f"Unknown API response format: {response_json}")
                                return True, f"Message sent (Response: {response_json.get('ApiResponse', 'Unknown')})"
                    
                    # If no ApiResponse field, check other common fields
                    if 'status' in response_json:
                        status = str(response_json['status']).lower()
                        if status in ['success', 'sent', 'delivered']:
                            logger.info(f"WhatsApp message sent successfully to {phone_number}")
                            return True, "Message sent successfully"
                        elif status in ['error', 'failed', 'fail']:
                            error_msg = response_json.get('message', 'Unknown error')
                            logger.error(f"WhatsApp API error: {error_msg}")
                            return False, f"API error: {error_msg}"
                    
                except (json.JSONDecodeError, ValueError) as e:
                    # Not JSON, check as plain text
                    logger.warning(f"Response is not JSON, parsing as text. JSON error: {str(e)}")
                    response_lower = response_text.lower()
                    
                    # Check for error indicators in plain text
                    error_keywords = ['invalid', 'error', 'failed', 'fail', 'denied', 'unauthorized']
                    if any(keyword in response_lower for keyword in error_keywords):
                        logger.error(f"WhatsApp API error (plain text): {response_text[:200]}")
                        return False, f"API error: {response_text[:200]}"
                    
                    # Check for success indicators
                    success_keywords = ['success', 'sent', 'delivered', 'queued', 'accepted']
                    if any(keyword in response_lower for keyword in success_keywords):
                        logger.info(f"WhatsApp message sent successfully to {phone_number}")
                        return True, "Message sent successfully"
                    
                    # Unknown response format - if it's short, might be a status code
                    if len(response_text) < 50:
                        logger.warning(f"Short API response (might be status): {response_text}")
                        # If it's just "Fail" or similar, treat as error
                        if response_lower in ['fail', 'error', 'failed']:
                            return False, f"API returned: {response_text}"
                        # Otherwise, might be a success code we don't recognize
                        return False, f"Unknown API response: {response_text}"
                    else:
                        logger.warning(f"Unknown API response format: {response_text[:200]}")
                        return False, f"Unknown API response: {response_text[:200]}"
            else:
                error_msg = f'HTTP {response.status_code}: {response.text[:200]}'
                logger.error(f"WhatsApp API error: {error_msg}")
                return False, f"API error: {error_msg}"
                
        except requests.exceptions.Timeout:
            logger.error(f"WhatsApp API request timeout for {phone_number}")
            return False, "Request timeout - API did not respond in time"
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API request exception: {str(e)}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending via API: {str(e)}")
            return False, f"Error: {str(e)}"


# Global instance
whatsapp_service = WhatsAppService()
