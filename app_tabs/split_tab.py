import asyncio
import time
import traceback
from pathlib import Path

import streamlit as st
from moviepy import VideoFileClip


def render_split_tab() -> None:
    st.subheader("Cut Video By Timestamps")
    split_file = st.file_uploader(
        "Choose a video file",
        type=["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm"],
        key="split_video_file",
        help="Select the video you want to cut",
    )

    start_ts = st.text_input(
        "Start time (e.g., 00:01:30 or 90)",
        key="split_start_ts",
        help="When cutting by timestamps, this is the starting position",
    )
    end_ts = st.text_input(
        "End time (e.g., 00:02:45 or 165)",
        key="split_end_ts",
        help="When cutting by timestamps, this is the end position",
    )

    split_disabled = split_file is None

    if st.button(
        "🎯 Cut By Timestamps",
        disabled=split_disabled,
        help="Export a single clip between the provided start and end times",
        key="cut_video_run",
    ):
        if split_file is None:
            st.error("Please select a file first!")
            return

        try:
            start_seconds = parse_timestamp_to_seconds(start_ts)
            end_seconds = parse_timestamp_to_seconds(end_ts)
        except ValueError as parse_err:
            st.error(str(parse_err))
            return

        if end_seconds <= start_seconds:
            st.error("End time must be greater than start time.")
            return

        asyncio.run(cut_video_range(split_file, start_seconds, end_seconds))


def parse_timestamp_to_seconds(value: str) -> float:
    value = value.strip()
    if not value:
        raise ValueError("Please enter a time in seconds or HH:MM:SS format.")

    if value.isdigit() or _looks_like_float(value):
        return float(value)

    parts = value.split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError("Invalid time format; use seconds or HH:MM:SS.")

    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise ValueError("Invalid time format; use seconds or HH:MM:SS.")

    while len(parts) < 3:
        parts.insert(0, 0.0)

    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def _looks_like_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


async def cut_video_range(uploaded_file, start_seconds: float, end_seconds: float):
    """Cut a single clip between start and end times and offer it for download."""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    st.session_state.pop("cut_file_path", None)

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Saving uploaded file...")
    progress_bar.progress(0.1)

    temp_video_path = temp_dir / f"cut_{uploaded_file.name}"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    video_clip = None
    output_path = None

    try:
        status_text.text("Loading video and preparing cut...")
        progress_bar.progress(0.2)

        video_clip = VideoFileClip(str(temp_video_path))
        duration = video_clip.duration
        if duration <= 0:
            raise ValueError("The video has no duration.")

        if start_seconds < 0 or end_seconds > duration:
            raise ValueError("Start/end times must be within the video duration.")

        clip = video_clip.subclipped(start_seconds, end_seconds)

        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        run_dir = exports_dir / f"cuts_{temp_video_path.stem}_{int(time.time())}"
        run_dir.mkdir(parents=True, exist_ok=True)

        output_path = (
            run_dir
            / f"{temp_video_path.stem}_{int(start_seconds)}-{int(end_seconds)}.mp4"
        )

        def _write_segment(with_audio: bool) -> None:
            clip.write_videofile(
                str(output_path),
                codec="libx264",
                audio=with_audio,
                audio_codec="aac" if with_audio else None,
                temp_audiofile=str(temp_dir / "temp-audio.m4a") if with_audio else None,
                remove_temp=True,
                logger=None,
            )

        try:
            _write_segment(with_audio=True)
        except AttributeError as attr_err:
            if "stdout" in str(attr_err):
                st.warning(
                    "Audio track failed to process; exporting clip without audio."
                )
                _write_segment(with_audio=False)
            else:
                raise
        except Exception as write_err:
            if "stdout" in str(write_err):
                st.warning(
                    "Audio track failed to process; exporting clip without audio."
                )
                _write_segment(with_audio=False)
            else:
                raise
        finally:
            clip.close()

        status_text.text("Preparing download...")
        progress_bar.progress(0.9)

        st.session_state.cut_file_path = str(output_path)
        with open(output_path, "rb") as outf:
            data = outf.read()

        status_text.text("Cut completed successfully!")
        progress_bar.progress(1.0)
        st.success("✅ Clip exported successfully!")

        st.download_button(
            label="Download Cut Clip",
            data=data,
            file_name=output_path.name,
            mime="video/mp4",
            help="Click to download the cut clip",
        )

    except Exception as e:
        st.error(f"❌ Error cutting video: {str(e)}")
        trace_lines = traceback.format_exception(type(e), e, e.__traceback__)
        if hasattr(st, "code"):
            st.code("".join(trace_lines[:6]))

    finally:
        if video_clip is not None:
            video_clip.close()
