import cv2 as cv
import numpy as np
import rasterio

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
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=20, minRadius=8, maxRadius=15)

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

        except Exception as e:
            print(f"Error opening image: {filename}")
            print(str(e))
            return None

def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to detect circles in images and save their coordinates to a JSON file."
    )
    parser.add_argument(
        '--input',
        type=str,
        nargs='+',
        required=True,
        help='List of input image files'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to the output JSON file'
    )

    args = parser.parse_args()

    detector = CircleDetector()

    coordinates = {}

    for filepath in args.input:
        # Extract the file name from the full path
        filename = os.path.basename(filepath)
        circle_points = detector.detect_circles(filepath)
        if circle_points is not None:
            coordinates[filename] = circle_points

    # Write the coordinates to a JSON file
    with open(args.output, 'w') as json_file:
        json.dump(coordinates, json_file)

    return 0
