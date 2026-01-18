"""
Example 2: Simple experiment workflow

This example shows how to:
- Load custom configuration
- Initialize an experiment
- Run a simple experimental procedure
- Save the results
"""

from laguna import FlumeLab


def main():
    """Run a simple experiment."""
    
    # Initialize with custom configuration file
    # lab = FlumeLab(config_file="config/my_experiment.yaml")
    
    # Or use default configuration
    lab = FlumeLab()
    
    # Define experiment parameters
    experiment_config = {
        "robot": {
            "start_position": (0, 0, 0),
        },
        "camera": {
            "fps": 30,
        },
        "hydraulics": {
            "pressure_target": 1000,  # Pascals
        }
    }
    
    # Run the experiment
    print("Starting experiment...")
    if lab.run_experiment(experiment_config):
        print("Experiment completed successfully!")
    else:
        print("Experiment failed!")


if __name__ == "__main__":
    main()
