@echo off
title Smart Attendance System
cd /d "C:\Users\marta\OneDrive\Desktop\face_attendance_system"
call venv\Scripts\activate
streamlit run app.py --server.port 8080
pause