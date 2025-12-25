import json
from openai import OpenAI
from pathlib import Path

client = OpenAI()


def transcribe_audio(audio_file_path: str) -> str:
    try:
        audio_file = open(audio_file_path, "rb")
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"],
        )

        # Save the transcription to a file
        transcription_file_path = Path(audio_file_path).with_suffix(".json")

        with transcription_file_path.open("w", encoding="utf-8") as f:
            json.dump(transcription.model_dump(), f, ensure_ascii=False, indent=2)

        return transcription_file_path

    except Exception as e:
        print(f"Error during transcription: {e}")
        raise
