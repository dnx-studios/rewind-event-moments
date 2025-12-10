document.addEventListener('DOMContentLoaded', function() {
    createParticles();
    initNavbar();
    initAnimations();
    initSmoothScroll();
    initCursorEffect();
    initCardEffects();
    initCookieBanner();
});

function createParticles() {
    const container = document.getElementById('particles');
    const particleCount = 25;
    const colors = ['#17DD62', '#4AEDD9', '#FCDB3B', '#5865F2'];
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 6) + 's';
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.width = (Math.random() * 4 + 2) + 'px';
        particle.style.height = particle.style.width;
        container.appendChild(particle);
    }
}

function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(13, 13, 21, 0.95)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(13, 13, 21, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    });
}

function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 50);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.clip-card, .category-card, .leader-card, .section-header');
    animatedElements.forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(40px)';
        el.style.transition = 'opacity 0.6s cubic-bezier(0.19, 1, 0.22, 1), transform 0.6s cubic-bezier(0.19, 1, 0.22, 1)';
        observer.observe(el);
    });

    const statValues = document.querySelectorAll('.stat-value');
    const statsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statValues.forEach(stat => statsObserver.observe(stat));
}

function animateCounter(element) {
    const text = element.textContent;
    const match = text.match(/(\d+(?:\.\d+)?)/);
    if (!match) return;
    
    const target = parseFloat(match[1]);
    const suffix = text.replace(match[1], '');
    const duration = 2000;
    const start = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 4);
        const current = target * easeOut;
        
        if (target >= 1000) {
            element.textContent = Math.floor(current).toLocaleString() + suffix;
        } else if (target >= 100) {
            element.textContent = Math.floor(current) + suffix;
        } else {
            element.textContent = current.toFixed(1) + suffix;
        }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = text;
        }
    }
    
    requestAnimationFrame(update);
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

function initCursorEffect() {
    if (window.innerWidth < 768) return;
    
    const cursor = document.createElement('div');
    cursor.style.cssText = `
        position: fixed;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(23, 221, 98, 0.06) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s, opacity 0.3s;
        will-change: left, top;
    `;
    document.body.appendChild(cursor);

    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateCursor() {
        const ease = 0.12;
        cursorX += (mouseX - cursorX) * ease;
        cursorY += (mouseY - cursorY) * ease;
        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    document.querySelectorAll('button, a, .clip-card, .category-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.style.width = '300px';
            cursor.style.height = '300px';
            cursor.style.background = 'radial-gradient(circle, rgba(23, 221, 98, 0.1) 0%, transparent 70%)';
        });
        el.addEventListener('mouseleave', () => {
            cursor.style.width = '200px';
            cursor.style.height = '200px';
            cursor.style.background = 'radial-gradient(circle, rgba(23, 221, 98, 0.06) 0%, transparent 70%)';
        });
    });
}

function initCardEffects() {
    document.querySelectorAll('.clip-card, .category-card, .leader-card').forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.style.setProperty('--mouse-x', `${x}px`);
            this.style.setProperty('--mouse-y', `${y}px`);
        });

        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.style.setProperty('--mouse-x', `${x}px`);
            this.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    const playBtns = document.querySelectorAll('.play-btn, .play-icon');
    playBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position: absolute;
                inset: 0;
                background: rgba(255,255,255,0.4);
                border-radius: 50%;
                animation: ripple 0.6s cubic-bezier(0.19, 1, 0.22, 1) forwards;
            `;
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        0% { transform: scale(0); opacity: 1; }
        100% { transform: scale(2.5); opacity: 0; }
    }
`;
document.head.appendChild(style);

document.querySelectorAll('.btn-primary, .btn-secondary, .cta-btn, .discord-btn').forEach(btn => {
    btn.addEventListener('mousedown', function() {
        this.style.transform = 'translateY(-2px) scale(0.98)';
    });
    
    btn.addEventListener('mouseup', function() {
        this.style.transform = '';
    });
    
    btn.addEventListener('mouseleave', function() {
        this.style.transform = '';
    });
});

function initCookieBanner() {
    const banner = document.getElementById('cookieBanner');
    const acceptBtn = document.getElementById('acceptCookies');
    const rejectBtn = document.getElementById('rejectCookies');
    
    if (!banner) return;
    
    const cookieChoice = localStorage.getItem('cookieConsent');
    if (cookieChoice) {
        banner.style.display = 'none';
        return;
    }
    
    acceptBtn.addEventListener('click', function() {
        localStorage.setItem('cookieConsent', 'accepted');
        hideBanner();
        showNotification('Cookies aceptadas', 'success');
    });
    
    rejectBtn.addEventListener('click', function() {
        localStorage.setItem('cookieConsent', 'rejected');
        hideBanner();
        showNotification('Cookies rechazadas', 'info');
    });
    
    function hideBanner() {
        banner.classList.add('hidden');
        setTimeout(() => {
            banner.style.display = 'none';
        }, 500);
    }
    
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = 'cookie-notification ' + type;
        notification.innerHTML = `
            <span class="notif-icon">${type === 'success' ? '✓' : 'ℹ'}</span>
            <span>${message}</span>
        `;
        notification.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            padding: 1rem 2rem;
            background: ${type === 'success' ? 'linear-gradient(135deg, #17DD62 0%, #0fa84a 100%)' : 'linear-gradient(135deg, #5865F2 0%, #4752c4 100%)'};
            border-radius: 12px;
            color: white;
            font-family: 'Press Start 2P', cursive;
            font-size: 0.65rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            z-index: 10000;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            animation: notifSlide 0.5s cubic-bezier(0.19, 1, 0.22, 1) forwards;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'notifSlideOut 0.4s cubic-bezier(0.19, 1, 0.22, 1) forwards';
            setTimeout(() => notification.remove(), 400);
        }, 2500);
    }
}

const notifStyle = document.createElement('style');
notifStyle.textContent = `
    @keyframes notifSlide {
        from { transform: translateX(-50%) translateY(100px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
    @keyframes notifSlideOut {
        from { transform: translateX(-50%) translateY(0); opacity: 1; }
        to { transform: translateX(-50%) translateY(100px); opacity: 0; }
    }
`;
document.head.appendChild(notifStyle);
