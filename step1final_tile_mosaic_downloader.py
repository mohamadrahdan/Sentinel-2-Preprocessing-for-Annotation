from __future__ import annotations
"""Download Sentinel-2 L2A tiles … """

import math
from datetime import date, timedelta
from pathlib import Path
from typing import List

import imageio.v2 as imageio
import numpy as np
import rasterio
from rasterio.merge import merge
from sentinelhub import (
    BBox, CRS, SentinelHubRequest, DataCollection,
    bbox_to_dimensions, MimeType)
from config_sentinelhub import get_config  # .env credentials

# user parameters
AOI_WGS84   = [51.20, 30.16, 52, 32]
START_DATE  = date(2017, 3, 30)
END_DATE    = date(2018, 3, 30)
RESOLUTION  = 10
TILE_PX     = 2400
KEEP_TILES        = False
VALID_RATIO_MIN   = 0.15
CLOUD_RATIO_MAX   = 0.80

# folder layout
CONFIG         = get_config()
TILE_TMP16_DIR = Path("tiles_tmp16"); TILE_TMP16_DIR.mkdir(exist_ok=True)
TILE_TMP8_DIR  = Path("tiles_tmp8");  TILE_TMP8_DIR.mkdir(exist_ok=True)
MOSAIC_16_DIR  = Path("mosaics_16b"); MOSAIC_16_DIR.mkdir(exist_ok=True)
MOSAIC_8_DIR   = Path("mosaics_8b");  MOSAIC_8_DIR.mkdir(exist_ok=True)

# evalscript_Java
EVALSCRIPT_RGB_MASK = """
function setup(){return{input:["B04","B03","B02","dataMask"],
         output:{bands:4,sampleType:"UINT16"}}}
function evaluatePixel(s){
  return [s.B04*10000,s.B03*10000,s.B02*10000,s.dataMask]}
"""

# helper functions
def save_array_as_tiff(arr: np.ndarray, bbox: BBox, path: Path) -> None:
    h, w, bands = arr.shape
    transform = rasterio.transform.from_bounds(*bbox, w, h)
    profile = dict(driver="GTiff", height=h, width=w, count=bands, dtype="uint16",
                   crs=bbox.crs.pyproj_crs(), transform=transform, compress="deflate")
    with rasterio.open(path, "w", **profile) as dst:
        for i in range(bands):
            dst.write(arr[..., i], i + 1)

def write_preview_png(arr16: np.ndarray, path: Path) -> None:
    if np.any(arr16):
        p2, p98 = np.percentile(arr16[arr16 > 0], (2, 98))
    else:
        p2, p98 = 0, 1
    stretched = np.clip((arr16 - p2)/(p98-p2+1e-6)*255,0,255).astype(np.uint8)
    imageio.imwrite(path, stretched)
