# import librosa
# import numpy as np
# import matplotlib.pyplot as plt
# import librosa.display
# import math

# # Load the audio file
# audio_path = './AudioSource/madhumalati.mp3'  # Replace with your audio file path
# y, sr = librosa.load(audio_path)

# # Set parameters for pitch detection
# fmin = librosa.note_to_hz('C1')  # Min frequency for pitch detection
# fmax = librosa.note_to_hz('B8')  # Max frequency for pitch detection

# # List of musical notes (C1 to B8)
# notes = [
#     'C1', 'C#1', 'D1', 'D#1', 'E1', 'F1', 'F#1', 'G1', 'G#1', 'A1', 'A#1', 'B1',
#     'C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2',
#     'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
#     'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
#     'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
#     'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',
#     'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7', 'A7', 'A#7', 'B7',
#     'C8', 'C#8', 'D8', 'D#8', 'E8', 'F8', 'F#8', 'G8', 'G#8', 'A8', 'A#8', 'B8'
# ]

# # Using librosa.pyin to detect pitch across the entire audio
# f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax)

# # Generate the list of pitch names for each frame, ignoring NaN values
# pitch_names = [
#     librosa.hz_to_note(f) if f is not None and not math.isnan(f) else None
#     for f in f0
# ]

# # Normalize pitch names (replace sharp symbols for consistency)
# normalized_pitch_names = [
#     pitch_name.replace('♯', '#') if pitch_name else None  # Replace ♯ with #
#     for pitch_name in pitch_names
# ]

# # Open transcription.txt for writing with UTF-8 encoding
# with open("transcription.txt", "w", encoding="utf-8") as f:
#     # Write header to file
#     f.write("Timestamp (s) - Pitch (Note) - Frequency (Hz)\n")
    
#     # Iterate through the pitch values and write the nearest pitch name, frequency, and timestamp
#     for idx, (pitch, timestamp) in enumerate(zip(f0, librosa.times_like(f0))):
#         if pitch is not None and not math.isnan(pitch):
#             pitch_name = librosa.hz_to_note(pitch)
#             if pitch_name is not None:  # Ensure pitch name is valid
#                 pitch_name = pitch_name.replace('♯', '#')  # Normalize sharp symbols
#                 f.write(f"{timestamp:.2f}s - Pitch: {pitch_name} ({pitch:.2f} Hz)\n")

# # Map pitch names to numeric values for plotting
# pitch_name_to_num = {note: idx for idx, note in enumerate(notes)}
# numeric_pitches = [
#     pitch_name_to_num[n] if n is not None else np.nan
#     for n in normalized_pitch_names
# ]

# # Plot pitch over time with pitch names on the Y-axis
# plt.figure(figsize=(10, 6))
# librosa.display.waveshow(y, sr=sr, alpha=0.5)
# plt.plot(librosa.times_like(f0), numeric_pitches, label='Pitch (fundamental frequency)', color='r')
# plt.yticks(np.arange(len(notes)), notes)
# plt.xlabel('Time (s)')
# plt.ylabel('Pitch (Note)')
# plt.title('Pitch Detection using librosa')
# plt.legend()
# plt.show()

#--------------------------------------------------------------------------#

# import librosa
# import numpy as np
# import math
# import csv

# # Function to process the audio, detect pitch, and save transcription to a CSV file
# def process_audio_for_transcription(audio_path, transcription_file='transcription.csv'):
#     # Load the audio file
#     y, sr = librosa.load(audio_path)

#     # Set parameters for pitch detection
#     fmin = librosa.note_to_hz('C1')  # Min frequency for pitch detection
#     fmax = librosa.note_to_hz('B8')  # Max frequency for pitch detection

#     # Using librosa.pyin to detect pitch across the entire audio
#     f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax)

#     # Generate the list of pitch names for each frame, ignoring NaN values
#     pitch_names = [
#         librosa.hz_to_note(f) if f is not None and not math.isnan(f) else None
#         for f in f0
#     ]

#     # Normalize pitch names (replace sharp symbols for consistency)
#     normalized_pitch_names = [
#         pitch_name.replace('♯', '#') if pitch_name else None  # Replace ♯ with #
#         for pitch_name in pitch_names
#     ]

#     # Write transcription to CSV file
#     with open(transcription_file, "w", newline='', encoding="utf-8") as f:
#         writer = csv.writer(f)
#         # Write CSV header
#         writer.writerow(['Timestamp (s)', 'Pitch (Note)', 'Frequency (Hz)'])
        
#         # Write each pitch and timestamp to CSV
#         for timestamp, pitch, frequency in zip(librosa.times_like(f0), normalized_pitch_names, f0):
#             if pitch is not None:  # Only write when pitch is detected
#                 writer.writerow([timestamp, pitch, frequency])

#     print(f"Transcription saved to {transcription_file}")

# # Function to read the transcription CSV and print notes played within the given time range
# def print_notes_in_range(transcription_file='transcription.csv', start_time=0, end_time=float('inf')):
#     # Check if the transcription file exists and is non-empty
#     try:
#         with open(transcription_file, "r", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             header = next(reader)  # Skip the header row
            
#             # Flag to track if any notes are printed
#             notes_found = False
            
#             # Read and print notes within the time range
#             for row in reader:
#                 timestamp, pitch, frequency = float(row[0]), row[1], float(row[2])
                
#                 # Check if the timestamp is within the given range
#                 if start_time <= timestamp <= end_time:
#                     print(f"{timestamp:.2f}s - Pitch: {pitch} ({frequency:.2f} Hz)")
#                     notes_found = True
            
#             if not notes_found:
#                 print(f"No notes found in the time range {start_time}s to {end_time}s.")
#     except FileNotFoundError:
#         print(f"Error: The file {transcription_file} does not exist.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Main execution
# if __name__ == "__main__":
#     audio_path = './AudioSource/madhumalati.mp3'  # Replace with your audio file path
    
#     # Step 1: Process the audio for transcription and save to CSV
#     process_audio_for_transcription(audio_path, 'transcription.csv')

#     # Step 2: Ask for time range and print notes
#     start_time = float(input("Enter start time (seconds): "))
#     end_time = float(input("Enter end time (seconds): "))
    
#     print(f"\nNotes played between {start_time}s and {end_time}s:")
#     print_notes_in_range('transcription.csv', start_time, end_time)

#--------------------------------------------------------------------------#

import librosa
import numpy as np
import math
import csv

# Function to map the detected pitch to Sargam notation based on the root pitch
def get_sargam_notation(root_pitch, detected_pitch, root_midi):
    # Define the semitone mapping of the Western notes to Sargam notation
    sargam_notes = ['S', 'r', 'R', 'g', 'G', 'm', 'M', 'P', 'd', 'D', 'n', 'N']
    
    # Map Western notes (C, C#, D, D#, ..., B) to MIDI note numbers
    western_notes_to_midi = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
        'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }
    
    # Ensure the detected pitch does not contain special symbols like ♯
    if '♯' in detected_pitch:
        detected_pitch = detected_pitch.replace('♯', '#')  # Convert ♯ to sharp notation (#)

    # Convert detected pitch to MIDI note numbers
    try:
        detected_midi = western_notes_to_midi[detected_pitch[:-1]] + (12 * (int(detected_pitch[-1]) - 1)) if len(detected_pitch) > 1 else western_notes_to_midi[detected_pitch]
    except KeyError:
        print(f"Warning: Pitch {detected_pitch} not found in mapping.")
        return None  # If pitch is invalid, return None

    # Calculate the difference in semitones between the detected pitch and root pitch
    semitone_diff = (detected_midi - root_midi) % 12
    
    # Map the semitone difference to the corresponding Sargam notation
    if semitone_diff < len(sargam_notes):
        return sargam_notes[semitone_diff]
    else:
        return None  # If the pitch is out of range for Sargam notation

# Function to process the audio, detect pitch, and save transcription to a CSV file
def process_audio_for_transcription(audio_path, transcription_file='transcription.csv', root_pitch='C'):
    # Load the audio file
    y, sr = librosa.load(audio_path)

    # Set parameters for pitch detection
    fmin = librosa.note_to_hz('C1')  # Min frequency for pitch detection
    fmax = librosa.note_to_hz('B8')  # Max frequency for pitch detection

    # Using librosa.pyin to detect pitch across the entire audio
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax)

    # Calculate the MIDI number for the root pitch
    western_notes_to_midi = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6,
        'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }
    root_midi = western_notes_to_midi[root_pitch]

    # Normalize pitch names (replace sharp symbols for consistency)
    normalized_pitch_names = [
        librosa.hz_to_note(f) if f is not None and not math.isnan(f) else None
        for f in f0
    ]

    # Write transcription to CSV file (directly without storing all in memory)
    with open(transcription_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write CSV header
        writer.writerow(['Timestamp (s)', 'Pitch (Note)', 'Frequency (Hz)', 'Sargam Notation'])
        
        # Write each pitch and timestamp to CSV
        for timestamp, pitch, frequency in zip(librosa.times_like(f0), normalized_pitch_names, f0):
            if pitch is not None:  # Only write when pitch is detected
                # Calculate Sargam notation based on the root pitch and detected pitch
                sargam = get_sargam_notation(root_pitch, pitch, root_midi)
                if sargam:  # Only write if sargam is valid
                    writer.writerow([timestamp, pitch, frequency, sargam])

    print(f"Transcription saved to {transcription_file}")

# Function to read the transcription CSV and print notes played within the given time range
def print_notes_in_range(transcription_file='transcription.csv', start_time=0, end_time=float('inf')):
    # Check if the transcription file exists and is non-empty
    try:
        with open(transcription_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip the header row
            
            # Flag to track if any notes are printed
            notes_found = False
            last_pitch = None
            count = 0
            summary = []

            # Read and print notes within the time range
            for row in reader:
                timestamp, pitch, frequency, sargam = float(row[0]), row[1], float(row[2]), row[3]
                
                # Check if the timestamp is within the given range
                if start_time <= timestamp <= end_time:
                    # Print the individual notes with Sargam notation
                    print(f"{timestamp:.2f}s - Pitch: {pitch} ({frequency:.2f} Hz) - Sargam: {sargam}")
                    notes_found = True
                    
                    # Group repeated subsequent notes
                    if sargam == last_pitch:
                        count += 1  # Increment the count for repeated note
                    else:
                        if last_pitch is not None and count > 1:  # Only include notes repeated more than once
                            # If we have a previous note, append it with repetition count
                            summary.append(f"{last_pitch}({count})")
                        # Reset for the new note
                        last_pitch = sargam
                        count = 1
            
            # Append the last note to summary if it was repeated more than once
            if last_pitch is not None and count > 1:
                summary.append(f"{last_pitch}({count})")

            if not notes_found:
                print(f"No notes found in the time range {start_time}s to {end_time}s.")
            else:
                # Print the summary (skipping single occurrence notes)
                print("\nSummary (repeated notes grouped):")
                if summary:
                    print(" -> ".join(summary))
                else:
                    print("No notes repeated more than once.")
    
    except FileNotFoundError:
        print(f"Error: The file {transcription_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    audio_path = './AudioSource/sourcefile.mp3'  # Replace with your audio file path
    root_pitch = input("Enter the root pitch note (e.g., C, D#, G): ").strip()  # Ask for root pitch
    
    # Step 1: Process the audio for transcription and save to CSV
    process_audio_for_transcription(audio_path, 'transcription.csv', root_pitch)

    # Step 2: Ask for time range and print notes
    start_time = float(input("Enter start time (seconds): "))
    end_time = float(input("Enter end time (seconds): "))
    
    print(f"\nNotes played between {start_time}s and {end_time}s:")
    print_notes_in_range('transcription.csv', start_time, end_time)

    print_notes_in_range('transcription.csv', start_time, end_time)
