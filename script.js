let currentUser = null;
let allClips = [];
let videoSeekUsed = {};

const API_BASE_URL = window.location.hostname.includes('github.io') 
    ? 'https://e97c596c-1393-4a77-9095-957f14de7d2f-00-3apfzvtuj9297.janeway.replit.dev'
    : '';

document.addEventListener('DOMContentLoaded', function() {
    createParticles();
    initNavbar();
    initAnimations();
    initSmoothScroll();
    initCursorEffect();
    initCardEffects();
    initCookieBanner();
    loadDiscordStats();
    initUploadModal();
    loadApprovedClips();
    initLoginSystem();
    checkSavedSession();
    initNavigation();
    initCategoryView();
    initRequirementsModal();
    initLegalModals();
});

function initNavigation() {
    document.querySelectorAll('[data-nav]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const nav = this.dataset.nav;
            
            if (nav === 'inicio') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else if (nav === 'clips') {
                const clipsSection = document.getElementById('clips');
                clipsSection.scrollIntoView({ behavior: 'smooth' });
                const btnSubir = document.querySelector('.btn-subir-clip');
                if (btnSubir) {
                    btnSubir.classList.add('glow-effect');
                    setTimeout(() => btnSubir.classList.remove('glow-effect'), 3000);
                }
            } else if (nav === 'categorias') {
                const categoriesSection = document.getElementById('categorias');
                categoriesSection.scrollIntoView({ behavior: 'smooth' });
                document.querySelectorAll('.category-card').forEach((card, i) => {
                    setTimeout(() => {
                        card.classList.add('glow-effect');
                        setTimeout(() => card.classList.remove('glow-effect'), 2000);
                    }, i * 150);
                });
            } else if (nav === 'discord') {
                const discordSection = document.getElementById('discord');
                discordSection.scrollIntoView({ behavior: 'smooth' });
                const discordBtn = document.getElementById('discord-btn');
                if (discordBtn) {
                    discordBtn.classList.add('glow-effect');
                    setTimeout(() => discordBtn.classList.remove('glow-effect'), 3000);
                }
            }
        });
    });
}

function initRequirementsModal() {
    const btnReq = document.getElementById('btnRequisitos');
    const modal = document.getElementById('requirementsModal');
    const overlay = document.getElementById('requirementsModalOverlay');
    const closeBtn = document.getElementById('requirementsModalClose');
    const okBtn = document.getElementById('requirementsModalOk');
    
    if (!btnReq || !modal) return;
    
    btnReq.addEventListener('click', () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
    
    [overlay, closeBtn, okBtn].forEach(el => {
        if (el) {
            el.addEventListener('click', () => {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
    });
}

function initLegalModals() {
    const legalModal = document.getElementById('legalModal');
    const overlay = document.getElementById('legalModalOverlay');
    const closeBtn = document.getElementById('legalModalClose');
    const backBtn = document.getElementById('legalModalBack');
    
    const legalContent = {
        terminos: {
            icon: '📜',
            title: 'Terminos de Servicio',
            body: `
                <h3>1. Aceptacion de Terminos</h3>
                <p>Al usar Rewind Event Moments, aceptas estos terminos de servicio. Si no estas de acuerdo, no uses la plataforma.</p>
                
                <h3>2. Uso del Servicio</h3>
                <p>Debes tener al menos 13 años para usar este servicio. Eres responsable de mantener la seguridad de tu cuenta.</p>
                
                <h3>3. Contenido del Usuario</h3>
                <p>Al subir contenido, garantizas que tienes los derechos sobre el mismo. No subas contenido ilegal, ofensivo o que viole derechos de terceros.</p>
                
                <h3>4. Contenido Prohibido</h3>
                <p>Esta prohibido subir contenido que contenga violencia extrema, discurso de odio, contenido sexual, spam o malware.</p>
                
                <h3>5. Moderacion</h3>
                <p>Nos reservamos el derecho de eliminar cualquier contenido que viole estos terminos sin previo aviso.</p>
                
                <h3>6. Propiedad Intelectual</h3>
                <p>Minecraft es propiedad de Mojang Studios. Esta plataforma no esta afiliada con Mojang ni Microsoft.</p>
                
                <h3>7. Limitacion de Responsabilidad</h3>
                <p>El servicio se proporciona "tal cual". No garantizamos disponibilidad continua ni nos hacemos responsables por perdida de datos.</p>
                
                <h3>8. Modificaciones</h3>
                <p>Podemos modificar estos terminos en cualquier momento. Los cambios entraran en vigor al publicarse.</p>
            `
        },
        privacidad: {
            icon: '🔒',
            title: 'Politica de Privacidad',
            body: `
                <h3>1. Informacion que Recopilamos</h3>
                <p>Recopilamos informacion de tu cuenta de Discord (nombre de usuario, avatar, ID) cuando te registras.</p>
                
                <h3>2. Uso de la Informacion</h3>
                <p>Usamos tu informacion para identificarte en la plataforma, mostrar tu perfil y enviarte notificaciones sobre tus clips.</p>
                
                <h3>3. Almacenamiento</h3>
                <p>Tu informacion se almacena de forma segura. Los videos se guardan en nuestros servidores durante el tiempo que estes registrado.</p>
                
                <h3>4. Compartir Informacion</h3>
                <p>No vendemos ni compartimos tu informacion personal con terceros, excepto cuando sea requerido por ley.</p>
                
                <h3>5. Cookies</h3>
                <p>Usamos cookies para mantener tu sesion iniciada y mejorar tu experiencia en la plataforma.</p>
                
                <h3>6. Tus Derechos</h3>
                <p>Puedes solicitar la eliminacion de tu cuenta y datos contactandonos en Discord.</p>
                
                <h3>7. Menores de Edad</h3>
                <p>No recopilamos intencionalmente informacion de menores de 13 años.</p>
                
                <h3>8. Contacto</h3>
                <p>Para preguntas sobre privacidad, contactanos en nuestro servidor de Discord.</p>
            `
        },
        cookies: {
            icon: '🍪',
            title: 'Politica de Cookies',
            body: `
                <h3>1. Que son las Cookies</h3>
                <p>Las cookies son pequeños archivos de texto que se almacenan en tu navegador para recordar informacion sobre ti.</p>
                
                <h3>2. Cookies que Usamos</h3>
                <p><strong>Cookies de Sesion:</strong> Para mantener tu sesion iniciada.</p>
                <p><strong>Cookies de Preferencias:</strong> Para recordar tus ajustes.</p>
                
                <h3>3. Cookies de Terceros</h3>
                <p>No usamos cookies de seguimiento de terceros ni publicidad.</p>
                
                <h3>4. Como Gestionar Cookies</h3>
                <p>Puedes desactivar las cookies en tu navegador, pero esto puede afectar la funcionalidad del sitio.</p>
                
                <h3>5. Cookies Esenciales</h3>
                <p>Algunas cookies son esenciales para el funcionamiento del sitio y no pueden desactivarse.</p>
                
                <h3>6. Duracion</h3>
                <p>Las cookies de sesion se eliminan al cerrar el navegador. Las de preferencias pueden durar hasta 1 año.</p>
            `
        }
    };
    
    function openLegal(type) {
        const content = legalContent[type];
        if (!content) return;
        
        document.getElementById('legalIcon').textContent = content.icon;
        document.getElementById('legalTitle').textContent = content.title;
        document.getElementById('legalBody').innerHTML = content.body;
        legalModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    document.getElementById('openTerminos')?.addEventListener('click', (e) => {
        e.preventDefault();
        openLegal('terminos');
    });
    
    document.getElementById('openPrivacidad')?.addEventListener('click', (e) => {
        e.preventDefault();
        openLegal('privacidad');
    });
    
    document.getElementById('openCookies')?.addEventListener('click', (e) => {
        e.preventDefault();
        openLegal('cookies');
    });
    
    [overlay, closeBtn, backBtn].forEach(el => {
        if (el) {
            el.addEventListener('click', () => {
                legalModal.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
    });
}

function initCategoryView() {
    const categoryCards = document.querySelectorAll('.category-card');
    const categoriesSection = document.getElementById('categorias');
    const categoryView = document.getElementById('categoryView');
    const btnBack = document.getElementById('btnBackCategories');
    
    const categoryNames = {
        'fails': { name: 'Fails Epicos', icon: '💀' },
        'pvp': { name: 'PvP Highlights', icon: '⚔️' },
        'builds': { name: 'Construcciones', icon: '🏰' },
        'redstone': { name: 'Redstone', icon: '🔴' },
        'survival': { name: 'Survival', icon: '🌲' },
        'mods': { name: 'Mods Locos', icon: '🧪' }
    };
    
    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const category = this.dataset.category;
            const info = categoryNames[category];
            const categoryClips = allClips.filter(c => c.category === category);
            
            document.getElementById('categoryViewIcon').textContent = info.icon;
            document.getElementById('categoryViewTitle').textContent = info.name;
            document.getElementById('categoryViewCount').textContent = `${categoryClips.length} videos`;
            
            const grid = document.getElementById('categoryClipsGrid');
            if (categoryClips.length > 0) {
                grid.innerHTML = categoryClips.map(clip => createClipCard(clip)).join('');
                initVideoControls(grid);
                initInteractionButtons(grid);
            } else {
                grid.innerHTML = `
                    <div class="category-empty">
                        <span class="category-empty-icon">${info.icon}</span>
                        <h3>No hay clips en esta categoria</h3>
                        <p>Se el primero en subir un clip de ${info.name}</p>
                    </div>
                `;
            }
            
            categoriesSection.style.display = 'none';
            categoryView.style.display = 'block';
            categoryView.scrollIntoView({ behavior: 'smooth' });
        });
    });
    
    btnBack?.addEventListener('click', function() {
        categoryView.style.display = 'none';
        categoriesSection.style.display = 'block';
        categoriesSection.scrollIntoView({ behavior: 'smooth' });
    });
}

function initLoginSystem() {
    const loginBtnNav = document.getElementById('loginBtnNav');
    const loginModal = document.getElementById('loginModal');
    const loginModalOverlay = document.getElementById('loginModalOverlay');
    const loginModalClose = document.getElementById('loginModalClose');
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    const logoutBtn = document.getElementById('logoutBtn');
    const howToLoginBtn = document.getElementById('howToLoginBtn');
    const loginInstructions = document.getElementById('loginInstructions');
    const loginPreview = document.getElementById('loginPreview');
    const loginConfirmBtn = document.getElementById('loginConfirmBtn');
    const loginCancelBtn = document.getElementById('loginCancelBtn');
    
    let pendingUser = null;
    
    if (loginBtnNav) {
        loginBtnNav.addEventListener('click', () => {
            loginModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (loginModalOverlay) {
        loginModalOverlay.addEventListener('click', () => {
            closeLoginModal();
        });
    }
    
    if (loginModalClose) {
        loginModalClose.addEventListener('click', () => {
            closeLoginModal();
        });
    }
    
    function closeLoginModal() {
        loginModal.classList.remove('active');
        document.body.style.overflow = '';
        loginError.style.display = 'none';
        if (loginInstructions) loginInstructions.style.display = 'none';
        if (loginPreview) loginPreview.style.display = 'none';
        if (loginForm) loginForm.style.display = 'block';
        pendingUser = null;
    }
    
    if (howToLoginBtn && loginInstructions) {
        howToLoginBtn.addEventListener('click', () => {
            loginInstructions.style.display = loginInstructions.style.display === 'none' ? 'block' : 'none';
        });
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('loginPassword').value;
            
            try {
                const response = await fetch(API_BASE_URL + '/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    pendingUser = result.user;
                    document.getElementById('loginPreviewAvatar').src = result.user.avatar_url;
                    document.getElementById('loginPreviewName').textContent = result.user.display_name;
                    loginForm.style.display = 'none';
                    loginPreview.style.display = 'block';
                    if (loginInstructions) loginInstructions.style.display = 'none';
                } else {
                    loginError.style.display = 'flex';
                    setTimeout(() => {
                        loginError.style.display = 'none';
                    }, 3000);
                }
            } catch (error) {
                console.error('Login error:', error);
                loginError.style.display = 'flex';
            }
        });
    }
    
    if (loginConfirmBtn) {
        loginConfirmBtn.addEventListener('click', () => {
            if (pendingUser) {
                currentUser = pendingUser;
                saveSession(pendingUser);
                updateUserUI();
                closeLoginModal();
                loginForm.reset();
                loadApprovedClips();
            }
        });
    }
    
    if (loginCancelBtn) {
        loginCancelBtn.addEventListener('click', () => {
            pendingUser = null;
            loginPreview.style.display = 'none';
            loginForm.style.display = 'block';
            loginForm.reset();
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            currentUser = null;
            localStorage.removeItem('rewind_session');
            updateUserUI();
            loadApprovedClips();
        });
    }
}

function saveSession(user) {
    localStorage.setItem('rewind_session', JSON.stringify(user));
}

function checkSavedSession() {
    const cookiesAccepted = localStorage.getItem('cookiesAccepted');
    if (cookiesAccepted === 'true') {
        const savedSession = localStorage.getItem('rewind_session');
        if (savedSession) {
            try {
                currentUser = JSON.parse(savedSession);
                updateUserUI();
            } catch (e) {
                localStorage.removeItem('rewind_session');
            }
        }
    }
}

function updateUserUI() {
    const loginBtnNav = document.getElementById('loginBtnNav');
    const userProfile = document.getElementById('userProfile');
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    
    if (currentUser) {
        loginBtnNav.style.display = 'none';
        userProfile.style.display = 'flex';
        userAvatar.src = currentUser.avatar_url;
        userName.textContent = currentUser.display_name;
    } else {
        loginBtnNav.style.display = 'flex';
        userProfile.style.display = 'none';
    }
}

function loadDiscordStats() {
    const onlineCount = document.getElementById('online-count');
    const membersCount = document.getElementById('members-count');
    const discordBtn = document.getElementById('discord-btn');
    
    if (!onlineCount || !membersCount) return;
    
    function fetchStats() {
        fetch(API_BASE_URL + '/api/discord-stats')
            .then(response => response.json())
            .then(data => {
                if (data.members > 0) {
                    onlineCount.textContent = data.online.toLocaleString() + ' online';
                    membersCount.textContent = data.members.toLocaleString() + ' miembros';
                }
                if (data.invite_url && discordBtn) {
                    discordBtn.href = data.invite_url;
                }
            })
            .catch(error => {
                console.log('Discord stats not available');
                onlineCount.textContent = '-- online';
                membersCount.textContent = '-- miembros';
            });
    }
    
    fetchStats();
    setInterval(fetchStats, 30000);
}

function initUploadModal() {
    const modal = document.getElementById('uploadModal');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalClose = document.getElementById('modalClose');
    const uploadForm = document.getElementById('uploadForm');
    const uploadLoginRequired = document.getElementById('uploadLoginRequired');
    const uploadLoginForm = document.getElementById('uploadLoginForm');
    const uploadHowToLoginBtn = document.getElementById('uploadHowToLoginBtn');
    const uploadLoginInstructions = document.getElementById('uploadLoginInstructions');
    const uploadLoginError = document.getElementById('uploadLoginError');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const videoFileInput = document.getElementById('videoFile');
    const fileSelected = document.getElementById('fileSelected');
    const fileName = document.getElementById('fileName');
    const fileRemove = document.getElementById('fileRemove');
    const durationError = document.getElementById('durationError');
    const uploadSuccess = document.getElementById('uploadSuccess');
    const closeSuccess = document.getElementById('closeSuccess');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!modal || !modalOverlay || !uploadForm) return;
    
    const uploadButtons = document.querySelectorAll('.btn-subir-clip');
    uploadButtons.forEach(btn => {
        btn.addEventListener('click', openModal);
    });
    
    if (uploadHowToLoginBtn && uploadLoginInstructions) {
        uploadHowToLoginBtn.addEventListener('click', () => {
            uploadLoginInstructions.style.display = uploadLoginInstructions.style.display === 'none' ? 'block' : 'none';
        });
    }
    
    if (uploadLoginForm) {
        uploadLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('uploadLoginPassword').value;
            
            try {
                const response = await fetch(API_BASE_URL + '/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentUser = result.user;
                    saveSession(result.user);
                    updateUserUI();
                    updateUploadModalState();
                    uploadLoginForm.reset();
                    if (uploadLoginInstructions) uploadLoginInstructions.style.display = 'none';
                    loadApprovedClips();
                } else {
                    if (uploadLoginError) {
                        uploadLoginError.style.display = 'flex';
                        setTimeout(() => {
                            uploadLoginError.style.display = 'none';
                        }, 3000);
                    }
                }
            } catch (error) {
                console.error('Login error:', error);
                if (uploadLoginError) uploadLoginError.style.display = 'flex';
            }
        });
    }
    
    function updateUploadModalState() {
        if (currentUser) {
            if (uploadLoginRequired) uploadLoginRequired.style.display = 'none';
            if (uploadForm) uploadForm.style.display = 'block';
        } else {
            if (uploadLoginRequired) uploadLoginRequired.style.display = 'block';
            if (uploadForm) uploadForm.style.display = 'none';
        }
    }
    
    function openModal() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        updateUploadModalState();
    }
    
    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        resetForm();
    }
    
    function resetForm() {
        uploadForm.reset();
        fileSelected.style.display = 'none';
        document.querySelector('.file-upload-content').style.display = 'block';
        durationError.style.display = 'none';
        uploadForm.style.display = 'block';
        uploadSuccess.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>⬆</span> Enviar para revision';
    }
    
    modalOverlay.addEventListener('click', closeModal);
    modalClose.addEventListener('click', closeModal);
    closeSuccess.addEventListener('click', closeModal);
    
    fileUploadArea.addEventListener('click', () => {
        videoFileInput.click();
    });
    
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.classList.add('drag-over');
    });
    
    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.classList.remove('drag-over');
    });
    
    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
    
    videoFileInput.addEventListener('change', () => {
        if (videoFileInput.files.length > 0) {
            handleFileSelect(videoFileInput.files[0]);
        }
    });
    
    function handleFileSelect(file) {
        if (!file.type.startsWith('video/')) {
            alert('Por favor selecciona un archivo de video');
            return;
        }
        
        const video = document.createElement('video');
        video.preload = 'metadata';
        
        video.onloadedmetadata = function() {
            window.URL.revokeObjectURL(video.src);
            
            if (video.duration > 20) {
                durationError.style.display = 'block';
                videoFileInput.value = '';
                return;
            }
            
            durationError.style.display = 'none';
            fileName.textContent = file.name;
            document.querySelector('.file-upload-content').style.display = 'none';
            fileSelected.style.display = 'flex';
        };
        
        video.src = URL.createObjectURL(file);
    }
    
    fileRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        videoFileInput.value = '';
        fileSelected.style.display = 'none';
        document.querySelector('.file-upload-content').style.display = 'block';
        durationError.style.display = 'none';
    });
    
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!videoFileInput.files.length) {
            alert('Por favor selecciona un video');
            return;
        }
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>⏳</span> Enviando...';
        
        const formData = new FormData();
        formData.append('username', currentUser ? currentUser.username : 'Anónimo');
        formData.append('title', document.getElementById('videoTitle').value);
        formData.append('category', document.getElementById('category').value);
        formData.append('video', videoFileInput.files[0]);
        
        if (currentUser) {
            formData.append('user_id', currentUser.id);
            formData.append('avatar_url', currentUser.avatar_url);
        }
        
        try {
            const response = await fetch(API_BASE_URL + '/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                uploadForm.style.display = 'none';
                uploadSuccess.style.display = 'block';
            } else {
                alert('Error al enviar el clip: ' + (result.error || 'Error desconocido'));
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>⬆</span> Enviar para revision';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al enviar el clip. Por favor intenta de nuevo.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>⬆</span> Enviar para revision';
        }
    });
}

function loadApprovedClips() {
    fetch(API_BASE_URL + '/api/clips')
        .then(response => response.json())
        .then(clips => {
            allClips = clips || [];
            if (clips && clips.length > 0) {
                displayApprovedClips(clips);
                updateCategoryCounts(clips);
                updateHeroStats(clips);
            }
        })
        .catch(error => {
            console.log('No clips available yet');
        });
    
    setInterval(() => {
        fetch(API_BASE_URL + '/api/clips')
            .then(response => response.json())
            .then(clips => {
                allClips = clips || [];
                if (clips && clips.length > 0) {
                    displayApprovedClips(clips);
                    updateCategoryCounts(clips);
                    updateHeroStats(clips);
                }
            })
            .catch(() => {});
    }, 30000);
}

function createClipCard(clip) {
    const categoryIcons = {
        'fails': '💀',
        'pvp': '⚔️',
        'builds': '🏰',
        'redstone': '🔴',
        'survival': '🌲',
        'mods': '🧪'
    };
    
    const isLiked = currentUser && currentUser.likes && currentUser.likes.includes(clip.id);
    const isDisliked = currentUser && currentUser.dislikes && currentUser.dislikes.includes(clip.id);
    const isFavorite = currentUser && currentUser.favorites && currentUser.favorites.includes(clip.id);
    const avatarUrl = clip.avatar_url || 'https://cdn.discordapp.com/embed/avatars/0.png';
    
    return `
    <div class="approved-clip-card">
        <div class="video-wrapper">
            <video data-clip-id="${clip.id}" preload="metadata" playsinline>
                <source src="${API_BASE_URL}/approved/${clip.filename}" type="video/mp4">
            </video>
            <div class="video-play-overlay">
                <div class="play-circle">▶</div>
            </div>
            <div class="custom-video-controls">
                <div class="video-progress-bar">
                    <div class="video-progress-fill"></div>
                </div>
                <div class="video-controls-row">
                    <div class="video-controls-left">
                        <button class="video-ctrl-btn play-pause" title="Play/Pause">▶</button>
                        <span class="video-time">0:00 / 0:00</span>
                    </div>
                    <div class="video-controls-right">
                        <button class="video-ctrl-btn fullscreen-btn" title="Pantalla completa">⛶</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="approved-clip-info">
            <div class="clip-author-row">
                <img class="clip-author-avatar" src="${avatarUrl}" alt="Avatar">
                <div class="clip-author-info">
                    <h4>${escapeHtml(clip.title)}</h4>
                    <span class="clip-author">@${escapeHtml(clip.username)}</span>
                </div>
            </div>
            <div class="clip-meta">
                <span class="clip-category">${categoryIcons[clip.category] || ''} ${clip.category}</span>
                <span class="clip-views" data-clip-id="${clip.id}">${clip.views || 0} vistas</span>
            </div>
            <div class="clip-interactions">
                <button class="interaction-btn like-btn ${isLiked ? 'active' : ''}" data-clip-id="${clip.id}" title="Me gusta">
                    <span>👍</span>
                    <span class="interaction-count">${clip.likes || 0}</span>
                </button>
                <button class="interaction-btn dislike-btn ${isDisliked ? 'active' : ''}" data-clip-id="${clip.id}" title="No me gusta">
                    <span>👎</span>
                    <span class="interaction-count">${clip.dislikes || 0}</span>
                </button>
                <button class="interaction-btn favorite-btn ${isFavorite ? 'active' : ''}" data-clip-id="${clip.id}" title="Agregar a favoritos">
                    <span>⭐</span>
                </button>
            </div>
        </div>
    </div>
    `;
}

function displayApprovedClips(clips) {
    const clipsSection = document.getElementById('clips');
    if (!clipsSection) return;
    
    const existingEmpty = clipsSection.querySelector('.clips-empty-state');
    let clipsGrid = clipsSection.querySelector('.clips-grid-approved');
    
    if (clips.length > 0) {
        if (existingEmpty) {
            existingEmpty.style.display = 'none';
        }
        
        if (!clipsGrid) {
            clipsGrid = document.createElement('div');
            clipsGrid.className = 'clips-grid-approved';
            clipsSection.appendChild(clipsGrid);
        }
        
        clipsGrid.innerHTML = clips.map(clip => createClipCard(clip)).join('');
        
        initVideoControls(clipsGrid);
        initInteractionButtons(clipsGrid);
    }
}

function initVideoControls(clipsGrid) {
    clipsGrid.querySelectorAll('.approved-clip-card').forEach(card => {
        const video = card.querySelector('video');
        const overlay = card.querySelector('.video-play-overlay');
        const controls = card.querySelector('.custom-video-controls');
        const playPauseBtn = card.querySelector('.play-pause');
        const fullscreenBtn = card.querySelector('.fullscreen-btn');
        const progressBar = card.querySelector('.video-progress-bar');
        const progressFill = card.querySelector('.video-progress-fill');
        const timeDisplay = card.querySelector('.video-time');
        const wrapper = card.querySelector('.video-wrapper');
        const clipId = video.dataset.clipId;
        
        let viewCounted = false;
        let hasSkipped = false;
        let maxTimeReached = 0;
        
        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        
        function updateProgress() {
            if (video.duration) {
                const percent = (video.currentTime / video.duration) * 100;
                progressFill.style.width = percent + '%';
                timeDisplay.textContent = `${formatTime(video.currentTime)} / ${formatTime(video.duration)}`;
                if (video.currentTime > maxTimeReached) {
                    maxTimeReached = video.currentTime;
                }
            }
        }
        
        video.addEventListener('loadedmetadata', function() {
            timeDisplay.textContent = `0:00 / ${formatTime(video.duration)}`;
        });
        
        video.addEventListener('timeupdate', updateProgress);
        
        overlay.addEventListener('click', function(e) {
            e.stopPropagation();
            video.play();
        });
        
        playPauseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        });
        
        progressBar.addEventListener('click', function(e) {
            e.stopPropagation();
            const rect = progressBar.getBoundingClientRect();
            const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            const newTime = percent * video.duration;
            if (newTime > maxTimeReached + 1) {
                hasSkipped = true;
            }
            video.currentTime = newTime;
        });
        
        let isDragging = false;
        progressBar.addEventListener('mousedown', function(e) {
            isDragging = true;
            const rect = progressBar.getBoundingClientRect();
            const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            const newTime = percent * video.duration;
            if (newTime > maxTimeReached + 1) {
                hasSkipped = true;
            }
            video.currentTime = newTime;
        });
        
        document.addEventListener('mousemove', function(e) {
            if (isDragging && video.duration) {
                const rect = progressBar.getBoundingClientRect();
                const percent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                const newTime = percent * video.duration;
                if (newTime > maxTimeReached + 1) {
                    hasSkipped = true;
                }
                video.currentTime = newTime;
            }
        });
        
        document.addEventListener('mouseup', function() {
            isDragging = false;
        });
        
        fullscreenBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (document.fullscreenElement || document.webkitFullscreenElement) {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
            } else {
                if (wrapper.requestFullscreen) {
                    wrapper.requestFullscreen();
                } else if (wrapper.webkitRequestFullscreen) {
                    wrapper.webkitRequestFullscreen();
                } else if (video.webkitEnterFullscreen) {
                    video.webkitEnterFullscreen();
                }
            }
        });
        
        document.addEventListener('fullscreenchange', function() {
            if (document.fullscreenElement === wrapper) {
                fullscreenBtn.textContent = '✕';
                fullscreenBtn.title = 'Salir de pantalla completa';
            } else if (!document.fullscreenElement) {
                fullscreenBtn.textContent = '⛶';
                fullscreenBtn.title = 'Pantalla completa';
            }
        });
        
        video.addEventListener('play', function() {
            overlay.classList.add('hidden');
            playPauseBtn.textContent = '⏸';
            controls.classList.add('active');
        });
        
        video.addEventListener('pause', function() {
            playPauseBtn.textContent = '▶';
        });
        
        video.addEventListener('ended', function() {
            if (!viewCounted && !hasSkipped) {
                viewCounted = true;
                fetch(API_BASE_URL + `/api/clip/${clipId}/view`).then(() => {
                    animateViewCounter(card, clipId);
                }).catch(() => {});
            }
            playPauseBtn.textContent = '▶';
        });
        
        wrapper.addEventListener('click', function(e) {
            if (e.target === video && !video.paused) {
                video.pause();
            }
        });
    });
}

function animateViewCounter(card, clipId) {
    const viewsEl = card.querySelector(`.clip-views[data-clip-id="${clipId}"]`);
    if (!viewsEl) return;
    
    const currentViews = parseInt(viewsEl.textContent) || 0;
    const newViews = currentViews + 1;
    
    viewsEl.classList.add('view-counted');
    viewsEl.innerHTML = `<span class="view-sparkle">✨</span> ${newViews} vistas <span class="view-sparkle">✨</span>`;
    
    setTimeout(() => {
        viewsEl.classList.remove('view-counted');
        viewsEl.textContent = `${newViews} vistas`;
    }, 2000);
}

function showLoginPrompt() {
    const loginModal = document.getElementById('loginModal');
    if (loginModal) {
        loginModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function initInteractionButtons(clipsGrid) {
    clipsGrid.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.stopPropagation();
            if (!currentUser) {
                showLoginPrompt();
                return;
            }
            
            const clipId = this.dataset.clipId;
            try {
                const response = await fetch(API_BASE_URL + '/api/like', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: currentUser.id, clip_id: clipId })
                });
                
                if (response.ok) {
                    if (!currentUser.likes) currentUser.likes = [];
                    if (!currentUser.likes.includes(clipId)) {
                        currentUser.likes.push(clipId);
                        currentUser.dislikes = currentUser.dislikes?.filter(id => id !== clipId) || [];
                    }
                    saveSession(currentUser);
                    loadApprovedClips();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
    
    clipsGrid.querySelectorAll('.dislike-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.stopPropagation();
            if (!currentUser) {
                showLoginPrompt();
                return;
            }
            
            const clipId = this.dataset.clipId;
            try {
                const response = await fetch(API_BASE_URL + '/api/dislike', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: currentUser.id, clip_id: clipId })
                });
                
                if (response.ok) {
                    if (!currentUser.dislikes) currentUser.dislikes = [];
                    if (!currentUser.dislikes.includes(clipId)) {
                        currentUser.dislikes.push(clipId);
                        currentUser.likes = currentUser.likes?.filter(id => id !== clipId) || [];
                    }
                    saveSession(currentUser);
                    loadApprovedClips();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
    
    clipsGrid.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.stopPropagation();
            if (!currentUser) {
                showLoginPrompt();
                return;
            }
            
            const clipId = this.dataset.clipId;
            
            if (currentUser.favorites && currentUser.favorites.includes(clipId)) {
                alert('Este clip ya está en tus favoritos');
                return;
            }
            
            try {
                const response = await fetch(API_BASE_URL + '/api/favorite', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: currentUser.id, clip_id: clipId })
                });
                
                if (response.ok) {
                    if (!currentUser.favorites) currentUser.favorites = [];
                    currentUser.favorites.push(clipId);
                    saveSession(currentUser);
                    this.classList.add('active');
                    alert('Clip agregado a favoritos. Te lo enviaremos por DM en Discord.');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
}

function updateCategoryCounts(clips) {
    const counts = {};
    clips.forEach(clip => {
        counts[clip.category] = (counts[clip.category] || 0) + 1;
    });
    
    const categoryMap = {
        'fails': '.cat-fails',
        'pvp': '.cat-pvp',
        'builds': '.cat-builds',
        'redstone': '.cat-redstone',
        'survival': '.cat-survival',
        'mods': '.cat-mods'
    };
    
    Object.keys(categoryMap).forEach(cat => {
        const card = document.querySelector(categoryMap[cat]);
        if (card) {
            const countEl = card.querySelector('.cat-count');
            if (countEl) {
                countEl.textContent = `${counts[cat] || 0} clips`;
            }
        }
    });
}

function updateHeroStats(clips) {
    const statClips = document.getElementById('stat-clips');
    const statVideoViews = document.getElementById('stat-video-views');
    const statCreators = document.getElementById('stat-creators');
    
    const uniqueUsers = new Set(clips.map(c => c.username)).size;
    const totalVideoViews = clips.reduce((sum, c) => sum + (c.views || 0), 0);
    
    if (statClips) statClips.textContent = clips.length;
    if (statVideoViews) statVideoViews.textContent = totalVideoViews;
    if (statCreators) statCreators.textContent = uniqueUsers;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
            if (this.dataset.nav) return;
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
}

function initCookieBanner() {
    const banner = document.getElementById('cookieBanner');
    const acceptBtn = document.getElementById('acceptCookies');
    const rejectBtn = document.getElementById('rejectCookies');
    
    if (!banner || !acceptBtn || !rejectBtn) return;
    
    const cookiesAccepted = localStorage.getItem('cookiesAccepted');
    
    if (cookiesAccepted === null) {
        setTimeout(() => {
            banner.classList.add('visible');
        }, 1500);
    } else {
        banner.classList.add('hidden');
    }
    
    acceptBtn.addEventListener('click', () => {
        localStorage.setItem('cookiesAccepted', 'true');
        banner.classList.add('hidden');
        checkSavedSession();
    });
    
    rejectBtn.addEventListener('click', () => {
        localStorage.setItem('cookiesAccepted', 'false');
        localStorage.removeItem('rewind_session');
        currentUser = null;
        updateUserUI();
        banner.classList.add('hidden');
    });
}
