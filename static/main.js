document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', (e) => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !hamburger.contains(e.target)) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });
    }
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (navMenu) navMenu.classList.remove('active');
            if (hamburger) hamburger.classList.remove('active');
        });
    });
    // On-Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.reveal');
    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        revealElements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            if (elementTop < windowHeight - 100) {
                el.classList.add('active');
            }
        });
    };
    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll();
    // Contact Form Handler with Popup
    const contactForm = document.getElementById('contactForm');
    const modal = document.getElementById('popupModal');
    const closeBtn = document.getElementById('popupCloseBtn');
    const popupIcon = document.getElementById('popupIcon');
    const popupTitle = document.getElementById('popupTitle');
    const popupMessage = document.getElementById('popupMessage');
    const showPopup = (success, title, message) => {
        popupIcon.innerHTML = success ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-times-circle"></i>';
        popupTitle.textContent = title;
        popupMessage.textContent = message;
        modal.classList.add('active');
    };
    const hidePopup = () => {
        modal.classList.remove('active');
    };
    closeBtn.addEventListener('click', hidePopup);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hidePopup();
        }
    });
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            const submitBtn = e.target.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;
            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                if (response.ok) {
                    showPopup(
                        true,
                        'Excellence Acknowledged!',
                        'Your inquiry has been received successfully. Our team will contact you shortly.'
                    );
                    e.target.reset();
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Server responded with an error.');
                }
            } catch (error) {
                showPopup(
                    false,
                    'Submission Error',
                    error.message || 'We encountered an issue submitting your inquiry. Please check your connection and try again.'
                );
                console.error('Form submission error:', error);
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
