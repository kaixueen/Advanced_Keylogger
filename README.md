# Advanced Keylogger

![Keylogger](overview.jpg)

## Overview
Hi guys, this is my first cybersecurity project! (theoretically)
This project is an advanced keylogger and system monitoring tool that captures keystrokes, clipboard data, microphone audio, screenshots, and system information. It is designed to run continuously, logging data and detecting changes in real-time. After that, the data is organized into categorized folders and zipped automatically for efficiency and portability. Every 2 hours, the results will be sent via email to the attacker.

## Features
### 1. **Keylogger**
- Captures all keystrokes typed by the user.
- Formats special keys (e.g., `[Enter]`, `[Space]`, etc.).

### 2. **Clipboard Monitoring**
- Detects changes in clipboard contents.
- Logs new clipboard data only when it changes.
- Stores clipboard history in a log file.

### 3. **Microphone Recording**
- Records audio when the volume exceeds a predefined threshold.
- Stops recording when silence is detected for a set duration.
- Saves audio recordings as `.wav` files.

### 4. **Screenshot Capture**
- Takes a screenshot of all connected screens every 30 minutes.

### 5. **System Information Collection**
- Retrieves system details, including OS, hostname, IP address, MAC address, and hardware specifications.
- Lists running processes, excluding common system processes.
- Updates every 1 hour.

## Technology Used
- **Python**: Main programming language.
- **Gmail API**: Email automation and attachment delivery.
- **Threading**: Concurrent background tasks.
- **shutil / zipfile**: File system manipulation and compression.
- **Pathlib & OS**: Directory handling.
- **Base64 & EmailMessage**: Email encoding and MIME formatting.
- **PyAudio, Pillow, etc.**: For microphone recording and screenshot capture.

## Setup & Execution
Follow the steps below to set up and run the Advanced Keylogger with Gmail integration:
## 1. Install Python Dependencies
Make sure you have Python 3 installed, then install the required packages:

```sh
pip install -r requirements.txt
```

## 2. Gmail API Setup (Google Cloud Console) 
To enable Gmail automation for email sending:

### Create a Project and Enable Gmail API 
1. Go to the Google Cloud Console.
2. Create a new project (e.g., `Keylogger Automation`).
3. Navigate to **APIs & Services > Library**.
4. Search for **Gmail API** and click **Enable**.

### Configure OAuth Consent and Credentials 
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. If prompted, first configure the **OAuth Consent Screen**:
   * Choose **External** for user type.
   * Fill in required details (App name, User support email, etc.).
   * Save and continue until the end.
4. Go back to **Credentials**, click **Create Credentials > OAuth client ID** again.
5. Choose **Desktop App** as the application type and name it accordingly.
6. After creation, click **Download JSON** and place the file in your project folder.
7. In your `.env` file, add:

```env
CREDENTIAL_FILE=your_downloaded_json_file.json
TOKEN_FILE=your_generated_token.json
```

### Add Test User (For OAuth in Development) 
1. Go to **OAuth consent screen > Test Users**.
2. Click **Add Users** and enter your Gmail address used for testing.

## 3. Generate Gmail API Token 
Once the JSON credentials are set:

```sh
python generate_token.py
```

If successful, a `token.json` file will be created in your project folder.

## 4. Run the Keylogger 
You might need administrator/root privileges for full access to system features (e.g., audio, clipboard, keylogging).

```sh
python keylogger.py
```

## Notes
- The script continuously runs in the background.
- The log files and captured data are stored in a specified directory.
- Ensure you have the necessary permissions to access system components.

## Disclaimer
This tool is intended for educational and ethical research purposes only. 
