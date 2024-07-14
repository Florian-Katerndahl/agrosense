from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import os
from shapely.strtree import STRtree
import pandas as pd

def load_geopackage(file_path, layer=None):
    """
    Loads GeoPackage file and returns a GeoDataFrame for later processing.

    Parameters:
    - file_path (str): The path to the GeoPackage file.
    - layer (str, optional): The name of the layer to load from the GeoPackage file. If not specified, all layers will be loaded.

    Returns:
    - gdf (GeoDataFrame): The loaded GeoDataFrame.

    Raises:
    - FileNotFoundError: If the specified file_path does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return gpd.read_file(file_path, layer=layer)

def create_circle(center, radius):
    """
    Generates a circular geometry using the Shapely library. Its used for creating synthetic circles during testing or visualization
    of circle geometries.

    Parameters:
    - center (tuple): The coordinates of the center of the circle.
    - radius (float): The radius of the circle.

    Returns:
    - circle (Polygon): A shapely Polygon object representing the circle.
    """
    return Point(center).buffer(radius)

def compute_iou(circle1, circle2):
    """
    This function calculates the Intersection over Union (IoU) value between two circle geometries.
    The IoU is a measure of the overlap between two geometries. In the context of circle geometries,
    it represents the overlap between the area of two circles.
    The IoU value ranges from 0 to 1, where 0 indicates no overlap and 1 indicates complete overlap.

    Parameters:
    - circle1 (geometry): The first circle geometry.
    - circle2 (geometry): The second circle geometry.

    Returns:
    - float: The Intersection over Union (IoU) value.
    """
    intersection = circle1.intersection(circle2).area
    union = circle1.union(circle2).area
    return intersection / union

def match_circles(predicted_circles, validation_circles, iou_threshold=0.4):
    """
    Compares each predicted circle to validation circles to identify true positives (correctly matched circles), false positives
    (incorrectly predicted circles), and false negatives (missed validation circles) based on the specified IoU threshold, in our case 0.4 
    (as it had good testing results). 

    Parameters:
    - predicted_circles (GeoDataFrame): The predicted circles as a GeoDataFrame.
    - validation_circles (GeoDataFrame): The validation circles as a GeoDataFrame.
    - iou_threshold (float, optional): The IoU threshold for matching circles. Default is 0.4.

    Returns:
    - tp (list): List of tuples representing true positive matches, where each tuple contains the indices of the matched circles.
    - fp (list): List of indices representing false positive matches.
    - fn (list): List of indices representing false negative matches.
    """
    tp, fp, fn = [], [], []
    for i, pred_circle in predicted_circles.iterrows():
        matched = False
        for j, val_circle in validation_circles.iterrows():
            if compute_iou(pred_circle.geometry, val_circle.geometry) > iou_threshold:
                tp.append((i, j))
                matched = True
                break
        if not matched:
            fp.append(i)

    matched_validation = [j for _, j in tp]
    for j, val_circle in validation_circles.iterrows():
        if j not in matched_validation:
            fn.append(j)

    return tp, fp, fn

def calculate_metrics(tp, fp, fn):
    """
    Precision measures the proportion of correctly identified positive samples out of the total samples identified as positive, 
    recall represents the proportion of correctly identified positive samples out of the total actual positive samples, and F1-score
    which is the harmonic mean of precision and recall. 
    It provides a balanced measure of the model's performance by considering both precision and recall.

    Parameters:
    - tp (list): List of tuples representing true positive matches.
    - fp (list): List of indices representing false positive matches.
    - fn (list): List of indices representing false negative matches.

    Returns:
    - precision (float): The precision value.
    - recall (float): The recall value.
    - f1_score (float): The F1-score value.
    """
    precision = len(tp) / (len(tp) + len(fp)) if tp else 0
    recall = len(tp) / (len(tp) + len(fn)) if tp else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1_score

def iou_matrix(y_pred, y_true):
    """
    Calculates the Intersection over Union (IoU) matrix between predicted and true geometries.
    The IoU matrix is a square matrix where each element represents the IoU value between a predicted geometry and a true geometry.

    Parameters:
    - y_pred (list): List of predicted geometries.
    - y_true (list): List of true geometries.

    Returns:
    - res (ndarray): The IoU matrix, where each element represents the IoU value between a predicted geometry and a true geometry.
    """
    res = np.zeros((len(y_pred), len(y_true)))
    for i, p_pred in enumerate(y_pred):
        for j, p_true in enumerate(y_true):
            intersection = p_pred.intersection(p_true).area
            union = p_pred.union(p_true).area + 1E-8
            iou = intersection / union
            res[i, j] = iou
    return res

def oversegmentation_factor(y_true, y_pred, threshold=0.4):
    """
    Calculates the oversegmentation factor, which measures the extent to which the predicted geometries exceed the necessary number of
    segments. A higher value indicates a tendency to oversegment.

    Parameters:
    - y_true (list): List of true geometries.
    - y_pred (list): List of predicted geometries.
    - threshold (float): IoU threshold to consider a match.

    Returns:
    - float: The oversegmentation factor.
    """
    overlapping_polygons = 0
    y_pred_tree = STRtree(y_pred)
    for p_true in y_true:
        intersecting_indices = y_pred_tree.query(p_true)
        intersecting_polygons = [y_pred[idx] for idx in intersecting_indices]
        for p_inter in intersecting_polygons:
            a = p_inter.area
            intersection = p_true.intersection(p_inter).area
            if intersection / a > threshold:
                overlapping_polygons += 1
    return overlapping_polygons / len(y_true) if len(y_true) > 0 else 0

def accuracy_assessment(pred_file, val_file, val_layer):
    """
    This function evaluates the accuracy of the predicted circle geometries by comparing them with the validation geometries.
    It calculates precision, recall, F1-score, and oversegmentation factor.

    Parameters:
    - pred_file (str): Path to the predicted GeoPackage file.
    - val_file (str): Path to the validation GeoPackage file.
    - val_layer (str): Name of the layer in the validation GeoPackage file.

    Returns:
    - results_df (DataFrame): DataFrame containing the accuracy assessment results, including precision, recall, F1-score, and oversegmentation factor.
    """
    iou_threshold = 0.4
    metrics = []

    validation_circles = load_geopackage(val_file, layer=val_layer)
    predicted_circles = load_geopackage(pred_file)

    tp, fp, fn = match_circles(validation_circles, predicted_circles, iou_threshold)
    precision, recall, f1_score = calculate_metrics(tp, fp, fn)

    pred_polygons = list(predicted_circles.geometry)
    val_polygons = list(validation_circles.geometry)

    iou_mat = iou_matrix(pred_polygons, val_polygons)
    overseg_factor = oversegmentation_factor(val_polygons, pred_polygons, iou_threshold)

    metrics.append({
        'precision': precision, 
        'recall': recall, 
        'f1_score': f1_score,
        'oversegmentation_factor': overseg_factor
    })

    return pd.DataFrame(metrics)

def main() -> int:
    """
    This function sets up the argument parser for command-line inputs, loads
    the necessary data from GeoPackage files, performs the
    accuracy assessment, and saves the results to a CSV file.

    Parameters:
    --validation-file: Path to the validation GeoPackage file.
    --predicted-file: Path to the predicted GeoPackage file.
    --validation-layer: Name of the layer in the validation GeoPackage file.
    --output-file: Path to the output CSV file.

    Returns:
    - int: Returns 0 if the program runs successfully.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to assess the accuracy of predicted irrigation circles. "
                    "The validation data should be located in the 'data/validation' directory in the main branch. "
                    "The predicted files can be downloaded and provided as inputs. "
                    "The layer name in the validation GeoPackage file should be specified."
                    "The output CSV file name must be specified by the user."
    )
    parser.add_argument(
        '--validation-file',
        type=str,
        required=True,
        help='Path to the validation GeoPackage file.'
    )
    parser.add_argument(
        '--predicted-file',
        type=str,
        required=True,
        help='Path to the predicted GeoPackage file.'
    )
    parser.add_argument(
        '--validation-layer',
        type=str,
        required=True,
        help='Layer name in the validation GeoPackage file.'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        required=True,
        help='Path to the output CSV file.'
    )

    args: Namespace = parser.parse_args()

    # Perform accuracy assessment
    results_df = accuracy_assessment(args.predicted_file, args.validation_file, args.validation_layer)
    results_df.to_csv(args.output_file, index=False)
    print("Results for Accuracy Assessment:")
    print(results_df)

    return 0

if __name__ == "__main__":
    main()
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import os
from shapely.strtree import STRtree
import pandas as pd

def load_geopackage(file_path, layer=None):
    """
    Loads GeoPackage file and returns a GeoDataFrame for later processing.

    Parameters:
    - file_path (str): The path to the GeoPackage file.
    - layer (str, optional): The name of the layer to load from the GeoPackage file. If not specified, all layers will be loaded.

    Returns:
    - gdf (GeoDataFrame): The loaded GeoDataFrame.

    Raises:
    - FileNotFoundError: If the specified file_path does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return gpd.read_file(file_path, layer=layer)

def create_circle(center, radius):
    """
    Generates a circular geometry using the Shapely library. Its used for creating synthetic circles during testing or visualization
    of circle geometries.

    Parameters:
    - center (tuple): The coordinates of the center of the circle.
    - radius (float): The radius of the circle.

    Returns:
    - circle (Polygon): A shapely Polygon object representing the circle.
    """
    return Point(center).buffer(radius)

def compute_iou(circle1, circle2):
    """
    This function calculates the Intersection over Union (IoU) value between two circle geometries.
    The IoU is a measure of the overlap between two geometries. In the context of circle geometries,
    it represents the overlap between the area of two circles.
    The IoU value ranges from 0 to 1, where 0 indicates no overlap and 1 indicates complete overlap.

    Parameters:
    - circle1 (geometry): The first circle geometry.
    - circle2 (geometry): The second circle geometry.

    Returns:
    - float: The Intersection over Union (IoU) value.
    """
    intersection = circle1.intersection(circle2).area
    union = circle1.union(circle2).area
    return intersection / union

def match_circles(predicted_circles, validation_circles, iou_threshold=0.4):
    """
    Compares each predicted circle to validation circles to identify true positives (correctly matched circles), false positives
    (incorrectly predicted circles), and false negatives (missed validation circles) based on the specified IoU threshold, in our case 0.4 
    (as it had good testing results). 

    Parameters:
    - predicted_circles (GeoDataFrame): The predicted circles as a GeoDataFrame.
    - validation_circles (GeoDataFrame): The validation circles as a GeoDataFrame.
    - iou_threshold (float, optional): The IoU threshold for matching circles. Default is 0.4.

    Returns:
    - tp (list): List of tuples representing true positive matches, where each tuple contains the indices of the matched circles.
    - fp (list): List of indices representing false positive matches.
    - fn (list): List of indices representing false negative matches.
    """
    tp, fp, fn = [], [], []
    for i, pred_circle in predicted_circles.iterrows():
        matched = False
        for j, val_circle in validation_circles.iterrows():
            if compute_iou(pred_circle.geometry, val_circle.geometry) > iou_threshold:
                tp.append((i, j))
                matched = True
                break
        if not matched:
            fp.append(i)

    matched_validation = [j for _, j in tp]
    for j, val_circle in validation_circles.iterrows():
        if j not in matched_validation:
            fn.append(j)

    return tp, fp, fn

def calculate_metrics(tp, fp, fn):
    """
    Precision measures the proportion of correctly identified positive samples out of the total samples identified as positive, 
    recall represents the proportion of correctly identified positive samples out of the total actual positive samples, and F1-score
    which is the harmonic mean of precision and recall. 
    It provides a balanced measure of the model's performance by considering both precision and recall.

    Parameters:
    - tp (list): List of tuples representing true positive matches.
    - fp (list): List of indices representing false positive matches.
    - fn (list): List of indices representing false negative matches.

    Returns:
    - precision (float): The precision value.
    - recall (float): The recall value.
    - f1_score (float): The F1-score value.
    """
    precision = len(tp) / (len(tp) + len(fp)) if tp else 0
    recall = len(tp) / (len(tp) + len(fn)) if tp else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1_score

def calculate_iou(predicted_circles, validation_circles):
    """
    Calculates the average Intersection over Union (IoU) for all matched circles.
    The IoU is a measure of the overlap between two geometries. In the context of circle geometries,
    it represents the overlap between the area of two circles.
    
    Parameters:
    - predicted_circles (GeoDataFrame): The predicted circles as a GeoDataFrame.
    - validation_circles (GeoDataFrame): The validation circles as a GeoDataFrame.

    Returns:
    - average_iou (float): The average IoU value for all matched circles.
    """
    total_iou = 0
    match_count = 0
    for pred_circle in predicted_circles.geometry:
        best_iou = 0
        for val_circle in validation_circles.geometry:
            iou = compute_iou(pred_circle, val_circle)
            if iou > best_iou:
                best_iou = iou
        total_iou += best_iou
        match_count += 1 if best_iou > 0 else 0
    return total_iou / match_count if match_count > 0 else 0

def iou_matrix(y_pred, y_true):
    """
    Calculates the Intersection over Union (IoU) matrix between predicted and true geometries.
    The IoU matrix is a square matrix where each element represents the IoU value between a predicted geometry and a true geometry.

    Parameters:
    - y_pred (list): List of predicted geometries.
    - y_true (list): List of true geometries.

    Returns:
    - res (ndarray): The IoU matrix, where each element represents the IoU value between a predicted geometry and a true geometry.
    """
    res = np.zeros((len(y_pred), len(y_true)))
    for i, p_pred in enumerate(y_pred):
        for j, p_true in enumerate(y_true):
            intersection = p_pred.intersection(p_true).area
            union = p_pred.union(p_true).area + 1E-8
            iou = intersection / union
            res[i, j] = iou
    return res

def oversegmentation_factor(y_true, y_pred, threshold=0.4):
    """
    Calculates the oversegmentation factor, which measures the extent to which the predicted geometries exceed the necessary number of
    segments. A higher value indicates a tendency to oversegment.

    Parameters:
    - y_true (list): List of true geometries.
    - y_pred (list): List of predicted geometries.
    - threshold (float): IoU threshold to consider a match.

    Returns:
    - float: The oversegmentation factor.
    """
    overlapping_polygons = 0
    y_pred_tree = STRtree(y_pred)
    for p_true in y_true:
        intersecting_indices = y_pred_tree.query(p_true)
        intersecting_polygons = [y_pred[idx] for idx in intersecting_indices]
        for p_inter in intersecting_polygons:
            a = p_inter.area
            intersection = p_true.intersection(p_inter).area
            if intersection / a > threshold:
                overlapping_polygons += 1
    return overlapping_polygons / len(y_true) if len(y_true) > 0 else 0

def accuracy_assessment(pred_file, val_file, val_layer):
    """
    This function evaluates the accuracy of the predicted circle geometries by comparing them with the validation geometries.
    It calculates precision, recall, F1-score, average IoU, and oversegmentation factor.

    Parameters:
    - pred_file (str): Path to the predicted GeoPackage file.
    - val_file (str): Path to the validation GeoPackage file.
    - val_layer (str): Name of the layer in the validation GeoPackage file.

    Returns:
    - results_df (DataFrame): DataFrame containing the accuracy assessment results, including precision, recall, F1-score, average IoU, and oversegmentation factor.
    """
    iou_threshold = 0.4
    metrics = []
    
    validation_circles = load_geopackage(val_file, layer=val_layer)
    predicted_circles = load_geopackage(pred_file)

    tp, fp, fn = match_circles(validation_circles, predicted_circles, iou_threshold)
    precision, recall, f1_score = calculate_metrics(tp, fp, fn)
    average_iou = calculate_iou(predicted_circles, validation_circles)
    overseg_factor = oversegmentation_factor(validation_circles.geometry, predicted_circles.geometry, iou_threshold)

    metrics.append({
        'precision': precision, 
        'recall': recall, 
        'f1_score': f1_score,
        'average_iou': average_iou,
        'oversegmentation_factor': overseg_factor
    })

    return pd.DataFrame(metrics)

def main() -> int:
    """
    This function sets up the argument parser for command-line inputs, loads
    the necessary data from GeoPackage files, performs the
    accuracy assessment, and saves the results to a CSV file.

    Parameters:
    --validation-file: Path to the validation GeoPackage file.
    --predicted-file: Path to the predicted GeoPackage file.
    --validation-layer: Name of the layer in the validation GeoPackage file.
    --output-file: Path to the output CSV file.

    Returns:
    - int: Returns 0 if the program runs successfully.
    """
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to assess the accuracy of predicted irrigation circles. "
                    "The validation data should be located in the 'data/validation' directory in the main branch. "
                    "The predicted files can be downloaded and provided as inputs. "
                    "The layer name in the validation GeoPackage file should be specified."
                    "The output CSV file name must be specified by the user."
    )
    parser.add_argument(
        '--validation-file',
        type=str,
        required=True,
        help='Path to the validation GeoPackage file.'
    )
    parser.add_argument(
        '--predicted-file',
        type=str,
        required=True,
        help='Path to the predicted GeoPackage file.'
    )
    parser.add_argument(
        '--validation-layer',
        type=str,
        required=True,
        help='Layer name in the validation GeoPackage file.'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        required=True,
        help='Path to the output CSV file.'
    )

    args: Namespace = parser.parse_args()

    # Perform accuracy assessment
    results_df = accuracy_assessment(args.predicted_file, args.validation_file, args.validation_layer)
    results_df.to_csv(args.output_file, index=False)
    return 0

if __name__ == "__main__":
    main()
