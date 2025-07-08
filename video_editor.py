import os
from datetime import datetime
from moviepy.editor import CompositeVideoClip, AudioFileClip, afx, ImageClip
from video_utils import create_background_clip, get_char_position

class VideoEditor:
    def __init__(self, config):
        self.config = config
        self.canvas_size = tuple(config.get("canvas_size", [720, 1280]))
        self.fps = config.get("fps", 24)

    def build_video(self, processed_characters):
        duration = max(c["start_time"] + c["duration"] for c in processed_characters)
        bg = create_background_clip(self.config["background"], duration, self.canvas_size)

        scenes = []
        for c in processed_characters:
            char_clip = (ImageClip(c["image_path"])
                         .set_start(c["start_time"])
                         .set_duration(c["duration"])
                         .resize(height=self.canvas_size[1] // 2)
                         .set_position(get_char_position(c.get("side", "left"), self.canvas_size)))

            text_clip = (ImageClip(c["text_image_path"], transparent=True)
                         .set_start(c["start_time"])
                         .set_duration(c["duration"])
                         .set_position(("center", 100)))

            scenes.extend([char_clip, text_clip])

        video = CompositeVideoClip([bg] + scenes, size=self.canvas_size)

        music_path = self.config.get("music")
        if music_path:
            audio = AudioFileClip(music_path)
            if audio.duration < video.duration:
                audio = afx.audio_loop(audio, duration=video.duration)
            else:
                audio = audio.set_duration(video.duration)
            video = video.set_audio(audio)

        return video