from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import cv2 as cv
import numpy as np

def detect_circles(filename):

    # Loads an image
    src = cv.imread(cv.samples.findFile(filename), cv.IMREAD_COLOR)

    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        print ('Usage: hough_circle.py [image_name -- default ' + default_file + '] \n')
        return -1

    gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

    gray = cv.medianBlur(gray, 5)

    rows = gray.shape[0]
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, rows / 8,
    param1=100, param2=30,
    minRadius=1, maxRadius=30)


    if circles is not None:
        circles = np.uint16(np.around(circles))
        
    for i in circles[0, :]:
        center = (i[0], i[1])
        # circle center
        cv.circle(src, center, 1, (0, 100, 100), 3)
        # circle outline
        radius = i[2]
        cv.circle(src, center, radius, (255, 0, 255), 3)

    print(src)
    return src

def main():

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to detect circles "
    )
    parser.add_argument(
        '--image-path',
        type=str,
        nargs='*',
        required=True, 
        default='../../scenes/img.png', 
        help='Path to the image file'
    )

    args = parser.parse_args()
    for filename in args.image_path:
        detect_circles(filename)

    return 0