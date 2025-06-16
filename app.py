from flask import Flask, render_template, request, jsonify, send_file, url_for
import numpy as np
import base64
import io
import time
import os
from PIL import Image
from sklearn.decomposition import PCA
from datetime import datetime
import traceback

app = Flask(__name__, static_folder='static')
app.secret_key = "pca_image_compression_secret"

class PCAImageCompressor:
    """
    Kelas untuk kompresi gambar menggunakan Principal Component Analysis (PCA)
    """
    
    def __init__(self):
        self.original_image = None
        self.compressed_image = None
        self.compression_ratio = 0
        self.processing_time = 0
        self.target_size = 100 * 1024  # Target 100KB dalam bytes
        self.last_compression_settings = None  # Tambahkan ini untuk menyimpan pengaturan terakhir
    
    def normalize_image(self, image_array):
        """
        Normalisasi array gambar ke rentang 0-1
        """
        return (image_array - np.min(image_array)) / (np.max(image_array) - np.min(image_array))
    
    def get_file_size(self, image_or_buffer):
        """Hitung ukuran file dalam KB"""
        if isinstance(image_or_buffer, Image.Image):
            buffer = io.BytesIO()
            image_or_buffer.save(buffer, format='JPEG', quality=95)
            size = len(buffer.getvalue())
        else:
            size = len(image_or_buffer.getvalue())
        return size / 1024  # Convert to KB
    
    def compress_image(self, image_file, compression_level):
        """
        Kompresi gambar menggunakan PCA
        
        Args:
            image_file: File gambar input
            compression_level: Tingkat kompresi (1-100)
            
        Returns:
            dict: Hasil kompresi dengan metadata
        """
        try:
            start_time = time.time()
            
            # Baca gambar dan dapatkan ukuran asli
            image = Image.open(image_file)
            original_buffer = io.BytesIO()
            image.save(original_buffer, format='JPEG', quality=95)
            original_size = self.get_file_size(original_buffer)
            
            # Resize gambar jika terlalu besar untuk menghindari memory error
            max_dimension = 1200  # Increased from 800
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Konversi ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # PCA compression
            img_array = np.array(image, dtype=np.float32)
            original_shape = img_array.shape
            
            # Adjust compression components based on level
            min_dimension = min(original_shape[0], original_shape[1])
            n_components = max(1, int((compression_level / 100) * min_dimension))
            n_components = min(n_components, min_dimension - 1)
            
            # Compress each channel
            compressed_channels = []
            for i in range(3):
                channel = img_array[:,:,i]
                pca = PCA(n_components=n_components)
                compressed = pca.fit_transform(channel)
                reconstructed = pca.inverse_transform(compressed)
                compressed_channels.append(reconstructed)
            
            compressed_array = np.stack(compressed_channels, axis=2)
            compressed_array = np.clip(compressed_array, 0, 255).astype(np.uint8)
            
            # Convert to PIL Image
            compressed_image = Image.fromarray(compressed_array)
            
            # Kompresi progresif dengan kualitas yang disesuaikan
            quality = max(5, min(95, int(100 - compression_level)))
            compressed_size = float('inf')
            best_buffer = None
            best_quality = quality
            
            # Coba beberapa level kualitas untuk mencapai ukuran target
            while quality >= 5 and compressed_size > 100:
                buffer = io.BytesIO()
                compressed_image.save(buffer, 
                                   format="JPEG", 
                                   quality=quality, 
                                   optimize=True, 
                                   progressive=True)
                compressed_size = self.get_file_size(buffer)
                
                if compressed_size <= 100:
                    best_buffer = buffer
                    best_quality = quality
                    break
                    
                quality -= 5
            
            if best_buffer is None:
                best_buffer = buffer
                best_quality = quality
                
            # Simpan pengaturan kompresi terakhir
            self.last_compression_settings = {
                'quality': best_quality,
                'optimize': True,
                'progressive': True
            }
            
            # Convert untuk display
            img_base64 = base64.b64encode(best_buffer.getvalue()).decode()
            
            # Simpan untuk download (dengan ukuran yang benar)
            self.compressed_image = best_buffer.getvalue()  # Simpan bytes langsung
            final_size = self.get_file_size(best_buffer)
            
            # Hitung statistik
            processing_time = time.time() - start_time
            compression_ratio = ((original_size - final_size) / original_size) * 100
            
            return {
                'success': True,
                'compressed_image': img_base64,
                'processing_time': round(processing_time, 3),
                'compression_ratio': round(compression_ratio, 2),
                'original_size': f"{original_size:.1f} KB",
                'final_size': f"{final_size:.1f} KB",
                'n_components': n_components,
                'quality': best_quality,
                'original_dimensions': f"{original_shape[1]}x{original_shape[0]}"
            }
            
        except Exception as e:
            print(f"Error in compress_image: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': f'Gagal memproses gambar: {str(e)}'
            }

# Inisialisasi compressor
compressor = PCAImageCompressor()

@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_image():
    """Endpoint untuk kompresi gambar"""
    try:
        # Validasi file
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Tidak ada file yang diunggah'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Tidak ada file yang dipilih'})
        
        # Validasi tipe file
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Format file tidak didukung'})
        
        # Ambil tingkat kompresi
        compression_level = int(request.form.get('compression_level', 50))
        
        # Validasi tingkat kompresi
        if not 1 <= compression_level <= 100:
            return jsonify({'success': False, 'error': 'Tingkat kompresi harus antara 1-100'})
        
        # Reset file pointer
        file.seek(0)
        
        # Kompresi gambar
        result = compressor.compress_image(file, compression_level)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in compress endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Terjadi kesalahan: {str(e)}'})

@app.route('/download')
def download_image():
    """Download gambar hasil kompresi"""
    try:
        if compressor.compressed_image is None:
            return jsonify({'success': False, 'error': 'Tidak ada gambar untuk diunduh'})
        
        # Simpan gambar sementara
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compressed_image_{timestamp}.jpg"
        
        # Buat folder temp jika belum ada
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        filepath = os.path.join(temp_dir, filename)
        
        # Tulis bytes langsung ke file
        with open(filepath, 'wb') as f:
            f.write(compressor.compressed_image)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"Error in download: {e}")
        return jsonify({'success': False, 'error': f'Gagal mengunduh: {str(e)}'})

if __name__ == '__main__':
    # Buat folder templates jika belum ada
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Add static folder check
    if not os.path.exists('static'):
        os.makedirs('static')

    print("Starting PCA Image Compression Server...")
    print("Akses aplikasi di: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)