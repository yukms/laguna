"""
Laguna: Robotic flume control system for experimental data acquisition and processing.

This package provides a modular framework for controlling robotic systems, acquiring camera data,
managing hydraulic systems, and processing experimental data from hydraulic flume experiments.
"""

__version__ = "0.1.0"
__author__ = "Lab Team"

from .core import FlumeLab

__all__ = ["FlumeLab"]
