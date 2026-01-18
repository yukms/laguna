"""Test suite for robot control subsystem."""

import pytest
from laguna.robot import RobotController


class TestRobotController:
    """Test cases for RobotController class."""
    
    @pytest.fixture
    def robot(self):
        """Create a robot instance for testing."""
        config = {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "protocol": "modbus",
            "timeout": 5.0,
        }
        return RobotController(config)
    
    def test_initialization(self, robot):
        """Test robot initialization."""
        assert robot.position == (0.0, 0.0, 0.0)
        assert not robot.is_connected
    
    def test_move_disconnected(self, robot):
        """Test that move fails when disconnected."""
        assert not robot.move_to((100, 100, 100))
    
    def test_home_disconnected(self, robot):
        """Test that home fails when disconnected."""
        assert not robot.home()
    
    def test_get_position(self, robot):
        """Test getting robot position."""
        pos = robot.get_position()
        assert pos == (0.0, 0.0, 0.0)
