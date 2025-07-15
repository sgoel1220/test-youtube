import os
from datetime import datetime
from moviepy.editor import CompositeVideoClip, afx, ImageClip, AudioFileClip, concatenate_videoclips, ColorClip, concatenate_audioclips
from video_utils import create_background_clip, get_char_position, create_scene_clips, create_outro_clip

class VideoEditor:
    def __init__(self, config, ImageClip_factory=ImageClip, AudioFileClip_factory=AudioFileClip, CompositeVideoClip_factory=CompositeVideoClip, ColorClip_factory=ColorClip):
        self.config = config
        self.canvas_size = tuple(config.get("canvas_size", [720, 1280]))
        self.fps = config.get("fps", 24)
        self.ImageClip_factory = ImageClip_factory
        self.AudioFileClip_factory = AudioFileClip_factory
        self.CompositeVideoClip_factory = CompositeVideoClip_factory
        self.ColorClip_factory = ColorClip_factory
        self.background_blur_radius = config.get("background_blur_radius", 0) # Default to 0 (no blur)
        self.outro_overlay_enabled = config.get("outro_overlay_enabled", False)
        self.outro_overlay_opacity = config.get("outro_overlay_opacity", 0.0)
        self.outro_tv_effect_enabled = config.get("outro_tv_effect_enabled", False)
        self.tv_noise_intensity = config.get("tv_noise_intensity", 0.0)
        self.tv_scanline_intensity = config.get("tv_scanline_intensity", 0.0)

    def _create_outro_clips(self, outro_images):
        outro_clips = []
        for outro_config in outro_images:
            img_path = outro_config["image"]
            duration = outro_config.get("duration", 2) # Default to 2 seconds if not specified
            img_clip = create_outro_clip(img_path, duration, self.canvas_size, self.ImageClip_factory, self.ColorClip_factory, self.outro_overlay_enabled, self.outro_overlay_opacity)
            outro_clips.append(img_clip)
        return outro_clips

    def build_video(self, processed_characters, outro_images=None):
        duration = max((c["start_time"] + c["duration"] for c in processed_characters), default=0)
        bg = create_background_clip(self.config["background"], duration, self.canvas_size, self.ImageClip_factory, self.ColorClip_factory, self.background_blur_radius)

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

        if outro_images:
            outro_clips = self._create_outro_clips(outro_images)
            video = concatenate_videoclips([video] + outro_clips)

        music_path = self.config.get("music")
        if music_path:
            dialogue_end_time = max((c['start_time'] + c['duration'] for c in processed_characters), default=0)
            audio = self.AudioFileClip_factory(music_path)

            if audio.duration < video.duration:
                audio = audio.fx(afx.audio_loop, duration=video.duration)
            else:
                audio = audio.set_duration(video.duration)

            # Create a beat drop effect by lowering the volume after the dialogue ends
            beat_drop_time = dialogue_end_time
            final_audio = audio.copy()
            final_audio.subclip(beat_drop_time).volumex(0.2)

            video = video.set_audio(final_audio)

        return video