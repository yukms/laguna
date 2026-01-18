"""Core orchestrator module that combines all subsystems.

This is the main interface for users - a single FlumeLab class that manages
all subsystems and provides a clean API for running experiments.
"""

from typing import Optional, Dict, Any
import logging
from pathlib import Path

from .config import Config
from .robot import RobotController
from .camera import CameraAcquisition
from .hydraulics import HydraulicsSystem
from .data import DataProcessor
from .storage import RemoteStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FlumeLab:
    """Main orchestrator for the flume lab robotic system.
    
    Coordinates all subsystems (robot, camera, hydraulics, data processing, storage)
    and provides a unified interface for running experiments.
    
    Attributes:
        robot: Robot control subsystem
        camera: Camera acquisition subsystem
        hydraulics: Hydraulics control subsystem
        data_processor: Data processing subsystem
        storage: Remote storage subsystem
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the FlumeLab system.
        
        Args:
            config_file: Path to YAML configuration file. If not provided,
                        default configuration will be used.
        """
        logger.info("Initializing FlumeLab system...")
        
        # Load configuration
        self.config = Config(config_file=config_file)
        
        # Initialize subsystems
        self.robot = RobotController(self.config.get("robot"))
        self.camera = CameraAcquisition(self.config.get("camera"))
        self.hydraulics = HydraulicsSystem(self.config.get("hydraulics"))
        self.data_processor = DataProcessor(self.config.get("data"))
        self.storage = RemoteStorage(self.config.get("storage"))
        
        self.is_running = False
        logger.info("FlumeLab system initialized successfully")
    
    def connect_all(self) -> bool:
        """Establish connections to all subsystems.
        
        Returns:
            True if all connections successful, False if any failed
        """
        logger.info("Connecting to all subsystems...")
        
        all_connected = True
        
        # Connect robot
        if not self.robot.connect():
            logger.warning("Failed to connect robot")
            all_connected = False
        
        # Connect camera
        if not self.camera.start():
            logger.warning("Failed to start camera")
            all_connected = False
        
        # Connect hydraulics
        if not self.hydraulics.connect():
            logger.warning("Failed to connect hydraulics")
            all_connected = False
        
        # Connect storage
        if not self.storage.connect():
            logger.warning("Failed to connect remote storage")
            all_connected = False
        
        if all_connected:
            logger.info("All subsystems connected successfully")
        
        return all_connected
    
    def disconnect_all(self) -> None:
        """Disconnect all subsystems."""
        logger.info("Disconnecting all subsystems...")
        
        self.robot.disconnect()
        self.camera.stop()
        self.hydraulics.disconnect()
        self.storage.disconnect()
        
        self.is_running = False
        logger.info("All subsystems disconnected")
    
    def initialize_experiment(self, experiment_config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the system for an experiment.
        
        Performs startup procedures including homing robot, setting pressure targets, etc.
        
        Args:
            experiment_config: Optional experiment-specific configuration
            
        Returns:
            True if initialization successful
        """
        logger.info("Initializing experiment...")
        
        try:
            # Home robot
            if not self.robot.home():
                logger.error("Failed to home robot")
                return False
            
            # Set hydraulic pressure if specified
            if experiment_config and "hydraulics" in experiment_config:
                pressure = experiment_config["hydraulics"].get("pressure_target")
                if pressure:
                    self.hydraulics.set_pressure(pressure)
            
            # Start hydraulics
            if not self.hydraulics.start():
                logger.error("Failed to start hydraulics")
                return False
            
            # Clear data buffer
            self.data_processor.clear_buffer()
            
            self.is_running = True
            logger.info("Experiment initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Experiment initialization failed: {e}")
            return False
    
    def run_experiment(self, experiment_config: Optional[Dict[str, Any]] = None) -> bool:
        """Run an experiment with the specified configuration.
        
        This is the main entry point for experiments. It handles the full workflow:
        connections, initialization, data collection, and cleanup.
        
        Args:
            experiment_config: Dictionary with experiment parameters
            
        Returns:
            True if experiment completed successfully
        """
        logger.info("Starting experiment...")
        
        try:
            # Connect all systems
            if not self.connect_all():
                logger.error("Failed to connect to all systems")
                return False
            
            # Initialize experiment
            if not self.initialize_experiment(experiment_config):
                logger.error("Failed to initialize experiment")
                self.disconnect_all()
                return False
            
            # TODO: Implement main experiment loop
            # - Capture frames from camera
            # - Move robot to specified positions
            # - Monitor hydraulic system
            # - Collect and buffer data
            # - Export/save data periodically
            
            logger.info("Experiment completed successfully")
            
            # Save data
            self.data_processor.save_data("experiment_data.csv")
            
            # Upload to remote storage if enabled
            if self.storage.enabled:
                output_path = self.data_processor.output_directory / "experiment_data.csv"
                self.storage.upload_file(str(output_path), "experiments/experiment_data.csv")
            
            return True
        except Exception as e:
            logger.error(f"Experiment failed: {e}")
            return False
        finally:
            # Always disconnect
            self.disconnect_all()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of all subsystems.
        
        Returns:
            Dictionary containing status of each subsystem
        """
        return {
            "robot": {
                "connected": self.robot.is_connected,
                "position": self.robot.get_position(),
            },
            "camera": {
                "recording": self.camera.is_recording,
                "frames_captured": self.camera.get_frame_count(),
            },
            "hydraulics": {
                "active": self.hydraulics.is_active,
                "status": self.hydraulics.get_status(),
            },
            "data": {
                "buffer_size": self.data_processor.get_buffer_size(),
            },
            "storage": {
                "enabled": self.storage.enabled,
                "connected": self.storage.is_connected,
            },
        }
    
    def emergency_stop(self) -> None:
        """Emergency stop - immediately shut down all systems."""
        logger.warning("EMERGENCY STOP activated!")
        
        self.robot.stop()
        self.hydraulics.stop()
        self.camera.stop()
        
        self.disconnect_all()
