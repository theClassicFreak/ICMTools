from pydub import AudioSegment
import io

def load_audio(uploaded_file):
    """Load an MP3 file from a Streamlit UploadedFile object."""
    # Save to a temporary file for pydub compatibility
    audio = AudioSegment.from_file(uploaded_file, format="mp3").set_channels(1).set_frame_rate(44100)
    # Export to wav bytes for playback
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
    return audio[start_ms:end_ms]

def get_audio_length(audio):
    """Return audio length as a formatted string."""
    if audio is None:
        return "N/A"
    total_ms = len(audio)
    hours = int(total_ms // (3600 * 1000))
    minutes = int((total_ms % (3600 * 1000)) // (60 * 1000))
    seconds = int((total_ms % (60 * 1000)) // 1000)
    milliseconds = int(total_ms % 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"