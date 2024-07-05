import cv2 as cv
import numpy as np

class CircleDetector:

    def __init__(self, num_points=360):
        self.num_points = num_points

    def generate_circle_points(self, center_x, center_y, radius):
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

    def detect_circles(self, filename):
        # Loads an image
        src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_COLOR)
        # Check if image is loaded fine
        if src is None:
            print(f'Error opening image: {filename}')
            return None

        gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
        gray = cv.medianBlur(gray, 5)
        rows = gray.shape[0]
        circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=0, maxRadius=0)

        circle_points = []

        if circles is not None:
            circles = np.around(circles)  # Avoid conversion to uint16
            for i in circles[0, :]:
                center_x = i[0]  # Keep as float
                center_y = i[1]  # Keep as float
                radius = i[2]  # Keep as float
                points = self.generate_circle_points(center_x, center_y, radius)
                circle_points.append(points)

        return circle_points
