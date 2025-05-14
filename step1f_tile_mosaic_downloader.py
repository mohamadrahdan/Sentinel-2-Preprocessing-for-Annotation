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

def download_tile(date_str: str, tile: BBox, idx: int):
    """Download one tile → rename into tiles_tmp/YYYY-MM-DD_###.tif."""
    size = bbox_to_dimensions(tile, resolution=RESOLUTION)

    req = SentinelHubRequest(
        data_folder=DIR_TILES,
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=(date_str, date_str)
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=tile,
        size=size,
        config=config
    )

    try:
        _ = req.get_data(save_data=True)                     # file saved on disk
        # path returned by SH is relative → join with data_folder
        rel = PurePosixPath(req.get_filename_list()[0])      # cross-platform
        src = Path(DIR_TILES) / rel                          # full path
        dst = Path(DIR_TILES) / f"{date_str}_{idx:03d}.tif"
        dst.parent.mkdir(exist_ok=True)
        shutil.move(src, dst)                                # safer than rename
        print(f"  ✔️ tile {idx:03d}")
        return dst
    except Exception as e:
        print(f"  ✘ tile {idx:03d}: {e}")
        return None

