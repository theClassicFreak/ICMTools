import librosa
import numpy as np
import math
import os

# Global mapping for Western notes to MIDI
western_notes_to_midi = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
    'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

# Function to map the detected pitch to Sargam notation based on the root pitch
def get_sargam_notation(root_pitch, detected_pitch, root_midi):
    sargam_notes = ['S', 'r', 'R', 'g', 'G', 'm', 'M', 'P', 'd', 'D', 'n', 'N']
    
    if '♯' in detected_pitch:
        detected_pitch = detected_pitch.replace('♯', '#')

    try:
        detected_midi = western_notes_to_midi[detected_pitch[:-1]] + (12 * (int(detected_pitch[-1]) - 1)) if len(detected_pitch) > 1 else western_notes_to_midi[detected_pitch]
    except KeyError:
        print(f"Warning: Pitch {detected_pitch} not found in mapping.")
        return None

    semitone_diff = (detected_midi - root_midi) % 12
    return sargam_notes[semitone_diff] if semitone_diff < len(sargam_notes) else None

# Function to process the audio, detect pitch, and return pitch data
def process_audio_for_transcription(audio_path, root_pitch='C', hop_length=512, frame_length=2048):
    y, sr = librosa.load(audio_path)
    fmin = librosa.note_to_hz('C1')
    fmax = librosa.note_to_hz('B8')
    
    # Detect pitch using librosa.pyin with custom hop_length and frame_length
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax, hop_length=hop_length, frame_length=frame_length)

    # Calculate root pitch MIDI value
    root_midi = western_notes_to_midi.get(root_pitch, None)
    if root_midi is None:
        raise ValueError(f"Invalid root pitch: {root_pitch}. Please enter a valid pitch.")
    
    # Normalize pitch names to Western notes
    normalized_pitch_names = [librosa.hz_to_note(f) if f is not None and not math.isnan(f) else None for f in f0]
    
    return y, sr, f0, normalized_pitch_names, root_midi

# Function to save repeated notes transitions summary to text file
def save_repeated_notes_transitions_to_text(start_time, end_time, f0, normalized_pitch_names, root_pitch, sr, y):
    transcription_filename = f"transcription_{root_pitch}_{start_time:.2f}_{end_time:.2f}.txt"
    
    last_pitch = None
    count = 0
    summary = []
    last_timestamp = start_time
    line = []

    # Loop through the pitch data and track repeated notes
    for timestamp, pitch, frequency in zip(librosa.times_like(f0), normalized_pitch_names, f0):
        if pitch is not None and start_time <= timestamp <= end_time:
            sargam = get_sargam_notation(root_pitch, pitch, root_midi)
            if sargam:
                if sargam == last_pitch:
                    count += 1  # Increment count for repeated note
                else:
                    if last_pitch and count > 1:  # Only add repeated notes if count > 1
                        if len(line) == 10:
                            summary.append(" -> ".join(line))
                            line = []
                        line.append(f"{last_pitch}({count}) @ {last_timestamp:.2f}s")
                    last_pitch = sargam
                    count = 1
                    last_timestamp = timestamp  # Update to new timestamp
    
    # Add the last note if it falls within the time range or just before the end of the file
    if last_pitch and count > 1 and last_timestamp <= end_time:
        if len(line) == 10:
            summary.append(" -> ".join(line))
            line = []
        line.append(f"{last_pitch}({count}) @ {last_timestamp:.2f}s")
    
    # Add any remaining notes in the line to summary
    if line:
        summary.append(" -> ".join(line))

    # Write the summary to the text file
    with open(transcription_filename, "w", encoding="utf-8") as f:
        f.write("Summary (repeated notes grouped):\n")
        f.write("\n".join(summary))
    
    print(f"Repeated notes transitions saved to {transcription_filename}")

# Function to prompt the user for start and end timestamps and perform transcriptions
def prompt_for_transcriptions(f0, normalized_pitch_names, root_pitch, sr, y):
    # Get the total duration of the audio file
    total_duration = librosa.get_duration(y=y, sr=sr)
    print(f"\nThe total duration of the file is {total_duration:.2f} seconds.")
    
    while True:
        try:
            start_time = float(input(f"Enter start time (seconds) [0.00 - {total_duration:.2f}]: "))
            end_time = float(input(f"Enter end time (seconds) [{start_time:.2f} - {total_duration:.2f}]: "))

            if start_time >= end_time or start_time < 0 or end_time > total_duration:
                print(f"Invalid input. Please enter valid start and end times within the file duration.")
                continue

            # Save transcription with specific timestamp range
            save_repeated_notes_transitions_to_text(start_time, end_time, f0, normalized_pitch_names, root_pitch, sr, y)

        except ValueError:
            print("Invalid input. Please enter valid numerical values for start and end time.")
            continue

        # Ask user whether to continue or cancel
        user_input = input("Do you want to perform another transcription? (yes/cancel): ").strip().lower()
        if user_input == 'cancel':
            print("Cancelling transcription.")
            break
        elif user_input != 'yes':
            print("Invalid input, cancelling.")
            break

# Main execution
if __name__ == "__main__":
    audio_path = './AudioSource/sourcefile.mp3'  # Replace with your audio file path
    root_pitch = input("Enter the root pitch note (e.g., C, D#, G): ").strip()
    
    try:
        # Set hop_length and frame_length based on desired time resolution
        hop_length = int(input("Enter hop length (default is 512): ") or 512)  # Default to 512 if not specified
        frame_length = int(input("Enter frame length (default is 2048): ") or 2048)  # Default to 2048 if not specified
        
        # Process audio and get pitch information
        y, sr, f0, normalized_pitch_names, root_midi = process_audio_for_transcription(audio_path, root_pitch, hop_length, frame_length)
    
        # Ask for start and end time ranges, and perform transcriptions
        prompt_for_transcriptions(f0, normalized_pitch_names, root_pitch, sr, y)

    except ValueError as e:
        print(e)
