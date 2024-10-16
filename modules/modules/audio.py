from pydub import AudioSegment
import os

def convert_audio(input_path, output_path, format="wav"):
    """
    Convert audio to a different format.
    """
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format=format)
        print(f"Audio converted and saved at {output_path}")
    except Exception as e:
        print(f"Error converting audio: {e}")

def change_volume(input_path, output_path, increase_db):
    """
    Change the volume of an audio file.
    """
    try:
        audio = AudioSegment.from_file(input_path)
        louder_audio = audio + increase_db  # Increase volume by specified dB
        louder_audio.export(output_path, format="wav")
        print(f"Volume changed and saved at {output_path}")
    except Exception as e:
        print(f"Error changing audio volume: {e}")

def trim_audio(input_path, output_path, start_ms, end_ms):
    """
    Trim an audio file between start and end time (in milliseconds).
    """
    try:
        audio = AudioSegment.from_file(input_path)
        trimmed_audio = audio[start_ms:end_ms]
        trimmed_audio.export(output_path, format="wav")
        print(f"Trimmed audio saved at {output_path}")
    except Exception as e:
        print(f"Error trimming audio: {e}")
