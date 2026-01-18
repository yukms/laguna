"""
Example 3: Manual subsystem control

This example demonstrates how to control individual subsystems
without going through the main experiment workflow. Useful for:
- Testing individual components
- Calibration procedures
- Troubleshooting
"""

from laguna import FlumeLab


def test_robot():
    """Test robot control independently."""
    print("=== Testing Robot ===")
    
    lab = FlumeLab()
    
    # Connect only the robot
    if not lab.robot.connect():
        print("Failed to connect to robot")
        return
    
    # Home the robot
    print("Homing robot...")
    lab.robot.home()
    
    # Move to a position
    print("Moving to position (100, 100, 50)...")
    lab.robot.move_to((100, 100, 50), speed=0.5)
    
    # Get current position
    pos = lab.robot.get_position()
    print(f"Current position: {pos}")
    
    # Return home and disconnect
    lab.robot.home()
    lab.robot.disconnect()
    print("Done!\n")


def test_camera():
    """Test camera independently."""
    print("=== Testing Camera ===")
    
    lab = FlumeLab()
    
    # Start camera
    if not lab.camera.start():
        print("Failed to start camera")
        return
    
    print("Capturing 10 frames...")
    for i in range(10):
        frame = lab.camera.get_frame()
        if frame is not None:
            print(f"  Frame {i+1} captured")
    
    # Stop camera
    total_frames = lab.camera.get_frame_count()
    lab.camera.stop()
    print(f"Total frames captured: {total_frames}")
    print("Done!\n")


def test_hydraulics():
    """Test hydraulics independently."""
    print("=== Testing Hydraulics ===")
    
    lab = FlumeLab()
    
    # Connect to hydraulics
    if not lab.hydraulics.connect():
        print("Failed to connect to hydraulics")
        return
    
    # Start system
    if not lab.hydraulics.start():
        print("Failed to start hydraulics")
        return
    
    # Set pressure
    print("Setting pressure to 2000 Pa...")
    lab.hydraulics.set_pressure(2000)
    
    # Get status
    import time
    time.sleep(1)  # Wait for system to settle
    
    status = lab.hydraulics.get_status()
    print(f"Hydraulics status: {status}")
    
    # Stop and disconnect
    lab.hydraulics.stop()
    lab.hydraulics.disconnect()
    print("Done!\n")


def main():
    """Run all subsystem tests."""
    test_robot()
    test_camera()
    test_hydraulics()


if __name__ == "__main__":
    main()
