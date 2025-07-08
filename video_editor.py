import os
from datetime import datetime
from moviepy.editor import CompositeVideoClip, afx, ImageClip, AudioFileClip
from video_utils import create_background_clip, get_char_position, create_scene_clips

class VideoEditor:
    def __init__(self, config, ImageClip_factory=ImageClip, AudioFileClip_factory=AudioFileClip, CompositeVideoClip_factory=CompositeVideoClip):
        self.config = config
        self.canvas_size = tuple(config.get("canvas_size", [720, 1280]))
        self.fps = config.get("fps", 24)
        self.ImageClip_factory = ImageClip_factory
        self.AudioFileClip_factory = AudioFileClip_factory
        self.CompositeVideoClip_factory = CompositeVideoClip_factory

    def build_video(self, processed_characters):
        duration = max((c["start_time"] + c["duration"] for c in processed_characters), default=0)
        bg = create_background_clip(self.config["background"], duration, self.canvas_size, self.ImageClip_factory)

        scenes = []
        for c in processed_characters:
            scenes.extend(create_scene_clips(
                c["image"],
                c["text_image"],
                c["start_time"],
                c["duration"],
                self.canvas_size,
                c.get("side", "left"),
                self.ImageClip_factory
            ))

        video = self.CompositeVideoClip_factory([bg] + scenes, size=self.canvas_size)

        music_path = self.config.get("music")
        if music_path:
            audio = self.AudioFileClip_factory(music_path)
            if audio.duration < video.duration:
                audio = afx.audio_loop(audio, duration=video.duration)
            else:
                audio = audio.set_duration(video.duration)
            video = video.set_audio(audio)

        return video