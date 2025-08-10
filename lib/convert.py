import moviepy as mp

def convert_video_to_audio(video_file_path: str, output_audio_path: str) -> None:

  """Convert video file to audio file using moviepy"""
  video_clip = mp.VideoFileClip(video_file_path)
  audio_clip = video_clip.audio

  print('audio_clip:', audio_clip)

  if audio_clip is None:
    raise ValueError("The video file does not contain an audio track.")
  
  # Compress the audio to reduce file size for Whisper transcription

  audio_clip.write_audiofile(
    output_audio_path,
    bitrate="64k",
    fps=22050,
    codec='mp3'
  )
  
  audio_clip.close()
  video_clip.close()
  return