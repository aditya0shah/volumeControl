from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np
import subprocess

app = Flask(__name__)

# Initialize MediaPipe pose detection
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Global variables
jumping_jacks_count = 0
is_tracking = False
volume_increment = 1
volume_up = True

# Set macOS volume
def set_volume(level):
    """Set system volume on macOS (0-100)"""
    try:
        script = f'set volume output volume {level}'
        subprocess.run(['osascript', '-e', script], check=True)
    except Exception as e:
        print(f"Error setting volume: {e}")

# Get current volume
def get_volume():
    """Get current system volume on macOS (0-100)"""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'output volume of (get volume settings)'],
            capture_output=True,
            text=True
        )
        return int(result.stdout.strip())
    except Exception:
        return 50

# Detect jumping jacks
class JumpingJackDetector:
    def __init__(self):
        self.previous_left_wrist_y = None
        self.previous_right_wrist_y = None
        self.left_arm_up = False
        self.right_arm_up = False
        self.left_arm_down = False
        self.right_arm_down = False
        
    def detect(self, landmarks, image_width, image_height):
        global jumping_jacks_count
        
        # Get key points
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * image_width,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * image_height]
        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * image_width,
                      landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * image_height]
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * image_width,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * image_height]
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * image_width,
                         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * image_height]
        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * image_width,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * image_height]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * image_width,
                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * image_height]
        
        # Detect vertical movement of wrists relative to shoulders
        if self.previous_left_wrist_y is not None and self.previous_right_wrist_y is not None:
            # Check if arms are going up
            if left_wrist[1] < left_shoulder[1] - 20 and not self.left_arm_up:
                self.left_arm_up = True
                self.left_arm_down = False
            # Check if arms are going down
            if left_wrist[1] > left_shoulder[1] + 20 and self.left_arm_up and not self.left_arm_down:
                self.left_arm_down = True
                
            if right_wrist[1] < right_shoulder[1] - 20 and not self.right_arm_up:
                self.right_arm_up = True
                self.right_arm_down = False
            if right_wrist[1] > right_shoulder[1] + 20 and self.right_arm_up and not self.right_arm_down:
                self.right_arm_down = True
            
            # Detect complete cycle (both arms up then down)
            if self.left_arm_up and self.right_arm_up and self.left_arm_down and self.right_arm_down:
                jumping_jacks_count += 1
                # Reset flags
                self.left_arm_up = False
                self.right_arm_up = False
                self.left_arm_down = False
                self.right_arm_down = False
                global volume_up
                
                if get_volume() == 100:
                    volume_up = False
                elif get_volume() == 0:
                    volume_up = True
                
                if volume_up:
                    new_volume = min(100, get_volume() + volume_increment)
                else:
                    new_volume = max(0, get_volume() - volume_increment)
                    
                set_volume(new_volume)
        
        self.previous_left_wrist_y = left_wrist[1]
        self.previous_right_wrist_y = right_wrist[1]
        
        return {
            'left_arm_up': self.left_arm_up,
            'right_arm_up': self.right_arm_up,
            'left_arm_down': self.left_arm_down,
            'right_arm_down': self.right_arm_down
        }

detector = JumpingJackDetector()

def generate_frames():
    global is_tracking
    
    # Try to open camera with different backends
    camera = None
    for i in range(3):  # Try camera indices 0, 1, 2
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            print(f"Successfully opened camera {i}")
            break
        camera.release()
    
    if camera is None or not camera.isOpened():
        print("ERROR: Cannot open any camera")
        # Send a blank frame with error message
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank_frame, "ERROR: Cannot access camera", (50, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(blank_frame, "Check permissions in System Settings", (50, 290),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
        ret, buffer = cv2.imencode('.jpg', blank_frame)
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = camera.read()
        if not success:
            print("ERROR: Failed to read from camera")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        if is_tracking:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # Detect jumping jacks
                detector.detect(results.pose_landmarks.landmark, frame.shape[1], frame.shape[0])
        
        # Display count
        cv2.putText(frame, f'Jumping Jacks: {jumping_jacks_count}', 
                   (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(frame, f'Volume: {get_volume()}%', 
                   (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 165, 0), 3)
        cv2.putText(frame, 'Status: Tracking' if is_tracking else 'Status: Stopped', 
                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255) if is_tracking else (128, 128, 128), 3)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start', methods=['POST'])
def start_tracking():
    global is_tracking
    is_tracking = True
    return jsonify({'status': 'started'})

@app.route('/stop', methods=['POST'])
def stop_tracking():
    global is_tracking
    is_tracking = False
    return jsonify({'status': 'stopped'})

@app.route('/reset', methods=['POST'])
def reset_count():
    global jumping_jacks_count
    jumping_jacks_count = 0
    return jsonify({'status': 'reset', 'count': jumping_jacks_count})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'count': jumping_jacks_count,
        'volume': get_volume(),
        'tracking': is_tracking
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)

