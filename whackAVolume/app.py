from flask import Flask, render_template, jsonify, request
import random
import subprocess
import threading
import time

app = Flask(__name__)

# Global variables
mole_grid = []  # Grid showing which holes have moles
mole_numbers = {}  # Dictionary mapping (row, col) to volume numbers
mole_timers = {}  # Dictionary mapping (row, col) to spawn time
score = 0
game_active = False
spawn_thread = None
volume_decay_thread = None
spawn_interval = 0.8  # Seconds between mole spawns
mole_ttl = 3.0  # Time to live for moles (seconds)
volume_decay_interval = 1.0  # Seconds between volume decreases
volume_decay_amount = 5  # Amount to decrease volume by
lock = threading.Lock()

# Initialize mole grid (10x10)
def init_grid():
    global mole_grid
    mole_grid = [[False for _ in range(10)] for _ in range(10)]
    mole_numbers.clear()
    mole_timers.clear()

# Set macOS volume
def set_volume(level):
    """Set system volume on macOS (0-100)"""
    try:
        script = f'set volume output volume {level}'
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False

# Get current volume
def get_volume():
    """Get current system volume on macOS (0-100)"""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'output volume of (get volume settings)'],
            capture_output=True,
            text=True
        )
        level = int(result.stdout.strip())
        # level = max(0, level - 5)
        return level
    except Exception:
        return 50

# Spawn moles randomly
def spawn_mole():
    """Continuously spawn moles while game is active"""
    while game_active:
        with lock:
            # Remove expired moles
            current_time = time.time()
            expired_moles = []
            for (row, col), spawn_time in mole_timers.items():
                if current_time - spawn_time > mole_ttl:
                    expired_moles.append((row, col))
            
            for pos in expired_moles:
                row, col = pos
                mole_grid[row][col] = False
                if pos in mole_numbers:
                    del mole_numbers[pos]
                if pos in mole_timers:
                    del mole_timers[pos]
            
            # Find empty holes
            empty_holes = []
            for row in range(10):
                for col in range(10):
                    if not mole_grid[row][col]:
                        empty_holes.append((row, col))
            
            # Spawn new mole if conditions are met
            if empty_holes and len(mole_numbers) < 3:  # Max 3 moles at once
                row, col = random.choice(empty_holes)
                mole_grid[row][col] = True
                mole_numbers[(row, col)] = random.randint(1, 100)
                mole_timers[(row, col)] = time.time()
        
        time.sleep(spawn_interval)

# Volume decay function
def volume_decay():
    """Continuously decrease volume while game is active"""
    while game_active:
        try:
            current_volume = get_volume()
            new_volume = max(0, current_volume - volume_decay_amount)
            set_volume(new_volume)
        except Exception as e:
            print(f"Error in volume decay: {e}")
        
        time.sleep(volume_decay_interval)

# Initialize grid on startup
init_grid()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grid', methods=['GET'])
def get_grid():
    """Return the current grid state"""
    with lock:
        # Convert mole_numbers dict to grid format
        grid = [[0 for _ in range(10)] for _ in range(10)]
        for (row, col), number in mole_numbers.items():
            grid[row][col] = number
        
        return jsonify({'grid': grid, 'score': score, 'game_active': game_active})

@app.route('/hit', methods=['POST'])
def hit_cell():
    """Handle hitting a mole"""
    global mole_numbers, score
    
    try:
        data = request.json
        row = data['row']
        col = data['col']
        
        volume_level = None
        with lock:
            # Check if there's a mole at this position
            if (row, col) in mole_numbers:
                # Get the volume number
                volume_level = mole_numbers[(row, col)]
                
                # Remove the mole
                mole_grid[row][col] = False
                del mole_numbers[(row, col)]
                if (row, col) in mole_timers:
                    del mole_timers[(row, col)]
        
        # Set volume outside of lock to avoid blocking
        if volume_level is not None:
            if set_volume(volume_level):
                score += 1
                
                return jsonify({
                    'success': True,
                    'volume_set': volume_level,
                    'score': score,
                    'current_volume': get_volume()
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to set volume'})
        else:
            return jsonify({'success': False, 'error': 'No mole here!'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/start', methods=['POST'])
def start_game():
    """Start the game"""
    global game_active, spawn_thread, volume_decay_thread
    
    if not game_active:
        game_active = True
        spawn_thread = threading.Thread(target=spawn_mole, daemon=True)
        spawn_thread.start()
        volume_decay_thread = threading.Thread(target=volume_decay, daemon=True)
        volume_decay_thread.start()
        return jsonify({'success': True, 'message': 'Game started!'})
    else:
        return jsonify({'success': False, 'message': 'Game already running!'})

@app.route('/stop', methods=['POST'])
def stop_game():
    """Stop the game"""
    global game_active, mole_grid, mole_numbers
    game_active = False
    
    # Clear all moles
    init_grid()
    
    return jsonify({'success': True, 'message': 'Game stopped!'})

@app.route('/status', methods=['GET'])
def get_status():
    """Get current status including volume"""
    return jsonify({
        'score': score,
        'current_volume': get_volume(),
        'game_active': game_active
    })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the game"""
    global score, game_active, mole_grid, mole_numbers
    game_active = False
    init_grid()
    score = 0
    return jsonify({'success': True, 'score': score, 'message': 'Game reset!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001, threaded=True)
