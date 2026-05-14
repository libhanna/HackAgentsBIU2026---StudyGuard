@mcp.tool()
def check_user_presence() -> str:
    """Uses the webcam to check if a face is present in front of the computer."""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return "Error: Could not access camera."
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return "Error: Could not read frame from camera."
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    return "User Present" if len(faces) > 0 else "User Absent"