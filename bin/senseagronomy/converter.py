"""
converter.py

This module provides functions for converting lists of string flags into
corresponding Pixel, Radsat, Aerosol, and Cloud enumerations from
the senseagronomy module.
"""

from typing import List, Union
from senseagronomy import Pixel, Aerosol, Radsat, Cloud


def str2pixel(flags: List[str]) -> List[Pixel]:
    """
    Convert a list of string flags into a list of Pixel enumeration values.

    Args:
        flags (List[str]): A list of string flags representing pixel types.

    Returns:
        List[Pixel]: A list of Pixel enumeration values corresponding to the
        input flags.

    Raises:
        RuntimeError: If an unknown flag is encountered.
    """
    out: List[Pixel] = []
    for flag in flags:
        match flag:
            case "FILL":
                out.append(Pixel.FILL)
            case "DILLATED_CLOUD":
                out.append(Pixel.DILLATED_CLOUD)
            case "CIRRUS":
                out.append(Pixel.CIRRUS)
            case "CLOUD":
                out.append(Pixel.CLOUD)
            case "CLOUD_SHADOW":
                out.append(Pixel.CLOUD_SHADOW)
            case "SNOW":
                out.append(Pixel.SNOW)
            case "CLEAR":
                out.append(Pixel.CLEAR)
            case "WATER":
                out.append(Pixel.WATER)
            case "C_UNKNOWN":
                out.append(Pixel.C_UNKNOWN)
            case "C_LOW":
                out.append(Pixel.C_LOW)
            case "C_MEDIUM":
                out.append(Pixel.C_MEDIUM)
            case "C_HIGH":
                out.append(Pixel.C_HIGH)
            case "CS_UNKNOWN":
                out.append(Pixel.CS_UNKNOWN)
            case "CS_LOW":
                out.append(Pixel.CS_LOW)
            case "CS_MEDIUM":
                out.append(Pixel.CS_MEDIUM)
            case "CS_HIGH":
                out.append(Pixel.CS_HIGH)
            case "SC_UNKNOWN":
                out.append(Pixel.SC_UNKNOWN)
            case "SC_LOW":
                out.append(Pixel.SC_LOW)
            case "SC_MEDIUM":
                out.append(Pixel.SC_MEDIUM)
            case "SC_HIGH":
                out.append(Pixel.SC_HIGH)
            case "CC_UNKNOWN":
                out.append(Pixel.CC_UNKNOWN)
            case "CC_LOW":
                out.append(Pixel.CC_LOW)
            case "CC_MEDIUM":
                out.append(Pixel.CC_MEDIUM)
            case "CC_HIGH":
                out.append(Pixel.CC_HIGH)
            case _:
                raise RuntimeError(f"Unknown flag: {flag}")

    return out


def str2radsat(flags: List[str]) -> List[Radsat]:
    """
    Convert a list of string flags into a list of Radsat enumeration values.

    Args:
        flags (List[str]): A list of string flags representing radsat bands.

    Returns:
        List[Radsat]: A list of Radsat enumeration values corresponding to
        the input flags.

    Raises:
        RuntimeError: If an unknown flag is encountered.
    """
    out: List[Radsat] = []
    for flag in flags:
        match flag:
            case "B1":
                out.append(Radsat.B1)
            case "B2":
                out.append(Radsat.B2)
            case "B3":
                out.append(Radsat.B3)
            case "B4":
                out.append(Radsat.B4)
            case "B5":
                out.append(Radsat.B5)
            case "B6":
                out.append(Radsat.B6)
            case "B7":
                out.append(Radsat.B7)
            case "B6H_9":
                out.append(Radsat.B6H_B9)
            case "DROPPED":
                out.append(Radsat.DROPPED_PIXEL)
            case "TERRAIN_OCCLUSION":
                out.append(Radsat.TERRAIN_OCCLUSION)
            case _:
                raise RuntimeError(f"Unknown flag: {flag}")

    return out


def str2aerosol(
    platform: str,
    a_flags: List[str],
    c_flags: List[str]
) -> List[Union[Aerosol, Cloud]]:
    """
    Convert a list of string flags into a list of Aerosol or Cloud
    enumeration values based on the platform.

    Args:
        platform (str): The platform name which determines the flag type.
        a_flags (List[str]): A list of string flags representing aerosol types
        (if platform is "OLI").
        c_flags (List[str]): A list of string flags representing cloud types
        (if platform is not "OLI").

    Returns:
        List[Union[Aerosol, Cloud]]: A list of Aerosol or Cloud enumeration
        values corresponding to the input flags.

    Raises:
        RuntimeError: If an unknown flag is encountered.
    """
    out: List[Union[Aerosol, Cloud]] = []
    if platform == "OLI":
        for flag in a_flags:
            match flag:
                case "FILL":
                    out.append(Aerosol.FILL)
                case "VALID_RETRIEVAL":
                    out.append(Aerosol.VALID_RETRIEVAL)
                case "INTERPOLATED":
                    out.append(Aerosol.INTERPOLATED)
                case "CLIMATOLOGY":
                    out.append(Aerosol.CLIMATOLOGY)
                case "LOW":
                    out.append(Aerosol.LOW)
                case "MEDIUM":
                    out.append(Aerosol.MEDIUM)
                case "HIGH":
                    out.append(Aerosol.HIGH)
                case _:
                    raise RuntimeError(f"Unknown aerosol flag: {flag}")
    else:
        for flag in c_flags:
            match flag:
                case "DDV":
                    out.append(Cloud.DDV)
                case "CLOUD":
                    out.append(Cloud.CLOUD)
                case "CLOUD_SHADOW":
                    out.append(Cloud.CLOUD_SHADOW)
                case "NEAR_CLOUD":
                    out.append(Cloud.NEAR_CLOUD)
                case "SNOW":
                    out.append(Cloud.SNOW)
                case "WATER":
                    out.append(Cloud.WATER)
                case _:
                    raise RuntimeError(f"Unknown cloud flag: {flag}")

    return out
