from typing import List, Union
from senseagronomy import Pixel, Aerosol, Radsat, Cloud

def str2pixel(flags: List[str]) -> List[Pixel]:
    out: List[Pixel] = []
    for flag in flags:
        match flag:
            case "FILL":
                out.append(Pixel.fill)
            case "DILLATED_CLOUD":
                out.append(Pixel.dillated_cloud)
            case "CIRRUS":
                out.append(Pixel.cirrus)
            case "CLOUD":
                out.append(Pixel.cloud)
            case "CLOUD_SHADOW":
                out.append(Pixel.cloud_shadow)
            case "SNOW":
                out.append(Pixel.snow)
            case "CLEAR":
                out.append(Pixel.clear)
            case "WATER":
                out.append(Pixel.water)
            case "C_UNKNOWN":
                out.append(Pixel.c_unknown)
            case "C_LOW":
                out.append(Pixel.c_low)
            case "C_MEDIUM":
                out.append(Pixel.c_medium)
            case "C_HIGH":
                out.append(Pixel.c_high)
            case "CS_UNKNOWN":
                out.append(Pixel.cs_unknown)
            case "CS_LOW":
                out.append(Pixel.cs_low)
            case "CS_MEDIUM":
                out.append(Pixel.cs_medium)
            case "CS_HIGH":
                out.append(Pixel.cs_high)
            case "SC_UNKNOWN":
                out.append(Pixel.sc_unknown)
            case "SC_LOW":
                out.append(Pixel.sc_low)
            case "SC_MEDIUM":
                out.append(Pixel.sc_medium)
            case "SC_HIGH":
                out.append(Pixel.sc_high)
            case "CC_UNKNOWN":
                out.append(Pixel.cc_unknown)
            case "CC_LOW":
                out.append(Pixel.cc_low)
            case "CC_MEDIUM":
                out.append(Pixel.cc_medium)
            case "CC_HIGH":
                out.append(Pixel.cc_high)
            case _:
                raise RuntimeError

    return out


def str2radsat(flags: List[str]) -> List[Radsat]:
    out: List[Radsat] = []
    for flag in flags:
        match flag:
            case "B1":
                out.append(Radsat.b1)
            case "B2":
                out.append(Radsat.b2)
            case "B3":
                out.append(Radsat.b3)
            case "B4":
                out.append(Radsat.b4)
            case "B5":
                out.append(Radsat.b5)
            case "B6":
                out.append(Radsat.b6)
            case "B7":
                out.append(Radsat.b7)
            case "B6H_9":
                out.append(Radsat.b6h_b9)
            case "DROPPED":
                out.append(Radsat.dropped_pixel)
            case "TERRAIN_OCCLUSION":
                out.append(Radsat.terrain_occlusion)
            case _:
                raise RuntimeError

    return out


def str2aerosol(platform: str, a_flags: List[str], c_flags: List[str]) -> List[Union[Aerosol, Cloud]]:
    out: List[Union[Aerosol, Cloud]] = []
    if platform == "OLI":
        for flag in a_flags:
            match flag:
                case "FILL":
                    out.append(Aerosol.fill)
                case "VALID_RETRIEVAL":
                    out.append(Aerosol.valid_retrieval)
                case "INTERPOLATED":
                    out.append(Aerosol.interpolated)
                case "CLIMATOLOGY":
                    out.append(Aerosol.climatology)
                case "LOW":
                    out.append(Aerosol.low)
                case "MEDIUM":
                    out.append(Aerosol.medium)
                case "HIGH":
                    out.append(Aerosol.high)
                case _:
                    raise RuntimeError
    else:
        for flag in c_flags:
            match flag:
                case "DDV":
                    out.append(Cloud.ddv)
                case "CLOUD":
                    out.append(Cloud.cloud)
                case "CLOUD_SHADOW":
                    out.append(Cloud.cloud_shadow)
                case "NEAR_CLOUD":
                    out.append(Cloud.near_cloud)
                case "SNOW":
                    out.append(Cloud.snow)
                case "WATER":
                    out.append(Cloud.water)
                case _:
                    raise RuntimeError

    return out
