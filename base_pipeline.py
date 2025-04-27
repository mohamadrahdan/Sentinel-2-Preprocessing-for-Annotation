import os

class BasePipeline:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.check_paths()

    def check_paths(self):
        """Create input and output directories if they don't exist."""
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def log(self, message):
        """Simple logger for displaying messages."""
        print(f"[INFO] {message}")
