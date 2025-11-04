// Additional UI Functions for Google Photos Style Interface

// Dark Mode Toggle
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.toggle('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Update theme icon
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = isDark ? 'light_mode' : 'dark_mode';
    }
}

// Load saved theme on startup
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        const icon = document.querySelector('.theme-icon');
        if (icon) {
            icon.textContent = 'light_mode';
        }
    }
}

// Sidebar Toggle (Mobile)
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
}

// User Menu Toggle
function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    menu.classList.toggle('show');
}

// Close user menu when clicking outside
document.addEventListener('click', function(event) {
    const menu = document.getElementById('user-menu');
    const avatar = document.querySelector('.user-avatar');
    
    if (menu && !menu.contains(event.target) && !avatar.contains(event.target)) {
        menu.classList.remove('show');
    }
});

// Upload Dialog
function showUploadDialog() {
    document.getElementById('upload-dialog').classList.add('show');
}

function closeUploadDialog() {
    document.getElementById('upload-dialog').classList.remove('show');
}

// Search Panel
function showSearch(event) {
    if (event) {
        event.preventDefault();
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        event.currentTarget.classList.add('active');
    }
    document.getElementById('search-panel').classList.add('show');
}

function closeSearch() {
    document.getElementById('search-panel').classList.remove('show');
}

function showPhotos(event) {
    if (event) {
        event.preventDefault();
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        event.currentTarget.classList.add('active');
    }
    closeSearch();
    loadGallery();
}

// View Toggle
function setView(viewType) {
    const gallery = document.getElementById('gallery');
    gallery.className = 'gallery ' + viewType + '-view';
    
    // Update active button
    document.querySelectorAll('.view-toggle .icon-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    localStorage.setItem('galleryView', viewType);
}

// Load saved view preference
function loadViewPreference() {
    const savedView = localStorage.getItem('galleryView') || 'comfortable';
    setView(savedView);
}

// Update showApp function to set user initial
function updateShowApp(email) {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    document.getElementById('user-email').textContent = email;
    
    // Set user initial in avatar
    const initial = email.charAt(0).toUpperCase();
    const userInitials = document.querySelectorAll('#user-initial, #user-initial-large');
    userInitials.forEach(el => el.textContent = initial);
}

// Enhanced Image Display for Gallery
function displayGalleryNew(images) {
    const gallery = document.getElementById('gallery');
    
    if (!images || images.length === 0) {
        gallery.innerHTML = `
            <div class="empty-state">
                <span class="material-icons">photo_library</span>
                <h2>No photos yet</h2>
                <p>Upload your first photos to get started</p>
                <button onclick="showUploadDialog()" class="btn btn-primary">
                    <span class="material-icons">cloud_upload</span>
                    Upload photos
                </button>
            </div>
        `;
        return;
    }
    
    gallery.innerHTML = images.map(image => {
        const tags = (image.tags || []).slice(0, 3);
        const tagsHTML = tags.map(tag => 
            `<span class="tag-chip-small">${tag}</span>`
        ).join('');
        
        return `
            <div class="gallery-item" onclick="openModal('${image.imageId}')">
                <img src="${image.urls.thumbnail}" alt="${image.imageName}" loading="lazy">
                <div class="gallery-item-overlay">
                    <div class="gallery-item-info">
                        <div>${image.imageName}</div>
                        ${tagsHTML ? `<div class="gallery-item-tags">${tagsHTML}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Update title
    document.getElementById('gallery-title').textContent = `Your Photos`;
    document.getElementById('photo-count').textContent = `${images.length} photo${images.length !== 1 ? 's' : ''}`;
}

// Enhanced Modal Display
function displayModalNew(image) {
    document.getElementById('modal-img').src = image.urls.large;
    document.getElementById('modal-filename').textContent = image.imageName;
    document.getElementById('modal-filesize').textContent = formatFileSize(image.fileSize);
    document.getElementById('modal-date').textContent = formatDate(image.uploadTimestamp);
    document.getElementById('modal-dimensions').textContent = `${image.width} × ${image.height}`;
    
    // Tags
    const tagsContainer = document.getElementById('modal-tags');
    const tagsSection = document.getElementById('tags-section');
    if (image.tags && image.tags.length > 0) {
        tagsContainer.innerHTML = image.tags.map(tag => 
            `<span class="tag-chip">${tag}</span>`
        ).join('');
        tagsSection.style.display = 'block';
    } else {
        tagsSection.style.display = 'none';
    }
    
    // AI Analysis
    const aiContainer = document.getElementById('modal-ai');
    const aiSection = document.getElementById('ai-section');
    if (image.aiAnalysis) {
        const ai = image.aiAnalysis;
        aiContainer.innerHTML = `
            ${ai.faceCount > 0 ? `<div class="ai-info-item">
                <div class="ai-info-label">Faces detected</div>
                <div class="ai-info-value">${ai.faceCount} ${ai.faceCount === 1 ? 'person' : 'people'}</div>
            </div>` : ''}
            ${ai.hasText ? `<div class="ai-info-item">
                <div class="ai-info-label">Text detected</div>
                <div class="ai-info-value">Yes</div>
            </div>` : ''}
            <div class="ai-info-item">
                <div class="ai-info-label">Content safety</div>
                <div class="ai-info-value">${ai.isSafe ? '✓ Safe' : '⚠ Flagged'}</div>
            </div>
        `;
        aiSection.style.display = 'block';
    } else {
        aiSection.style.display = 'none';
    }
    
    document.getElementById('image-modal').classList.add('show');
    currentImageId = image.imageId;
}

// Helper Functions
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleString('en-US', options);
}

// Initialize theme on load
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadViewPreference();
});

// Export functions to make them available globally
window.toggleTheme = toggleTheme;
window.toggleSidebar = toggleSidebar;
window.toggleUserMenu = toggleUserMenu;
window.showUploadDialog = showUploadDialog;
window.closeUploadDialog = closeUploadDialog;
window.showSearch = showSearch;
window.closeSearch = closeSearch;
window.showPhotos = showPhotos;
window.setView = setView;
window.displayGalleryNew = displayGalleryNew;
window.displayModalNew = displayModalNew;
window.updateShowApp = updateShowApp;
