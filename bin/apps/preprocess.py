from senseagronomy import Scene, Pixel, Radsat
import numpy as np
import rasterio as rio

with Scene("./test-data_2", "test.tif") as S:
    S.get_metadata_from_xml()
    S.read_raw()
    S.apply_transformation(clamp=True)

clear_mask = ~S.get_pixel_qa([Pixel.clear, Pixel.c_low, Pixel.cc_low, Pixel.sc_low, Pixel.cs_low])[np.newaxis, ...]

radsat_mask = S.get_radsat_qa([Radsat.b1, Radsat.b2, Radsat.b3, Radsat.b4, Radsat.b5, Radsat.b6, Radsat.b7])[np.newaxis, ...]

mask = np.any(np.concatenate([clear_mask, radsat_mask], axis=0), axis=0, keepdims=True).repeat(6, axis=0)

# can be saved as float32 -> roughly 1 GB per tile or as int32 which cuts disk space in half
out_dtype = np.int32
# out_dtype = np.float32
nodata_value = np.iinfo(out_dtype).min 
# nodata_value = np.nan

S.raw[mask] = nodata_value

# scale factor influences how many digits are "saved". Here: four digits after decimal point which is in line with FORCE
S.raw = S.raw * 10_000

# rio.int32 if nodata_value is not np.isnan(out_dtype) else rio.float32
S.metadata.update(dtype = rio.int32, compress = "DEFLATE", nodata = nodata_value, predictor=2)

with rio.open("lol_ls5_consolidated.tif", "w", **S.metadata) as ds:
    # TODO if converting to int, nans from read_raw need to be converted to nodata_value first to silent warning. Output raster looks correct nonetheless
    ds.write(S.raw.astype(rio.int32))