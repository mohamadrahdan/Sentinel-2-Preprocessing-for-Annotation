from step1a_simulated_downloader import ImageDownloader
from step2_preprocess_images import ImagePreprocessor
from step3_save_ready_images import ImageSaver
from config_sentinelhub import get_config, test_config
from step1b_sentinel_downloader import SentinelDownloader


if __name__ == "__main__":
    # Step 1: Download images
    downloader = ImageDownloader(input_folder="input", output_folder="output", api_key="fake_api_key")
    downloader.download_images()

    # Step 2: Preprocess images
    preprocessor = ImagePreprocessor(input_folder="output", output_folder="processed")
    preprocessor.preprocess_images()

    # Step 3: Save ready images for annotation
    saver = ImageSaver(input_folder="processed", output_folder="ready_for_annotation")
    saver.save_images()

    config = get_config(profile_name="landsat-pipeline")
    test_config(config)

    # Define bounding box [min_lon, min_lat, max_lon, max_lat]
    bbox = [51.17, 30.39, 51.59, 31.13]  # an small area around the Isfahan city

    # Define date range
    time_interval = ("2023-08-01", "2023-08-10")

    # Create downloader instance and start download
    downloader = SentinelDownloader(bbox=bbox, time_interval=time_interval)
    downloader.download()