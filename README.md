# Video Editing Agent

An AI-powered video editing agent that automatically transcribes videos, processes scripts, and creates intelligent video cuts based on the content. The agent uses OpenAI's Whisper for transcription and GPT-4 for intelligent editing decisions, delivering a streamlined Streamlit interface for easy video processing.

## 🎯 Use Cases

This AI agent is designed for content creators, educators, and video professionals who need to:

- **Automatically transcribe** video content with precise timestamps
- **Remove stutters and repetitions** from video recordings
- **Extract best takes** when multiple attempts of the same line exist
- **Create clean edits** based on provided scripts
- **Generate downloadable segments** for further editing
- **Streamline post-production** workflows for talking-head videos

Perfect for:
- Content creators recording tutorials or presentations
- Educators creating course materials
- Podcasters and video bloggers
- Anyone who needs to clean up recorded video content
- Teams looking to automate video editing workflows

## 🚀 Features

- **Video-to-Audio Conversion**: Automatically extracts audio from uploaded video files
- **AI Transcription**: Uses OpenAI Whisper for accurate speech-to-text with word-level timestamps
- **Intelligent Editing**: LLM-powered analysis to identify the best takes and remove repetitions
- **Script Matching**: Compares transcription against provided scripts for targeted editing
- **Segment Export**: Creates individual video segments for each selected clip
- **Batch Processing**: Processes multiple segments and packages them for download
- **Web Interface**: Clean Streamlit UI for easy file upload and processing
- **Progress Tracking**: Real-time progress updates during processing

## 🔧 How It Works

The video editing agent follows this workflow:

1. **File Upload**: Users upload video files through the Streamlit interface
2. **Audio Extraction**: [`convert_video_to_audio`](lib/convert.py) uses MoviePy to extract audio tracks
3. **Transcription**: [`transcribe_audio`](lib/transcribe.py) leverages OpenAI's Whisper API for accurate transcription with timestamps
4. **LLM Processing**: [`process_transcription_with_llm`](lib/llm.py) uses GPT-4 to analyze transcripts and identify best segments
5. **Video Cutting**: [`cut_video_segments`](lib/cut_video.py) creates individual video clips based on LLM recommendations
6. **File Packaging**: [`zip_and_download_files`](lib/download.py) bundles processed segments for download

### APIs Used

- **OpenAI Whisper API**: For speech-to-text transcription
- **OpenAI GPT-4**: For intelligent content analysis and editing decisions
- **MoviePy**: For video/audio processing and manipulation

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key with access to Whisper and GPT-4
- Sufficient storage space for temporary video processing
- FFmpeg (automatically handled by MoviePy)

## ⚙️ Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Getting Your OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key to your `.env` file
4. Ensure you have credits and access to both Whisper and GPT-4 models

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd video-editing-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Run the Streamlit application:
```bash
streamlit run main.py
```

5. Open your browser to `http://localhost:8501`

### Project Structure

```
video-editing-agent/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── .env.example          # Environment template
├── lib/
│   ├── convert.py        # Video-to-audio conversion
│   ├── transcribe.py     # Audio transcription with Whisper
│   ├── llm.py           # LLM processing for editing decisions
│   ├── cut_video.py     # Video segment cutting
│   └── download.py      # File packaging and download
├── temp/                 # Temporary processing files
├── exports/             # Processed video segments
└── .streamlit/
    └── config.toml      # Streamlit configuration
```

## 🎬 Usage

### Web Interface

1. **Start the application**:
```bash
streamlit run main.py
```

2. **Upload a video file**:
   - Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
   - Maximum file size: 10GB (configurable in .streamlit/config.toml)

3. **Enter your script** (optional):
   - Provide the intended script or talking points
   - The AI will match transcription against this script

4. **Click "Run"** to start processing:
   - Watch real-time progress updates
   - View processing metrics and results
   - Download the final edited segments

### Processing Steps

The interface shows progress through these stages:
- **File Upload**: Saving uploaded video to temporary storage
- **Audio Conversion**: Extracting audio track using [`convert_video_to_audio`](lib/convert.py)
- **Transcription**: Processing audio with [`transcribe_audio`](lib/transcribe.py)
- **LLM Analysis**: Analyzing content with [`process_transcription_with_llm`](lib/llm.py)
- **Video Cutting**: Creating segments with [`cut_video_segments`](lib/cut_video.py)
- **File Preparation**: Packaging downloads with [`zip_and_download_files`](lib/download.py)

## 🛠️ Configuration

### Streamlit Settings

Modify `.streamlit/config.toml` to adjust:
- Maximum upload file size
- Server port and browser settings
- Theme and UI customization
- Logging levels

### Video Processing Settings

The agent includes intelligent buffering and quality settings:
- **Audio Compression**: 64k bitrate, 22050 fps for efficient processing
- **Video Codec**: H.264 with AAC audio for compatibility
- **Segment Buffering**: Automatic 1-2 second padding for clean cuts
- **Export Quality**: Maintains original video quality in segments

## 🔍 Features in Detail

### Intelligent Editing

The [`VideoEdit`](lib/llm.py) model defines segments with:
- **Start/End timestamps**: Precise timing for video cuts
- **Script matching**: Links segments to intended content
- **Repetition removal**: Automatically selects best takes
- **Quality optimization**: Prefers later attempts over earlier ones

### File Management

- **Temporary Storage**: All processing files stored in `temp` directory
- **Export Organization**: Final segments saved to `exports` with descriptive names
- **Automatic Cleanup**: Temporary files managed automatically
- **Download Packaging**: ZIP archives for easy file transfer

## 🐛 Troubleshooting

### Common Issues

1. **Large File Uploads**: Adjust `maxUploadSize` in `.streamlit/config.toml`
2. **API Rate Limits**: Monitor OpenAI usage and implement delays if needed
3. **Audio Extraction Errors**: Ensure video files have valid audio tracks
4. **Memory Issues**: Process shorter videos or reduce audio quality settings

This project is only a prototype and may not cover all edge cases. User feedback is welcome for improvements.

### Debug Information

The application provides detailed logging:
- File size and format validation
- Audio extraction confirmation
- Transcription file creation
- LLM processing results
- Segment cutting progress

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with various video formats
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the console output for detailed error messages
- Verify your OpenAI API key has sufficient credits
- Ensure video files are in supported formats
- Review temporary file permissions

## 👨‍💻 Credits

Created by **Tom Shaw** - [https://github.com/IAmTomShaw](https://github.com/IAmTomShaw)

This project demonstrates the power of combining modern AI APIs with practical video editing workflows, making professional-quality video editing accessible through a simple web interface.