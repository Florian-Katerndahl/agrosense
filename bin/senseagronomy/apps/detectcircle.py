from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import cv2 as cv
import numpy as np
import os
import json


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

    circle_list = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x = int(i[0])  # Convert to native Python int
            y = int(i[1])  # Convert to native Python int
            radius = int(i[2])  # Convert to native Python int
            circle_list.append({'x': x, 'y': y, 'radius': radius})
            # Optional: Draw the circles on the image
            cv.circle(src, (x, y), 1, (0, 100, 100), 3)  # circle center
            cv.circle(src, (x, y), radius, (255, 0, 255), 3)  # circle outline

    return circle_list


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
    for filename in image_files:
        circles = detect_circles(filename)
        if circles is not None:
            coordinates[filename] = circles

    # Write the coordinates to a JSON file
    with open(args.output_file, 'w') as json_file:
        json.dump(coordinates, json_file, indent=4)

    return 0