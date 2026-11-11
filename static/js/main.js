document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const recommendationResult = document.getElementById('recommendationResult');
    const errorMessage = document.getElementById('errorMessage');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide previous results/errors
        recommendationResult.style.display = 'none';
        errorMessage.style.display = 'none';
        
        // Show loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        
        // Collect form data
        const formData = {
            name: document.getElementById('name').value,
            age: document.getElementById('age').value,
            weight: document.getElementById('weight').value,
            height: document.getElementById('height').value,
            gender: document.getElementById('gender').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            symptoms: document.getElementById('symptoms').value,
            existing_conditions: document.getElementById('existing_conditions').value
        };
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            
            if (data.success) {
                displayRecommendation(data);
            } else {
                showError(data.error || 'An error occurred. Please try again.');
            }
        } catch (error) {
            // Reset button state
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            
            showError('Network error. Please check your connection and try again.');
            console.error('Error:', error);
        }
    });
    
    function displayRecommendation(data) {
        const recommendation = data.recommendation;
        const packageCard = document.getElementById('packageCard');
        const reasoningBox = document.getElementById('reasoningBox');
        
        // Build package card HTML
        packageCard.innerHTML = `
            <div class="package-name">${recommendation.package_name}</div>
            <div class="package-price">
                <span class="currency">₹</span>
                <span>${recommendation.price.toLocaleString()}</span>
            </div>
            <div class="package-description">${recommendation.description}</div>
            <div class="package-includes">
                <h4>This Package Includes:</h4>
                <ul class="includes-list">
                    ${recommendation.includes.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
            ${recommendation.bmi ? `<div style="margin-top: 20px; opacity: 0.9; font-size: 0.95rem;">Your BMI: ${recommendation.bmi}</div>` : ''}
        `;
        
        // Build reasoning HTML
        let reasoningHTML = `
            <h4>Why This Package?</h4>
            <p>${recommendation.reasoning}</p>
        `;
        
        if (recommendation.priority_factors && recommendation.priority_factors.length > 0) {
            reasoningHTML += `
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #fecaca;">
                    <strong>Key Factors Considered:</strong>
                    <ul style="margin-top: 8px; padding-left: 20px; color: var(--text-secondary);">
                        ${recommendation.priority_factors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        reasoningBox.innerHTML = reasoningHTML;
        
        // Show recommendation
        recommendationResult.style.display = 'block';
        
        // Scroll to recommendation
        recommendationResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Optional: Track conversion or send data to analytics
        // You can add Google Analytics, Facebook Pixel, or other tracking here
        if (typeof gtag !== 'undefined') {
            gtag('event', 'health_checkup_recommendation', {
                'package_id': recommendation.package_id,
                'package_price': recommendation.price,
                'patient_age': data.patient_data.age,
                'patient_bmi': recommendation.bmi
            });
        }
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Add input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });
});

function resetForm() {
    document.getElementById('patientForm').reset();
    document.getElementById('recommendationResult').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

