# Funkzentrale

With this simple Flask app, audio files can be played via the audio output. A GPIO is also connected, which can be used to control the push-to-talk button on a radio device

## Features

- **Audio Playback:** Users can preview or play an existing audio file from the list. The app uses mplayer to play audio.

- **Text-to-Speech:** Enter a text in the web interface, which will be generated into an MP3 file using "gTTS" and played.

- **File Upload:** Upload new audio files with the extensions `.mp3`, `.wav`, `.m4a`, and `.aac`. Uploaded files are stored in the "audio_files" directory.

- **File Management:** Rename and delete existing audio files.

## Requirements

- Python 3.x
- Flask
- RPi.GPIO (if running on a Raspberry Pi)
- mplayer (for audio playback)
- gTTS (a Python library for Text-to-Speech support)

## Usage

1. Clone this repository. 
   ```bash
   git clone https://github.com/cascha42/funkzentrale.git
   ```
2. Run app.py (sudo if using port 80)
   ```bash
   sudo python3 app.py
   ```
