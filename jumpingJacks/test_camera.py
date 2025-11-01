#!/usr/bin/env python3
"""Quick test script to check if camera is accessible"""
import cv2
import sys

print("Testing camera access...")
print("=" * 50)

# Try different camera indices
for i in range(3):
    print(f"\nTrying camera index {i}...")
    camera = cv2.VideoCapture(i)
    
    if camera.isOpened():
        print(f"✓ Successfully opened camera {i}")
        
        # Try to read a frame
        success, frame = camera.read()
        if success:
            print(f"✓ Successfully read frame from camera {i}")
            print(f"  Frame shape: {frame.shape}")
            camera.release()
            print("\nCamera is working! You can now run the main app.")
            sys.exit(0)
        else:
            print(f"✗ Failed to read frame from camera {i}")
    else:
        print(f"✗ Cannot open camera {i}")
    
    camera.release()

print("\n" + "=" * 50)
print("ERROR: Cannot access any camera!")
print("\nTroubleshooting steps:")
print("1. Make sure no other app is using the camera")
print("2. Grant camera permissions to Terminal:")
print("   System Settings → Privacy & Security → Camera")
print("   Enable Terminal/Python")
print("3. Check your macOS version and OpenCV compatibility")
sys.exit(1)

