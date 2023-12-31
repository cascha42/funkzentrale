import pathlib
import urllib
import zoneinfo
from pprint import pprint

import gtts.lang
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
import os
import subprocess
import RPi.GPIO as GPIO
import time
from gtts import gTTS
from datetime import datetime

app = Flask(__name__)

# Webserver Port (HTTP)
http_port = 8000

# App-Name (HTML)
app_name = "37C3 Funkzentrale"

# App-Name (PWA / Progressive Web App)
app_pwa_name = "37C3 DMR-Funkzentrale"
app_pwa_short_name = "37C3 Funk"

# App-Logo in '/static' Sub-Folder
app_logo = "logo.png"

# Push-to-Talk GPIO (BCM / Broadcom notation, https://pinout.xyz/)
gpio_pin = 17

# Audio-Files Sub-Folder
audio_folder = 'audio_files'

# GPIO INIT
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)
GPIO.output(gpio_pin, GPIO.LOW)


@app.route('/')
def index():
    # audio_files = [f for f in os.listdir(audio_folder) if f.endswith(('.mp3', '.wav', 'm4a', 'aac'))]
    audio_files = generate_tree(audio_folder)
    tts_langs = gtts.lang.tts_langs()
    return render_template('index.html.j2', audio_files=audio_files, tts_langs=tts_langs, app_name=app_name,
                           app_logo=app_logo)


@app.route('/cancel', methods=['POST'])
def cancel_playback():
    subprocess.run(['killall', '-9', 'mplayer'])
    return redirect("/")


@app.route('/play/<path:filename>')
def play_audio(filename):
    selected_audio = filename
    print(selected_audio)
    print(os.path.join(audio_folder, selected_audio))

    GPIO.output(gpio_pin, GPIO.HIGH)

    time.sleep(1.0)
    subprocess.run(['open', os.path.join(audio_folder, selected_audio)])
    #subprocess.run(['mplayer', '-ao', 'alsa', os.path.join(audio_folder, selected_audio)])

    GPIO.output(gpio_pin, GPIO.LOW)

    return redirect('/')


@app.route('/tts', methods=['POST'])
def play_tts():
    tts_text = request.form['tts']
    tts_lang = request.form['lang']
    print(tts_lang)
    say(tts_text, tts_lang)

    return redirect('/')


@app.route('/time', methods=['POST'])
def time_announce():
    tz = zoneinfo.ZoneInfo("Europe/Berlin")
    tts_text = f"Es folgt eine Servicemeldung: Es ist nun {datetime.now(tz).strftime('%H:%M')} und {datetime.now(tz).strftime('%S')} Sekunden!"

    say(tts_text, 'de')

    return redirect("/")


@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        allowed_extensions = {'mp3', 'wav', 'm4a', 'aac'}
        file_extension = uploaded_file.filename.rsplit('.', 1)[-1].lower()
        if file_extension in allowed_extensions:
            uploaded_file.save(os.path.join(audio_folder, uploaded_file.filename))
    return redirect('/')


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(audio_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect('/')


@app.route('/rename/<old_filename>/<new_filename>')
def rename_file(old_filename, new_filename):
    old_path = os.path.join(audio_folder, old_filename)
    new_path = os.path.join(audio_folder, new_filename)

    if os.path.exists(old_path):
        os.rename(old_path, new_path)

    return redirect('/')


@app.route('/audio_files/<path:filename>')
def serve_audio(filename):
    print(filename)
    return send_from_directory(audio_folder, filename)


@app.route('/files')
def file_browser():
    audio_files = [f for f in os.listdir(audio_folder)]
    return render_template('file_browser.html.j2', audio_files=audio_files)


@app.route('/manifest.json')
def manifest():
    return render_template('manifest.json.j2', app_pwa_name=app_pwa_name, app_pwa_short_name=app_pwa_short_name)


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')


# Helper Funcs
def say(tts_text, tts_lang):
    tts = gTTS(tts_text, lang=tts_lang)
    tts.save(os.path.join('/tmp', 'tts.mp3'))

    GPIO.output(gpio_pin, GPIO.HIGH)

    time.sleep(0.2)
    subprocess.run(['mplayer', '-ao', 'alsa', os.path.join('/tmp', 'tts.mp3')])

    os.remove(os.path.join('/tmp', 'tts.mp3'))

    GPIO.output(gpio_pin, GPIO.LOW)


def generate_tree(root_dir):
    tree = {'name': os.path.basename(root_dir), 'type': '0folder', 'children': []}
    try:
        for entry in os.listdir(root_dir):
            full_path = os.path.join(root_dir, entry)
            if os.path.isdir(full_path):
                tree['children'].append(generate_tree(full_path))
            else:
                corrected_path = pathlib.Path(*pathlib.Path(full_path).parts[1:])
                tree['children'].append({'name': entry, 'type': '1file', 'full_path': corrected_path})
    except OSError:
        pass
    tree['children'] = sorted(tree['children'], key=lambda x: (x['type'], x['name']))

    return tree


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=http_port, debug=True)
