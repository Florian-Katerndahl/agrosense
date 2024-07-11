"""
Circle Detector Module

This module contains a class for detecting circles in images using the Hough Circle Transform.
"""

from typing import List, Tuple, Optional
import sys
import rasterio
import cv2 as cv
import numpy as np

class CircleDetector:
    """Class for detecting circles in images."""

    def __init__(self, num_points: int = 360) -> None:
        """Initialize the CircleDetector with a specified number of points."""
        self.num_points = num_points

    def generate_circle_points(
        self, center_x: float, center_y: float, radius: float
    ) -> List[Tuple[float, float]]:
        """Generate (x, y) points around the circumference of a circle."""
        points = []
        for i in range(self.num_points):
            theta = 2 * np.pi * i / self.num_points
            point_x = center_x + radius * np.cos(theta)
            point_y = center_y + radius * np.sin(theta)
            points.append((point_x, point_y))  # Keep coordinates as float

        if points:
            points.append(points[0])

        return points

    def detect_circles(self, filename: str) -> Optional[List[List[Tuple[float, float]]]]:
        """Detect circles in an image file."""
        try:
            # Use rasterio to open the image
            with rasterio.open(filename) as dataset:
                # Read the image data
                image_data = dataset.read(1)  # Read the first band

            # Convert the image to 8-bit if it's not already
            if image_data.dtype != np.uint8:
                image_data = cv.normalize(
                    image_data, None, 0, 255, cv.NORM_MINMAX
                )
                image_data = image_data.astype(np.uint8)

            gray = cv.medianBlur(image_data, 5)
            rows = gray.shape[0]

            circles = cv.HoughCircles(
                gray,  # Input image
                cv.HOUGH_GRADIENT,  # Detection method
                1,  # dp: Inverse ratio of the accumulator resolution to the image resolution
                rows / 8,  # minDist: Minimum distance between the centers of the detected circles
                param1=100,  # Higher threshold for the Canny edge detector
                param2=20,  # Accumulator threshold for the circle centers
                minRadius=8,  # Minimum circle radius
                maxRadius=15  # Maximum circle radius
            )

            circle_points = []

            if circles is not None:
                circles = np.around(circles)  # Avoid conversion to uint16
                for circle in circles[0, :]:
                    center_x = float(circle[0])  # Keep as float
                    center_y = float(circle[1])  # Keep as float
                    radius = float(circle[2])  # Keep as float
                    points = self.generate_circle_points(center_x, center_y, radius)
                    circle_points.append(points)

            return circle_points

        except (rasterio.errors.RasterioIOError, ValueError):
            sys.stderr.write(f"Error opening or processing image: {filename}\n")
            return None
