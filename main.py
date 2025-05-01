from step1_download_images import ImageDownloader
from step2_preprocess_images import ImagePreprocessor


if __name__ == "__main__":
    # Step 1: Download images
    downloader = ImageDownloader(input_folder="input", output_folder="output", api_key="fake_api_key")
    downloader.download_images()

    # Step 2: Preprocess images
    preprocessor = ImagePreprocessor(input_folder="output", output_folder="processed")
    preprocessor.preprocess_images()
