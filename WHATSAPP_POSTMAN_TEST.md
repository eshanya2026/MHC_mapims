# WhatsApp API Testing Guide - Postman

## How to Test WhatsApp API in Postman

### Step 1: Open Postman
1. Open Postman application
2. Click "New" → "HTTP Request"
3. Select **GET** method from the dropdown

### Step 2: Enter the Base URL
```
https://wa.s3infosystem.in/api/sendtemplate.php
```

### Step 3: Add Query Parameters
Click on the **Params** tab and add these parameters:

| Key | Value | Description |
|-----|-------|-------------|
| `LicenseNumber` | `15142666871` | Your license number |
| `APIKey` | `Jzay1hHu6eQO8tYn3WRGcqMjF` | Your API key |
| `Contact` | `91XXXXXXXXXX` | Recipient phone number (format: 91XXXXXXXXXX, no + sign) |
| `Template` | `appointment_healthcheck_fasting` | Your template name |
| `Param` | `Patient Name,Booking Ref,Date,Time,Package,Price` | Comma-separated template variables |

### Step 4: Example Test Request

**URL (will be auto-generated):**
```
https://wa.s3infosystem.in/api/sendtemplate.php?LicenseNumber=15142666871&APIKey=Jzay1hHu6eQO8tYn3WRGcqMjF&Contact=919047910212&Template=appointment_healthcheck_fasting&Param=John%20Doe,MAP20250101120000,01-01-2025,08:00,Premium%20Health%20Checkup,1799
```

**Parameters Breakdown:**
- `LicenseNumber`: `15142666871`
- `APIKey`: `Jzay1hHu6eQO8tYn3WRGcqMjF`
- `Contact`: `919047910212` (recipient phone - format: 91XXXXXXXXXX)
- `Template`: `appointment_healthcheck_fasting`
- `Param`: `John Doe,MAP20250101120000,01-01-2025,08:00,Premium Health Checkup,1799`
  - This is comma-separated values matching your template variables
  - Order matters! Must match your template variable order

### Step 5: Send Request
1. Click **Send** button
2. Check the response in the bottom panel

### Step 6: Check Response

**Success Response Example:**
```json
{
  "ApiResponse": "Success"
}
```
or
```json
{
  "ApiResponse": "Message sent successfully"
}
```

**Error Response Example:**
```json
{
  "ApiResponse": "Fail"
}
```
or
```json
{
  "ApiResponse": "Invalid license number / api key"
}
```

### Common Issues & Solutions

#### Issue 1: "Invalid license number / api key"
- **Solution**: Double-check `LicenseNumber` and `APIKey` are correct
- Make sure there are no extra spaces

#### Issue 2: "Fail" response
- **Possible causes:**
  - Template name doesn't match exactly (case-sensitive)
  - Template parameter order doesn't match template variables
  - Phone number format is wrong (should be 91XXXXXXXXXX)
  - Template requires different number of parameters

#### Issue 3: Phone number format
- **Correct format**: `91XXXXXXXXXX` (12 digits total)
- **Wrong formats**: 
  - `+919047910212` (has + sign)
  - `9190479102120` (too many digits)
  - `9047910212` (missing country code)

### Step 7: Get the Exact URL from Your App

After creating a booking in your app, check the terminal logs. You'll see:

```
================================================================================
FULL API URL (Copy this to Postman):
================================================================================
https://wa.s3infosystem.in/api/sendtemplate.php?LicenseNumber=...&APIKey=...&...
================================================================================
```

Copy that exact URL and paste it directly into Postman's URL bar to test.

### Step 8: Verify Template Parameters

Your template `appointment_healthcheck_fasting` expects parameters in a specific order. 

**Current order in code:**
1. Patient Name
2. Booking Reference
3. Booking Date
4. Booking Time
5. Package Name
6. Total Price

**If your template expects different order**, you need to:
1. Check your WhatsApp template configuration
2. Adjust the `template_params` array in `whatsapp_service.py` to match

### Testing Checklist

- [ ] Base URL is correct: `https://wa.s3infosystem.in/api/sendtemplate.php`
- [ ] Method is **GET** (not POST)
- [ ] LicenseNumber matches your credentials
- [ ] APIKey matches your credentials
- [ ] Contact is recipient phone in format `91XXXXXXXXXX`
- [ ] Template name matches exactly (case-sensitive)
- [ ] Param values are comma-separated
- [ ] Param order matches your template variable order
- [ ] Phone number is valid and has correct format

### Quick Test URL

Replace `YOUR_PHONE` with a test number (format: 91XXXXXXXXXX):

```
https://wa.s3infosystem.in/api/sendtemplate.php?LicenseNumber=15142666871&APIKey=Jzay1hHu6eQO8tYn3WRGcqMjF&Contact=YOUR_PHONE&Template=appointment_healthcheck_fasting&Param=Test%20Patient,MAP123456,19-12-2025,10:00,Test%20Package,999
```

### Debugging Tips

1. **Test with minimal parameters first**: Try with just LicenseNumber, APIKey, Contact, and Template (no Param) to see if credentials work
2. **Check template name**: Make sure `appointment_healthcheck_fasting` is the exact name in your WhatsApp Business account
3. **Verify parameter count**: Your template might expect fewer or more parameters
4. **Check phone number**: Make sure the recipient number is registered/verified in your WhatsApp Business account

