# pages/3_AI_Personal_Trainer.py

import streamlit as st
import cv2
import numpy as np
import os
import sys

# Add the parent directory to sys.path to properly import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our theme system
from utils.theme import apply_theme

# Apply consistent dark theme with page config
apply_theme("AI Personal Trainer", set_page=True)

# Try to import mediapipe, handle import error gracefully
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mediapipe_available = True
except ImportError as e:
    mediapipe_available = False
    import_error = str(e)

# Try to import streamlit_webrtc, handle import error gracefully
try:
    from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
    webrtc_available = True
except ImportError:
    webrtc_available = False

st.markdown("""
<div class="card fade-in">
    <h3>💪 Real-time Exercise Form Analysis</h3>
    <p>Select an exercise below and follow along with your webcam to get personalized form feedback and accurate rep counting!</p>
</div>
""", unsafe_allow_html=True)

# Check if required packages are available
if not mediapipe_available or not webrtc_available:
    st.error("⚠️ Required packages for AI Personal Trainer are not available.")
    
    if not mediapipe_available:
        st.error(f"MediaPipe error: {import_error}")
        st.markdown("""
        ### How to fix MediaPipe issues:
        
        1. **Install Visual C++ Redistributable:**
           - Download and install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
        
        2. **Try a different Python version:**
           - MediaPipe works best with Python 3.9 or 3.10 on Windows
           - Create a new environment with `python -m venv venv-py39` using Python 3.9
        
        3. **Reinstall packages:**
           ```
           pip uninstall mediapipe opencv-python streamlit-webrtc -y
           pip install mediapipe==0.10.0 opencv-python streamlit-webrtc
           ```
        """)
    
    if not webrtc_available:
        st.error("streamlit-webrtc is not installed.")
        st.markdown("""
        ### Install streamlit-webrtc:
        ```
        pip install streamlit-webrtc
        ```
        """)
        
    st.markdown("""
    ### Using Sample Exercise Videos Instead
    
    While the AI Personal Trainer feature is unavailable, you can follow along with these sample exercise videos:
    """)
    
    # Sample exercise videos
    exercise_videos = {
        "Squat": "https://www.youtube.com/watch?v=YaXPRqUwItQ",
        "Push-up": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "Lunge": "https://www.youtube.com/watch?v=QOVaHwm-Q6U"
    }
    
    for exercise, video_url in exercise_videos.items():
        st.markdown(f"#### {exercise} Form Guide")
        st.video(video_url)
        
    st.stop()  # Stop execution of the rest of the page

# --- SELECT EXERCISE ---
EXERCISES = ["Squat", "Push‑up", "Lunge"]
exercise = st.selectbox("Choose Exercise", EXERCISES)

# Exercise descriptions
exercise_descriptions = {
    "Squat": """
        <div class="card">
            <h4>Proper Squat Form</h4>
            <ul>
                <li>Stand with feet shoulder-width apart</li>
                <li>Keep your back straight and chest up</li>
                <li>Lower your body by bending at the knees and hips</li>
                <li>Keep knees tracking over toes, not caving inward</li>
                <li>Aim for thighs parallel to the ground</li>
            </ul>
        </div>
    """,
    "Push‑up": """
        <div class="card">
            <h4>Proper Push-up Form</h4>
            <ul>
                <li>Position hands slightly wider than shoulder-width</li>
                <li>Keep your body in a straight line from head to heels</li>
                <li>Lower your chest toward the ground by bending elbows</li>
                <li>Keep elbows at about 45° angle to your body</li>
                <li>Push back up to starting position</li>
            </ul>
        </div>
    """,
    "Lunge": """
        <div class="card">
            <h4>Proper Lunge Form</h4>
            <ul>
                <li>Stand with feet hip-width apart</li>
                <li>Step forward with one leg, lowering hips until both knees are bent at 90°</li>
                <li>Keep front knee aligned with ankle</li>
                <li>Keep torso upright and core engaged</li>
                <li>Push through the heel of your front foot to return to starting position</li>
            </ul>
        </div>
    """
}

# Display exercise description
st.markdown(exercise_descriptions[exercise], unsafe_allow_html=True)

# --- POSE ESTIMATION SETUP ---

# Threshold angles for counting reps
ANGLE_THRESHOLDS = {
    "Squat":    {"min": 70,  "max": 160, "joints": ("left_hip", "left_knee", "left_ankle")},
    "Push‑up":  {"min": 50,  "max": 160, "joints": ("left_shoulder", "left_elbow", "left_wrist")},
    "Lunge":    {"min": 70,  "max": 160, "joints": ("left_hip", "left_knee", "left_ankle")},
}

# Helper to calculate angle between three landmarks
def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle

class PoseTrainer(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(min_detection_confidence=0.5,
                                 min_tracking_confidence=0.5)
        # Rep counters & states
        self.count = 0
        self.direction = 0  # 0 = down, 1 = up
        self.feedback = "Starting..."

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Extract required landmarks
            thr = ANGLE_THRESHOLDS[exercise]
            lm = results.pose_landmarks.landmark
            joints = thr["joints"]
            
            try:
                a = [lm[mp_pose.PoseLandmark[joints[0].upper()].value].x,
                     lm[mp_pose.PoseLandmark[joints[0].upper()].value].y]
                b = [lm[mp_pose.PoseLandmark[joints[1].upper()].value].x,
                     lm[mp_pose.PoseLandmark[joints[1].upper()].value].y]
                c = [lm[mp_pose.PoseLandmark[joints[2].upper()].value].x,
                     lm[mp_pose.PoseLandmark[joints[2].upper()].value].y]

                angle = calculate_angle(a, b, c)

                # Map angle to percentage for UI bar
                per = np.interp(angle, (thr["min"], thr["max"]), (100, 0))
                bar = np.interp(angle, (thr["min"], thr["max"]), (0, 100))

                # Generate form feedback
                if angle < thr["min"] + 5:
                    self.feedback = "Good depth!"
                elif angle > thr["max"] - 10:
                    self.feedback = "Lower your body more"
                else:
                    self.feedback = "Keep going"

                # Count reps: down → up pattern
                if per == 100 and self.direction == 0:
                    self.direction = 1
                    self.count += 0.5
                if per == 0 and self.direction == 1:
                    self.direction = 0
                    self.count += 0.5

                # Draw UI overlays - in white for better visibility in dark theme
                # Background for text
                cv2.rectangle(img, (5, 5), (350, 135), (0, 0, 0), -1)
                
                # Rep counter
                cv2.putText(img, f'{exercise} Count: {int(self.count)}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                # Angle display            
                cv2.putText(img, f'Angle: {int(angle)}°', (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                # Feedback display
                cv2.putText(img, f'Feedback: {self.feedback}', (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                # Progress Bar
                cv2.rectangle(img, (10, 150), (30, 350), (255, 255, 255), 2)
                cv2.rectangle(img, (10, int(350 - bar*2)), (30, 350), (0, 255, 0), -1)
                
            except Exception as e:
                # Handle any errors with landmark detection
                cv2.putText(img, "Error: Position yourself in camera view", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # No pose detected
            cv2.putText(img, "No pose detected - move into camera view", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return img

# --- CAMERA SETUP INFO ---
st.markdown("""
<div class="card fade-in">
    <h4>💻 Camera Setup Tips</h4>
    <ul>
        <li>Position your camera to show your full body</li>
        <li>Ensure you have adequate lighting</li>
        <li>Wear contrasting clothes to your background</li>
        <li>Allow camera permissions when prompted</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- START STREAM ---
try:
    webrtc_ctx = webrtc_streamer(
        key="trainer",
        mode="SENDRECV",
        video_processor_factory=PoseTrainer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
    
    if not webrtc_ctx.state.playing:
        st.warning("Click 'START' to begin the exercise tracking")
except Exception as e:
    error_msg = str(e)
    st.error(f"Error with webcam: {error_msg}")
    st.info("Make sure your webcam is connected and you've given permission to access it. If using a mobile device, this feature may be limited.")
    
    # Fallback instructions
    st.markdown("""
    <div class="card">
        <h4>Unable to access camera?</h4>
        <p>You can still follow along with these tips:</p>
        <ul>
            <li>Set up a mirror to check your form</li>
            <li>Follow the form guidelines above</li>
            <li>Start with fewer repetitions to master form</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
