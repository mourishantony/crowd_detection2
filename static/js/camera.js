document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const openCameraBtn = document.getElementById('openCameraBtn');
    const captureBtn = document.getElementById('captureBtn');
    const closeCameraBtn = document.getElementById('closeCameraBtn');
    const cameraFeed = document.getElementById('cameraFeed');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const uploadForm = document.getElementById('uploadForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const submitBtn = document.getElementById('submitBtn');
    const successMessage = document.getElementById('successMessage');
    const placeInput = document.getElementById('placeInput');
    const placeList = document.getElementById('placeList');
    const comboboxToggle = document.getElementById('comboboxToggle');

    let stream = null;

    // Combobox functionality
    if (placeInput && placeList && comboboxToggle) {
        const listItems = placeList.querySelectorAll('li');
        
        // Toggle dropdown
        comboboxToggle.addEventListener('click', (e) => {
            e.preventDefault();
            placeList.classList.toggle('show');
            if (placeList.classList.contains('show')) {
                placeInput.focus();
            }
        });
        
        // Show dropdown on input focus
        placeInput.addEventListener('focus', () => {
            placeList.classList.add('show');
            filterList('');
        });
        
        // Filter list as user types
        placeInput.addEventListener('input', () => {
            filterList(placeInput.value);
        });
        
        // Select item on click
        listItems.forEach(item => {
            item.addEventListener('click', () => {
                placeInput.value = item.dataset.value;
                placeList.classList.remove('show');
            });
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.combobox-wrapper')) {
                placeList.classList.remove('show');
            }
        });
        
        function filterList(query) {
            const q = query.toLowerCase();
            listItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(q) || q === '') {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });
        }
    }

    // Click to browse files
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    // Drag & drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#2563eb';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '#d1d5db';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#d1d5db';
        if (e.dataTransfer.files.length > 0) {
            imageInput.files = e.dataTransfer.files;
            showPreview(e.dataTransfer.files[0]);
        }
    });

    // File selected
    imageInput.addEventListener('change', () => {
        if (imageInput.files.length > 0) {
            showPreview(imageInput.files[0]);
        }
    });

    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
            uploadPlaceholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    function resetForm() {
        imagePreview.style.display = 'none';
        uploadPlaceholder.style.display = 'block';
        imageInput.value = '';
        uploadForm.reset();
    }

    // Open camera
    openCameraBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: 1280, height: 720 }
            });
            cameraFeed.srcObject = stream;
            cameraFeed.style.display = 'block';
            captureBtn.style.display = 'inline-block';
            closeCameraBtn.style.display = 'inline-block';
            openCameraBtn.style.display = 'none';
        } catch (err) {
            IPS Tech CommunityAlert('Could not access camera: ' + err.message, 'error');
        }
    });

    // Capture photo
    captureBtn.addEventListener('click', () => {
        cameraCanvas.width = cameraFeed.videoWidth;
        cameraCanvas.height = cameraFeed.videoHeight;
        cameraCanvas.getContext('2d').drawImage(cameraFeed, 0, 0);

        cameraCanvas.toBlob((blob) => {
            const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            imageInput.files = dataTransfer.files;
            showPreview(file);
            closeCamera();
        }, 'image/jpeg', 0.95);
    });

    // Close camera
    closeCameraBtn.addEventListener('click', closeCamera);

    function closeCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        cameraFeed.style.display = 'none';
        captureBtn.style.display = 'none';
        closeCameraBtn.style.display = 'none';
        openCameraBtn.style.display = 'inline-block';
    }

    // AJAX form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate place
        const place = placeInput ? placeInput.value.trim() : '';
        if (!place) {
            IPS Tech CommunityAlert('Please enter or select a place.', 'error');
            return;
        }

        if (!imageInput.files || imageInput.files.length === 0) {
            IPS Tech CommunityAlert('Please select or capture an image first.', 'error');
            return;
        }

        loadingOverlay.style.display = 'flex';
        submitBtn.disabled = true;

        const formData = new FormData(uploadForm);

        try {
            const response = await fetch(uploadForm.action, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            loadingOverlay.style.display = 'none';
            submitBtn.disabled = false;

            if (data.success) {
                // Show success toast
                successMessage.style.display = 'flex';
                resetForm();
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 2000);
            } else {
                IPS Tech CommunityAlert(data.error || 'An error occurred.', 'error');
            }
        } catch (err) {
            loadingOverlay.style.display = 'none';
            submitBtn.disabled = false;
            IPS Tech CommunityAlert('Upload failed: ' + err.message, 'error');
        }
    });
});
