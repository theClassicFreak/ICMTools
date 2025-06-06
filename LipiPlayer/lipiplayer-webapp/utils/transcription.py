import parselmouth
import numpy as np

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SOLFEGE_MAP = {
    0: "S", 1: "r", 2: "R", 3: "g", 4: "G", 5: "M", 6: "m",
    7: "P", 8: "d", 9: "D", 10: "n", 11: "N",
}

def note_to_solfege(freq, root_note):
    if freq <= 0:
        return None
    midi_num = int(round(69 + 12 * np.log2(freq / 440.0)))
    index = (midi_num - NOTE_NAMES.index(root_note)) % 12
    return SOLFEGE_MAP.get(index)

def transcribe_audio(audio, root_note):
    """Transcribe the audio segment to solfege and return a list of rows."""
    import tempfile
    import os

    # Export audio to a temporary wav file for parselmouth
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        audio.export(temp_wav_file, format="wav")
        wav_path = temp_wav_file.name

    try:
        snd = parselmouth.Sound(wav_path)
        pitch = snd.to_pitch(time_step=0.001, pitch_floor=75, pitch_ceiling=1000)
        times = pitch.xs()
        frequencies = pitch.selected_array["frequency"]
        transcription_data = []
        prev_solfege = None
        count = 0
        start_time = times[0] if len(times) > 0 else 0
        for t, freq in zip(times, frequencies):
            solfege = note_to_solfege(freq, root_note)
            if solfege != prev_solfege:
                if prev_solfege:
                    end_time = t
                    duration = end_time - start_time
                    timestamp = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02}.{int((start_time%1)*1000):03}"
                    transcription_data.append(
                        (
                            timestamp,
                            f"{last_freq:.2f}",
                            prev_solfege,
                            f"{duration:.3f}s",
                            count,
                        )
                    )
                prev_solfege = solfege
                start_time = t
                count = 1
            else:
                count += 1
                last_freq = freq
        return transcription_data
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)