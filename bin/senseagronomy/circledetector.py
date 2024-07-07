from typing import List, Tuple, Optional
import sys
import cv2 as cv
import numpy as np
import rasterio

class CircleDetector:
    def __init__(self, num_points: int = 360) -> None:
        self.num_points = num_points

    def generate_circle_points(self, center_x: float, center_y: float, radius: float) -> List[Tuple[float, float]]:
        """Generate (x, y) points around the circumference of a circle."""
        points = []
        for i in range(self.num_points):
            theta = 2 * np.pi * i / self.num_points
            x = center_x + radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            points.append((x, y))  # Keep coordinates as float

        if points:
            points.append(points[0])

        return points

    def detect_circles(self, filename: str) -> Optional[List[List[Tuple[float, float]]]]:
        try:
            # Use rasterio to open the image
            with rasterio.open(filename) as dataset:
                # Read the image data
                image_data = dataset.read(1)  # Read the first band

            # Convert the image to 8-bit if it's not already
            if image_data.dtype != np.uint8:
                image_data = cv.normalize(image_data, None, 0, 255, cv.NORM_MINMAX)
                image_data = image_data.astype(np.uint8)

            gray = cv.medianBlur(image_data, 5)
            rows = gray.shape[0]
            circles = cv.HoughCircles(
                gray, cv.HOUGH_GRADIENT, 1, rows / 8,
                param1=100, param2=20, minRadius=8, maxRadius=15
            )

            circle_points = []

            if circles is not None:
                circles = np.around(circles)  # Avoid conversion to uint16
                for i in circles[0, :]:
                    center_x = float(i[0])  # Keep as float
                    center_y = float(i[1])  # Keep as float
                    radius = float(i[2])  # Keep as float
                    points = self.generate_circle_points(center_x, center_y, radius)
                    circle_points.append(points)

            return circle_points

        except (rasterio.errors.RasterioIOError, ValueError) as e:
            sys.stderr.write(f"Error opening or processing image: {filename}\n")
            return None
