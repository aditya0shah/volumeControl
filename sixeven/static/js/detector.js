const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('canvas');
const canvasCtx = canvasElement.getContext('2d');
const detectionStatus = document.getElementById('detection-status');
const statusText = detectionStatus.querySelector('.status-text');

let hands;
let camera;
let isDetected = false;

// Gesture tracking variables
const motionHistory = [];
const maxHistoryLength = 30; // ~1 second at 30fps

// Initialize MediaPipe Hands
function initializeHands() {
    hands = new Hands({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        }
    });
    
    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    hands.onResults(onResults);
}

// Process results from MediaPipe
function onResults(results) {
    // Clear canvas
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Draw hand landmarks (MediaPipe coordinates are normalized 0-1)
    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            // Draw hand connections
            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 2 });
            // Draw hand landmarks
            drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 1, radius: 3 });
        }
    }
    
    canvasCtx.restore();
    
    // Detect gesture
    detectSixSevenGesture(results);
}

// Main gesture detection function
function detectSixSevenGesture(results) {
    if (!results.multiHandLandmarks || results.multiHandLandmarks.length < 2) {
        // Need both hands
        motionHistory.length = 0;
        updateDetectionStatus(false, 'Waiting for both hands...');
        return;
    }
    
    const leftHand = results.multiHandLandmarks[0];
    const rightHand = results.multiHandLandmarks[1];
    
    // Determine which hand is left and which is right
    const hands = determineHandPositions(leftHand, rightHand);
    
    // Check if palms are facing upward
    const leftPalmUp = isPalmUp(hands.left);
    const rightPalmUp = isPalmUp(hands.right);
    
    if (!leftPalmUp || !rightPalmUp) {
        updateDetectionStatus(false, 'Palms should face upward');
        return;
    }
    
    // Get wrist positions (landmark 0 is wrist)
    const leftWristY = hands.left[0].y;
    const rightWristY = hands.right[0].y;
    
    // Store current hand positions
    const currentState = {
        leftY: leftWristY,
        rightY: rightWristY,
        timestamp: Date.now()
    };
    
    motionHistory.push(currentState);
    
    // Keep only recent history
    if (motionHistory.length > maxHistoryLength) {
        motionHistory.shift();
    }
    
    // Need enough history to detect pattern
    if (motionHistory.length < 10) {
        updateDetectionStatus(false, 'Moving hands...');
        return;
    }
    
    // Detect seesaw pattern
    const detected = detectSeesawPattern(motionHistory);
    
    if (detected) {
        updateDetectionStatus(true, 'SIX-SEVEN DETECTED!');
    } else {
        updateDetectionStatus(false, 'Make seesaw motion...');
    }
}

// Determine which hand is left and which is right
function determineHandPositions(hand1, hand2) {
    // Use wrist position relative to the center
    const hand1WristX = hand1[0].x;
    const hand2WristX = hand2[0].x;
    
    return {
        left: hand1WristX < hand2WristX ? hand1 : hand2,
        right: hand1WristX < hand2WristX ? hand2 : hand1
    };
}

// Check if palm is facing upward
function isPalmUp(landmarks) {
    // Use wrist (0), middle finger MCP (9), and index finger MCP (5)
    // to determine palm orientation
    const wrist = landmarks[0];
    const middleMcp = landmarks[9];
    const indexMcp = landmarks[5];
    
    // Calculate normal vector of the palm
    // Vector from wrist to middle of MCP points
    const midMcp = {
        x: (middleMcp.x + indexMcp.x) / 2,
        y: (middleMcp.y + indexMcp.y) / 2,
        z: (middleMcp.z + indexMcp.z) / 2
    };
    
    // For palm up, the z-coordinate should be negative (closer to camera)
    // and the vector from wrist to palm center should point upward in Y
    // Simple heuristic: check if wrist is below the MCP points in Y
    const palmUp = wrist.y > midMcp.y;
    
    return palmUp;
}

// Detect seesaw pattern (alternating up/down motion)
function detectSeesawPattern(history) {
    if (history.length < 10) return false;
    
    // Calculate relative positions (left hand relative to right hand)
    const relativePositions = history.map(state => state.leftY - state.rightY);
    
    // Check for alternating pattern
    // Count zero-crossings (when relative position changes sign)
    let zeroCrossings = 0;
    let lastSign = relativePositions[0] >= 0 ? 1 : -1;
    
    for (let i = 1; i < relativePositions.length; i++) {
        const currentSign = relativePositions[i] >= 0 ? 1 : -1;
        if (currentSign !== lastSign) {
            zeroCrossings++;
            lastSign = currentSign;
        }
    }
    
    // Check motion amplitude (hands should move significantly)
    const minY = Math.min(...history.map(h => Math.min(h.leftY, h.rightY)));
    const maxY = Math.max(...history.map(h => Math.max(h.leftY, h.rightY)));
    const amplitude = maxY - minY;
    
    // Detection criteria:
    // - At least 2 zero-crossings (alternating motion)
    // - Significant vertical movement (amplitude > threshold)
    const minZeroCrossings = 2;
    const minAmplitude = 0.05; // Minimum movement in normalized coordinates
    
    const hasAlternatingMotion = zeroCrossings >= minZeroCrossings;
    const hasEnoughMovement = amplitude > minAmplitude;
    
    // Additional check: verify hands are moving in opposite directions
    let oppositeMotionCount = 0;
    for (let i = 1; i < history.length; i++) {
        const leftDelta = history[i].leftY - history[i-1].leftY;
        const rightDelta = history[i].rightY - history[i-1].rightY;
        
        // If one hand moves up and the other moves down
        if ((leftDelta > 0 && rightDelta < 0) || (leftDelta < 0 && rightDelta > 0)) {
            oppositeMotionCount++;
        }
    }
    
    const hasOppositeMotion = oppositeMotionCount > history.length * 0.3; // At least 30% of frames
    
    return hasAlternatingMotion && hasEnoughMovement && hasOppositeMotion;
}

// Update detection status UI
function updateDetectionStatus(detected, message) {
    statusText.textContent = message;
    
    if (detected && !isDetected) {
        detectionStatus.classList.add('detected');
        isDetected = true;
    } else if (!detected && isDetected) {
        detectionStatus.classList.remove('detected');
        isDetected = false;
    }
}

// Initialize camera and MediaPipe
async function initCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        videoElement.srcObject = stream;
        
        // Set canvas size to match video
        videoElement.addEventListener('loadedmetadata', () => {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
        });
        
        // Initialize MediaPipe Hands
        initializeHands();
        
        // Start camera processing
        camera = new Camera(videoElement, {
            onFrame: async () => {
                await hands.send({ image: videoElement });
            },
            width: 640,
            height: 480
        });
        
        camera.start();
    } catch (error) {
        console.error('Error accessing webcam:', error);
        statusText.textContent = 'Error: Could not access webcam';
        alert('Please allow webcam access to use this application.');
    }
}

// Start when page loads
window.addEventListener('load', () => {
    initCamera();
});

