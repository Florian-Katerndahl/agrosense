from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import cv2 as cv
import numpy as np
import os
import json


def generate_circle_points(center_x, center_y, radius, num_points=100):
    """Generate (x, y) points around the circumference of a circle."""
    points = []
    for i in range(num_points):
        theta = 2 * np.pi * i / num_points
        x = center_x + radius * np.cos(theta)
        y = center_y + radius * np.sin(theta)
        points.append((x, y))  # Keep coordinates as float
    return points

def detect_circles(filename):
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
            points = generate_circle_points(center_x, center_y, radius)
            circle_points.append(points)

    return circle_points


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to detect circles in images and save their coordinates to a JSON file."
    )
    parser.add_argument(
        '--images-directory-path',
        type=str,
        required=True,
        help='Path to the images directory'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        required=True,
        help='Path to the output JSON file'
    )

    args = parser.parse_args()

    # List all files in the directory
    image_files = [os.path.join(args.images_directory_path, f) for f in os.listdir(args.images_directory_path) if os.path.isfile(os.path.join(args.images_directory_path, f))]

    coordinates = {}
    for filepath in image_files:
        # Extract the file name from the full path
        filename = os.path.basename(filepath)
        circle_points = detect_circles(filepath)
        if circle_points is not None:
            coordinates[filename] = circle_points

    # Write the coordinates to a JSON file
    with open(args.output_file, 'w') as json_file:
        json.dump(coordinates, json_file, indent=4)

    return 0


if __name__ == "__main__":
    main()
