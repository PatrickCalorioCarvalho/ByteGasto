import os
import tempfile
import subprocess
import whisper

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
WHISPER_MODEL_DIR = os.getenv("WHISPER_MODEL_DIR", "./models/whisper")

whisper_model = whisper.load_model(
    WHISPER_MODEL_SIZE,
    download_root=WHISPER_MODEL_DIR
)

def preprocess_audio(input_path):
    output_path = input_path.replace('.oga', '_clean.wav')
    command = [
        'ffmpeg', '-y', '-i', input_path,
        '-ac', '1',
        '-ar', '16000',
        '-af', 'loudnorm',
        output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def transcribe_audio_with_whisper(audio_path):
    result = whisper_model.transcribe(audio_path, language="pt")
    return result["text"]