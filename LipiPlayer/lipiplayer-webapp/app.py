import streamlit as st
import os
import tempfile
import pandas as pd
import time
from utils.audio_utils import (
    load_audio,
    export_wav,
    slice_audio,
    get_audio_length,
)
from utils.transcription import (
    transcribe_audio,
    NOTE_NAMES,
)
from utils.pdf_utils import generate_pdf

st.set_page_config(page_title="LipiPlayer WebApp", layout="centered")
st.title("LipiPlayer WebApp 🎶")

# --- Session State Initialization ---
if "audio" not in st.session_state:
    st.session_state.audio = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "audio_file_name" not in st.session_state:
    st.session_state.audio_file_name = ""
if "root_note" not in st.session_state:
    st.session_state.root_note = NOTE_NAMES[0]
if "sliced_audio" not in st.session_state:
    st.session_state.sliced_audio = None
if "transcription_data" not in st.session_state:
    st.session_state.transcription_data = []
if "playback_status" not in st.session_state:
    st.session_state.playback_status = "stopped"

# --- File Upload ---
uploaded_file = st.file_uploader("Upload MP3", type=["mp3"])
if uploaded_file:
    st.session_state.audio, st.session_state.audio_bytes = load_audio(uploaded_file)
    st.session_state.audio_file_name = uploaded_file.name
    st.session_state.sliced_audio = None  # Reset slice
    st.session_state.transcription_data = []
    st.success(f"Loaded: {uploaded_file.name}")

# --- Root Note Selection ---
st.session_state.root_note = st.selectbox("Root Note", NOTE_NAMES, index=NOTE_NAMES.index(st.session_state.root_note))

# --- Audio Length Display ---
if st.session_state.audio:
    total_length = get_audio_length(st.session_state.audio)
    st.write(f"Total Length: {total_length}")

# --- Slicing Controls ---
st.subheader("Slice Audio (optional)")
col1, col2, col3, col4 = st.columns(4)
start_h = col1.text_input("Start Hour", "00")
start_m = col2.text_input("Start Min", "00")
start_s = col3.text_input("Start Sec", "00")
start_ms = col4.text_input("Start ms", "000")
col5, col6, col7, col8 = st.columns(4)
end_h = col5.text_input("End Hour", "00")
end_m = col6.text_input("End Min", "00")
end_s = col7.text_input("End Sec", "00")
end_ms = col8.text_input("End ms", "000")

slice_col, reset_col = st.columns([1, 1])
with slice_col:
    if st.button("Slice Audio") and st.session_state.audio:
        # Stop playback by clearing audio_bytes
        audio_bytes = None
        st.session_state.sliced_audio = None  # Clear any previous slice
        start_ms_total = int(start_h)*3600*1000 + int(start_m)*60*1000 + int(start_s)*1000 + int(start_ms)
        end_ms_total = int(end_h)*3600*1000 + int(end_m)*60*1000 + int(end_s)*1000 + int(end_ms)
        if 0 <= start_ms_total < end_ms_total <= len(st.session_state.audio):
            st.session_state.sliced_audio = slice_audio(st.session_state.audio, start_ms_total, end_ms_total)
            st.success("Audio sliced!")
        else:
            st.error("Invalid slice times.")
with reset_col:
    if st.button("Reset to Full Audio"):
        # Stop playback by clearing audio_bytes
        audio_bytes = None
        st.session_state.sliced_audio = None
        st.success("Reverted to full audio.")

# --- Playback Controls ---
st.subheader("Playback Controls")
audio_to_play = st.session_state.sliced_audio if st.session_state.sliced_audio else st.session_state.audio
audio_bytes = export_wav(audio_to_play) if audio_to_play else None

loop = st.checkbox("Loop audio (browser support required)", value=False)

if audio_bytes:
    import base64
    audio_bytes.seek(0)
    b64 = base64.b64encode(audio_bytes.read()).decode()
    audio_format = "audio/wav"
    if loop:
        audio_html = f"""
            <audio controls autoplay loop>
                <source src="data:{audio_format};base64,{b64}">
                Your browser does not support the audio element.
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.audio(audio_bytes, format=audio_format)
else:
    st.info("Upload and/or slice audio to enable playback.")

# --- Transcription ---
st.subheader("Transcription")
if st.button("Transcribe") and audio_to_play:
    st.session_state.transcription_data = transcribe_audio(audio_to_play, st.session_state.root_note)
    if st.session_state.transcription_data:
        st.success("Transcription complete!")
    else:
        st.warning("No transcription data found.")

if st.session_state.transcription_data:
    df = pd.DataFrame(
        st.session_state.transcription_data,
        columns=["Timestamp", "Frequency", "Solfege", "Duration", "Count"]
    )
    st.dataframe(df)
    # --- PDF Export ---
    pdf_bytes = generate_pdf(
        st.session_state.transcription_data,
        st.session_state.audio_file_name,
        st.session_state.root_note,
        get_audio_length(audio_to_play)
    )
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(st.session_state.audio_file_name)[0]
    pdf_filename = f"Transcription_{base_name}_{st.session_state.root_note}_{timestamp}.pdf"

    st.download_button(
        "Download PDF",
        pdf_bytes,
        file_name=pdf_filename,
        mime="application/pdf"
    )