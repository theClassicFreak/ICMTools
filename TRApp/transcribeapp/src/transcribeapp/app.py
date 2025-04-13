# Updated MP3PlayerApp code with real-time tracker and loop markers
# (Same base as your last working checkpoint, with waveform animation features)

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import traceback
import pygame
import asyncio
import numpy as np
import tempfile
from pydub import AudioSegment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class MP3PlayerApp(toga.App):
    def startup(self):
        pygame.mixer.init()

        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        self.label = toga.Label("Select an MP3 file to play", style=Pack(padding=5))
        self.length_label = toga.Label("Total Length: N/A", style=Pack(padding=5))

        self.load_button = toga.Button("Load MP3", on_press=self.load_file, style=Pack(padding=5))
        self.play_button = toga.Button("Play", on_press=self.play_audio, style=Pack(padding=5))
        self.pause_button = toga.Button("Pause", on_press=self.pause_audio, style=Pack(padding=5))
        self.stop_button = toga.Button("Stop", on_press=self.stop_audio, style=Pack(padding=5))

        self.loop_toggle = toga.Switch("Loop", on_change=self.toggle_loop, style=Pack(padding=5))

        self.start_time_input = toga.TextInput(placeholder="Start time (seconds)", style=Pack(padding=5), readonly=True)
        self.end_time_input = toga.TextInput(placeholder="End time (seconds)", style=Pack(padding=5), readonly=True)

        self.loop_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.loop_box.add(self.start_time_input)
        self.loop_box.add(self.end_time_input)

        self.play_button.enabled = False
        self.pause_button.enabled = False
        self.stop_button.enabled = False

        self.waveform_image = toga.ImageView(style=Pack(height=120, padding=5))

        self.main_box.add(self.label)
        self.main_box.add(self.length_label)
        self.main_box.add(self.waveform_image)
        self.main_box.add(self.load_button)
        self.main_box.add(self.loop_toggle)
        self.main_box.add(self.play_button)
        self.main_box.add(self.pause_button)
        self.main_box.add(self.stop_button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

        self.file_path = None
        self.is_paused = False
        self.looping = False
        self.audio_length = 0
        self.paused_pos = 0
        self.start_time = 0
        self.end_time = 0
        self.loop_monitor_task = None
        self.tracker_task = None
        self.samples = None
        self.sample_rate = None
        self.duration = 0

    async def load_file(self, widget):
        try:
            dialog = toga.OpenFileDialog("Select MP3", file_types=['mp3'])
            path = await self.main_window.dialog(dialog)
            if not path:
                return

            self.file_path = path
            self.label.text = f"File selected: {self.file_path}"

            audio = AudioSegment.from_mp3(self.file_path)
            self.audio_length = len(audio) / 1000.0
            self.length_label.text = f"Total Length: {self.audio_length:.2f} seconds"

            self.play_button.enabled = True
            self.display_waveform(audio)

        except Exception as e:
            print("[ERROR] Error loading file:", e)
            traceback.print_exc()
            self.label.text = "Error occurred while loading the file."

    def display_waveform(self, audio, tracker_time=None):
        try:
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)

            samples = samples / np.max(np.abs(samples))
            self.samples = samples
            self.sample_rate = audio.frame_rate
            self.duration = len(samples) / self.sample_rate
            time = np.linspace(0, self.duration, num=len(samples))

            fig, ax = plt.subplots(figsize=(10, 1.5), dpi=100)
            ax.plot(time, samples, linewidth=0.5, color='steelblue')

            # Draw tracker line
            if tracker_time is not None:
                ax.axvline(tracker_time, color='red', linewidth=1)

            # Draw loop region markers
            if self.loop_toggle.value and self.update_loop_values():
                ax.axvline(self.start_time, color='green', linestyle='--', linewidth=1)
                ax.axvline(self.end_time, color='orange', linestyle='--', linewidth=1)

            ax.set_axis_off()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                fig.savefig(tmp.name, bbox_inches='tight', pad_inches=0)
                plt.close(fig)

                with open(tmp.name, "rb") as img_file:
                    img_data = img_file.read()

                image = toga.Image(data=img_data)
                self.waveform_image.image = image

        except Exception as e:
            print("[ERROR] Error displaying waveform:", e)
            traceback.print_exc()

    def stop_audio(self, widget):
        try:
            if self.file_path:
                self.looping = False
                if self.loop_monitor_task:
                    self.loop_monitor_task.cancel()
                if self.tracker_task:
                    self.tracker_task.cancel()
                self.is_paused = False
                pygame.mixer.music.stop()
                self.label.text = "Audio stopped."
                self.pause_button.enabled = False
                self.stop_button.enabled = False
                self.display_waveform(AudioSegment.from_mp3(self.file_path), tracker_time=0)
        except Exception as e:
            print("[ERROR] Error stopping audio:", e)
            traceback.print_exc()

    def update_loop_values(self):
        try:
            start = float(self.start_time_input.value or 0)
            end = float(self.end_time_input.value or 0)
            if start < 0 or end <= start or end > self.audio_length:
                return False
            self.start_time = start
            self.end_time = end
            return True
        except:
            return False

    def play_audio(self, widget):
        try:
            if self.file_path:
                if self.loop_toggle.value:
                    if not self.update_loop_values():
                        self.label.text = "Invalid loop times."
                        return
                    self.looping = True
                    pygame.mixer.music.load(self.file_path)
                    pygame.mixer.music.play(start=self.start_time)
                    self.loop_monitor_task = asyncio.ensure_future(self.loop_monitor())
                    self.tracker_task = asyncio.ensure_future(self.track_position(loop=True))
                else:
                    self.looping = False
                    pygame.mixer.music.load(self.file_path)
                    if self.is_paused:
                        pygame.mixer.music.play(start=self.paused_pos / 1000)
                        self.tracker_task = asyncio.ensure_future(self.track_position(start=self.paused_pos / 1000))
                    else:
                        pygame.mixer.music.play()
                        self.tracker_task = asyncio.ensure_future(self.track_position())
                self.is_paused = False
                self.pause_button.enabled = True
                self.stop_button.enabled = True
                self.label.text = "Playing audio..."
        except Exception as e:
            print("[ERROR] Error playing audio:", e)
            traceback.print_exc()

    def pause_audio(self, widget):
        try:
            if self.file_path:
                self.paused_pos = pygame.mixer.music.get_pos()
                pygame.mixer.music.pause()
                self.is_paused = True
                self.label.text = "Audio paused."
        except Exception as e:
            print("[ERROR] Error pausing audio:", e)
            traceback.print_exc()

    async def loop_monitor(self):
        try:
            while self.looping:
                await asyncio.sleep(0.01)
                current = pygame.mixer.music.get_pos() / 1000
                if current < 0 or current >= self.end_time:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play(start=self.start_time)
        except asyncio.CancelledError:
            pass

    async def track_position(self, loop=False, start=0):
        try:
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                current = pygame.mixer.music.get_pos() / 1000
                if loop:
                    current = self.start_time + current
                print(f"[DEBUG] Current playback position: {current:.3f} sec")
                self.display_waveform(AudioSegment.from_mp3(self.file_path), tracker_time=current)
        except asyncio.CancelledError:
            pass

    def toggle_loop(self, widget):
        if self.loop_toggle.value:
            self.start_time_input.readonly = False
            self.end_time_input.readonly = False
            if self.loop_box not in self.main_box.children:
                self.main_box.add(self.loop_box)
        else:
            self.start_time_input.readonly = True
            self.end_time_input.readonly = True
            if self.loop_box in self.main_box.children:
                self.main_box.remove(self.loop_box)
            self.looping = False
            if self.loop_monitor_task:
                self.loop_monitor_task.cancel()
                self.loop_monitor_task = None


def main():
    return MP3PlayerApp("MP3 Player", "com.soundofsarod.mp3player")
