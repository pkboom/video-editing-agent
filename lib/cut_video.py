from moviepy import VideoFileClip, concatenate_videoclips
import json

from pathlib import Path


async def cut_video_segments(video_path: str, processed_result_path: str) -> None:
    with open(processed_result_path, "r") as f:
        actual_edits = json.loads(f.read())

    """Cut video segments based on the provided edits."""

    try:
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)

        video_clip = VideoFileClip(video_path)

        print(actual_edits[0]["start"])

        sorted_edits = sorted(actual_edits, key=lambda x: x["start"])

        clips_to_keep = []
        exported_files = []

        for i, edit in enumerate(sorted_edits):
            start_time = edit["start"]
            end_time = edit["end"]

            # If start time is greater than 2, reduce it to 2 seconds otherwise set to 0
            if start_time > 2:
                start_time -= 2
            else:
                start_time = 0

            # If end time is within 2 seconds of the video duration, set it to the video duration otherwise increase it by 2 seconds
            if end_time < video_clip.duration - 2:
                end_time += 2
            else:
                end_time = video_clip.duration

            # Ensure times are within bounds
            if start_time < 0:
                start_time = 0
            if end_time > video_clip.duration:
                end_time = video_clip.duration

            # Keep this segment
            if start_time < end_time:
                segment = video_clip.subclipped(start_time, end_time)
                clips_to_keep.append(segment)

                # Export individual segment with audio
                segment_filename = (
                    f"segment_{i+1:03d}_{start_time:.1f}s-{end_time:.1f}s.mp4"
                )
                segment_path = exports_dir / segment_filename
                segment.write_videofile(
                    str(segment_path),
                    codec="libx264",
                    audio_codec="aac",  # Ensure audio codec is specified
                    temp_audiofile="temp/temp-audio.m4a",  # Temporary audio file
                    remove_temp=True,  # Clean up temp files
                )
                exported_files.append(str(segment_path))

        # Concatenate the clips to keep for the main output
        # if clips_to_keep:
        #     final_clip = concatenate_videoclips(clips_to_keep)
        # else:
        #     final_clip = video_clip

        # # Save the concatenated edited video
        # output_path = str(video_path).replace(".mp4", "_edited.mp4")
        # final_clip.write_videofile(
        #     output_path,
        #     codec="libx264",
        #     audio_codec="aac",
        #     temp_audiofile="temp/temp-audio.m4a",
        #     remove_temp=True,
        # )

    except Exception as e:
        print(f"Error cutting video segments: {e}")
        raise
