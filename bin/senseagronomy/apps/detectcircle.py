from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from senseagronomy import CircleDetector
import os
import json

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