# USB Audio Player with Web Interface

A simple Python USB audio player with a web interface using Flask.  
Allows selection of USB audio playback devices and USB drives via the terminal, and lets you browse and play audio files from the USB stick through a clean browser-based player.


## Features

- Select USB stick via terminal  
- Web interface to browse and play audio files from the USB stick  
- Simple audio player with play/pause, stop, progress bar, and seek functionality  
- Clean, minimalistic tabular design with external CSS  
- Works fully offline (no internet required)  

## Requirements

- Python 3.7 or higher  
- Flask (Python web framework)  
- pygame (for audio playback)
- mutagen (to handle audio metadata)


## Installation

1. Clone the repository or download and extract the ZIP  
2. Install dependencies:

   ```bash
   pip install flask
   pip install pygame
   pip install waitress
   pip install mutagen

3. Run the main script:

   ```bash
   python app.py

## Usage

   1. On start, select your USB stick from the list shown in the terminal.

   2. Next, select the desired audio output device from the terminal list.

   3. The web interface will start automatically, accessible at http://localhost:8080.

   4. Browse the audio files on your USB stick and play them by clicking.

   5. Control playback with play/pause, stop buttons, see progress and time, and click on the progress bar to seek.

## Folder Structure

usbaudioplayer-with-webinterface/\
├── app.py               # Main program with Flask server & audio logic\
├── templates/\
│   └── index.html        # Web interface HTML\
└── static/\
    └── style.css         # External CSS for the web interface

## Notes

   - Plays audio files only from the selected USB stick

   - Supports multi-user usage

   - Supported audio formats (commonly mp3, wav, ogg)
     
## License

This project is licensed under the MIT License.
