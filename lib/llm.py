import json
from openai import OpenAI
from agents import Agent, Runner
from pydantic import BaseModel

client = OpenAI()


class VideoEdit(BaseModel):
    start: int
    end: int
    targeted_script_snippet: str


async def process_transcription_with_llm(
    transcript_path: str, prompt: str, processed_result_path: str
) -> None:
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()

        transcript = json.loads(transcript)["words"] if transcript else {}

        agent = Agent(
            name="Video Editing Agent",
            model="gpt-5.1",
            output_type=list[VideoEdit],
        )

        result = await Runner.run(agent, prompt)

        # Handle different result structures
        if hasattr(result, "content") and result.content:
            output_data = result.content
        elif hasattr(result, "final_output") and result.final_output:
            output_data = result.final_output
        else:
            return

        # Save the result as JSON
        with open(processed_result_path, "w", encoding="utf-8") as f:
            # Convert VideoEdit objects to dict for JSON serialization
            if isinstance(output_data, list):
                json_data = [
                    edit.dict() if hasattr(edit, "dict") else edit
                    for edit in output_data
                ]
            else:
                json_data = output_data
            json.dump(json_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error processing transcript: {e}")
