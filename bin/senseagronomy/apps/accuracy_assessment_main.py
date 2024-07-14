from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
#from accuracy_assessment import accuracy_assessment
import pandas as pd
from senseagronomy import accuracy_assessment

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
    --tp-output-file: Path to the output GeoPackage file for true positives.

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
                    "The output GeoPackage file for true positives should be specified by the user."
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
    parser.add_argument(
        '--tp-output-file',
        type=str,
        required=True,
        help='Path to the output GeoPackage file for true positives.'
    )

    args: Namespace = parser.parse_args()

    # Perform accuracy assessment
    results_df, tp, predicted_circles = accuracy_assessment(args.predicted_file, args.validation_file, args.validation_layer)
    results_df.to_csv(args.output_file, index=False)

    # Save true positives to a GeoPackage and add "correct" column to predicted_circles
    predicted_circles["correct"] = False
    tp_indices = [i for i, _ in tp]
    predicted_circles.loc[tp_indices, "correct"] = True

    predicted_circles.to_file(args.tp_output_file, driver="GPKG")

    return 0

if __name__ == "__main__":
    main()
