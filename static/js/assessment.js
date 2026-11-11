// Assessment Form JavaScript

let currentStep = 1;
const totalSteps = 4;
let recognition = null;
let isRecording = false;

// Initialize Web Speech API for voice input
function initSpeechRecognition() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported in this browser');
        return false;
    }

    try {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        // Get current language (with fallback)
        const lang = (typeof currentLanguage !== 'undefined' && currentLanguage === 'ta') ? 'ta-IN' : 'en-IN';
        recognition.lang = lang;

        recognition.onresult = function (event) {
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                }
            }

            // Voice input feature removed with symptoms step
        };

        recognition.onerror = function (event) {
            console.error('Speech recognition error:', event.error);

            let errorMessage = 'Speech recognition error: ';
            switch (event.error) {
                case 'no-speech':
                    errorMessage = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    errorMessage = 'Microphone not found. Please check your microphone.';
                    break;
                case 'not-allowed':
                    errorMessage = 'Microphone permission denied. Please allow microphone access.';
                    break;
                case 'network':
                    errorMessage = 'Network error. Please check your connection.';
                    break;
                default:
                    errorMessage = 'Speech recognition error: ' + event.error;
            }

            // Show user-friendly error
            const voiceStatus = document.getElementById('voiceStatus');
            if (voiceStatus) {
                const statusText = document.getElementById('voiceStatusText');
                if (statusText) {
                    statusText.textContent = errorMessage;
                    statusText.style.color = '#E31837';
                }
            }

            stopVoiceInput();
        };

        recognition.onend = function () {
            if (isRecording) {
                // Restart if still recording (for continuous mode)
                try {
                    setTimeout(() => {
                        if (isRecording && recognition) {
                            recognition.start();
                        }
                    }, 100);
                } catch (e) {
                    console.error('Error restarting recognition:', e);
                    stopVoiceInput();
                }
            }
        };

        recognition.onstart = function () {
            console.log('Speech recognition started');
            const voiceStatus = document.getElementById('voiceStatus');
            if (voiceStatus) {
                const statusText = document.getElementById('voiceStatusText');
                if (statusText) {
                    statusText.textContent = 'Recording... Speak now';
                    statusText.style.color = '#E31837';
                }
            }
        };

        return true;
    } catch (error) {
        console.error('Error initializing speech recognition:', error);
        return false;
    }
}

// Language toggle function
function toggleLanguage() {
    const newLang = currentLanguage === 'en' ? 'ta' : 'en';
    setLanguage(newLang);
}

// Validate age input - prevent values greater than 120
function validateAgeInput(event) {
    const ageField = event.target;
    let value = ageField.value;

    // Remove any non-numeric characters
    value = value.replace(/[^0-9]/g, '');

    // If value is greater than 120, limit it to 120
    if (value && parseInt(value) > 120) {
        value = '120';
    }

    ageField.value = value;
}

// Validate age on change
function validateAge() {
    const ageField = document.getElementById('age');
    if (!ageField) return;

    const age = parseInt(ageField.value);

    if (ageField.value && (isNaN(age) || age < 1 || age > 120)) {
        ageField.setCustomValidity('Age must be between 1 and 120');
        ageField.style.borderColor = '#E31837';
    } else {
        ageField.setCustomValidity('');
        ageField.style.borderColor = '';
    }
}

// Validate phone input - allow only digits and limit to 10
function validatePhoneInput(event) {
    const phoneField = event.target;
    let value = phoneField.value;

    // Remove any non-digit characters (including spaces, dashes, country codes)
    value = value.replace(/[^0-9]/g, '');

    // Limit to 10 digits
    if (value.length > 10) {
        value = value.substring(0, 10);
    }

    phoneField.value = value;
}

// Validate phone on change
function validatePhone() {
    const phoneField = document.getElementById('phone');
    if (!phoneField) return;

    const phone = phoneField.value.replace(/[^0-9]/g, '');

    if (phoneField.value && phone.length !== 10) {
        phoneField.setCustomValidity('Phone number must be exactly 10 digits');
        phoneField.style.borderColor = '#E31837';
    } else {
        phoneField.setCustomValidity('');
        phoneField.style.borderColor = '';
    }
}

// Check and show/hide dynamic fields based on age and gender
function checkDynamicFields() {
    const age = parseInt(document.getElementById('age')?.value) || 0;
    const gender = document.getElementById('gender')?.value || '';

    const femaleFields = document.getElementById('femaleFields');
    const age40Fields = document.getElementById('age40Fields');
    const pediatricFields = document.getElementById('pediatricFields');

    // Hide all dynamic sections first
    if (femaleFields) femaleFields.style.display = 'none';
    if (age40Fields) age40Fields.style.display = 'none';
    if (pediatricFields) pediatricFields.style.display = 'none';

    // Validate age (only check if age exists and is positive)
    if (!age || age < 1) {
        return; // Invalid age
    }

    // CHILDREN AND TEENAGERS (< 18 years)
    if (age < 18) {
        // Always show pediatric fields for children
        if (pediatricFields) {
            pediatricFields.style.display = 'block';
        }

        // No adult screening questions for children
        return;
    }

    // ADULTS (age 18+)
    if (age >= 18) {
        // Show Women's Health section for females
        if (gender === 'female' && femaleFields) {
            femaleFields.style.display = 'block';
        }

        // Show age 40+ screening fields
        if (age >= 40 && age40Fields) {
            age40Fields.style.display = 'block';
        }
    }
}


// Toggle pediatric details textarea
function togglePediatricDetails() {
    const yesRadio = document.querySelector('input[name="pediatric_concerns"][value="yes"]');
    const detailsField = document.getElementById('pediatric_details_field');
    if (yesRadio && detailsField) {
        detailsField.style.display = yesRadio.checked ? 'block' : 'none';
    }
}

// Voice input functions
function toggleVoiceInput() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari for voice input.');
        return;
    }

    // Initialize if not already done
    if (!recognition) {
        const initialized = initSpeechRecognition();
        if (!initialized) {
            alert('Failed to initialize voice input. Please refresh the page and try again.');
            return;
        }
    }

    if (isRecording) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

function startVoiceInput() {
    if (!recognition) {
        const initialized = initSpeechRecognition();
        if (!initialized) {
            alert('Speech recognition is not available. Please use Chrome, Edge, or Safari.');
            return;
        }
    }

    // Check if mediaDevices is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Microphone access is not available in this browser. Please use a modern browser like Chrome, Edge, or Safari.');
        return;
    }

    // Request microphone permission
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            // Permission granted, start recognition
            try {
                // Update language if needed
                const lang = (typeof currentLanguage !== 'undefined' && currentLanguage === 'ta') ? 'ta-IN' : 'en-IN';
                recognition.lang = lang;

                recognition.start();
                isRecording = true;

                const voiceBtn = document.getElementById('voiceInputBtn');
                const voiceStatus = document.getElementById('voiceStatus');
                const voiceIcon = document.getElementById('voiceIcon');
                const voiceText = document.getElementById('voiceText');

                if (voiceBtn) {
                    voiceBtn.classList.add('recording');
                    voiceBtn.style.background = '#E31837';
                    voiceBtn.style.color = '#FFFFFF';
                }
                if (voiceStatus) {
                    voiceStatus.style.display = 'flex';
                }
                if (voiceIcon) {
                    voiceIcon.textContent = '🔴';
                }
                if (voiceText) {
                    voiceText.textContent = 'Recording... Speak now';
                }

                // Store stream to stop it later
                window.voiceStream = stream;
            } catch (error) {
                console.error('Error starting voice input:', error);
                // Stop the stream if recognition fails
                if (window.voiceStream) {
                    window.voiceStream.getTracks().forEach(track => track.stop());
                    window.voiceStream = null;
                }
                if (error.name === 'InvalidStateError') {
                    alert('Voice input is already running. Please stop it first.');
                } else {
                    alert('Error starting voice input: ' + error.message);
                }
            }
        })
        .catch((error) => {
            console.error('Microphone permission error:', error);
            let errorMessage = 'Microphone permission is required for voice input.';

            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage = 'Microphone permission denied. Please:\n1. Click the lock icon in your browser address bar\n2. Allow microphone access\n3. Refresh the page and try again';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage = 'No microphone found. Please:\n1. Connect a microphone to your device\n2. Check your system settings\n3. Refresh the page and try again';
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                errorMessage = 'Microphone is being used by another application. Please close other apps using the microphone and try again.';
            } else {
                errorMessage = 'Microphone access error: ' + error.message + '\n\nPlease check your browser settings and try again.';
            }

            // Show error in UI
            const voiceStatus = document.getElementById('voiceStatus');
            if (voiceStatus) {
                const statusText = document.getElementById('voiceStatusText');
                if (statusText) {
                    statusText.textContent = errorMessage.split('\n')[0];
                    statusText.style.color = '#E31837';
                }
                voiceStatus.style.display = 'flex';
            }

            alert(errorMessage);
        });
}

function stopVoiceInput() {
    if (recognition && isRecording) {
        try {
            recognition.stop();
        } catch (e) {
            console.error('Error stopping recognition:', e);
        }
        isRecording = false;
    }

    // Stop the audio stream
    if (window.voiceStream) {
        window.voiceStream.getTracks().forEach(track => track.stop());
        window.voiceStream = null;
    }

    const voiceBtn = document.getElementById('voiceInputBtn');
    const voiceStatus = document.getElementById('voiceStatus');
    const voiceIcon = document.getElementById('voiceIcon');
    const voiceText = document.getElementById('voiceText');

    if (voiceBtn) {
        voiceBtn.classList.remove('recording');
        voiceBtn.style.background = '';
        voiceBtn.style.color = '';
    }
    if (voiceStatus) {
        voiceStatus.style.display = 'none';
    }
    if (voiceIcon) {
        voiceIcon.textContent = '🎤';
    }
    if (voiceText) {
        voiceText.textContent = 'Voice Input';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Check browser support for speech recognition
    const speechSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

    if (!speechSupported) {
        // Show warning and disable voice input button if not supported
        const voiceBtn = document.getElementById('voiceInputBtn');
        const voiceWarning = document.getElementById('voiceBrowserWarning');

        if (voiceBtn) {
            voiceBtn.style.opacity = '0.6';
            voiceBtn.style.cursor = 'not-allowed';
            voiceBtn.title = 'Voice input not supported in this browser. Use Chrome, Edge, or Safari.';
            voiceBtn.onclick = function () {
                alert('Voice input is not supported in this browser.\n\nPlease use one of these browsers:\n• Google Chrome\n• Microsoft Edge\n• Safari (Mac/iOS)\n\nFirefox does not support Web Speech API.');
            };
        }

        if (voiceWarning) {
            voiceWarning.style.display = 'block';
            voiceWarning.innerHTML = '<strong>⚠️ Browser Not Supported:</strong> Voice input requires Chrome, Edge, or Safari. Please use one of these browsers for voice input feature.';
        }
    } else {
        // Show helpful message for supported browsers
        const voiceWarning = document.getElementById('voiceBrowserWarning');
        if (voiceWarning) {
            voiceWarning.style.display = 'block';
            voiceWarning.style.background = '#d1ecf1';
            voiceWarning.style.borderColor = '#17a2b8';
            voiceWarning.style.color = '#0c5460';
            voiceWarning.innerHTML = '<strong>💡 Tip:</strong> Click the microphone button to start voice input. Make sure your microphone is connected and browser permissions are granted.';
        }
        console.log('✅ Speech recognition is supported in this browser');
    }

    // Initialize Stepper Progress and Question Card listeners
    updateStepperProgress();
    setupQuestionCardListeners();

    // Set up dynamic field checking
    const ageField = document.getElementById('age');
    const genderField = document.getElementById('gender');
    const phoneField = document.getElementById('phone');

    if (ageField) {
        ageField.addEventListener('change', checkDynamicFields);
        ageField.addEventListener('input', checkDynamicFields);
    }
    if (genderField) {
        genderField.addEventListener('change', checkDynamicFields);
    }
    if (phoneField) {
        phoneField.addEventListener('blur', validatePhone);
    }

    // Set up BMI calculation
    const weightField = document.getElementById('weight');
    const heightField = document.getElementById('height');

    if (weightField && heightField) {
        weightField.addEventListener('input', calculateBMI);
        weightField.addEventListener('change', calculateBMI);
        heightField.addEventListener('input', calculateBMI);
        heightField.addEventListener('change', calculateBMI);

        if (weightField.value && heightField.value) {
            calculateBMI();
        }
    }

    // Prefill from Quick Start URL parameters if present
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const pGender = urlParams.get('gender');
        const pAge = urlParams.get('age');
        
        if (pGender) {
            const genderSelect = document.getElementById('gender');
            if (genderSelect) {
                genderSelect.value = pGender;
            }
        }
        if (pAge) {
            const ageInput = document.getElementById('age');
            if (ageInput) {
                ageInput.value = pAge;
            }
        }
        if (pGender || pAge) {
            const nameInput = document.getElementById('name');
            if (nameInput) setTimeout(() => nameInput.focus(), 250);
        }
    } catch(err) {
        console.warn('URL params prefill skipped:', err);
    }

    // Run dynamic fields check after initial load / prefill
    checkDynamicFields();
});

function setupQuestionCardListeners() {
    const radioInputs = document.querySelectorAll('.condition-question-card input[type="radio"], .symptom-question-card input[type="radio"]');
    radioInputs.forEach(input => {
        input.addEventListener('change', function() {
            const card = this.closest('.condition-question-card, .symptom-question-card');
            if (card) {
                card.classList.add('card-answered');
            }
        });
        if (input.checked) {
            const card = input.closest('.condition-question-card, .symptom-question-card');
            if (card) card.classList.add('card-answered');
        }
    });
}

function updateStepperProgress() {
    const total = totalSteps || 4;
    const pct = Math.round((currentStep / total) * 100);
    
    const fillBar = document.getElementById('stepperFillBar');
    if (fillBar) fillBar.style.width = pct + '%';

    const counterBadge = document.getElementById('stepCounterBadge');
    if (counterBadge) counterBadge.textContent = `Step ${currentStep} of ${total}`;

    const percentBadge = document.getElementById('stepPercentBadge');
    if (percentBadge) percentBadge.textContent = `${pct}% Completed`;

    const stepNames = {
        1: 'Basic Information',
        2: 'Medical History',
        3: 'Lifestyle & Habits',
        4: 'Special Health Details'
    };
    const stepNameBadge = document.getElementById('stepNameBadge');
    if (stepNameBadge && stepNames[currentStep]) {
        stepNameBadge.textContent = stepNames[currentStep];
    }

    // Update progress steps indicators
    for (let i = 1; i <= total; i++) {
        const stepEl = document.querySelector(`.progress-step[data-step="${i}"]`);
        if (stepEl) {
            if (i < currentStep) {
                stepEl.classList.add('completed');
                stepEl.classList.remove('active');
                const circle = stepEl.querySelector('.step-circle');
                if (circle) circle.innerHTML = '✓';
            } else if (i === currentStep) {
                stepEl.classList.add('active');
                stepEl.classList.remove('completed');
                const circle = stepEl.querySelector('.step-circle');
                if (circle) circle.innerHTML = i;
            } else {
                stepEl.classList.remove('active', 'completed');
                const circle = stepEl.querySelector('.step-circle');
                if (circle) circle.innerHTML = i;
            }
        }
    }
}

// Calculate BMI on weight/height change
function calculateBMI() {
    const weightField = document.getElementById('weight');
    const heightField = document.getElementById('height');
    const bmiDisplay = document.getElementById('bmiDisplay');
    const bmiValue = document.getElementById('bmiValue');
    const bmiCategory = document.getElementById('bmiCategory');

    if (!weightField || !heightField) return;
    if (!bmiDisplay || !bmiValue || !bmiCategory) return;

    const weight = parseFloat(weightField.value);
    const height = parseFloat(heightField.value);

    // Validate inputs
    if (isNaN(weight) || isNaN(height) || weight <= 0 || height <= 0) {
        bmiDisplay.style.display = 'none';
        bmiDisplay.style.visibility = 'hidden';
        return;
    }

    // Calculate BMI: BMI = weight (kg) / height (m)²
    const heightM = height / 100;
    const bmi = (weight / (heightM * heightM)).toFixed(1);
    const category = getBMICategory(parseFloat(bmi));

    // Update display
    bmiDisplay.style.display = 'block';
    bmiDisplay.style.visibility = 'visible';
    bmiValue.textContent = bmi;
    bmiCategory.textContent = category;

    // Highlight visual zone
    const zones = bmiDisplay.querySelectorAll('.bmi-zone');
    zones.forEach(z => z.classList.remove('zone-active'));
    const bmiNum = parseFloat(bmi);
    if (bmiNum < 18.5) {
        const z = bmiDisplay.querySelector('.zone-under');
        if (z) z.classList.add('zone-active');
        bmiCategory.className = 'bmi-cat-under';
    } else if (bmiNum < 25) {
        const z = bmiDisplay.querySelector('.zone-normal');
        if (z) z.classList.add('zone-active');
        bmiCategory.className = 'bmi-cat-normal';
    } else if (bmiNum < 30) {
        const z = bmiDisplay.querySelector('.zone-over');
        if (z) z.classList.add('zone-active');
        bmiCategory.className = 'bmi-cat-over';
    } else {
        const z = bmiDisplay.querySelector('.zone-obese');
        if (z) z.classList.add('zone-active');
        bmiCategory.className = 'bmi-cat-obese';
    }
}

function getBMICategory(bmi) {
    const lang = (typeof currentLanguage !== 'undefined' && currentLanguage === 'ta') ? 'ta' : 'en';
    if (bmi < 18.5) return lang === 'ta' ? 'குறைந்த எடை' : 'Underweight';
    if (bmi < 25) return lang === 'ta' ? 'இயல்பான' : 'Normal Weight';
    if (bmi < 30) return lang === 'ta' ? 'அதிக எடை' : 'Overweight';
    return lang === 'ta' ? 'உடல் பருமன்' : 'Obese';
}

function nextStep() {
    if (currentStep < totalSteps) {
        // Validate current step
        const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#E31837';
            } else {
                field.style.borderColor = '';
            }
        });

        if (!isValid) {
            alert(typeof t !== 'undefined' ? t('common.fillRequired') : 'Please fill in all required fields');
            return;
        }

        // Check age validation for step 1
        if (currentStep === 1) {
            const ageField = document.getElementById('age');
            if (ageField && ageField.value) {
                const age = parseInt(ageField.value);
                if (!isNaN(age) && age > 120) {
                    alert('Age cannot be greater than 120. Please enter a valid age.');
                    ageField.style.borderColor = '#E31837';
                    ageField.focus();
                    return;
                }
            }
        }

        // Move to next step
        document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.remove('active');

        currentStep++;

        document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');
        updateStepperProgress();

        // Scroll to top of the page
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.remove('active');

        currentStep--;

        document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');
        updateStepperProgress();

        // Scroll to top of the page
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Form submission
document.getElementById('assessmentForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Show loading
    document.getElementById('loadingOverlay').style.display = 'flex';

    // Stop voice input if recording
    if (isRecording) {
        stopVoiceInput();
    }

    // Collect basic info
    const name = document.getElementById('name').value.trim();
    const age = parseInt(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const phone = document.getElementById('phone').value.trim();
    const weightValue = document.getElementById('weight')?.value.trim() || '';
    const heightValue = document.getElementById('height')?.value.trim() || '';
    const weight = parseFloat(weightValue);
    const height = parseFloat(heightValue);
    const email = document.getElementById('email')?.value.trim() || '';
    const preferredContact = document.getElementById('preferred_contact')?.value || '';

    // Validate required fields before submission
    if (!name || !age || !gender || !phone) {
        alert('Please fill in all required fields (marked with *)');
        document.getElementById('loadingOverlay').style.display = 'none';
        return;
    }

    // Validate age is positive
    if (age < 1) {
        alert('Age must be at least 1');
        document.getElementById('age')?.focus();
        document.getElementById('loadingOverlay').style.display = 'none';
        return;
    }

    // Validate phone number (must be exactly 10 digits)
    const phoneDigits = phone.replace(/[^0-9]/g, '');
    if (phoneDigits.length !== 10) {
        alert('Phone number must be exactly 10 digits');
        document.getElementById('phone')?.focus();
        document.getElementById('loadingOverlay').style.display = 'none';
        return;
    }

    // Validate weight and height as numeric strings
    if (!weightValue || isNaN(weight) || weight <= 0) {
        alert('Please enter a valid weight (kg)');
        document.getElementById('weight')?.focus();
        document.getElementById('loadingOverlay').style.display = 'none';
        return;
    }

    if (!heightValue || isNaN(height) || height <= 0) {
        alert('Please enter a valid height (cm)');
        document.getElementById('height')?.focus();
        document.getElementById('loadingOverlay').style.display = 'none';
        return;
    }

    // Collect medical conditions (Step 2) - Yes/No/Not sure
    const conditions = {};
    const conditionFields = ['diabetes', 'hypertension', 'heart_disease', 'thyroid', 'asthma', 'kidney'];
    conditionFields.forEach(condition => {
        const radio = document.querySelector(`input[name="condition_${condition}"]:checked`);
        conditions[`condition_${condition}`] = radio ? radio.value : 'no';
    });
    const otherConditions = document.getElementById('other_conditions')?.value.trim() || '';

    // Collect family history (Step 3)
    const familyHistory = {};
    const familyFields = ['diabetes', 'heart_disease'];
    familyFields.forEach(field => {
        const radio = document.querySelector(`input[name="family_${field}"]:checked`);
        familyHistory[`family_${field}`] = radio ? radio.value : 'no';
    });

    // Collect lifestyle fields (Step 4)
    const sleepHours = document.getElementById('sleep_hours')?.value || '';
    const exerciseFrequency = document.getElementById('exercise_frequency')?.value || '';
    const smokingStatus = document.getElementById('smoking_status')?.value || '';
    const alcoholConsumption = document.getElementById('alcohol_consumption')?.value || '';
    const dietType = document.getElementById('diet_type')?.value || '';
    const lifestyleOther = document.getElementById('lifestyle_other')?.value.trim() || '';

    // Build form data
    const formData = {
        name: name,
        age: age,
        gender: gender,
        phone: phone,
        email: email,
        preferred_contact: preferredContact,
        weight: weight,
        height: height,
        // Medical conditions
        ...conditions,
        other_conditions: otherConditions,
        // Family history
        ...familyHistory,
        // Lifestyle
        sleep_hours: sleepHours,
        exercise_frequency: exerciseFrequency,
        smoking_status: smokingStatus,
        alcohol_consumption: alcoholConsumption,
        diet_type: dietType,
        lifestyle_other: lifestyleOther,
        consent: false
    };

    // Add Women's Health fields if visible (Step 4)
    const femaleFields = document.getElementById('femaleFields');
    if (femaleFields && femaleFields.style.display !== 'none') {
        const pregnant = document.querySelector('input[name="pregnant"]:checked');
        const menstrualRegular = document.querySelector('input[name="menstrual_regular"]:checked');
        const menopauseStatus = document.querySelector('input[name="menopause_status"]:checked');
        formData.pregnant = pregnant ? pregnant.value : null;
        formData.menstrual_regular = menstrualRegular ? menstrualRegular.value : null;
        formData.menopause_status = menopauseStatus ? menopauseStatus.value : null;
    }

    // Add age 40+ fields if visible (Step 5)
    const age40Fields = document.getElementById('age40Fields');
    if (age40Fields && age40Fields.style.display !== 'none') {
        const age40ChestPain = document.querySelector('input[name="age40_chest_pain"]:checked');
        const age40Breathless = document.querySelector('input[name="age40_breathless"]:checked');
        const age40HighBpSugar = document.querySelector('input[name="age40_high_bp_sugar"]:checked');
        const age40Swelling = document.querySelector('input[name="age40_swelling"]:checked');
        formData.age40_chest_pain = age40ChestPain ? age40ChestPain.value : 'no';
        formData.age40_breathless = age40Breathless ? age40Breathless.value : 'no';
        formData.age40_high_bp_sugar = age40HighBpSugar ? age40HighBpSugar.value : 'no';
        formData.age40_swelling = age40Swelling ? age40Swelling.value : 'no';
    }

    // Add pediatric fields if visible (Step 5)
    const pediatricFields = document.getElementById('pediatricFields');
    if (pediatricFields && pediatricFields.style.display !== 'none') {
        const pediatricVaccinations = document.querySelector('input[name="pediatric_vaccinations"]:checked');
        const pediatricConcerns = document.querySelector('input[name="pediatric_concerns"]:checked');
        formData.pediatric_vaccinations = pediatricVaccinations ? pediatricVaccinations.value : 'not_sure';
        formData.pediatric_concerns = pediatricConcerns ? pediatricConcerns.value : 'no';
        formData.pediatric_details = document.getElementById('pediatric_details')?.value.trim() || '';
    }

    try {
        const response = await fetch('/api/submit-assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle validation errors
            let errorMessage = data.error || 'Failed to submit assessment';

            if (data.details && Array.isArray(data.details)) {
                // Show validation errors
                errorMessage = 'Please fix the following errors:\n\n' + data.details.join('\n');
            } else if (response.status === 400) {
                errorMessage = data.error || 'Invalid data. Please check your inputs and try again.';
            } else if (response.status === 429) {
                errorMessage = 'Too many requests. Please wait a moment and try again.';
            }

            alert(errorMessage);
            document.getElementById('loadingOverlay').style.display = 'none';
            return;
        }

        if (data.success) {
            // Track event
            if (typeof fbq !== 'undefined') {
                fbq('track', 'CompleteRegistration');
                fbq('track', 'Lead');
            }

            // Redirect to analysis page
            window.location.href = '/analysis';
        } else {
            alert('Error: ' + (data.error || 'Failed to submit assessment'));
            document.getElementById('loadingOverlay').style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        let errorMessage = 'Network error. Please check your connection and try again.';

        if (error.message) {
            errorMessage = 'Error: ' + error.message;
        }

        alert(errorMessage);
        document.getElementById('loadingOverlay').style.display = 'none';
    }
});

