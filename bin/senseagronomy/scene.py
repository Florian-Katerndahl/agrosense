"""
Documentation from the USGS used as references:
- LSDS-1619, version 6: Landsat 8-9 Collection 2 (C2) Level 2 Science
    Product (L2SP) Guide
- LSDS-1618, version 4: Landsat 4-7 Collection 2 (C2) Level 2 Science
    Product (L2SP) Guide
"""
from enum import Enum
from glob import glob
from typing import Dict, Optional, Union, Tuple, List, Literal
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import rasterio as rio
import numpy as np


class Radsat(Enum):
    """
    Mask flag values for radiometric processing QA image

    .. note:: b6h_b9 applies to band 6H for Landsat 7 and band 9 for
        Landsat 8/9.
    """
    B1: np.uint16 = np.uint16(0b0000000000000001)
    B2: np.uint16 = np.uint16(0b0000000000000010)
    B3: np.uint16 = np.uint16(0b0000000000000100)
    B4: np.uint16 = np.uint16(0b0000000000001000)
    B5: np.uint16 = np.uint16(0b0000000000010000)
    B6: np.uint16 = np.uint16(0b0000000000100000)
    B7: np.uint16 = np.uint16(0b0000000001000000)
    B6H_B9: np.uint16 = np.uint16(0b0000000100000000)
    DROPPED_PIXEL: np.uint16 = np.uint16(0b0000001000000000)
    TERRAIN_OCCLUSION: np.uint16 = np.uint16(0b0000100000000000)


class Pixel(Enum):
    """
    Mask flag values for pixel QA image

    .. note:: Cirrus masks only apply to Landsat 8 and 9.
    """
    FILL: np.uint16 = np.uint16(0b0000000000000001)
    DILLATED_CLOUD: np.uint16 = np.uint16(0b0000000000000010)
    CIRRUS: np.uint16 = np.uint16(0b0000000000000100)  # only LS 8-9
    CLOUD: np.uint16 = np.uint16(0b0000000000001000)
    CLOUD_SHADOW: np.uint16 = np.uint16(0b0000000000010000)
    SNOW: np.uint16 = np.uint16(0b0000000000100000)
    CLEAR: np.uint16 = np.uint16(0b0000000001000000)
    WATER: np.uint16 = np.uint16(0b0000000010000000)
    # cloud confidence levels
    C_UNKNOWN: np.uint16 = np.uint16(0b0000000000000000)
    C_LOW: np.uint16 = np.uint16(0b0000000100000000)
    C_MEDIUM: np.uint16 = np.uint16(0b0000001000000000)
    C_HIGH: np.uint16 = np.uint16(0b0000001100000000)
    # cloud shadow confidence levels
    CS_UNKNOWN: np.uint16 = np.uint16(0b0000000000000000)
    CS_LOW: np.uint16 = np.uint16(0b0000010000000000)
    CS_MEDIUM: np.uint16 = np.uint16(0b0000100000000000)
    CS_HIGH: np.uint16 = np.uint16(0b0000110000000000)
    # snow/ice confidence
    SC_UNKNOWN: np.uint16 = np.uint16(0b0000000000000000)
    SC_LOW: np.uint16 = np.uint16(0b0001000000000000)
    SC_MEDIUM: np.uint16 = np.uint16(0b0010000000000000)
    SC_HIGH: np.uint16 = np.uint16(0b0011000000000000)
    # cirrus confidence
    CC_UNKNOWN: np.uint16 = np.uint16(0b0000000000000000)  # only LS 8-9
    CC_LOW: np.uint16 = np.uint16(0b0100000000000000)  # only LS 8-9
    CC_MEDIUM: np.uint16 = np.uint16(0b1000000000000000)  # only LS 8-9
    CC_HIGH: np.uint16 = np.uint16(0b1100000000000000)  # only LS 8-9


class Aerosol(Enum):
    """
    Mask flag values for Aerosol QA image

    .. note:: Landsat 8-9 equivalent to Cloud enum.
    """
    FILL: np.uint8 = np.uint8(0b00000001)
    VALID_RETRIEVAL: np.uint8 = np.uint8(0b00000010)
    WATER: np.uint8 = np.uint8(0b00000100)
    INTERPOLATED: np.uint8 = np.uint8(0b00100000)
    # aerosol levels
    CLIMATOLOGY: np.uint8 = np.uint8(0b00000000)
    LOW: np.uint8 = np.uint8(0b01000000)
    MEDIUM: np.uint8 = np.uint8(0b10000000)
    HIGH: np.uint8 = np.uint8(0b11000000)


class Cloud(Enum):
    """
    Mask flag values for Aerosol QA image

    .. note:: Landsat 4-7 equivalent to Aerosol enum.
    """
    DDV: np.uint8 = np.uint8(0b00000001)
    CLOUD: np.uint8 = np.uint8(0b00000010)
    CLOUD_SHADOW: np.uint8 = np.uint8(0b00000100)
    NEAR_CLOUD: np.uint8 = np.uint8(0b00001000)
    SNOW: np.uint8 = np.uint8(0b00010000)
    WATER: np.uint8 = np.uint8(0b00100000)


class Scene:
    """
    Take multiband image...original quality reports needed
        in same directory as image
    """
    FILL_VALUE: int = 0

    def __init__(self, directory: str, fglob: str) -> None:
        """
        Initialize scene object

        .. warning:: Valid data ranges are hardcoded for the L2SP
            processing level!

        :param directory: Directory path where files are stored
        :type directory: str
        :param fglob: File glob/name for main multiband images
        :type fglob: str
        """
        self.directory: str = directory
        self.fglob: str = fglob
        self.dataset: Optional[np.ndarray] = None
        self.metadata: Optional[Dict] = None
        self.gains: Optional[np.ndarray] = None
        self.offsets: Optional[np.ndarray] = None
        self.raw: Optional[np.ndarray] = None
        self.boundaries: Tuple[int, int] = (7273, 43636)

    def __enter__(self):
        self.dataset = rio.open(f"{self.directory}/{self.fglob}")
        self.metadata = self.dataset.meta
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.dataset is not None:
            self.dataset.close()

    def read_raw(self):
        """
        Read all bands as numpy arrays

        .. note:: Values outside valid value ranges are set to np.nan
            as well as values that equal the fill value.
        """
        if self.dataset is None:
            self.dataset = rio.open(f"{self.directory}/{self.fglob}")

        self.raw = self.dataset.read(self.dataset.indexes).astype(np.float64)
        for band in range(len(self.dataset.indexes)):
            self.raw[band] = np.where(
                ((self.raw[band] < self.boundaries[0]) |
                    (self.raw[band] > self.boundaries[1])),
                np.nan,
                self.raw[band]
            )

        self.raw[self.raw == Scene.FILL_VALUE] = np.nan

    def get_metadata_from_xml(self) -> Tuple[np.ndarray]:
        """
        Get metadata (i.e. gains and offsets) from corresponding XML file

        .. note:: As gain and offset are identical for all sensors in the
            Collection 2, Level2, Tier 1 (L2 Scientific Products), this is
            not needed strictly speaking but may make adoption to other
            data sources easier as well as dealing with different number
            of bands across sensors.

        :raises FileNotFoundError: If metadata file in XML format is not found
        :raises ParseError: If expected XML tags are not found
        :return: Tuple containing gains and offsets
        :rtype: Tuple[np.ndarray]
        """
        try:
            mtl_xml = glob("*MTL.xml", root_dir=self.directory).pop()
        except IndexError as exc:
            raise FileNotFoundError from exc

        tree = ET.parse(f"{self.directory}/{mtl_xml}")
        root = tree.getroot()
        surface_reflectance_entries = root.find(
            "LEVEL2_SURFACE_REFLECTANCE_PARAMETERS"
        )
        if surface_reflectance_entries is None:
            raise ParseError

        gains = np.array(
            [
                float(node.text)
                for node in surface_reflectance_entries
                if node.tag.startswith("REFLECTANCE_MULT_BAND")
            ]
        ).reshape((-1, 1, 1))
        offsets = np.array(
            [
                float(node.text)
                for node in surface_reflectance_entries
                if node.tag.startswith("REFLECTANCE_ADD_BAND")
            ]
        ).reshape((-1, 1, 1))
        if gains.size == 0 or offsets.size == 0:
            raise ParseError

        self.gains = gains
        self.offsets = offsets

        return gains, offsets

    def apply_transformation(self, clamp: bool = False):
        """
        Apply linear transformation of form `y = m*x + b` to input bands
        in order to retrieve reflectance values.

        .. note:: Clamp should not be needed if all data ranges are
            clipped correctly when reading raw data. However,
            still used as a precaution.

        .. note:: Reflectance of 0 would be incorrect, so it's set to
            smallest float value.

        :param clamp: Clamp values after linear transformation to range
            [float64.min, 1.0], defaults to False
        :type clamp: bool, optional
        """
        if (
            self.raw is not None and
            self.gains is not None and
            self.offsets is not None
        ):
            self.raw = self.raw * self.gains + self.offsets
            if clamp:
                self.raw = np.clip(self.raw, np.finfo(np.float64).tiny, 1.0)

    def get_pixel_qa(self, flags: List[Pixel]) -> np.ndarray:
        """
        Filter pixel QA image with regard to supplied flags

        .. note:: Pixels to be masked out are set to True.

        :param flags: List of flags to apply
        :type flags: List[Pixel]
        :raises FileNotFoundError: If respective QA image is not found
        :return: Binary mask array
        :rtype: np.ndarray
        """
        try:
            pixel_qa_fp = glob(f"{self.directory}/*QA_PIXEL.TIF").pop()
        except IndexError as exc:
            raise FileNotFoundError from exc

        compound_flag = np.uint16(0)
        for flag in flags:
            compound_flag = np.bitwise_or(compound_flag, flag.value)

        with rio.open(pixel_qa_fp, "r") as dataset:
            pixel_qa = dataset.read(1)

        pixel_qa = np.bitwise_and(pixel_qa, compound_flag)
        pixel_qa = np.where(pixel_qa == 0, 0, 1).astype(bool)
        return pixel_qa

    def get_aerosol_qa(
        self,
        flags: List[Union[Aerosol, Cloud]],
        fglob: Literal["SR_QA_AEROSOL", "SR_CLOUD_QA"]
    ) -> np.ndarray:
        """
        Filter aerosol QA image with regard to supplied flags

        .. note:: Pixels to be masked out are set to True.

        :param flags: List of flags to apply
        :type flags: List[Union[Aerosol, Cloud]]
        :param fglob: File glob for aerosol quality image. This file is named
            differently for Landsat 4 to 7 ("SR_CLOUD_QA") and Landsat 8 to 9
            ("SR_QA_AEROSOL")
        :type fglob: Literal["SR_QA_AEROSOL", "SR_CLOUD_QA"]
        :raises FileNotFoundError: If respective QA image is not found
        :return: Binary mask array
        :rtype: np.ndarray
        """
        try:
            aerosol_qa_fp = glob(f"{self.directory}/*{fglob}.TIF").pop()
        except IndexError as exc:
            raise FileNotFoundError from exc

        compound_flag = np.uint8(0)
        for flag in flags:
            compound_flag = np.bitwise_or(compound_flag, flag.value)

        with rio.open(aerosol_qa_fp, "r") as dataset:
            aerosol_qa = dataset.read(1)

        aerosol_qa = np.bitwise_and(aerosol_qa, compound_flag)
        aerosol_qa = np.where(aerosol_qa == 0, 0, 1).astype(bool)
        return aerosol_qa

    def get_radsat_qa(self, flags: List[Radsat]) -> np.ndarray:
        """
        Filter radiometric QA image with regard to supplied flags

        .. note:: Pixels to be masked out are set to True.

        :param flags: List of flags to apply
        :type flags: List[Radsat]
        :raises FileNotFoundError: If respective QA image is not found
        :return: Binary mask array
        :rtype: np.ndarray
        """
        try:
            radsat_qa_fp = glob(f"{self.directory}/*QA_RADSAT.TIF").pop()
        except IndexError as exc:
            raise FileNotFoundError from exc

        compound_flag = np.uint16(0)
        for flag in flags:
            compound_flag = np.bitwise_or(compound_flag, flag.value)

        with rio.open(radsat_qa_fp, "r") as dataset:
            radsat_qa = dataset.read(1)

        radsat_qa = np.bitwise_and(radsat_qa, compound_flag)
        radsat_qa = np.where(radsat_qa == 0, 0, 1).astype(bool)
        return radsat_qa
