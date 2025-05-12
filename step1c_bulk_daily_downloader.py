from sentinelhub import SHConfig, BBox, CRS, MimeType, SentinelHubRequest, DataCollection, bbox_to_dimensions
from config_sentinelhub import get_config
from datetime import datetime, timedelta
import os

# Define parameters
bbox_coords = [51.3463, 30.6981, 51.9443, 31.1949]  # Replace with your actual area of interest
bbox = BBox(bbox=bbox_coords, crs=CRS.WGS84)
resolution = 10
output_folder = "bulk_output"
start_date = datetime(2023, 12, 18)
end_date = datetime(2024, 1, 12)
profile_name = "landsat-pipeline"

# Load configuration
config = get_config(profile_name=profile_name)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define evalscript
evalscript = """
// Simple true color RGB composite
function setup() {
    return {
        input: ["B04", "B03", "B02"],
        output: { bands: 3 }
    };
}

function evaluatePixel(sample) {
    return [sample.B04, sample.B03, sample.B02];
}
"""

def download_image_for_date(date_str):
    request = SentinelHubRequest(
        data_folder=output_folder,
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(date_str, date_str)
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        bbox=bbox,
        size=bbox_to_dimensions(bbox, resolution=resolution),
        config=config
    )

    try:
        request.get_data(save_data=True)
        print(f"[SUCCESS] Downloaded image for {date_str}")
        return True
    except Exception as e:
        print(f"[ERROR] {date_str}: {e}")
        return False

# Loop through days and download available images
current_date = start_date
success_count = 0
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    print(f"[INFO] Downloading {date_str} ...")
    if download_image_for_date(date_str):
        success_count += 1
    current_date += timedelta(days=1)

print(f"\n[DONE] Downloaded: {success_count} | Skipped: {(end_date - start_date).days + 1 - success_count}")
