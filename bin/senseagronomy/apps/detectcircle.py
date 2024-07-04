from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import cv2 as cv
import numpy as np
import os

def detect_circles(filename):

    # Loads an image
    src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_COLOR)

    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        return -1

    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

    gray = cv.medianBlur(gray, 5)

    rows = gray.shape[0]
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=1, maxRadius=30)


    if circles is not None:
        circles = np.uint16(np.around(circles))
        
    for i in circles[0, :]:
        center = (i[0], i[1])
        # circle center
        cv.circle(src, center, 1, (0, 100, 100), 3)
        # circle outline
        radius = i[2]
        cv.circle(src, center, radius, (255, 0, 255), 3)

    return src

def main():

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to detect circles "
    )
    parser.add_argument(
        '--images-directory-path',
        type=str,
        nargs=1,
        required=True, 
        help='Path to the images directory'
    )

    args = parser.parse_args()

    # List all files in the directory
    image_files = [os.path.relpath(os.path.join(args.images_directory_path[0], f)) for f in os.listdir(args.images_directory_path[0]) if os.path.isfile(os.path.join(args.images_directory_path[0], f))]

    for filename in image_files:
        detect_circles(filename)

    return 0