import json
from openai import OpenAI
from agents import Agent, Runner
from pydantic import BaseModel

client = OpenAI()

class VideoEdit(BaseModel):
    start: int
    end: int
    targeted_script_snippet: str

async def process_transcription_with_llm(transcript_path: str, script: str) -> dict:
    try:

        # Get the transcription content from the file

        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()

        transcript = json.loads(transcript)['words'] if transcript else {}

        print(f"Transcription content loaded from {transcript_path}")
        # Process the transcript with the LLM

        agent = Agent(
            name="Video Editing Agent",
            instructions=f"""
            <background>
            You are a video editing agent. You are responsible for selecting and extracting snippets from a piece of un-edited video footage. When filming, the subject will often mess up or stutter which means that they need to repeat certain sections of the script. Your job is to identify the best bits of their talking that would be used in the final version of the edited video.
            </background>
            <task>
            You will receive a transcription of a video and a script. Your task is to identify the snippets of speech in the transcript that should be used in the final edit of the video. If the subject has attempted to say their lines multiple times, you should only select one version of the line they have attempted to say. Do not return multiple copies of the same line. Usually I'd recommend to return the last attempt of the line as this is usually the best. The lines that you return should be the ones that are most relevant to the script provided. The subject may repeat themselves in quick succession, so you should be careful to not return the same line multiple times.
            </task>
            <output>
            You will return a JSON object that will contain the segments that will be taken from the original video clip to create the final edited version. Each segment that you output should not have the same script snippet being repeated. The output numbers should be in seconds. You should add a 1 second buffer to the start and end of each segment to ensure that the cuts are clean, unless the end of the video is reached.
            </output>
            """,
            tools=[],
            model="gpt-4o",
            output_type=list[VideoEdit]
        )

        user_prompt = f"""
        <script>
        {script}
        </script>
        <video_transcription>
        {transcript}
        </video_transcription>
        """

        result = await Runner.run(agent, user_prompt)

        # Handle different result structures
        if hasattr(result, 'content') and result.content:
            output_data = result.content
        elif hasattr(result, 'final_output') and result.final_output:
            output_data = result.final_output
        else:
            return []

        # Save the result as JSON
        with open("temp/processed_result.json", "w", encoding="utf-8") as f:
            # Convert VideoEdit objects to dict for JSON serialization
            if isinstance(output_data, list):
                json_data = [edit.dict() if hasattr(edit, 'dict') else edit for edit in output_data]
            else:
                json_data = output_data
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        return output_data

    except Exception as e:
        print(f"Error processing transcript: {e}")