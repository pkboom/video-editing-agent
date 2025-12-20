# Installation

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Verification:**

```bash
ffmpeg -version
```

```bash
uv sync

cp .env.example .env
# OPENAI_API_KEY=openai-api-key

streamlit run main.py
```

# Configuration

Modify `.streamlit/config.toml` to adjust:

- Maximum upload file size
- Server port and browser settings
- Theme and UI customization
- Logging levels
