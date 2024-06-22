from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from senseagronomy import Scene
from senseagronomy.converter import str2pixel, str2radsat, str2aerosol
import numpy as np
import rasterio as rio


def main() -> int:
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="This program is used to apply linear transformations and mask out erroneous "
        "pixels based on quality flags. Additionally, the output can be converted to integer "
        "values and scaled accordingly to save disk space. It's expected that an input directory "
        "is given with a stacked image containing the surface reflectance bands, metadata file "
        "in XML format as well as quality images for pixel, radiometric and aerosol processing.",
    )
    parser.add_argument(
        "--platform",
        type=str,
        required=True,
        choices=["TM", "OLI"],
        help="The sensor group to process. TM/ETM/ETM+ are Landsat 4 to 7, "
        "OLI is Landsat 8 and 9.",
    )
    parser.add_argument(
        "--pixel-qa",
        type=str,
        nargs="*",
        metavar="PIXEL",
        required=False,
        choices=[
            "FILL",
            "DILLATED_CLOUD",
            "CIRRUS",
            "CLOUD",
            "CLOUD_SHADOW",
            "SNOW",
            "CLEAR",
            "WATER",
            "C_UNKNOWN",
            "C_LOW",
            "C_MEDIUM",
            "C_HIGH",
            "CS_UNKNOWN",
            "CS_LOW",
            "CS_MEDIUM",
            "CS_HIGH",
            "SC_UNKNOWN",
            "SC_LOW",
            "SC_MEDIUM",
            "SC_HIGH",
            "CC_UNKNOWN",
            "CC_LOW",
            "CC_MEDIUM",
            "CC_HIGH",
        ],
        default=["FILL", "C_LOW", "CS_LOW", "SC_LOW", "CC_LOW"],
        help="Pixel quality mask flags to apply. Flags prefixed with 'C' correspond to "
        "cloud confidence, flags prefixed with 'CS' correspond to cloud shadows, flags "
        "prefixed with 'SC' correspond to snow/ice condifence and flags prefixed with "
        "'CC' correspond to cirrus confidence (not applicable when platform == 'TM'). "
        "Choices: {%(choices)s}",
    )
    parser.add_argument(
        "--radsat-qa",
        type=str,
        nargs="*",
        metavar="RADSAT",
        required=False,
        choices=[
            "B1", 
            "B2", 
            "B3", 
            "B4", 
            "B5", 
            "B6", 
            "B7", 
            "B6H_9", 
            "DROPPED", 
            "TERRAIN_OCCLUSION"
        ],
        default=["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
        help="Radiometric correction quality mask flags. Individual bands correspond "
        "to detected saturation. Choices: {%(choices)s}",
    )
    parser.add_argument(
        "--aerosol-qa",
        type=str,
        nargs="*",
        metavar="AEROSOL",
        required=False,
        choices=[
            "FILL", 
            "VALID_RETRIEVAL", 
            "INTERPOLATED", 
            "CLIMATOLOGY", 
            "LOW", 
            "MEDIUM", 
            "HIGH"
        ],
        default=["FILL"],
        help="Aerosol processing qualiy mask flags. These only apply for OLI platform and "
        "correspond to 'cloud' flags for TM. Choices: {%(choices)s}",
    )
    parser.add_argument(
        "--cloud-qa",
        type=str,
        nargs="*",
        metavar="CLOUD",
        required=False,
        choices=["DDV", "CLOUD", "CLOUD_SHADOW", "NEAR_CLOUD", "SNOW", "WATER"],
        default=["CLOUD", "CLOUD_SHADOW", "NEAR_CLOUD"],
        help="Aerosol processing qualiy mask flags. These only apply for TM platform and "
        "correspond to 'aerosol' flags for OLI. Choices: {%(choices)s}",
    )
    parser.add_argument(
        "--otype",
        type=str,
        default="int32",
        choices=["int32", "float32"],
        required=False,
        help="Output data type. Note that choosing 'int32' will raise a runtime warning which "
        "can safely be ignored here.",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10_000,
        required=False,
        help="Scale factor for output band stack. Only applicable if 'otype' == int32. "
        "Default is in line with FORCE processing system.",
    )
    parser.add_argument(
        "--clamp",
        action="store_true",
        required=False,
        help="Clamp values after applying linear transformation. "
        "Since values are restricted to valid ranges, should not be needed.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        type=str,
        required=True,
        help="Name of output file, stored in 'directory'.",
    )
    parser.add_argument("fileglob", type=str, help="File glob/name of multiband image.")
    parser.add_argument(
        "directory", type=str, help="Directory containing metadata and multiband image files."
    )

    args = parser.parse_args()

    with Scene(args.directory, args.fileglob) as S:
        S.get_metadata_from_xml()
        S.read_raw()
        S.apply_transformation(clamp=args.clamp)

    clear_mask = ~S.get_pixel_qa(str2pixel(args.pixel_qa))[np.newaxis, ...]
    radsat_mask = S.get_radsat_qa(str2radsat(args.radsat_qa))[np.newaxis, ...]
    aerosol_mask = S.get_aerosol_qa(
        str2aerosol(args.platform, args.aerosol_qa, args.cloud_qa),
        "SR_QA_AEROSOL" if args.platform == "OLI" else "SR_CLOUD_QA",
    )[np.newaxis, ...]

    mask = np.any(
        np.concatenate([clear_mask, radsat_mask, aerosol_mask], axis=0), axis=0, keepdims=True
    ).repeat(S.raw.shape[0], axis=0)

    out_dtype = np.int32 if args.otype == "int32" else np.float32
    rout_dtype = rio.int32 if args.otype == "int32" else rio.float32
    predictor = 2 if args.otype == "int32" else 3
    nodata_value = np.iinfo(out_dtype).min if args.otype == "int32" else np.nan

    S.raw[mask] = nodata_value

    if args.otype == "int32":
        S.raw = S.raw * args.scale

    S.metadata.update(
        dtype=rout_dtype, compress="DEFLATE", nodata=nodata_value, predictor=predictor
    )

    with rio.open(args.directory + "/" + args.output, "w", **S.metadata) as ds:
        ds.write(S.raw.astype(rout_dtype))

    return 0
