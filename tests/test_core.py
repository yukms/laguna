"""Test suite for core FlumeLab orchestrator."""

import pytest
from laguna import FlumeLab


class TestFlumeLab:
    """Test cases for FlumeLab class."""
    
    @pytest.fixture
    def lab(self):
        """Create a FlumeLab instance for testing."""
        return FlumeLab()
    
    def test_initialization(self, lab):
        """Test FlumeLab initialization."""
        assert lab.robot is not None
        assert lab.camera is not None
        assert lab.hydraulics is not None
        assert lab.data_processor is not None
        assert lab.storage is not None
        assert not lab.is_running
    
    def test_get_system_status(self, lab):
        """Test getting system status."""
        status = lab.get_system_status()
        
        assert "robot" in status
        assert "camera" in status
        assert "hydraulics" in status
        assert "data" in status
        assert "storage" in status
