from pydub import AudioSegment
import io

def load_audio(uploaded_file):
    """Load an MP3 file from a Streamlit UploadedFile object and return AudioSegment and WAV bytes."""
    # Ensure mono and standard sample rate for consistency
    audio = AudioSegment.from_file(uploaded_file, format="mp3").set_channels(1).set_frame_rate(44100)
    wav_bytes = export_wav(audio)
    return audio, wav_bytes

def export_wav(audio):
    """Export an AudioSegment to WAV bytes."""
    if audio is None:
        return None
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    buf.seek(0)
    return buf

def slice_audio(audio, start_ms, end_ms):
    """Slice the audio between start_ms and end_ms (milliseconds)."""
    # Clamp values to valid range
    start_ms = max(0, start_ms)
    end_ms = min(len(audio), end_ms)
    if start_ms >= end_ms:
        return audio[0:0]  # Return empty audio segment
    return audio[start_ms:end_ms]

def get_audio_length(audio):
    """Return audio length as a formatted string (HH:MM:SS.mmm)."""
    if audio is None:
        return "N/A"
    total_ms = len(audio)
    hours = int(total_ms // (3600 * 1000))
    minutes = int((total_ms % (3600 * 1000)) // (60 * 1000))
    seconds = int((total_ms % (60 * 1000)) // 1000)
    milliseconds = int(total_ms % 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"