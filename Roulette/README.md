# Volume Roulette 🎰

A Flask web application that controls your macOS volume through a fun roulette game!

## How It Works

- **Red numbers**: Increase your volume by 10-30%
- **Black numbers**: Decrease your volume by 10-30%
- **Green (0)**: Sets volume to a random level (0-100%)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

4. Click the "SPIN" button and watch the roulette wheel determine your volume!

## Requirements

- Python 3.7+
- Flask
- macOS (for volume control functionality)

## Notes

- The app requires macOS as it uses AppleScript (`osascript`) to control system volume
- You may need to grant Terminal/Python permissions to control system volume in System Preferences > Security & Privacy

