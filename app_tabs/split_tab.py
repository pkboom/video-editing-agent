import asyncio
import time
import traceback
from pathlib import Path

import streamlit as st
from moviepy import VideoFileClip

from lib.download import zip_and_download_files


def render_split_tab() -> None:
    st.subheader("Split Video Evenly")
    split_file = st.file_uploader(
        "Choose a video file to split",
        type=["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"],
        key="split_video_file",
        help="Select the video you want to break into equal parts",
    )

    num_parts = st.number_input(
        "Number of segments",
        min_value=2,
        max_value=20,
        value=2,
        step=1,
        help="Choose how many equal parts to create",
    )

    split_disabled = split_file is None

    if st.button(
        "✂️ Split Video",
        disabled=split_disabled,
        help="Split the selected video into equal parts",
        key="split_video_run",
    ):
        if split_file is not None:
            asyncio.run(split_video(split_file, int(num_parts)))
        else:
            st.error("Please select a file first!")


async def split_video(uploaded_file, num_parts: int):
    """Split the uploaded video into equal parts and prepare a download."""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    st.session_state.pop("split_zip_file_path", None)

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Saving uploaded file...")
    progress_bar.progress(0.1)

    temp_video_path = temp_dir / f"split_{uploaded_file.name}"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    video_clip = None
    run_dir = None

    try:
        status_text.text("Splitting video into equal parts...")
        progress_bar.progress(0.2)

        video_clip = VideoFileClip(str(temp_video_path))
        duration = video_clip.duration
        if duration <= 0:
            raise ValueError("The video has no duration.")

        segment_duration = duration / num_parts

        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        run_dir = exports_dir / f"splits_{temp_video_path.stem}_{int(time.time())}"
        run_dir.mkdir(parents=True, exist_ok=True)

        for idx in range(num_parts):
            start_time = idx * segment_duration
            end_time = (
                duration if idx == num_parts - 1 else (idx + 1) * segment_duration
            )

            if start_time >= end_time:
                continue

            clip = video_clip.subclipped(start_time, end_time)
            segment_path = run_dir / f"{temp_video_path.stem}_part_{idx + 1:02d}.mp4"
            clip.write_videofile(
                str(segment_path),
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(temp_dir / "temp-audio.m4a"),
                remove_temp=True,
                logger=None,
            )
            clip.close()

            progress_bar.progress(0.2 + 0.6 * ((idx + 1) / num_parts))

        status_text.text("Preparing files for download...")
        progress_bar.progress(0.85)

        if run_dir is None:
            raise ValueError("No split output directory was created.")

        zip_file_path = await zip_and_download_files(str(run_dir), str(temp_dir))
        st.session_state.split_zip_file_path = zip_file_path

        status_text.text("Split completed successfully!")
        progress_bar.progress(1.0)
        st.success("✅ Video split completed successfully!")

        if st.session_state.split_zip_file_path:
            with open(st.session_state.split_zip_file_path, "rb") as zip_file:
                zip_data = zip_file.read()

            st.download_button(
                label="Download Split Files",
                data=zip_data,
                file_name="split_files.zip",
                mime="application/zip",
                help="Click to download the split video files",
            )
        else:
            st.warning("No split files available for download yet.")

    except Exception as e:
        st.error(f"❌ Error splitting video: {str(e)}")
        trace_lines = traceback.format_exception(type(e), e, e.__traceback__)
        st.code("".join(trace_lines[:6]))

    finally:
        if video_clip is not None:
            video_clip.close()
