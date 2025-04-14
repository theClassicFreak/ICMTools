import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import pygame
import asyncio
from pydub import AudioSegment
import parselmouth
import numpy as np
import tempfile
import io
import logging
from tabulate import tabulate
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SOLFEGE_MAP = {
    0: "S",
    1: "r",
    2: "R",
    3: "g",
    4: "G",
    5: "M",
    6: "m",
    7: "P",
    8: "d",
    9: "D",
    10: "n",
    11: "N",
}


class LipiPlayerWindows(toga.App):
    def startup(self):
        """Initialize the UI for the MP3 player."""
        pygame.mixer.init()

        # Configure logging globally
        self.configure_logging()
        logging.info("Application started.")

        # Main UI box
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Initialize variables
        self.file_path = None  # Ensure file_path is initialized
        self.wav_path = None
        self.transcription_data = []
        self.is_paused = False
        self.paused_pos = 0
        self.audio_length = 0
        self.tracker_task = None
        self.temp_wav_path = None
        self.last_played_time = 0

        # Label to display instructions
        self.label = toga.Label(
            "00:00.000", style=Pack(padding=10, font_size=40, text_align="center")
        )

        # Label to display the total length of the audio
        self.length_label = toga.Label("Total Length: N/A", style=Pack(padding=5))

        # Transcription table
        self.transcription_table = toga.Table(
            headings=["Timestamp", "Frequency", "Solfege", "Duration", "Count"],
            style=Pack(flex=1, padding=10),
        )

        # Root note dropdown
        self.root_dropdown = toga.Selection(items=NOTE_NAMES, style=Pack(padding=5))
        self.root_dropdown.on_select = self.on_root_note_selected

        # Buttons for playback controls
        self.load_button = toga.Button(
            "Load MP3", on_press=self.load_file, style=Pack(padding=5)
        )
        self.transcribe_button = toga.Button(
            "Transcribe",
            on_press=self.start_transcription,
            style=Pack(padding=5),
            enabled=False,
        )
        self.play_button = toga.Button(
            "Play", on_press=self.play_audio, style=Pack(padding=5), enabled=False
        )
        self.pause_button = toga.Button(
            "Pause", on_press=self.pause_audio, style=Pack(padding=5), enabled=False
        )
        self.stop_button = toga.Button(
            "Stop", on_press=self.stop_audio, style=Pack(padding=5), enabled=False
        )

        # Replace the loop checkbox with a repeat checkbox
        self.repeat_checkbox = toga.Switch("Repeat", style=Pack(padding=5))

        # Add separate input fields for start and end times
        self.start_hour = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.start_minute = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.start_second = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.start_millisecond = toga.TextInput(
            value="000", style=Pack(width=70, padding=5)
        )

        self.end_hour = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.end_minute = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.end_second = toga.TextInput(value="00", style=Pack(width=50, padding=5))
        self.end_millisecond = toga.TextInput(
            value="000", style=Pack(width=70, padding=5)
        )

        # Add a Reset Slice button
        self.reset_slice_button = toga.Button(
            "Reset Slice", on_press=self.reset_slice, style=Pack(padding=5)
        )

        # Add a Slice button
        self.slice_button = toga.Button(
            "Slice Audio", on_press=self.slice_audio, style=Pack(padding=5)
        )

        # Group playback controls
        playback_controls = toga.Box(
            children=[
                self.play_button,
                self.pause_button,
                self.stop_button,
                self.repeat_checkbox,
            ],
            style=Pack(direction=ROW, padding=5),
        )

        # Add tooltips
        self.play_button.tooltip = "Play the audio file."
        self.pause_button.tooltip = "Pause or resume playback."
        self.stop_button.tooltip = "Stop playback."
        self.repeat_checkbox.tooltip = "Enable or disable repeat mode."

        # Add widgets to the main box
        self.main_box.add(self.label)
        self.main_box.add(self.length_label)
        self.main_box.add(toga.Label("Root Note:", style=Pack(padding=5)))
        self.main_box.add(self.root_dropdown)
        self.main_box.add(self.load_button)
        self.main_box.add(self.transcribe_button)
        self.main_box.add(playback_controls)
        self.main_box.add(toga.Label("Start Time:", style=Pack(padding=5)))
        self.main_box.add(
            toga.Box(
                children=[
                    self.start_hour,
                    self.start_minute,
                    self.start_second,
                    self.start_millisecond,
                ],
                style=Pack(direction=ROW),
            )
        )
        self.main_box.add(toga.Label("End Time:", style=Pack(padding=5)))
        self.main_box.add(
            toga.Box(
                children=[
                    self.end_hour,
                    self.end_minute,
                    self.end_second,
                    self.end_millisecond,
                ],
                style=Pack(direction=ROW),
            )
        )
        self.main_box.add(self.reset_slice_button)
        self.main_box.add(self.slice_button)
        self.main_box.add(self.transcription_table)

        # Set up the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    async def load_file(self, widget):
        """Load an MP3 file and reset relevant states."""
        dialog = toga.OpenFileDialog("Select MP3", file_types=["mp3"])
        path = await self.main_window.dialog(dialog)
        if not path:
            return
        self.file_path = path

        try:
            self.transcription_data = []
            self.transcription_table.data.clear()
            self.label.text = "00:00.000"
            self.pause_button.enabled = False
            self.stop_button.enabled = False
            self.pause_button.text = "Pause"

            audio = (
                AudioSegment.from_mp3(self.file_path)
                .set_channels(1)
                .set_frame_rate(44100)
            )
            # Use a context manager to ensure the file is properly closed
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                audio.export(temp_wav_file, format="wav")
                self.temp_wav_path = temp_wav_file.name
                self.original_temp_wav_path = self.temp_wav_path  # Initialize original_temp_wav_path

            self.wav_buffer = io.BytesIO()
            audio.export(self.wav_buffer, format="wav")
            self.wav_buffer.seek(0)

            self.audio_length = len(audio) / 1000.0  # Set audio length in seconds
            hours = int(self.audio_length // 3600)
            minutes = int((self.audio_length % 3600) // 60)
            seconds = int(self.audio_length % 60)
            milliseconds = int((self.audio_length % 1) * 1000)
            self.length_label.text = f"Total Length: {hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
            self.play_button.enabled = True
            self.transcribe_button.enabled = True

            logging.info(f"Loaded file: {self.file_path}")
            logging.info(f"Total length: {self.length_label.text}")

        except Exception as e:
            logging.error(f"Error in load_file: {e}")

    def start_transcription(self, widget):
        """Perform transcription and generate a PDF report."""
        if not hasattr(self, "wav_buffer") or self.wav_buffer is None:
            logging.error("No audio loaded for transcription.")
            return

        root_note = self.root_dropdown.value
        if root_note not in NOTE_NAMES:
            logging.error("Invalid root note selected.")
            return

        logging.info("\n--- Transcription Process Started ---")
        temp_wav_path = None

        try:
            self.wav_buffer.seek(0)
            # Use a context manager to ensure the file is properly closed
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                temp_wav_file.write(self.wav_buffer.read())
                temp_wav_path = temp_wav_file.name

            snd = parselmouth.Sound(temp_wav_path)
            pitch = snd.to_pitch(time_step=0.001, pitch_floor=75, pitch_ceiling=1000)
            times = pitch.xs()
            frequencies = pitch.selected_array["frequency"]
            self.transcription_data = []

            prev_solfege = None
            count = 0
            start_time = times[0]

            for t, freq in zip(times, frequencies):
                solfege = self.note_to_solfege(freq, root_note)
                if solfege != prev_solfege:
                    if prev_solfege:
                        end_time = t
                        duration = end_time - start_time
                        timestamp = f"{int(start_time//3600):02}:{int(start_time%3600//60):02}:{int(start_time%60):02}.{int((start_time%1)*1000):03}"
                        self.transcription_data.append(
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

            # Populate the transcription table
            self.transcription_table.data.clear()
            for row in self.transcription_data:
                self.transcription_table.data.append([str(col) for col in row])

            # Generate PDF transcription report
            self.generate_pdf_transcription()
            logging.info("Transcription completed successfully.")
            logging.info("--- Transcription Process Ended ---\n")

        except Exception as e:
            logging.error(f"Error in start_transcription: {e}")

        finally:
            if temp_wav_path and os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

    def play_audio(self, widget):
        """Play the audio."""
        if not self.temp_wav_path or not os.path.exists(self.temp_wav_path):
            logging.error("Temporary WAV file does not exist.")
            return

        try:
            pygame.mixer.music.load(self.temp_wav_path)
            if self.repeat_checkbox.value:
                pygame.mixer.music.play(loops=-1)  # Infinite playback
                logging.info("Audio playback started in repeat mode.")
            else:
                pygame.mixer.music.play()
                logging.info("Audio playback started.")

            self.tracker_task = asyncio.ensure_future(self.track_position())
            self.is_paused = False
            self.pause_button.enabled = True
            self.stop_button.enabled = True
            self.pause_button.text = "Pause"

        except Exception as e:
            logging.error(f"Error in play_audio: {e}")

    def pause_audio(self, widget):
        if not self.file_path:
            return
        if not self.is_paused:
            self.paused_pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.pause()
            self.is_paused = True
            widget.text = "Resume"
            if self.tracker_task:
                self.tracker_task.cancel()
            logging.info("Audio paused.")
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False
            widget.text = "Pause"
            self.tracker_task = asyncio.ensure_future(self.track_position())
            logging.info("Audio resumed.")

    def stop_audio(self, widget):
        """Stop the audio and clean up resources."""
        if self.tracker_task and not self.tracker_task.done():
            self.tracker_task.cancel()
        pygame.mixer.music.stop()
        self.is_paused = False
        self.label.text = "00:00.000"
        self.pause_button.enabled = False
        self.stop_button.enabled = False
        self.pause_button.text = "Pause"
        logging.info("Audio stopped.")

    async def track_position(self):
        """Track the current playback position and update the time display."""
        try:
            audio_length_ms = self.audio_length * 1000  # Cache audio length
            start_time_ms = 0
            if self.temp_wav_path != self.original_temp_wav_path:
                start_time_ms = self.parse_time_from_inputs(
                    self.start_hour,
                    self.start_minute,
                    self.start_second,
                    self.start_millisecond,
                )
                end_time_ms = self.parse_time_from_inputs(
                    self.end_hour,
                    self.end_minute,
                    self.end_second,
                    self.end_millisecond,
                )
                audio_length_ms = end_time_ms - start_time_ms

            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.001)  # Sample every 1 millisecond
                current = pygame.mixer.music.get_pos()  # Get position in milliseconds

                if current >= 0 and audio_length_ms > 0:
                    current = current % audio_length_ms
                    current_with_offset = current + start_time_ms
                    self.last_played_time = (
                        current_with_offset  # Update last played time
                    )
                    self.update_time_display(current_with_offset)

            self.update_time_display(self.last_played_time)

        except asyncio.CancelledError:
            pass

    def note_to_solfege(self, freq, root_note):
        if freq <= 0:
            return None
        midi_num = int(round(69 + 12 * np.log2(freq / 440.0)))
        index = (midi_num - NOTE_NAMES.index(root_note)) % 12
        return SOLFEGE_MAP.get(index)

    def update_time_display(self, current_ms):
        """Update the time display label in HH:MM:SS.mmm format."""
        hours = int(current_ms // (3600 * 1000))
        minutes = int((current_ms % (3600 * 1000)) // (60 * 1000))
        seconds = int((current_ms % (60 * 1000)) // 1000)
        milliseconds = int(current_ms % 1000)
        self.label.text = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

    def exit(self):
        """Stop playback and clean up tasks when the app is closed."""
        self.stop_audio(None)
        pygame.mixer.music.unload()
        if self.temp_wav_path and os.path.exists(self.temp_wav_path):
            try:
                os.remove(self.temp_wav_path)
            except PermissionError as e:
                logging.error(f"Error cleaning up temporary file on exit: {e}")
        logging.info("Application closed.")
        logging.info("=" * 80 + "\n")
        super().exit()

    def parse_time_from_inputs(
        self, hour_input, minute_input, second_input, millisecond_input
    ):
        """Parse time from separate input fields into milliseconds."""
        try:
            hours = int(hour_input.value)
            minutes = int(minute_input.value)
            seconds = int(second_input.value)
            milliseconds = int(millisecond_input.value)
            return (
                (hours * 3600 * 1000)
                + (minutes * 60 * 1000)
                + (seconds * 1000)
                + milliseconds
            )
        except ValueError:
            return -1  # Invalid format

    def reset_slice(self, widget):
        """Reset to the original full audio file and reset timestamp inputs."""
        # Stop audio playback first
        self.stop_audio(None)

        # Revert to the original full audio file
        self.temp_wav_path = self.original_temp_wav_path
        logging.info("Reset to the original full audio file.")

        # Reset timestamp inputs to default values (00:00:00.000)
        self.start_hour.value = "00"
        self.start_minute.value = "00"
        self.start_second.value = "00"
        self.start_millisecond.value = "000"

        self.end_hour.value = "00"
        self.end_minute.value = "00"
        self.end_second.value = "00"
        self.end_millisecond.value = "000"

        logging.info("Timestamp inputs reset to default values.")

    def slice_audio(self, widget):
        """Slice the audio based on start and end times."""
        start_time_ms = self.parse_time_from_inputs(
            self.start_hour, self.start_minute, self.start_second, self.start_millisecond
        )
        end_time_ms = self.parse_time_from_inputs(
            self.end_hour, self.end_minute, self.end_second, self.end_millisecond
        )

        if start_time_ms < 0 or end_time_ms <= start_time_ms:
            logging.error("Invalid start or end time for slicing.")
            return

        try:
            # Always slice from the original file
            with open(self.original_temp_wav_path, "rb") as temp_file:
                audio = AudioSegment.from_file(temp_file)
                sliced_audio = audio[start_time_ms:end_time_ms]

            # Save the sliced audio to a new temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                sliced_audio.export(temp_wav_file, format="wav")
                self.temp_wav_path = temp_wav_file.name

            logging.info("Audio sliced successfully.")
        except Exception as e:
            logging.error(f"Error slicing audio: {e}")

    def generate_pdf_transcription(self):
        """Generate a PDF transcription report with improved formatting."""
        # Include source file name and root note in the PDF file name
        source_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        root_note = self.root_dropdown.value
        pdf_file_name = f"{source_file_name}_{root_note}_Transcription.pdf"
        pdf_file = os.path.join(os.path.dirname(self.file_path), pdf_file_name)

        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.setFont("Courier", 12)  # Use a larger font for better readability

        # Add header
        c.drawString(50, 750, "Transcription Report")
        c.drawString(50, 735, f"File: {os.path.basename(self.file_path)}")
        c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 705, f"Root Note: {root_note}")
        c.drawString(50, 690, f"Total Duration: {self.length_label.text}")
        c.drawString(50, 675, "-" * 80)

        # Add table headers
        y = 660
        c.setFont("Courier", 12)
        c.drawString(50, y, "Timestamp")
        c.drawString(150, y, "Frequency")
        c.drawString(250, y, "Solfege")
        c.drawString(350, y, "Duration")
        c.drawString(450, y, "Count")
        y -= 20  # Add more spacing between the header and the rows
        c.setFont("Courier", 12)  # Reset to normal font for the rows

        # Add transcription data
        for row in self.transcription_data:
            if y < 50:  # Start a new page if space runs out
                c.showPage()
                c.setFont("Courier", 12)
                y = 750

            c.drawString(50, y, row[0])
            c.drawString(150, y, row[1])
            c.drawString(250, y, row[2])
            c.drawString(350, y, row[3])
            c.drawString(450, y, str(row[4]))
            y -= 20  # Add more spacing between rows for better readability

        # Add summary
        c.drawString(50, y, "-" * 80)
        y -= 20
        c.drawString(50, y, f"Total Notes: {len(self.transcription_data)}")
        y -= 20
        total_duration = sum(float(row[3].replace("s", "")) for row in self.transcription_data)
        c.drawString(50, y, f"Total Duration of Notes: {total_duration:.3f} seconds")

        # Save PDF
        c.save()
        logging.info(f"PDF transcription saved to {pdf_file}.")

    def configure_logging(self):
        """Configure logging to save logs to a file named after the class."""
        try:
            # Use the class name as the log file name
            log_file_path = os.path.join(os.getcwd(), f"{self.__class__.__name__}_LOG.log")

            # Get the root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            # Create a file handler
            file_handler = logging.FileHandler(log_file_path, mode="a")  # Append mode
            file_handler.setLevel(logging.INFO)

            # Create a formatter and add it to the handler
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)

            # Add the handler to the root logger
            if not root_logger.handlers:  # Avoid adding multiple handlers
                root_logger.addHandler(file_handler)

            # Redirect warnings and errors to the log file
            logging.captureWarnings(True)

            # Add a distinct line break when the app starts
            logging.info("\n" + "=" * 80)
            logging.info("APPLICATION STARTED")
            logging.info("=" * 80)

        except Exception as e:
            # Log the error to the terminal if the log file cannot be created
            print(f"Error: Unable to create log file. {e}")

    def on_root_note_selected(self, widget):
        logging.info(f"Root note selected: {self.root_dropdown.value}")


def main():
    return LipiPlayerWindows("LipiPlayer", "com.soundofsarod.lipiplayer")
