# Contributing to Laguna

Thank you for your interest in contributing to the Laguna project!

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd laguna

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/laguna

# Run specific test file
pytest tests/test_robot.py
```

## Code Style

This project uses Black for code formatting and isort for import sorting.

```bash
# Format code
black src/ tests/ examples/

# Sort imports
isort src/ tests/ examples/

# Type checking
mypy src/laguna
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes and add tests
3. Run tests and ensure code style compliance
4. Commit with clear message: `git commit -m "Add feature description"`
5. Push to your fork and create a Pull Request

## Adding New Subsystems

To add a new subsystem (e.g., pressure sensors, environmental controls):

1. Create a new module in `src/laguna/<subsystem_name>/`
2. Implement main class following the pattern of existing subsystems
3. Add configuration defaults to `config.py`
4. Integrate into `core.py` FlumeLab class
5. Add tests in `tests/test_<subsystem_name>.py`
6. Update README with new subsystem documentation

## Documentation

- Docstrings use Google style format
- Update README.md when adding major features
- Add examples in `examples/` directory

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Minimal code to reproduce the issue
- Error messages and stack traces
