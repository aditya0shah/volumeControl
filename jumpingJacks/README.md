# Jumping Jack Volume Control

A fun web application that adjusts your macOS system volume based on how many jumping jacks you do! The app uses your webcam and computer vision to detect when you perform jumping jacks.

## Features

- 🎥 Real-time pose detection using MediaPipe
- 🏃 Automatic jumping jack counting
- 🔊 Dynamic volume control (2% increase per jumping jack)
- 🎨 Beautiful, modern web interface
- 📱 Responsive design

## Requirements

- macOS (for volume control)
- Python 3.8 or higher
- Webcam/Camera
- Internet connection (for downloading dependencies)

## Installation

1. Navigate to the project directory:
```bash
cd jumpingJacks
```

2. Create a virtual environment (recommended):
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**Note:** This project requires Python 3.12 (Python 3.13 is not compatible with MediaPipe yet)

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Start the Flask server:
```bash
python app.py
```

   Or use the convenience script:
```bash
./run.sh
```

3. Open your web browser and navigate to:
```
http://localhost:8000
```

   **Note:** The app uses port 8000 instead of 5000 to avoid conflicts with macOS AirPlay Receiver.

4. Allow camera access when prompted

5. Click "Start Tracking" to begin detecting jumping jacks

6. Perform jumping jacks in front of your camera:
   - Stand in front of the camera
   - Do complete jumping jacks (arms up, then down)
   - Each complete cycle increases volume by 2%

7. Click "Stop Tracking" when done

8. Click "Reset Count" to reset the jumping jack counter

## How It Works

The application uses:
- **MediaPipe Pose**: Detects your body pose in real-time
- **Computer Vision**: Analyzes arm movement to detect complete jumping jack cycles
- **macOS AppleScript**: Controls system volume through `osascript`
- **Flask**: Serves the web interface and handles video streaming

### Jumping Jack Detection Logic

The app detects a complete jumping jack by tracking:
1. Both arms raised above shoulder level
2. Both arms lowered below shoulder level

Each complete cycle (both arms up and back down) counts as one jumping jack.

## File Structure

```
jumpingJacks/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt       # Python dependencies
├── run.sh                # Convenience script to run the app
├── test_camera.py        # Camera testing script
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Troubleshooting

### Camera not working
- **Test camera access first**: Run the test script to diagnose camera issues:
  ```bash
  python test_camera.py
  ```
- **Grant camera permissions**: On macOS, grant camera access for Terminal or Python:
  - Go to System Settings/Settings → Privacy & Security → Camera
  - Enable Terminal (or Python/your IDE)
- Make sure no other application is using your camera
- Check terminal for error messages
- On some Macs, try different camera indices in app.py (change `VideoCapture(0)` to `VideoCapture(1)`)

### Volume not changing
- Verify you're on macOS (this app is macOS-specific)
- Try adjusting volume manually to ensure system volume works
- Check terminal for any error messages

### Pose not detected
- Ensure you're visible in the camera frame
- Improve lighting in the room
- Stand further back from the camera
- Wear contrasting clothing

## Customization

### Adjust Volume Increment

In `app.py`, find the volume update line:
```python
new_volume = min(100, get_volume() + 2)  # Change 2 to your desired increment
```

### Change Port

In `app.py`, modify the last line:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change 8000 to your desired port
```

## License

This project is open source and available for personal use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements!

