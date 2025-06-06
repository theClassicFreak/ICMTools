# LipiPlayer WebApp

A web-based audio player and transcription tool for Indian classical music, built with Streamlit.

## Features
- Upload and play MP3 files
- Select root note
- Slice audio by time
- Transcribe to solfege
- Export transcription as PDF
- Playback controls (play, pause, stop)

## Setup

```sh
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py