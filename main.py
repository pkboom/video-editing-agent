import streamlit as st
import os
import asyncio
from pathlib import Path
from lib.convert import convert_video_to_audio
from lib.transcribe import transcribe_audio
from lib.llm import process_transcription_with_llm
from lib.cut_video import cut_video_segments
from lib.download import zip_and_download_files

# Set page config
st.set_page_config(page_title="Video Editing Agent", page_icon="🎬", layout="wide")


def main():
    st.title("🎬 Video Editing Agent")
    st.write("Select a video file and click 'Run' to process it.")

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("File Selection")

        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"],
            help="Select a video file to process",
        )

        # Text script input
        st.subheader("Script Input")
        user_script = st.text_area(
            "Enter your script:",
            height=150,
            placeholder="Enter your script here...",
            help="Provide the script for video editing",
        )

        # Display file information if a file is selected
        if uploaded_file is not None:
            st.success(f"File selected: {uploaded_file.name}")
            st.write(f"File size: {uploaded_file.size / (1024*1024):.2f} MB")
            st.write(f"File type: {uploaded_file.type}")
        else:
            st.info("Please select a video file to proceed.")

        # Display script info if provided
        if user_script.strip():
            st.success(f"Script provided: {len(user_script)} characters")
        else:
            st.info("Add a script or editing instructions above.")

    with col2:
        st.subheader("Actions")

        # Run button
        run_disabled = uploaded_file is None

        if st.button(
            "🚀 Run",
            disabled=run_disabled,
            help=(
                "Process the selected video file"
                if not run_disabled
                else "Please select a file first"
            ),
        ):
            if uploaded_file is not None:
                asyncio.run(process_video(uploaded_file, user_script))
            else:
                st.error("Please select a file first!")


async def process_video(uploaded_file, user_script: str):
    """Process the uploaded video file"""
    try:
        # Create a temp directory
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Save uploaded file to temporary location
        status_text.text("Saving uploaded file...")
        progress_bar.progress(0.1)

        temp_video_path = temp_dir / f"video_{uploaded_file.name}"
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert to audio
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

        # Update progress
        progress_bar.progress(0.1)
        status_text.text("Transcribing audio...")

        # Transcribe video using API

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

        # Update progress
        progress_bar.progress(0.4)
        status_text.text("Processing transcription with LLM...")

        # Send transcript with timestamps to LLM for processing

        processed_res = await process_transcription_with_llm(
            transcription_file_path, user_script
        )

        print(f"Processed Result: {processed_res}")

        # Update progress
        status_text.text("Cutting video segments...")
        progress_bar.progress(0.6)

        await cut_video_segments(temp_video_path, processed_res)

        # Update final progress
        progress_bar.progress(0.9)

        status_text.text("Preparing files for download...")

        # Zip the processed files and make them available for download

        zip_file_path = await zip_and_download_files("exports", temp_dir)

        print(f"Zip file created: {zip_file_path}")

        # Set the zip file path as a global variable for download button
        st.session_state.zip_file_path = zip_file_path

        status_text.text("Processing completed successfully!")
        progress_bar.progress(1.0)

        # Success message
        st.success("✅ Video processing completed successfully!")

        # Display results section
        st.subheader("📊 Processing Results")

        # Add download button
        if "zip_file_path" in st.session_state and st.session_state.zip_file_path:
            # Read the zip file data
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
        st.write("Please check the file format and try again.")


if __name__ == "__main__":
    main()
