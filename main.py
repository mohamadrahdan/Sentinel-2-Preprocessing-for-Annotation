from step1_download_images import ImageDownloader
from step2_preprocess_images import ImagePreprocessor
from step3_save_ready_images import ImageSaver

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
