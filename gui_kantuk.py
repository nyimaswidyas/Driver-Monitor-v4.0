import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from scipy.spatial import distance as dist
import threading
import pygame
import time
import os
import csv
import sys
from datetime import datetime
from gtts import gTTS


def resource_path(relative_path):
    """ Dapatkan path absolut untuk resource (penting buat PyInstaller) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class DriverMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        
        self.title("Driver Monitor - by: nyimaswidyas")
        self.geometry("1100x700")

        self.cap = None
        self.is_running = False
        self.alarm_on = False
        self.counter_frames = 0
        self.total_kantuk = 0
        self.total_uap = 0
        self.yawn_state = False
        
        
        self.EYE_AR_THRESH = 0.22      
        self.EYE_CONSEC_FRAMES = 20    
        self.MOUTH_AR_THRESH = 0.65     

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        pygame.mixer.init()

        
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        self.MOUTH = [13, 14, 78, 308]

        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="DRIVER MONITOR", font=("Arial", 22, "bold"), text_color="#3498db").pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text="v4.0", font=("Arial", 22, "bold")).pack(pady=(0, 10))
        

        self.btn_start = ctk.CTkButton(self.sidebar, text="START MONITORING", fg_color="#27ae60", height=40, font=("Arial", 13, "bold"), command=self.threaded_start)
        self.btn_start.pack(pady=10, padx=20)

        self.btn_stop = ctk.CTkButton(self.sidebar, text="STOP MONITORING", fg_color="#c0392b", height=40, font=("Arial", 13, "bold"), command=self.stop_camera)
        self.btn_stop.pack(pady=10, padx=20)

        ctk.CTkLabel(self.sidebar, text="STATISTIK", font=("Arial", 14, "bold")).pack(pady=(40, 10))
        self.lbl_kantuk = ctk.CTkLabel(self.sidebar, text=f"Total Kantuk: 0", font=("Arial", 16))
        self.lbl_kantuk.pack(pady=5)
        self.lbl_uap = ctk.CTkLabel(self.sidebar, text=f"Total Menguap: 0", font=("Arial", 16))
        self.lbl_uap.pack(pady=5)

        self.video_label = ctk.CTkLabel(self, text="Klik Start untuk Memulai", fg_color="#1a1a1a", corner_radius=15)
        self.video_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    
    def play_warning_sound(self, pesan, file_voice, use_beep=False):
        try:
            
            if use_beep:
                path_beep = resource_path("beep.mp3") 
                if os.path.exists(path_beep):
                    pygame.mixer.music.load(path_beep)
                    pygame.mixer.music.play(-1)
                    time.sleep(1) 
                    pygame.mixer.music.stop()
            
            
            if not os.path.exists(file_voice):
                tts = gTTS(text=pesan, lang='id')
                tts.save(file_voice)
            
            pygame.mixer.music.load(file_voice)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                time.sleep(0.01)
        except Exception as e:
            print(f"Audio Error: {e}")
        finally:
            self.alarm_on = False

    def write_log(self, kejadian):
        filename = "laporan_driver_monitor.csv"
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not exists: writer.writerow(["Waktu", "Kejadian"])
            writer.writerow([waktu, kejadian])

    def threaded_start(self):
        if not self.is_running:
            self.btn_start.configure(state="disabled", text="Connecting...")
            threading.Thread(target=self.start_camera, daemon=True).start()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        if self.cap.isOpened():
            self.is_running = True
            self.btn_start.configure(state="normal", text="MONITORING ACTIVE")
            self.process_loop()
        else:
            self.btn_start.configure(state="normal", text="START MONITORING")

    def stop_camera(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.video_label.configure(image="", text="Sistem Off")
        self.btn_start.configure(text="START MONITORING")

    def get_ear(self, eye_pts, landmarks):
        p = [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in eye_pts]
        v1 = dist.euclidean(p[1], p[5]); v2 = dist.euclidean(p[2], p[4])
        h = dist.euclidean(p[0], p[3])
        return (v1 + v2) / (2.0 * h)

    def get_mar(self, mouth_pts, landmarks):
        p = [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in mouth_pts]
        v = dist.euclidean(p[0], p[1]); h = dist.euclidean(p[2], p[3])
        return v / h

    def process_loop(self):
        if self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = self.face_mesh.process(rgb_img)

                if res.multi_face_landmarks:
                    for face_lms in res.multi_face_landmarks:
                        ear = (self.get_ear(self.LEFT_EYE, face_lms) + self.get_ear(self.RIGHT_EYE, face_lms)) / 2.0
                        mar = self.get_mar(self.MOUTH, face_lms)

                        
                        if ear < self.EYE_AR_THRESH:
                            self.counter_frames += 1
                            if self.counter_frames >= self.EYE_CONSEC_FRAMES:
                                if not self.alarm_on:
                                    self.alarm_on = True
                                    self.total_kantuk += 1
                                    self.lbl_kantuk.configure(text=f"Total Kantuk: {self.total_kantuk}")
                                    self.write_log("KANTUK")
                                    threading.Thread(target=self.play_warning_sound, 
                                                     args=("kamu mengantuk, segera istirahat", "warn_k.mp3", True), daemon=True).start()
                        else:
                            self.counter_frames = 0

                        
                        if mar > self.MOUTH_AR_THRESH:
                            if not self.yawn_state:
                                self.yawn_state = True
                                self.total_uap += 1
                                self.lbl_uap.configure(text=f"Total Menguap: {self.total_uap}")
                                self.write_log("MENGUAP")
                                if not self.alarm_on:
                                    self.alarm_on = True
                                    threading.Thread(target=self.play_warning_sound, 
                                                     args=("istirahat dulu sejenak", "warn_u.mp3", False), daemon=True).start()
                        else:
                            self.yawn_state = False

                img_tk = ImageTk.PhotoImage(image=Image.fromarray(rgb_img))
                self.video_label.configure(image=img_tk, text="")
                self.video_label._image = img_tk 
            
            self.after(10, self.process_loop)

if __name__ == "__main__":
    app = DriverMonitorApp()
    app.mainloop()