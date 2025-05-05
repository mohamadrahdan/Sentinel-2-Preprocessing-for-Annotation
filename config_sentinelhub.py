from sentinelhub import SHConfig
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

def get_config(profile_name="default"):
    """
    Load Sentinel Hub configuration from .env file and save under a named profile.
    """

    config = SHConfig()

    # Read credentials from environment variables
    config.sh_client_id = os.getenv("SENTINEL_CLIENT_ID")
    config.sh_client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
    config.instance_id = os.getenv("SENTINEL_INSTANCE_ID")

    if not config.sh_client_id or not config.sh_client_secret or not config.instance_id:
        print("[WARNING] Missing one or more Sentinel Hub credentials in .env file!")
    else:
        print("[INFO] Sentinel Hub credentials loaded from .env")

    # Save under profile name
    config.save(profile_name)
    print(f"[INFO] Configuration saved under profile: {profile_name}")

    return config


def test_config(config):
    """Print config values to confirm connection (without exposing secrets)."""
    print("Instance ID:", config.instance_id)
    print("Client ID:", config.sh_client_id)
    print("Client Secret:", "OK" if config.sh_client_secret else "Missing")
