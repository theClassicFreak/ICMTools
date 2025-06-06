import parselmouth
import numpy as np
from scipy.signal import medfilt

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SWARA_MAP = {
    0: "Sa", 1: "re", 2: "Re", 3: "ga", 4: "Ga", 5: "ma", 6: "Ma",
    7: "Pa", 8: "dha", 9: "Dha", 10: "ni", 11: "Ni",
}

def note_to_swara(freq, semitone_shift=0):
    """Convert frequency to swara name, applying semitone shift."""
    if freq <= 0:
        return None
    midi_num = 69 + 12 * np.log2(freq / 440.0)
    midi_num += semitone_shift
    index = int(round(midi_num)) % 12
    return SWARA_MAP.get(index)

def transcribe_audio(
    audio,
    semitone_shift=0,
    min_note_duration=0.05,  # seconds
    pitch_floor=75,
    pitch_ceiling=1000,
    time_step=0.01
):
    """
    Transcribe the audio segment to swara and return a list of rows.
    Each row: (timestamp, frequency, swara, duration, count)
    """
    import tempfile
    import os

    # Export audio to a temporary wav file for parselmouth
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        audio.export(temp_wav_file, format="wav")
        wav_path = temp_wav_file.name

    try:
        snd = parselmouth.Sound(wav_path)
        pitch = snd.to_pitch(time_step=time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
        times = pitch.xs()
        frequencies = pitch.selected_array["frequency"]

        # Median filter to smooth pitch
        if len(frequencies) >= 5:
            frequencies = medfilt(frequencies, kernel_size=5)

        transcription_data = []
        prev_swara = None
        count = 0
        start_time = times[0] if len(times) > 0 else 0
        last_freq = 0
        for t, freq in zip(times, frequencies):
            swara = note_to_swara(freq, semitone_shift)
            if swara != prev_swara:
                if prev_swara and count > 0:
                    end_time = t
                    duration = end_time - start_time
                    if duration >= min_note_duration:
                        timestamp = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02}.{int((start_time%1)*1000):03}"
                        transcription_data.append(
                            (
                                timestamp,
                                f"{last_freq:.2f}",
                                prev_swara,
                                f"{duration:.3f}s",
                                count,
                            )
                        )
                prev_swara = swara
                start_time = t
                count = 1
            else:
                count += 1
                last_freq = freq
        # Add the last note
        if prev_swara and count > 0:
            end_time = times[-1]
            duration = end_time - start_time
            if duration >= min_note_duration:
                timestamp = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02}.{int((start_time%1)*1000):03}"
                transcription_data.append(
                    (
                        timestamp,
                        f"{last_freq:.2f}",
                        prev_swara,
                        f"{duration:.3f}s",
                        count,
                    )
                )
        return transcription_data
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)