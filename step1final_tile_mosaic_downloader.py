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
START_DATE  = date(2017, 3, 27)
END_DATE    = date(2018, 3, 30)
RESOLUTION  = 10          # metres / pixel
TILE_PX     = 2400        # keep well below 2500-px API limit
KEEP_TILES        = False     # True → keep individual tile files
VALID_RATIO_MIN   = 0.15      # ≥15 % land pixels required
CLOUD_RATIO_MAX   = 0.80      # reject if >80 % cloud/shadow

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

# tile download
def download_tile(day: str, tile_bbox: BBox, idx: int) -> Path | None:
    req = SentinelHubRequest(
        evalscript=EVALSCRIPT_RGB_MASK,
        input_data=[SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A, time_interval=(day, day)
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=tile_bbox,
        size=bbox_to_dimensions(tile_bbox, RESOLUTION),
        config=CONFIG,)
    try:
        data = req.get_data(save_data=False)
    except Exception as exc:
        print(f"  ⚠ tile {idx:03d}: {exc}")
        return None
    if not data:
        return None

    rgbm = data[0]
    mask = rgbm[..., 3] > 0
    if mask.mean() < VALID_RATIO_MIN:
        return None
    cloud = ((rgbm[..., :3] == 0).all(axis=-1)) & mask
    if cloud.mean() > CLOUD_RATIO_MAX:
        return None

    tif = TILE_TMP16_DIR / f"{day}_{idx:03d}.tif"
    png = TILE_TMP8_DIR  / f"{day}_{idx:03d}.png"
    save_array_as_tiff(rgbm[..., :3], tile_bbox, tif)
    write_preview_png(rgbm[..., :3], png)
    print(f"  ✔ tile {idx:03d}")
    return tif

# daily mosaic
def mosaic_day(day: str, tif_paths: List[Path]) -> None:
    if not tif_paths:
        print("  (no data)")
        return

    datasets = [rasterio.open(p) for p in tif_paths]
    mosaic, out_transform = merge(datasets)
    meta = datasets[0].meta.copy()
    for ds in datasets: ds.close()

    meta.update(height=mosaic.shape[1], width=mosaic.shape[2],
                transform=out_transform, compress="deflate")

    out_tif = MOSAIC_16_DIR / f"{day}.tif"
    with rasterio.open(out_tif, "w", **meta) as dst:
        dst.write(mosaic)

    rgb = np.transpose(mosaic, (1, 2, 0))
    out_png = MOSAIC_8_DIR / f"{day}.png"
    write_preview_png(rgb, out_png)

    print(f"[MOSAIC] {out_tif.name}  │  [PREVIEW] {out_png.name}")

    if not KEEP_TILES:
        for p in tif_paths:
            (TILE_TMP8_DIR / (p.stem + ".png")).unlink(missing_ok=True)
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    full_bbox = BBox(AOI_WGS84, CRS.WGS84)
    w_px, h_px = bbox_to_dimensions(full_bbox, RESOLUTION)
    cols = math.ceil(w_px / TILE_PX)
    rows = math.ceil(h_px / TILE_PX)

    x_step = (full_bbox.max_x - full_bbox.min_x) / cols
    y_step = (full_bbox.max_y - full_bbox.min_y) / rows

    tiles: list[BBox] = []
    for r in range(rows):
        for c in range(cols):
            minx = full_bbox.min_x + c * x_step
            maxx = minx + x_step
            maxy = full_bbox.max_y - r * y_step
            miny = maxy - y_step
            tiles.append(BBox([minx, miny, maxx, maxy], CRS.WGS84))

    print(f"[INIT] total tiles: {len(tiles)} (each ≤ 2500 px)\n")

    cur = START_DATE
    one_day = timedelta(days=1)
    while cur <= END_DATE:
        dstr = cur.isoformat()
        print(f"\n=== {dstr} ===")
        daily = [t for i, tbox in enumerate(tiles, 1)
                 if (t:=download_tile(dstr, tbox, i))]
        mosaic_day(dstr, daily)
        cur += one_day

    print("\n[DONE]")
