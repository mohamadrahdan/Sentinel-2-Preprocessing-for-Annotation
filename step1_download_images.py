from base_pipeline import BasePipeline  # Import the base class for folder handling

class ImageDownloader(BasePipeline):  # Define the image downloader class
    def __init__(self, input_folder, output_folder, api_key):
        super().__init__(input_folder, output_folder)  # Initialize the base class
        self.api_key = api_key  # Save the API key for future use

    def download_images(self):
        self.log("Starting image download...")

        # Simulate downloading three images
        for i in range(3):
            filename = f"image_{i+1}.jpg"
            filepath = f"{self.output_folder}/{filename}"
            with open(filepath, "w") as f:
                f.write("Fake image content")
            self.log(f"Created {filename}")

        self.log("Image download completed.")
