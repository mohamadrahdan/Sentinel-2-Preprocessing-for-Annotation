import math
from datetime import datetime
from sentinelhub import (
    CRS, bbox_to_dimensions, BBox, BBoxSplitter
)
from config_sentinelhub import get_config


AOI = [51.3463, 30.6981, 51.9443, 31.1949]   # minLon, minLat, maxLon, maxLat
RESOLUTION = 10                               # metres / pixel
TILE_PX = 2500                                # max 2500 as per API
DATE_START = datetime(2015, 6, 27)
DATE_END   = datetime.today()
PROFILE = "landsat-pipeline"
DIR_TILES   = "tiles_tmp"
DIR_MOSAICS = "mosaics"

config = get_config(profile_name=PROFILE)

# 1️⃣ build safe‑size tile list via BBoxSplitter
full_bbox = BBox(AOI, crs=CRS.WGS84)

# compute how many tiles keep each side ≤ 2500 px
width_px, height_px = bbox_to_dimensions(full_bbox, resolution=RESOLUTION)
cols = math.ceil(width_px  / TILE_PX)      
rows = math.ceil(height_px / TILE_PX)      

splitter = BBoxSplitter(
    [full_bbox],
    full_bbox.crs,
    split_shape=(rows, cols)
)

TILES = splitter.get_bbox_list()
print(f"[INIT] total tiles: {len(TILES)} (each ≤ {TILE_PX}px)\n")
