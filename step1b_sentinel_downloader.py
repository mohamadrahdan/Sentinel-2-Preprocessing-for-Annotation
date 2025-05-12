from sentinelhub import SHConfig, BBox, CRS, MimeType, SentinelHubRequest, DataCollection
from config_sentinelhub import get_config
import os

class SentinelDownloader:
    def __init__(self, bbox, time_interval, output_folder="output", profile_name="landsat-pipeline"):
        self.config = get_config(profile_name=profile_name)
        self.bbox = BBox(bbox=bbox, crs=CRS.WGS84)
        self.time_interval = time_interval
        self.output_folder = output_folder

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    def download(self):
        print("[DEBUG] Using bbox:", self.bbox)
        print("[DEBUG] Using time interval:", self.time_interval)

        request = SentinelHubRequest(
            data_folder=self.output_folder,
            evalscript="""
            function setup() {
                return {
                    input: ["B04", "B03", "B02"],
                    output: { bands: 3 }
                };
            }
            function evaluatePixel(sample) {
                return [sample.B04, sample.B03, sample.B02];
            }
            """,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=self.time_interval
                )
            ],
            responses=[
                SentinelHubRequest.output_response("default", MimeType.TIFF)
            ],
            bbox=self.bbox,
            resolution=(10, 10),
            config=self.config
        )

        response = request.get_data(save_data=True)
        print(f"[INFO] Downloaded {len(response)} image(s) to: {self.output_folder}")
