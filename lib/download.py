import zipfile
import os
from pathlib import Path


async def zip_and_download_files(
    exports_directory: str, temp_directory: str = "temp"
) -> str:
    """Zip the files in the directory and return the zip file path."""

    zip_file_path = Path(temp_directory) / "processed_files.zip"

    # Create a zip file
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(exports_directory):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(exports_directory))

    return str(zip_file_path)
