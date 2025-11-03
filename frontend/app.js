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
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('app-container').style.display = 'block';
    document.getElementById('user-email').textContent = email;
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
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;
    
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
    
    userPool.signUp(email, password, attributeList, null, function(err, result) {
        hideLoading();
        
        if (err) {
            showAuthError(err.message || 'Signup failed');
            return;
        }
        
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
        const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.images}?limit=50&sortOrder=desc`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load gallery');
        }
        
        const data = await response.json();
        currentImages = data.images || [];
        
        displayGallery(currentImages);
        document.getElementById('photo-count').textContent = `(${currentImages.length})`;
        
    } catch (error) {
        console.error('Error loading gallery:', error);
        alert('Failed to load gallery: ' + error.message);
    } finally {
        hideGalleryLoading();
    }
}

function displayGallery(images) {
    const gallery = document.getElementById('gallery');
    const noPhotos = document.getElementById('no-photos');
    
    if (images.length === 0) {
        gallery.innerHTML = '';
        noPhotos.style.display = 'block';
        return;
    }
    
    noPhotos.style.display = 'none';
    
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
async function searchImages() {
    const searchTerm = document.getElementById('search-input').value.trim();
    const hasFaces = document.getElementById('filter-faces').checked;
    const hasText = document.getElementById('filter-text').checked;
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    
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
    
    try {
        const response = await fetch(`${CONFIG.api.baseUrl}${CONFIG.api.endpoints.search}?${params}`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        currentImages = data.images || [];
        
        displayGallery(currentImages);
        document.getElementById('photo-count').textContent = `(${currentImages.length} found)`;
        
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
    const uploadBox = document.getElementById('upload-box');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => {
            uploadBox.classList.add('dragging');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => {
            uploadBox.classList.remove('dragging');
        });
    });
    
    uploadBox.addEventListener('drop', handleDrop, false);
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
    progress.style.display = 'block';
    progress.innerHTML = '<p>Uploading images...</p>';
    
    for (const file of validFiles) {
        try {
            await uploadFile(file);
            progress.innerHTML += `<p>✓ ${file.name} uploaded successfully</p>`;
        } catch (error) {
            progress.innerHTML += `<p>✗ ${file.name} failed: ${error.message}</p>`;
        }
    }
    
    setTimeout(() => {
        progress.style.display = 'none';
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
    const image = currentImages.find(img => img.imageId === imageId);
    if (!image) return;
    
    currentImageId = imageId;
    
    document.getElementById('modal-image').src = image.urls.large;
    document.getElementById('modal-title').textContent = image.imageName;
    
    // Display tags
    const tagsHtml = image.tags && image.tags.length > 0
        ? image.tags.map(tag => `<span class="tag">${tag}</span>`).join('')
        : '<p>No tags yet</p>';
    document.getElementById('modal-tags').innerHTML = tagsHtml;
    
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
    document.getElementById('modal-ai-info').innerHTML = aiHtml;
    
    document.getElementById('image-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('image-modal').style.display = 'none';
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
    document.getElementById('gallery-loading').style.display = 'flex';
}

function hideGalleryLoading() {
    document.getElementById('gallery-loading').style.display = 'none';
}
