# Six-Seven Meme Detector

A Flask web application that detects the "six-seven meme" hand gesture in real-time using webcam and MediaPipe Hands for hand landmark detection.

## What is the Six-Seven Meme?

The "six-seven meme" involves a hand gesture where both hands move up and down in a seesaw motion with palms facing upward. This gesture gained popularity on TikTok in late 2024.

## Features

- Real-time hand gesture detection using MediaPipe Hands
- Webcam integration for live video feed
- Visual feedback when the gesture is detected
- Modern, responsive UI
- Client-side processing (no data sent to server)

## Requirements

- Python 3.7+
- Modern web browser with webcam support
- Webcam/camera device

## Installation

1. Clone or navigate to this repository:
```bash
cd sixeven
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:3000
```

3. Allow webcam access when prompted.

4. Make the six-seven gesture:
   - Hold both hands with palms facing upward
   - Move them up and down in a seesaw motion (one hand goes up while the other goes down)
   - Keep both hands visible to the camera

5. When the gesture is detected, you'll see a green notification with "SIX-SEVEN DETECTED!"

## How It Works

1. **MediaPipe Hands**: Detects hand landmarks (21 points per hand) in real-time
2. **Palm Orientation**: Verifies both palms are facing upward
3. **Motion Tracking**: Tracks vertical movement of both hands over time
4. **Pattern Recognition**: Detects the seesaw pattern where:
   - Hands move in opposite directions
   - Alternating up/down motion occurs
   - Sufficient vertical amplitude is present

## Project Structure

```
sixeven/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── detector.js   # Gesture detection logic
└── README.md             # This file
```

## Technical Details

- **Backend**: Flask serves the static HTML page
- **Frontend**: JavaScript with MediaPipe Hands SDK for client-side ML processing
- **Gesture Algorithm**: Custom algorithm that analyzes hand landmark positions and motion patterns
- **Real-time Processing**: Processes video frames at ~30fps using MediaPipe's efficient pipeline

## Browser Compatibility

Works best in:
- Google Chrome (recommended)
- Microsoft Edge
- Firefox (with webcam support)
- Safari (with webcam support)

## Troubleshooting

- **Webcam not working**: Check browser permissions and allow camera access
- **Detection not working**: Ensure both hands are fully visible and well-lit
- **Poor performance**: Close other applications using the webcam or reduce video resolution

## License

This project is open source and available for educational purposes.


