# Driver-Monitor-v4.0
AI-based real time Driver Monitoring System to detect drowsiness and yawning using MediaPipe and OpenCV
Driver Monitor v4.0
**Developed by: nyimaswidyas**

Aplikasi deteksi kantuk real-time berbasis Python yang dirancang untuk meningkatkan keselamatan berkendara. Menggunakan teknologi Computer Vision untuk memantau kondisi wajah pengemudi secara presisi.

# Fitur Utama:
- **Anti-Sleep Alarm:** Bunyi beep 1 detik jika mata terdeteksi terpejam (kantuk).
- **Yawn Alert:** Peringatan suara otomatis jika pengemudi menguap.
- **Fast Launch:** Optimasi threading untuk pembukaan kamera yang cepat dan tanpa lag.
- **Automated Logging:** Mencatat setiap kejadian kantuk/menguap ke dalam file CSV secara otomatis.

# Teknologi yang Digunakan:
- Python 3.10
- OpenCV & MediaPipe (Face Mesh)
- CustomTkinter (Modern UI)
- gTTS (Google Text-to-Speech)
- Pygame (Audio Manager)
