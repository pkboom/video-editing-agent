from pathlib import Path
import time

exports_dir = Path("exports")
exports_dir.mkdir(exist_ok=True)
run_dir = exports_dir / f"splits_{int(time.time())}"
run_dir.mkdir(parents=True, exist_ok=True)
