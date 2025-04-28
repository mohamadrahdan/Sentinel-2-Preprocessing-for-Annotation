from step1_download_images import ImageDownloader

if __name__ == "__main__":
    # Create the downloader object
    downloader = ImageDownloader(input_folder="input", output_folder="output", api_key="fake_api_key")
    
    # Start the download simulation
    downloader.download_images()
