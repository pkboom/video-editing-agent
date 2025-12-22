from pathlib import Path
import time

exports_dir = Path("exports")
exports_dir.mkdir(exist_ok=True)

file_path = exports_dir / f"{time.time()}.README.md"
file_path.write_text("# Export Run\n\nThis directory contains processed exports.")
