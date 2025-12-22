import asyncio
from pathlib import Path
import traceback

import streamlit as st

from lib.cut_video import cut_video_segments
from lib.download import zip_and_download_files
from lib.llm import process_transcription_with_llm


default_prompt = """Developer: # Role and Objective
You are a video editing specialist. Your primary responsibility is to select and extract compelling segments from a provided video transcription that are likely to arouse users' interests.

# Instructions
- Review the provided video transcription carefully.
- Identify and select segments that are likely to capture user interest or arouse curiosity.
- Extract sections suitable for creating engaging short video clips.

After selecting the clips, validate that each segment is within the specified duration and meets the engagement criteria before finalizing your output. If a clip does not fit, self-correct your selection.

## Clip Guidelines
- Each clip should be between 1 and 3 minutes in length.
- Focus on content that is ideal for social media sharing and designed to pique user interest.

# Context
- Input: Un-edited video transcription is provided.
- Output: Selected video snippets based on your extraction.

# Stop Conditions
- Hand back when you have identified all relevant segments fitting the criteria (1–3 minutes, engaging for users, social-ready, and likely to arouse user interest).
"""


def render_process_tab() -> None:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("File Selection")

        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"],
            help="Select a video file to process",
            key="process_video_file",
        )

        st.subheader("Script Input")
        user_prompt = st.text_area(
            "Enter your script:",
            value=default_prompt,
            height=500,
            help="Provide the script for video editing",
            key="process_video_script",
        )

        if uploaded_file is not None:
            st.success(f"File selected: {uploaded_file.name}")
            st.write(f"File size: {uploaded_file.size / (1024*1024):.2f} MB")
            st.write(f"File type: {uploaded_file.type}")
        else:
            st.info("Please select a video file to proceed.")

        if user_prompt.strip():
            st.success(f"Script provided: {len(user_prompt)} characters")
        else:
            st.info("Add a script or editing instructions above.")

    with col2:
        st.subheader("Actions")

        run_disabled = uploaded_file is None

        if st.button(
            "🚀 Run",
            disabled=run_disabled,
            help=(
                "Process the selected video file"
                if not run_disabled
                else "Please select a file first"
            ),
            key="process_video_run",
        ):
            if uploaded_file is not None:
                asyncio.run(process_video(uploaded_file, user_prompt))
            else:
                st.error("Please select a file first!")


async def process_video(uploaded_file, user_prompt: str):
    """Process the uploaded video file."""
    try:
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Saving uploaded file...")
        progress_bar.progress(0.1)

        temp_video_path = temp_dir / f"video_{uploaded_file.name}"
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        status_text.text("Converting video to audio...")
        progress_bar.progress(0.2)

        audio_file_path = temp_dir / "audio.wav"
        # convert_video_to_audio(temp_video_path, audio_file_path)

        # # Debug: Check if audio file was created
        # if audio_file_path.exists():
        #     st.success(f"✅ Audio file created: {audio_file_path}")
        #     st.write(f"Audio file size: {audio_file_path.stat().st_size / 1024:.2f} KB")
        # else:
        #     st.error("❌ Audio file was not created")

        progress_bar.progress(0.1)
        status_text.text("Transcribing audio...")

        # temporary
        transcription_file_path = str(Path(audio_file_path).with_suffix(".json"))

        # transcription_file_path = transcribe_audio(audio_file_path)

        # # Debug: Check if transcription file was created
        # if Path(transcription_file_path).exists():
        #     st.success(f"✅ Transcription file created: {transcription_file_path}")
        #     st.write(
        #         f"Transcription file size: {Path(transcription_file_path).stat().st_size / 1024:.2f} KB"
        #     )
        # else:
        #     st.error("❌ Transcription file was not created")

        progress_bar.progress(0.4)
        status_text.text("Processing transcription with LLM...")

        processed_res = await process_transcription_with_llm(
            transcription_file_path, user_prompt
        )

        status_text.text("Cutting video segments...")
        progress_bar.progress(0.6)

        await cut_video_segments(temp_video_path, processed_res)

        progress_bar.progress(0.9)
        status_text.text("Preparing files for download...")

        zip_file_path = await zip_and_download_files("exports", temp_dir)

        st.session_state.zip_file_path = zip_file_path

        status_text.text("Processing completed successfully!")
        progress_bar.progress(1.0)

        st.success("✅ Video processing completed successfully!")
        st.subheader("📊 Processing Results")

        if "zip_file_path" in st.session_state and st.session_state.zip_file_path:
            with open(st.session_state.zip_file_path, "rb") as zip_file:
                zip_data = zip_file.read()

            st.download_button(
                label="Download Processed Files",
                data=zip_data,
                file_name="processed_files.zip",
                mime="application/zip",
                help="Click to download the processed video files",
            )
        else:
            st.warning("No processed files available for download yet.")

    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        trace_lines = traceback.format_exception(type(e), e, e.__traceback__)
        if hasattr(st, "code"):
            st.code("".join(trace_lines[:6]))
