from enum import Enum
from glob import glob
from pathlib import Path
from typing import Dict, Optional, Literal, Union, Tuple, List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import rasterio as rio
import numpy as np

# TODO Move back to Enums and Union QA values for LS4-7 and LS6-9 as they have identical value ranges, gains and non-interfering qa values


class Radsat(Enum):
    b1: np.uint16                =  np.uint16(0b0000000000000001)
    b2: np.uint16                =  np.uint16(0b0000000000000010)
    b3: np.uint16                =  np.uint16(0b0000000000000100)
    b4: np.uint16                =  np.uint16(0b0000000000001000)
    b5: np.uint16                =  np.uint16(0b0000000000010000)
    b6: np.uint16                =  np.uint16(0b0000000000100000)
    b7: np.uint16                =  np.uint16(0b0000000001000000)
    b6h_b9: np.uint16            =  np.uint16(0b0000000100000000)  # band 6H for LS7, band 9 for LS 8/9
    dropped_pixel: np.uint16     =  np.uint16(0b0000001000000000)
    terrain_occlusion: np.uint16 =  np.uint16(0b0000100000000000)


class Pixel(Enum):
    fill: np.uint16           = np.uint16(0b0000000000000001)
    dillated_cloud: np.uint16 = np.uint16(0b0000000000000010)
    cirrus: np.uint16         = np.uint16(0b0000000000000100)
    cloud: np.uint16          = np.uint16(0b0000000000001000)
    cloud_shadow: np.uint16   = np.uint16(0b0000000000010000)
    snow: np.uint16           = np.uint16(0b0000000000100000)
    clear: np.uint16          = np.uint16(0b0000000001000000)
    water: np.uint16          = np.uint16(0b0000000010000000)
    # cloud confidence levels
    c_unknown: np.uint16      = np.uint16(0b0000000000000000)
    c_low: np.uint16          = np.uint16(0b0000000100000000)
    c_medium: np.uint16       = np.uint16(0b0000001000000000)
    c_high: np.uint16         = np.uint16(0b0000001100000000)
    # cloud shadow confidence levels
    cs_unknown: np.uint16     = np.uint16(0b0000000000000000)
    cs_low: np.uint16         = np.uint16(0b0000010000000000)
    cs_medium: np.uint16      = np.uint16(0b0000100000000000)
    cs_high: np.uint16        = np.uint16(0b0000110000000000)
    # snow/ice confidence
    sc_unknown: np.uint16     = np.uint16(0b0000000000000000)
    sc_low: np.uint16         = np.uint16(0b0001000000000000)
    sc_medium: np.uint16      = np.uint16(0b0010000000000000)
    sc_high: np.uint16        = np.uint16(0b0011000000000000)
    # cirrus confidence
    cc_unknown: np.uint16     = np.uint16(0b0000000000000000)
    cc_low: np.uint16         = np.uint16(0b0100000000000000)
    cc_medium: np.uint16      = np.uint16(0b1000000000000000)
    cc_high: np.uint16        = np.uint16(0b1100000000000000)


class Aerosol(Enum):
    """
    Landsat 8-9 equivalent to Cloud enum
    """
    fill: np.uint8            = np.uint8(0b00000001)
    valid_retrieval: np.uint8 = np.uint8(0b00000010)
    water: np.uint8           = np.uint8(0b00000100)
    interpolated: np.uint8    = np.uint8(0b00100000)
    # aerosol levels
    climatology: np.uint8     = np.uint8(0b00000000)
    low: np.uint8             = np.uint8(0b01000000)
    medium: np.uint8          = np.uint8(0b10000000)
    high: np.uint8            = np.uint8(0b11000000)


class Cloud(Enum):
    """
    Landsat 4-7 equivalent to Aerosol enum
    """
    ddv: np.uint8          = np.uint8(0b00000001)
    cloud: np.uint8        = np.uint8(0b00000010)
    cloud_shadow: np.uint8 = np.uint8(0b00000100)
    near_cloud: np.uint8   = np.uint8(0b00001000)
    snow: np.uint8         = np.uint8(0b00010000)
    water: np.uint8        = np.uint8(0b00100000)

class Scene:
    """
    Take multiband image...original quality reports needed in same directory as image
    """
    FILL_VALUE: int = 0

    def __init__(self, directory: str, fglob: str) -> None:
        self.directory: str = directory
        self.fglob: str = fglob
        self.dataset: Optional[np.ndarray] = None
        self.metadata: Optional[Dict] = None
        self.gains: Optional[np.ndarray] = None
        self.offsets: Optional[np.ndarray] = None
        self.raw: Optional[np.ndarray] = None
        self.boundaries = (7273, 43636)  # note: hard coded for L2SP

    def __enter__(self):
        self.dataset = rio.open(self.directory + "/" + self.fglob)
        self.metadata = self.dataset.meta
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.dataset.close()

    def read_raw(self):
        if self.dataset is None:
            self.dataset = rio.open(self.directory + "/" + self.fglob)
        
        self.raw = self.dataset.read(self.dataset.indexes).astype(np.float64)
        for band in range(len(self.dataset.indexes)):
            self.raw[band] = np.where((self.raw[band] < self.boundaries[0]) | (self.raw[band] > self.boundaries[1]), np.nan, self.raw[band])
        
        self.raw[self.raw == Scene.FILL_VALUE] = np.nan

    def get_metadata_from_xml(self) -> Tuple[np.ndarray]:
        try:
            mtl_xml = glob("*MTL.xml", root_dir=self.directory).pop()
        except IndexError:
            raise FileNotFoundError

        tree = ET.parse(self.directory + "/" + mtl_xml)
        root = tree.getroot()
        surface_reflectance_entries = root.find("LEVEL2_SURFACE_REFLECTANCE_PARAMETERS")
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
        # note: clamp should not be needed if all data ranges are clipped correctly when reading raw data. However, stil used as a precaution
        # note: reflectance of 0 would be incorrect so I set it to smallest float
        self.raw = self.raw * self.gains + self.offsets
        if clamp:
            self.raw = np.clip(self.raw, np.finfo(np.float64).tiny, 1.0)

    def get_pixel_qa(self, flags: List[np.uint16]) -> np.ndarray:
        try:
            pixel_qa_fp = glob(self.directory + "/" + "*QA_PIXEL.TIF").pop()
        except IndexError:
            raise FileNotFoundError
        
        compund_flag = np.uint16(0)
        for flag in flags:
            compund_flag = np.bitwise_or(compund_flag, flag.value)
        
        with rio.open(pixel_qa_fp, "r") as ds:
            pixel_qa = ds.read(1)
        
        pixel_qa = np.bitwise_and(pixel_qa, compund_flag)
        # pixels to be masked out (i.e. invalid pixels) are True => in docstring as note
        pixel_qa = np.where(pixel_qa == 0, 0, 1).astype(bool)
        return pixel_qa        

    def get_aerosol_qa(self, flags: List[np.uint8]) -> np.ndarray:
        try:
            pixel_qa_fp = glob(self.directory + "/" + "*SR_QA_AEROSOL.TIF").pop()
        except IndexError:
            raise FileNotFoundError
        
        compund_flag = np.uint8(0)
        for flag in flags:
            compund_flag = np.bitwise_or(compund_flag, flag.value)
        
        with rio.open(pixel_qa_fp, "r") as ds:
            pixel_qa = ds.read(1)
        
        pixel_qa = np.bitwise_and(pixel_qa, compund_flag)
        # pixels to be masked out (i.e. invalid pixels) are True => in docstring as note
        pixel_qa = np.where(pixel_qa == 0, 0, 1).astype(bool)
        return pixel_qa

    def get_radsat_qa(self, flags: List[np.uint16]) -> np.ndarray:
        try:
            pixel_qa_fp = glob(self.directory + "/" + "*QA_RADSAT.TIF").pop()
        except IndexError:
            raise FileNotFoundError
        
        compund_flag = np.uint16(0)
        for flag in flags:
            compund_flag = np.bitwise_or(compund_flag, flag.value)
        
        with rio.open(pixel_qa_fp, "r") as ds:
            pixel_qa = ds.read(1)
        
        pixel_qa = np.bitwise_and(pixel_qa, compund_flag)
        # pixels to be masked out (i.e. invalid pixels) are True => in docstring as note
        pixel_qa = np.where(pixel_qa == 0, 0, 1).astype(bool)
        return pixel_qa
