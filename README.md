# AI Voice Assistant

This AI voice Assistant captures either your screen or webcam feed and processes audio commands. It generates responses based on image and voice input.  

## Requirements
You need an `OPENAI_API_KEY` to run this code. Store it in a `.env` file in the root directory of the project or set it as an environment variable.

### Additional Requirement for macOS (Apple Silicon)
If you are running the code on Apple Silicon, install the following dependency:
```bash
$ brew install portaudio
```

## Installation
1. **Set up a virtual environment**:
   ```bash
   $ python3 -m venv .venv
   $ source .venv/bin/activate
   ```
2. **Upgrade `pip` and install required packages**:
   ```bash
   $ pip install -U pip
   $ pip install -r requirements.txt
   ```

## Usage
Run the assistant with the following command:
```bash
$ python3 assistant.py
```

### Stream Type Selection
By default, the assistant uses screen capture (`screenstream`). You can switch to using a webcam by passing the `--stream_type` parameter:
- **Screen Capture (default)**:
  ```bash
  $ python3 assistant.py
  ```
- **Webcam**:
  ```bash
  $ python3 assistant.py --stream_type webcam
  ```

### Exiting
To exit the application:
- Press `Esc` or `q` in the stream window.
