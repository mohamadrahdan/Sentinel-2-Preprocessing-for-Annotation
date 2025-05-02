from base_pipeline import BasePipeline
import os
import shutil
import csv

class ImageSaver(BasePipeline):
    def __init__(self, input_folder, output_folder):
        super().__init__(input_folder, output_folder)

    def save_images(self):
        self.log("Saving final images for annotation...")

        metadata = []

        for filename in os.listdir(self.input_folder):
            if filename.endswith(".jpg"):
                src = os.path.join(self.input_folder, filename)
                dst = os.path.join(self.output_folder, filename)

                shutil.copy(src, dst)
                self.log(f"Saved {filename} for annotation")

                # Append basic metadata
                metadata.append({"filename": filename, "path": dst})

        # Save metadata to CSV
        metadata_file = os.path.join(self.output_folder, "metadata.csv")
        with open(metadata_file, mode="w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["filename", "path"])
            writer.writeheader()
            writer.writerows(metadata)

        self.log("Image saving and metadata export completed.")
