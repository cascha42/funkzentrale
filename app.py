from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
import os
import subprocess
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# GPIO PTT
gpio_pin = 17

# Audio-Files Folder
audio_folder = 'audio_files'

# GPIO INIT
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)
GPIO.output(gpio_pin, GPIO.LOW)

@app.route('/')
def index():
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith(('.mp3', '.wav', 'm4a', 'aac'))]
    return render_template('index.html', audio_files=audio_files)

@app.route('/play', methods=['POST'])
def play_audio():
    selected_audio = request.form['audio']
    
    GPIO.output(gpio_pin, GPIO.HIGH)
    
    time.sleep(0.2)
    subprocess.run(['mplayer', '-ao', 'alsa', os.path.join(audio_folder, selected_audio)])
    
    GPIO.output(gpio_pin, GPIO.LOW)
    
    return redirect('/')

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

@app.route('/audio_files/<filename>')
def serve_audio(filename):
    return send_from_directory(audio_folder, filename)

@app.route('/files')
def file_browser():
    audio_files = [f for f in os.listdir(audio_folder)]
    return render_template('file_browser.html', audio_files=audio_files)

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

