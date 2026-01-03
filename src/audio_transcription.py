import os
import tempfile
import subprocess
import whisper

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
    model = whisper.load_model("tiny") 
    result = model.transcribe(audio_path, language="pt")
    return result["text"]