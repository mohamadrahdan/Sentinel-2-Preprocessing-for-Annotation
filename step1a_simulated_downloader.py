# This is a simulated image downloader for development and testing purposes.
# In production, use `step1b_sentinel_downloader.py` for real data download from Sentinel Hub API.

from base_pipeline import BasePipeline  

class ImageDownloader(BasePipeline):  # Define a new class that inherits from BasePipeline
    def __init__(self, input_folder, output_folder, api_key):
        super().__init__(input_folder, output_folder)  # Initialize the parent class
        self.api_key = api_key  

    def download_images(self):
        self.log("Starting download process...")  # Log the start of the download process

        # Simulate downloading three images (replace this later with real download code)
        for i in range(3):
            filename = f"image_{i+1}.jpg"
            filepath = f"{self.output_folder}/{filename}"
            with open(filepath, "w") as f:
                f.write("Fake image content")  # Simulated content inside the created files
            self.log(f"Downloaded {filename}")  # Log each file creation

        self.log("Download process completed.")  # Log the completion of the download process
