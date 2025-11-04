// Photo Gallery Application
let cognitoUser = null;
let jwtToken = null;
let currentImages = [];
let currentImageId = null;
let signupEmail = '';

// Initialize Cognito User Pool
const poolData = {
    UserPoolId: CONFIG.cognito.userPoolId,
    ClientId: CONFIG.cognito.clientId
};
const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    hideLoading();
    checkAuthStatus();
    setupDragAndDrop();
});

// Authentication Functions
function checkAuthStatus() {
    const cognitoUser = userPool.getCurrentUser();
    
    if (cognitoUser) {
        cognitoUser.getSession((err, session) => {
            if (err) {
                showAuth();
                return;
            }
            
            if (session.isValid()) {
                jwtToken = session.getIdToken().getJwtToken();
                showApp(cognitoUser.getUsername());
                loadGallery();
            } else {
                showAuth();
            }
        });
    } else {
        showAuth();
    }
}

function showAuth() {
    document.getElementById('auth-container').style.display = 'flex';
    document.getElementById('app-container').style.display = 'none';
}

function showApp(email) {
    // Use the new UI function if available
    if (typeof updateShowApp === 'function') {
        updateShowApp(email);
    } else {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('app-container').style.display = 'flex';
        document.getElementById('user-email').textContent = email;
    }
}

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verify-form').style.display = 'none';
    clearAuthError();
}

function showSignup() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
    document.getElementById('verify-form').style.display = 'none';
    clearAuthError();
}

function showVerify() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('verify-form').style.display = 'block';
    clearAuthError();
}

function showAuthError(message) {
    const errorDiv = document.getElementById('auth-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearAuthError() {
    document.getElementById('auth-error').style.display = 'none';
}

function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    if (!email || !password) {
        showAuthError('Please enter email and password');
        return;
    }
    
    showLoading();
    
    const authenticationData = {
        Username: email,
        Password: password
    };
    
    const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
    
    const userData = {
        Username: email,
        Pool: userPool
    };
    
    cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    
    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function(result) {
            jwtToken = result.getIdToken().getJwtToken();
            hideLoading();
            showApp(email);
            loadGallery();
        },
        onFailure: function(err) {
            hideLoading();
            showAuthError(err.message || 'Login failed');
        }
    });
}

function signup() {
    console.log('Signup function called');
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;
    
    console.log('Email:', email, 'Password length:', password.length);
    
    if (!email || !password || !confirm) {
        showAuthError('Please fill in all fields');
        return;
    }
    
    if (password !== confirm) {
        showAuthError('Passwords do not match');
        return;
    }
    
    if (password.length < 8) {
        showAuthError('Password must be at least 8 characters');
        return;
    }
    
    showLoading();
    signupEmail = email;
    
    const attributeList = [
        new AmazonCognitoIdentity.CognitoUserAttribute({
            Name: 'email',
            Value: email
        })
    ];
    
    console.log('Attempting to sign up with Cognito...');
    userPool.signUp(email, password, attributeList, null, function(err, result) {
        hideLoading();
        
        if (err) {
            console.error('Signup error:', err);
            showAuthError(err.message || 'Signup failed');
            return;
        }
        
        console.log('Signup successful:', result);
        document.getElementById('verify-email').textContent = email;
        showVerify();
        alert('Signup successful! Please check your email for verification code.');
    });
}

function verifyEmail() {
    const code = document.getElementById('verify-code').value;
    
    if (!code) {
        showAuthError('Please enter verification code');
        return;
    }
    
    showLoading();
    
    const userData = {
        Username: signupEmail,
        Pool: userPool
    };
    
    cognitoUser = new AmazonCognitoIdentity.CognitoUser(userData);
    
    cognitoUser.confirmRegistration(code, true, function(err, result) {
        hideLoading();
        
        if (err) {
            showAuthError(err.message || 'Verification failed');
            return;
        }
        
        alert('Email verified! Please sign in.');
        showLogin();
    });
}

function logout() {
    if (cognitoUser) {
        cognitoUser.signOut();
    }
    
    jwtToken = null;
    cognitoUser = null;
    currentImages = [];
    
    showAuth();
    showLogin();
}

// Gallery Functions
async function loadGallery() {
    showGalleryLoading();
    
    try {
        console.log('Loading gallery with token:', jwtToken ? 'Token exists' : 'No token');
        const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.images}?limit=50&sortOrder=desc`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        console.log('Gallery response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Gallery error response:', errorText);
            throw new Error('Failed to load gallery');
        }
        
        const data = await response.json();
        console.log('Gallery data received:', data);
        console.log('Number of images:', data.images ? data.images.length : 0);
        
        currentImages = data.images || [];
        
        displayGallery(currentImages);
        const photoCountEl = document.getElementById('photo-count');
        if (photoCountEl) {
            photoCountEl.textContent = `${currentImages.length} photo${currentImages.length !== 1 ? 's' : ''}`;
        }
        
    } catch (error) {
        console.error('Error loading gallery:', error);
        alert('Failed to load gallery: ' + error.message);
    } finally {
        hideGalleryLoading();
    }
}

function displayGallery(images) {
    // Use the new UI function if available
    if (typeof displayGalleryNew === 'function') {
        displayGalleryNew(images);
        return;
    }
    
    // Fallback to old display
    const gallery = document.getElementById('gallery');
    const noPhotos = document.getElementById('no-photos');
    
    if (images.length === 0) {
        gallery.innerHTML = '';
        if (noPhotos) noPhotos.style.display = 'block';
        return;
    }
    
    if (noPhotos) noPhotos.style.display = 'none';
    
    gallery.innerHTML = images.map(img => `
        <div class="gallery-item" onclick="openModal('${img.imageId}')">
            <img src="${img.urls.thumbnail}" alt="${img.imageName}" loading="lazy">
            <div class="gallery-item-info">
                <div class="gallery-item-title">${img.imageName}</div>
                ${img.tags && img.tags.length > 0 ? `
                    <div class="tags">
                        ${img.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// Search Functions
async function searchImages(event) {
    if (event) event.preventDefault();
    
    // Try to get search term from either the top search bar or search panel
    const topSearchInput = document.getElementById('search-input');
    const panelSearchInput = document.getElementById('search-tags');
    
    let searchTerm = '';
    if (topSearchInput && topSearchInput.value.trim()) {
        searchTerm = topSearchInput.value.trim();
    } else if (panelSearchInput && panelSearchInput.value.trim()) {
        searchTerm = panelSearchInput.value.trim();
    }
    
    const facesFilter = document.getElementById('filter-faces');
    const textFilter = document.getElementById('filter-text');
    const dateFromFilter = document.getElementById('filter-date-from');
    const dateToFilter = document.getElementById('filter-date-to');
    
    const hasFaces = facesFilter ? facesFilter.checked : false;
    const hasText = textFilter ? textFilter.checked : false;
    const dateFrom = dateFromFilter ? dateFromFilter.value : '';
    const dateTo = dateToFilter ? dateToFilter.value : '';
    
    console.log('Search params:', { searchTerm, hasFaces, hasText, dateFrom, dateTo });
    
    if (!searchTerm && !hasFaces && !hasText && !dateFrom && !dateTo) {
        loadGallery();
        return;
    }
    
    showGalleryLoading();
    
    const params = new URLSearchParams();
    if (searchTerm) params.append('tags', searchTerm);
    if (hasFaces) params.append('hasFaces', 'true');
    if (hasText) params.append('hasText', 'true');
    if (dateFrom) params.append('dateFrom', dateFrom);
    if (dateTo) params.append('dateTo', dateTo);
    params.append('limit', '50');
    
    console.log('Search URL:', `${CONFIG.api.baseUrl}${CONFIG.api.endpoints.search}?${params}`);
    
    try {
        const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.search}?${params}`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        console.log('Search response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Search error response:', errorText);
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        console.log('Search results:', data);
        currentImages = data.images || [];
        
        displayGallery(currentImages);
        const photoCountEl = document.getElementById('photo-count');
        if (photoCountEl) {
            photoCountEl.textContent = `${currentImages.length} photo${currentImages.length !== 1 ? 's' : ''}`;
        }
        
    } catch (error) {
        console.error('Search error:', error);
        alert('Search failed: ' + error.message);
    } finally {
        hideGalleryLoading();
    }
}

function clearSearch() {
    document.getElementById('search-input').value = '';
    document.getElementById('filter-faces').checked = false;
    document.getElementById('filter-text').checked = false;
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    loadGallery();
}

// Upload Functions
function setupDragAndDrop() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    
    if (!uploadZone || !fileInput) {
        console.log('Upload elements not found');
        return;
    }
    
    // Setup file input change handler
    fileInput.addEventListener('change', handleFileSelect);
    
    // Setup drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => {
            uploadZone.classList.remove('drag-over');
        });
    });
    
    uploadZone.addEventListener('drop', handleDrop, false);
    
    // Make upload zone clickable
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
}

function handleDrop(e) {
    const files = e.dataTransfer.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

async function handleFiles(files) {
    const validFiles = Array.from(files).filter(file => {
        const isImage = file.type.startsWith('image/');
        const isValidSize = file.size <= 10 * 1024 * 1024; // 10MB
        
        if (!isImage) {
            alert(`${file.name} is not an image file`);
        } else if (!isValidSize) {
            alert(`${file.name} is too large (max 10MB)`);
        }
        
        return isImage && isValidSize;
    });
    
    if (validFiles.length === 0) return;
    
    const progress = document.getElementById('upload-progress');
    if (progress) {
        progress.style.display = 'block';
        progress.innerHTML = '<p style="text-align: center; padding: 12px;">Uploading images...</p>';
    }
    
    let successCount = 0;
    let errorCount = 0;
    
    for (const file of validFiles) {
        try {
            await uploadFile(file);
            successCount++;
            if (progress) {
                progress.innerHTML += `<div class="upload-item"><span class="material-icons" style="color: green;">check_circle</span><span>${file.name}</span></div>`;
            }
        } catch (error) {
            errorCount++;
            if (progress) {
                progress.innerHTML += `<div class="upload-item"><span class="material-icons" style="color: red;">error</span><span>${file.name}: ${error.message}</span></div>`;
            }
        }
    }
    
    setTimeout(() => {
        if (progress) {
            progress.style.display = 'none';
            progress.innerHTML = '';
        }
        // Reset file input
        const fileInput = document.getElementById('file-input');
        if (fileInput) fileInput.value = '';
        
        // Close dialog and reload
        if (typeof closeUploadDialog === 'function') {
            closeUploadDialog();
        }
        loadGallery();
    }, 2000);
}

async function uploadFile(file) {
    // Step 1: Get pre-signed URL
    const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.upload}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${jwtToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: file.name,
            contentType: file.type,
            fileSize: file.size
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to get upload URL');
    }
    
    const data = await response.json();
    
    // Step 2: Upload to S3
    const uploadResponse = await fetch(data.uploadUrl, {
        method: 'PUT',
        headers: {
            'Content-Type': file.type
        },
        body: file
    });
    
    if (!uploadResponse.ok) {
        throw new Error('Failed to upload to S3');
    }
}

// Modal Functions
function openModal(imageId) {
    console.log('openModal called with imageId:', imageId);
    console.log('currentImages array:', currentImages);
    
    const image = currentImages.find(img => img.imageId === imageId);
    if (!image) {
        console.error('Image not found in currentImages:', imageId);
        return;
    }
    
    console.log('Found image:', image);
    currentImageId = imageId;
    
    // Use the new UI function if available
    if (typeof displayModalNew === 'function') {
        console.log('Using displayModalNew');
        displayModalNew(image);
        return;
    }
    
    console.log('Using fallback modal display');
    
    // Fallback to old display
    const modalImg = document.getElementById('modal-image') || document.getElementById('modal-img');
    if (modalImg) modalImg.src = image.urls.large;
    
    const modalTitle = document.getElementById('modal-title') || document.getElementById('modal-filename');
    if (modalTitle) modalTitle.textContent = image.imageName;
    
    // Display tags
    const tagsHtml = image.tags && image.tags.length > 0
        ? image.tags.map(tag => `<span class="tag">${tag}</span>`).join('')
        : '<p>No tags yet</p>';
    const modalTags = document.getElementById('modal-tags');
    if (modalTags) modalTags.innerHTML = tagsHtml;
    
    // Display AI info
    let aiHtml = '';
    if (image.aiAnalysis) {
        aiHtml = `
            <p>🤖 AI Analysis:</p>
            <p>Faces detected: ${image.aiAnalysis.faceCount}</p>
            <p>Text detected: ${image.aiAnalysis.hasText ? 'Yes' : 'No'}</p>
            <p>Content: ${image.aiAnalysis.isSafe ? '✓ Safe' : '⚠ Flagged'}</p>
            ${image.aiAnalysis.topLabels ? `<p>Top labels: ${image.aiAnalysis.topLabels.join(', ')}</p>` : ''}
        `;
    } else {
        aiHtml = '<p>Processing...</p>';
    }
    const modalAiInfo = document.getElementById('modal-ai-info') || document.getElementById('modal-ai');
    if (modalAiInfo) modalAiInfo.innerHTML = aiHtml;
    
    const modal = document.getElementById('image-modal');
    console.log('Modal element:', modal);
    if (modal) {
        // Remove any inline styles first
        modal.style.display = '';
        // Add show class to trigger display
        modal.classList.add('show');
        console.log('Modal opened, show class added');
    } else {
        console.error('Modal element not found');
    }
}

function closeModal() {
    console.log('closeModal called');
    const modal = document.getElementById('image-modal');
    if (modal) {
        console.log('Closing modal, removing show class');
        modal.classList.remove('show');
    }
    currentImageId = null;
}

function downloadImage() {
    const image = currentImages.find(img => img.imageId === currentImageId);
    if (!image) return;
    
    const link = document.createElement('a');
    link.href = image.urls.original;
    link.download = image.imageName;
    link.click();
}

async function deleteCurrentImage() {
    if (!currentImageId) return;
    
    if (!confirm('Are you sure you want to delete this image? This cannot be undone.')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.delete}/${currentImageId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete image');
        }
        
        closeModal();
        loadGallery();
        
    } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete image: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Helper Functions
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showGalleryLoading() {
    const loadingEl = document.getElementById('gallery-loading');
    if (loadingEl) {
        loadingEl.style.display = 'flex';
    }
    // Show spinner in gallery
    const gallery = document.getElementById('gallery');
    if (gallery) {
        gallery.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;"><div class="spinner"></div></div>';
    }
}

function hideGalleryLoading() {
    const loadingEl = document.getElementById('gallery-loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}
