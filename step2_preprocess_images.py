from base_pipeline import BasePipeline
import os
import shutil

class ImagePreprocessor(BasePipeline):
    def __init__(self, input_folder, output_folder):
        super().__init__(input_folder, output_folder)

    def preprocess_images(self):
        self.log("Starting image preprocessing...")

        # Loop through files in input folder
        for filename in os.listdir(self.input_folder):
            if filename.endswith(".jpg"):
                input_path = os.path.join(self.input_folder, filename)
                output_path = os.path.join(self.output_folder, f"pre_{filename}")
                
                # Simulate preprocessing by copying the file with new name
                shutil.copy(input_path, output_path)
                self.log(f"Preprocessed {filename} → pre_{filename}")

        self.log("Preprocessing completed.")
