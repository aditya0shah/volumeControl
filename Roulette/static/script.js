let isSpinning = false;
let audioContext = null;
let clickTimeout = null;

// Initialize audio context for sound effects
function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    // Resume audio context if suspended (required for browser autoplay policies)
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

// Play a clicking sound
function playClickSound() {
    if (!audioContext) {
        initAudioContext();
    }
    
    try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Create a sharp click sound
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.01);
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.01);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.01);
    } catch (error) {
        // Silently fail if audio context is not available
        console.debug('Audio context not available:', error);
    }
}

// Roulette number configuration: 0 = green, others are red or black
const rouletteNumbers = [
    { num: 0, color: 'green' },
    { num: 1, color: 'red' },
    { num: 2, color: 'black' },
    { num: 3, color: 'red' },
    { num: 4, color: 'black' },
    { num: 5, color: 'red' },
    { num: 6, color: 'black' },
    { num: 7, color: 'red' },
    { num: 8, color: 'black' },
    { num: 9, color: 'red' },
    { num: 10, color: 'black' },
    { num: 11, color: 'black' },
    { num: 12, color: 'red' },
    { num: 13, color: 'black' },
    { num: 14, color: 'red' },
    { num: 15, color: 'black' },
    { num: 16, color: 'red' },
    { num: 17, color: 'black' },
    { num: 18, color: 'red' },
    { num: 19, color: 'red' },
    { num: 20, color: 'black' },
    { num: 21, color: 'red' },
    { num: 22, color: 'black' },
    { num: 23, color: 'red' },
    { num: 24, color: 'black' },
    { num: 25, color: 'red' },
    { num: 26, color: 'black' },
    { num: 27, color: 'red' },
    { num: 28, color: 'black' },
    { num: 29, color: 'black' },
    { num: 30, color: 'red' },
    { num: 31, color: 'black' },
    { num: 32, color: 'red' },
    { num: 33, color: 'black' },
    { num: 34, color: 'red' },
    { num: 35, color: 'black' },
    { num: 36, color: 'red' }
];

// Initialize roulette wheel
function initRouletteWheel() {
    const wheelSvg = document.getElementById('wheelSvg');
    const segmentsGroup = document.getElementById('wheelSegments');
    const totalNumbers = rouletteNumbers.length;
    const anglePerNumber = 360 / totalNumbers;
    const centerX = 250;
    const centerY = 250;
    const radius = 240;
    const innerRadius = 80;
    
    // First, create all segments
    rouletteNumbers.forEach((item, index) => {
        const startAngle = (index * anglePerNumber - 90) * (Math.PI / 180);
        const endAngle = ((index + 1) * anglePerNumber - 90) * (Math.PI / 180);
        
        // Calculate points for the segment
        const x1 = centerX + radius * Math.cos(startAngle);
        const y1 = centerY + radius * Math.sin(startAngle);
        const x2 = centerX + radius * Math.cos(endAngle);
        const y2 = centerY + radius * Math.sin(endAngle);
        const x3 = centerX + innerRadius * Math.cos(endAngle);
        const y3 = centerY + innerRadius * Math.sin(endAngle);
        const x4 = centerX + innerRadius * Math.cos(startAngle);
        const y4 = centerY + innerRadius * Math.sin(startAngle);
        
        // Create path for donut segment
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const largeArcFlag = anglePerNumber > 180 ? 1 : 0;
        // Create a ring segment: outer arc -> line -> inner arc (reverse) -> line back
        const d = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
        path.setAttribute('d', d);
        path.setAttribute('fill', item.color === 'red' ? '#c41e3a' : item.color === 'black' ? '#1a1a1a' : '#0d6e42');
        path.setAttribute('stroke', '#2c3e50');
        path.setAttribute('stroke-width', '2');
        segmentsGroup.appendChild(path);
    });
    
    // Add inner circle after all segments
    const innerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    innerCircle.setAttribute('cx', centerX);
    innerCircle.setAttribute('cy', centerY);
    innerCircle.setAttribute('r', innerRadius);
    innerCircle.setAttribute('fill', '#2c3e50');
    innerCircle.setAttribute('stroke', '#1a1a1a');
    innerCircle.setAttribute('stroke-width', '3');
    segmentsGroup.appendChild(innerCircle);
    
    // Add number text labels (on top of inner circle)
    rouletteNumbers.forEach((item, index) => {
        const textAngle = (index * anglePerNumber + anglePerNumber / 2 - 90) * (Math.PI / 180);
        const textRadius = (radius + innerRadius) / 2;
        const textX = centerX + textRadius * Math.cos(textAngle);
        const textY = centerY + textRadius * Math.sin(textAngle);
        
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', textX);
        text.setAttribute('y', textY);
        text.textContent = item.num;
        text.setAttribute('fill', 'white');
        text.setAttribute('font-size', '20');
        text.setAttribute('font-weight', 'bold');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        segmentsGroup.appendChild(text);
    });
}

// Update volume display on page load
window.addEventListener('DOMContentLoaded', () => {
    initAudioContext();
    initRouletteWheel();
    updateVolumeDisplay();
    // Refresh volume every 2 seconds
    setInterval(updateVolumeDisplay, 2000);
});

async function updateVolumeDisplay() {
    try {
        const response = await fetch('/api/volume/current');
        const data = await response.json();
        const volume = data.volume;
        
        document.getElementById('currentVolume').textContent = volume + '%';
        document.getElementById('volumeBar').style.width = volume + '%';
    } catch (error) {
        console.error('Error fetching volume:', error);
    }
}

async function spinRoulette() {
    if (isSpinning) return;
    
    isSpinning = true;
    const spinButton = document.getElementById('spinButton');
    const wheelSvg = document.getElementById('wheelSvg');
    const resultPanel = document.getElementById('resultPanel');
    
    spinButton.disabled = true;
    resultPanel.style.display = 'none';
    
    try {
        const response = await fetch('/api/roulette/spin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        // Calculate rotation needed to land on the result number
        // Each number occupies 360/37 degrees, and we want it to land at the top (pointer position)
        const anglePerNumber = 360 / rouletteNumbers.length;
        const targetAngle = result.number * anglePerNumber;
        // Add multiple full rotations for spinning effect
        const baseRotation = 1800; // 5 full rotations
        const finalRotation = baseRotation - targetAngle + (360 - (anglePerNumber / 2));
        
        // Get current rotation
        const currentRotation = wheelSvg.style.transform.match(/rotate\(([^)]+)\)/) 
            ? parseFloat(wheelSvg.style.transform.match(/rotate\(([^)]+)\)/)[1]) || 0 
            : 0;
        
        // Start clicking sounds
        startClickingSounds();
        
        // Add spinning animation
        wheelSvg.style.transition = 'transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99)';
        wheelSvg.style.transform = `rotate(${currentRotation + finalRotation}deg)`;
        
        // Wait for animation to complete, then apply volume change
        setTimeout(async () => {
            // Stop clicking sounds
            stopClickingSounds();
            
            // Apply the volume change after the wheel stops spinning
            try {
                await fetch('/api/volume/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ volume: result.new_volume })
                });
            } catch (error) {
                console.error('Error setting volume:', error);
            }
            
            displayResult(result);
            updateVolumeDisplay();
            spinButton.disabled = false;
            isSpinning = false;
        }, 4000);
        
    } catch (error) {
        console.error('Error spinning roulette:', error);
        stopClickingSounds();
        spinButton.disabled = false;
        isSpinning = false;
        alert('Error spinning roulette. Please try again.');
    }
}

// Start clicking sounds with decreasing frequency (like a real roulette wheel)
function startClickingSounds() {
    initAudioContext();
    
    // Clear any existing timeouts
    if (clickTimeout) {
        clearTimeout(clickTimeout);
    }
    
    const startTime = Date.now();
    const duration = 4000; // 4 seconds
    const totalClicks = 50; // Total number of clicks
    
    // Play initial click
    playClickSound();
    
    let clickCount = 1;
    
    // Schedule clicks with increasing interval (slowing down)
    function scheduleNextClick() {
        if (clickCount >= totalClicks) {
            stopClickingSounds();
            return;
        }
        
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out curve - clicks slow down as wheel stops
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        
        // Interval starts fast (~50ms) and ends slow (~300ms)
        const minInterval = 50;
        const maxInterval = 300;
        const currentInterval = minInterval + (maxInterval - minInterval) * easedProgress;
        
        clickTimeout = setTimeout(() => {
            playClickSound();
            clickCount++;
            scheduleNextClick();
        }, currentInterval);
    }
    
    scheduleNextClick();
}

// Stop clicking sounds
function stopClickingSounds() {
    if (clickTimeout) {
        clearTimeout(clickTimeout);
        clickTimeout = null;
    }
}

function displayResult(result) {
    const resultPanel = document.getElementById('resultPanel');
    const resultText = document.getElementById('resultText');
    const volumeChangeText = document.getElementById('volumeChangeText');
    
    const colorEmoji = {
        'red': '🔴',
        'black': '⚫',
        'green': '🟢'
    };
    
    resultPanel.style.display = 'block';
    resultText.textContent = `${colorEmoji[result.color]} Landed on ${result.number} (${result.color.toUpperCase()})`;
    
    const volumeChange = result.volume_change;
    let changeText = '';
    
    if (result.color === 'green') {
        changeText = `Volume set to ${result.new_volume}% (random)`;
    } else if (volumeChange > 0) {
        changeText = `Volume increased by ${volumeChange}% (${result.previous_volume}% → ${result.new_volume}%)`;
    } else {
        changeText = `Volume decreased by ${Math.abs(volumeChange)}% (${result.previous_volume}% → ${result.new_volume}%)`;
    }
    
    volumeChangeText.textContent = changeText;
}

