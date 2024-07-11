"""
This module detects circles in images and saves their
coordinates to a JSON file.
"""

import os
import json
from typing import List, Dict, Tuple
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from senseagronomy import CircleDetector


def main() -> int:
    """
    Main function to parse arguments and detect circles in images.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=(
            "This program is used to detect circles in images "
            "and save their coordinates to a JSON file."
        )
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

    args: Namespace = parser.parse_args()

    detector = CircleDetector()

    coordinates: Dict[str, List[List[Tuple[float, float]]]] = {}

    for filepath in args.input:
        # Extract the file name from the full path
        filename = os.path.basename(filepath)
        circle_points = detector.detect_circles(filepath)
        if circle_points is not None:
            coordinates[filename] = circle_points

    # Write the coordinates to a JSON file
    with open(args.output, 'w', encoding='utf-8') as json_file:
        json.dump(coordinates, json_file, ensure_ascii=False, indent=4)

    return 0
