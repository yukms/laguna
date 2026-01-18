"""
Example 1: Basic system initialization and status check

This example shows how to:
- Initialize the FlumeLab system
- Check connection status
- View system status
- Gracefully shutdown
"""

from laguna import FlumeLab


def main():
    """Run basic initialization example."""
    
    # Initialize the system with default configuration
    lab = FlumeLab()
    
    # Connect to all subsystems
    print("Connecting to all subsystems...")
    if not lab.connect_all():
        print("ERROR: Failed to connect to all systems")
        return
    
    # Check system status
    print("\nSystem Status:")
    status = lab.get_system_status()
    for subsystem, info in status.items():
        print(f"  {subsystem}: {info}")
    
    # Disconnect gracefully
    print("\nDisconnecting...")
    lab.disconnect_all()
    print("Done!")


if __name__ == "__main__":
    main()
