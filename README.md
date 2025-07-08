# Wojak Video Maker

This project generates "Wojak" style videos based on a configuration file. It uses Python with the MoviePy and Pillow libraries to create video clips from images, add text, and combine them into a final video with a background and music.

## Features

-   Creates videos from a sequence of character scenes.
-   Adds text dialogue to each scene.
-   Supports custom backgrounds and background music.
-   Configurable video resolution and FPS.
-   Mirrors character images for right-side placement.

## Prerequisites

-   Python 3.x
-   pip (Python package installer)

## Installation

1.  **Clone the repository or download the project files.**

2.  **Install the required Python libraries:**

    ```bash
    pip install moviepy Pillow
    ```

## Usage

1.  **Edit the `config.json` file** to define your video scenes. See the configuration section below for more details.

2.  **Run the `main.py` script:**

    ```bash
    python main.py
    ```

3.  The output video will be saved in the project directory with the filename specified in `config.json`.

## Configuration (`config.json`)

The `config.json` file defines the structure and content of the video.

```json
{
  "canvas_size": [720, 1280],
  "background": "./assets/classroom2.png",
  "music": "./assets/best_background.mp3",
  "fps": 24,
  "output_video": "output.mp4",
  "characters": [
    {
      "image": "./assets/tuxedo.png",
      "start_time": 0,
      "duration": 2,
      "text": "Why are we still here?",
      "side": "left"
    },
    {
      "image": "./assets/CoomerMasked.PNG",
      "start_time": 2,
      "duration": 2,
      "text": "Just to suffer...",
      "side": "right"
    }
  ]
}
```

### Top-Level Properties:

-   `canvas_size`: `[width, height]` in pixels for the output video.
-   `background`: Path to the background image file.
-   `music`: Path to the background music file.
-   `fps`: Frames per second for the output video.
-   `output_video`: Filename for the generated video.

### Character Properties:

The `characters` array contains a list of scene objects, each with the following properties:

-   `image`: Path to the character's image file.
-   `start_time`: The time (in seconds) when the scene should start.
-   `duration`: The duration (in seconds) of the scene.
-   `text`: The dialogue text to display for the character.
-   `side`: The side of the screen where the character appears (`"left"` or `"right"`). If `"right"`, the image will be mirrored by default.
-   `rotate`: (Optional) Set to `false` to prevent the image from being mirrored when `side` is `"right"`.
