// Landing Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // FAQ Accordion interaction
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length > 0) {
        faqItems.forEach(item => {
            item.addEventListener('click', function(e) {
                // If text was selected by the user, don't toggle
                const selection = window.getSelection();
                if (selection && selection.toString().length > 0) return;

                const wasOpen = this.classList.contains('open');

                // Close other items (clean accordion behavior)
                faqItems.forEach(other => {
                    if (other !== this) {
                        other.classList.remove('open');
                        other.setAttribute('aria-expanded', 'false');
                    }
                });

                // Toggle clicked item
                if (wasOpen) {
                    this.classList.remove('open');
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    this.classList.add('open');
                    this.setAttribute('aria-expanded', 'true');
                }
            });

            // Keyboard accessibility (Enter or Space)
            item.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });
    }

    // Quick Start Widget interaction
    const quickStart = document.getElementById('heroQuickStart');
    if (quickStart) {
        let qGender = 'male';
        let qAge = '28';

        // Gender switch
        quickStart.querySelectorAll('.qswitch-gender').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                quickStart.querySelectorAll('.qswitch-gender').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                qGender = this.dataset.val || 'male';
                updateActionUrl();
            });
        });

        // Age switch
        quickStart.querySelectorAll('.qswitch-age').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                quickStart.querySelectorAll('.qswitch-age').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                qAge = this.dataset.val || '28';
                updateActionUrl();
            });
        });

        const actionBtn = quickStart.querySelector('.btn-quickstart-submit');
        function updateActionUrl() {
            if (!actionBtn) return;
            const baseUrl = actionBtn.getAttribute('data-base-url') || actionBtn.getAttribute('href').split('?')[0];
            actionBtn.setAttribute('data-base-url', baseUrl);
            actionBtn.setAttribute('href', `${baseUrl}?gender=${encodeURIComponent(qGender)}&age=${encodeURIComponent(qAge)}`);
        }
        updateActionUrl();
    }

    // Track page view
    if (typeof fbq !== 'undefined') {
        fbq('track', 'PageView');
    }
});
