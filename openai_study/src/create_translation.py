from openai import OpenAI
from pathlib import Path
client = OpenAI()

audio_path = Path(__file__).parent.parent / "output.wav"

audio_file = open(audio_path, "rb")
transcript = client.audio.translations.create(
  model="whisper-1",
  file=audio_file
)

print(transcript.text)