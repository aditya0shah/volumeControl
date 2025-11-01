from flask import Flask, render_template, jsonify, request
import subprocess
import random
import json

app = Flask(__name__)

def get_current_volume():
    """Get current macOS volume level (0-100)"""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'output volume of (get volume settings)'],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except:
        return 50  # Default if unable to get volume

def set_volume(level):
    """Set macOS volume level (0-100)"""
    try:
        level = max(0, min(100, int(level)))  # Clamp between 0-100
        subprocess.run(
            ['osascript', '-e', f'set volume output volume {level}'],
            check=True
        )
        return True
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False

@app.route('/')
def index():
    """Render the main roulette game page"""
    return render_template('index.html')

@app.route('/api/volume/current', methods=['GET'])
def current_volume():
    """Get current volume level"""
    volume = get_current_volume()
    return jsonify({'volume': volume})

@app.route('/api/volume/set', methods=['POST'])
def set_volume_api():
    """Set volume level via API"""
    data = request.json
    volume = data.get('volume', 50)
    success = set_volume(volume)
    current = get_current_volume()
    return jsonify({'success': success, 'volume': current})

@app.route('/api/roulette/spin', methods=['POST'])
def spin_roulette():
    """Handle roulette spin and return result with volume change"""
    data = request.json
    spin_result = random.randint(0, 36)
    
    # Calculate volume change based on roulette result
    # Red (1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36) = increase volume
    # Black (2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35) = decrease volume
    # 0 (green) = random volume
    
    red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    black_numbers = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
    
    current_vol = get_current_volume()
    color = None
    volume_change = 0
    
    if spin_result == 0:
        color = 'green'
        # Random volume between 0-100
        new_volume = random.randint(0, 100)
        volume_change = new_volume - current_vol
    elif spin_result in red_numbers:
        color = 'red'
        # Increase volume by random amount (10-30%)
        volume_change = random.randint(10, 30)
        new_volume = min(100, current_vol + volume_change)
    else:  # black
        color = 'black'
        # Decrease volume by random amount (10-30%)
        volume_change = -random.randint(10, 30)
        new_volume = max(0, current_vol + volume_change)
    
    # Don't apply volume change yet - return the target volume
    # The frontend will apply it after the animation completes
    
    return jsonify({
        'number': spin_result,
        'color': color,
        'volume_change': volume_change,
        'previous_volume': current_vol,
        'new_volume': new_volume
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

