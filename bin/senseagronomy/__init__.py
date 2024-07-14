"""
This module initializes the senseagronomy package and
imports key components for scene analysis.
"""

from senseagronomy.scene import Scene, Pixel, Aerosol, Cloud, Radsat
from senseagronomy.circledetector import CircleDetector
from senseagronomy.spatialtransformer import SpatialTransformer
from senseargonomy.accuracy_assessment import accuracy_assessment

__all__ = [
        "Scene",
        "Pixel",
        "Aerosol",
        "Cloud",
        "Radsat",
        "CircleDetector",
        "SpatialTransformer"
        "accuracy_assessment"
    ]
