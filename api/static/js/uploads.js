/**
 * Upload functionality - Drag & drop and file validation
 */

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadForm = document.getElementById('upload-form');
    const filePreview = document.getElementById('file-preview');
    const removeFileBtn = document.getElementById('remove-file');
    
    if (!dropZone || !fileInput) return;
    
    // File size limits
    const MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024; // 4GB
    const ALLOWED_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
    
    // Browse button click
    if (browseBtn) {
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    // Click on drop zone to browse
    dropZone.addEventListener('click', (e) => {
        if (e.target === dropZone || e.target.classList.contains('upload-area')) {
            fileInput.click();
        }
    });
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }
    
    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFiles(e.target.files);
        }
    });
    
    // Handle files
    function handleFiles(files) {
        const file = files[0];
        
        // Validate file
        if (!validateFile(file)) {
            return;
        }
        
        // Show preview
        showFilePreview(file);
    }
    
    // Validate file
    function validateFile(file) {
        // Check type
        if (!ALLOWED_TYPES.includes(file.type)) {
            alert('Invalid file type. Please upload MP4, MOV, AVI, or MKV.');
            return false;
        }
        
        // Check size
        if (file.size > MAX_FILE_SIZE) {
            alert('File is too large. Maximum size is 4GB.');
            return false;
        }
        
        return true;
    }
    
    // Show file preview
    function showFilePreview(file) {
        const uploadArea = document.querySelector('.upload-area');
        
        // Hide upload area, show preview
        uploadArea.style.display = 'none';
        filePreview.style.display = 'block';
        
        // Set file info
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('file-size').textContent = formatFileSize(file.size);
    }
    
    // Remove file
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Reset file input
            fileInput.value = '';
            
            // Hide preview, show upload area
            filePreview.style.display = 'none';
            document.querySelector('.upload-area').style.display = 'block';
        });
    }
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Uploading...';
                submitBtn.disabled = true;
            }
        });
    }
});
