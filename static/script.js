document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    const compressBtn = document.getElementById('compressBtn');
    const compressionLevel = document.getElementById('compressionLevel');
    const compressionValue = document.getElementById('compressionValue');
    const downloadBtn = document.getElementById('downloadBtn');
    const statistics = document.getElementById('statistics');
    
    // Drag and drop handling
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    dropZone.addEventListener('click', () => {
        imageInput.click();
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    compressionLevel.addEventListener('input', (e) => {
        compressionValue.textContent = e.target.value;
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            showAlert('Please select an image file');
            return;
        }
        compressBtn.disabled = false;
        dropZone.innerHTML = `<img src="${URL.createObjectURL(file)}" style="max-height: 200px;">`;
    }

    compressBtn.addEventListener('click', async () => {
        const file = imageInput.files[0] || dropZone.querySelector('img').src;
        const formData = new FormData();
        formData.append('image', file);
        formData.append('compression_level', compressionLevel.value);

        compressBtn.disabled = true;
        compressBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        try {
            const response = await fetch('/compress', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.success) {
                document.getElementById('resultImage').innerHTML = 
                    `<img src="data:image/jpeg;base64,${data.compressed_image}">`;
                document.getElementById('processingTime').textContent = `${data.processing_time}s`;
                document.getElementById('compressionRatio').textContent = `${data.compression_ratio}%`;
                document.getElementById('originalSize').textContent = data.original_size;
                document.getElementById('finalSize').textContent = data.final_size;
                statistics.classList.remove('d-none');
            } else {
                showAlert(data.error);
            }
        } catch (error) {
            showAlert('An error occurred during compression');
        } finally {
            compressBtn.disabled = false;
            compressBtn.innerHTML = '<i class="fas fa-compress"></i> Compress Image';
        }
    });

    downloadBtn.addEventListener('click', () => {
        window.location.href = '/download';
    });

    function showAlert(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.main-card').prepend(alert);
    }
});
