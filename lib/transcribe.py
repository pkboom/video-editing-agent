import json
from openai import OpenAI
from pathlib import Path

client = OpenAI()

def transcribe_audio(audio_file_path: str) -> str:
    print(f'Transcribing audio file: {audio_file_path}')
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            res = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",  # Correct model name
                response_format="verbose_json",  # Use verbose JSON for detailed output
                language="en",  # Specify language if known
                prompt="Please transcribe all repeated words and sentences exactly as spoken, including duplicates.",  # Hint to include repetitions
                temperature=0.0,  # Lower temperature for more consistent output
                timestamp_granularities=["word"]
            )
        
        # Save the transcription to a file
        transcription_file_path = str(Path(audio_file_path).with_suffix('.json'))
        
        with open(transcription_file_path, 'w', encoding='utf-8') as f:
            # Convert the TranscriptionVerbose object to JSON
            json.dump(res.model_dump(), f, ensure_ascii=False, indent=2)
        
        return transcription_file_path
        
    except Exception as e:
        print(f'Error during transcription: {e}')
        raise

