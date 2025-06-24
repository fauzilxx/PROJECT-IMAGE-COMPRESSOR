# PCA Image Compression Web App

## Table of Contents
- [Penjelasan Program](#penjelasan-program)  
- [Basic Information](#basic-information)  
- [Display Program](#display-program)  
- [How to Run](#how-to-run)  
- [Project Structure](#project-structure)  

---

## Penjelasan Program
Aplikasi web ini menggunakan Principal Component Analysis (PCA) untuk mengurangi dimensi data gambar dan menghasilkan versi terkompresi dengan kualitas terkontrol.  
Komponen utama:
- **Backend**: Flask (Python) menangani upload, kompresi, dan endpoint untuk pratinjau & unduhan.  
- **Frontend**: HTML/JavaScript interaktif dengan drag-&-drop, slider tingkat kompresi, dan area tampilan hasil.  
- **Algoritma**:  
  1. Baca dan (opsional) ubah ke grayscale  
  2. Normalisasi piksel dan hitung PCA  
  3. Rekonstruksi dengan _n_ komponen sesuai slider  
  4. Iterasi kualitas JPEG hingga mencapai rasio yang diinginkan  

---

### Basic Information
- **Bahasa & Framework**: Python 3.8+, Flask  
- **Dependencies**: `numpy`, `scikit-learn`, `Pillow`, `flask`  
- **Antarmuka**:
  - Drag-&-drop area  
  - File picker  
  - Slider kompresi (1–100)  
  - Tombol **Compress Image** & **Download**  
  - Tampilan metadata (waktu, rasio, ukuran, dimensi)  

### Display Program
![image](https://github.com/user-attachments/assets/d88481b9-6057-4d5b-b224-53ca45c56916)


## How to Run
1. Pastikan Anda berada di direktori proyek.  
2. Instal dependencies:
   ```bash
   pip install -r requirements.txt
3. Jalankan server Flask langsung:
   ```bash
   python run.py

### Project Structure
```text
repo/
├── app.py                  
├── run.py                  
├── requirements.txt        
├── templates/
│   └── index.html          
├── static/
│   ├── style.css           
│   └── script.js           
└── temp/                   
```
