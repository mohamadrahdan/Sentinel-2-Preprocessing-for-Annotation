from step2_preprocess_images import ImagePreprocessor
from step3_save_ready_images import ImageSaver
from config_sentinelhub import get_config, test_config
from step1b_sentinel_downloader import SentinelDownloader

if __name__ == "__main__":
    # Step 1: Download real Sentinel-2 image for actual AOI
    #bbox = [51.3463, 30.6981, 51.9443, 31.1949]  # ← from your KML
    bbox = [51.40, 30.80, 51.41, 30.81]
    time_interval = ("2023-08-01", "2023-08-10")

    downloader = SentinelDownloader(bbox=bbox, time_interval=time_interval)
    downloader.download()

    # Step 2: Preprocess images
    preprocessor = ImagePreprocessor(input_folder="output", output_folder="processed")
    preprocessor.preprocess_images()

    # Step 3: Save ready images for annotation
    saver = ImageSaver(input_folder="processed", output_folder="ready_for_annotation")
    saver.save_images()

    # Optional: test and save config
    config = get_config(profile_name="landsat-pipeline")
    test_config(config)
