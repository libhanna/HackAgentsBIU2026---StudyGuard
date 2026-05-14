import cv2
import pygetwindow as gw

print("Checking Window...")
try:
    print(f"Active Window: {gw.getActiveWindow().title}")
except:
    print("Window detection failed")

print("Checking Camera...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("Camera is working!")
    cap.release()
else:
    print("Camera failed")